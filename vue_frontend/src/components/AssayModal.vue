<template>
   <b-modal id="assay-modal" size="xl" class="" scrollable :hide-footer="tabIndex > 0">
    <template #modal-header>
      <div class="w-100">
        <b-row><b-col cols=12 lg=4><h5 class="modal-title">Assay Options</h5></b-col><b-col class="text-right pr-3 disclaimer" cols=12 lg=8 style="line-height: 1.1;">
          Assays made for RPA primers and LwaCas13a crRNAs<br>
          Positions based on a multiple sequence alignment of available genomes
        </b-col></b-row>
      </div>
    </template>
    <b-tabs content-class="mt-4" justified pills v-model="tabIndex">
      <b-tab title="Visualization" active>
        <div id="clusters-viz" :key="updated">
          <div v-for="label in labels" :key="label[0]">
            <h2 v-if="label[1]!=''" style="text-align: center;">{{ label[1] }}</h2>
            <div v-for="(cluster, index) in resulttable[label[0]]" :key="index">
              <template v-if='aln_sum[label[0]] && aln_sum[label[0]][index]'>
                <Genome :cluster_id="label[0] + index" :alignmentLength="aln_sum[label[0]][index].length" :assays="cluster" :annotations="ann[label[0]][index]"/>
                <Assay v-for="result in cluster" :key="result.rank" :result="result" :cluster_id="label[0] + index" :aln_sum="aln_sum[label[0]][index]" :genomeHeight="(100 + 8*cluster.length + (ann[label[0]][index].length>0)*40)*(width/800)" :complement="complement" :activityColorScale="activityColorScale" :objectiveColorScale="objectiveColorScale" :entropyColorScale="entropyColorScale"/>
              </template>
              <template v-else>
                <Assay v-for="result in cluster" :key="result.rank" :result="result" :cluster_id="label[0] + index" :aln_sum="[]" :genomeHeight="0" :complement="complement" :activityColorScale="activityColorScale" :objectiveColorScale="objectiveColorScale" :entropyColorScale="entropyColorScale"/>
              </template>
            </div>
          </div>
        </div>
      </b-tab>
      <b-tab title="Table">
        <div id="clusters-table" v-if="resulttable" :key="updated">
          <div v-for="label in labels" :key="label[0]">
            <h2 v-if="label[1]!=''" style="text-align: center;">{{ label[1] }}</h2>
            <br/>
            <div v-for="(cluster, index) in resulttable[label[0]]" :key="index">
              <AssayTable :cluster="cluster" :cluster_id="label[0] + index" :complement="complement"/>
            </div>
          </div>
        </div>
      </b-tab>
       <template #tabs-end>
        <b-nav-item role="presentation" @click.prevent="download_file('download')" href="#">Results <b-icon-download aria-label="Download Results"></b-icon-download></b-nav-item>
        <b-nav-item v-if='aln' role="presentation" @click.prevent="download_file('alignment')" href="#">Alignment <b-icon-download aria-label="Download Alignments"></b-icon-download></b-nav-item>
      </template>
    </b-tabs>
    <template #modal-footer>
      <div class="w-100">
        <ColorLegend :genome="aln" :activityColorScale="activityColorScale" :objectiveColorScale="objectiveColorScale" :entropyColorScale="entropyColorScale"/>
        </div>
    </template>
  </b-modal>
</template>

<script>
// const Cookies = require('js-cookie')
// Needs CSRF for the server to accept the request
// const csrfToken = Cookies.get('csrftoken')
import Assay from '@/components/Assay.vue'
import ColorLegend from '@/components/ColorLegend.vue'
import Genome from '@/components/Genome.vue'
import AssayTable from '@/components/AssayTable.vue'
import * as d3 from "d3";

export default {
  name: 'AssayModal',
  components: {
    Assay,
    ColorLegend,
    Genome,
    AssayTable,
  },
  data() {
    var red = getComputedStyle(document.documentElement)
      .getPropertyValue('--red')
    var orange = getComputedStyle(document.documentElement)
      .getPropertyValue('--orange')
    var lemon = getComputedStyle(document.documentElement)
      .getPropertyValue('--lemon')
    var mint = getComputedStyle(document.documentElement)
      .getPropertyValue('--mint')
    var activityColorScale = d3.scaleLinear()
      .domain([0, 1.5, 3, 4])
      .interpolate(d3.interpolateRgb.gamma(2.2))
      .range([red, orange, lemon, mint])

    var fracBoundColorScale = d3.scaleLinear()
      .domain([0, .375, .75, 1])
      .interpolate(d3.interpolateRgb.gamma(2.2))
      .range([red, orange, lemon, mint])

    var objectiveColorScale = d3.scaleLinear()
      .domain([0, 1.875, 3.75, 5])
      .interpolate(d3.interpolateRgb.gamma(2.2))
      .range([red, orange, lemon, mint])

    var entropyScale = d3.scaleLinear()
      .domain([0, 2])
      .range([0, 1])
    var entropyColorScale = function (t) {
      return d3.interpolatePlasma(entropyScale(t));
    }

    var complement = function (bases, rna=false, reverse=false) {
      let complementBasesArr = Array.prototype.map.call(bases, x => {
        if (x == 'G') {
          return 'C'
        } else if (x == 'C') {
          return 'G'
        } else if (x == 'A') {
          if (rna) {
            return 'U'
          } else {
            return 'T'
          }
        } else {
          return 'A'
        }
      });
      if (reverse) {
        return complementBasesArr.reverse().join('')
      }
      return complementBasesArr.join('')
    }

    return {
      tabIndex: 0,
      resulttable: {},
      labels: [],
      updated: 0,
      aln_sum: {},
      ann: {},
      width: 0,
      "activityColorScale": activityColorScale,
      "fracBoundColorScale": fracBoundColorScale,
      "objectiveColorScale": objectiveColorScale,
      "entropyColorScale": entropyColorScale,
      "complement": complement,
    }
  },
  mounted() {
    var vm = this
    vm.$root.$data.resulttable = {}
    vm.$root.$data.aln_sum = {}
    vm.$root.$data.aln = false;
    vm.$root.$data.ann = {}
    vm.$root.$data.labels = []
    vm.$root.$data.runid = ''
    vm.$root.$on('show-assays', async function() {
      vm.resulttable = vm.$root.$data.resulttable;
      vm.aln_sum = vm.$root.$data.aln_sum
      vm.aln = vm.$root.$data.aln;
      vm.ann = vm.$root.$data.ann;
      vm.labels = vm.$root.$data.labels;
      vm.updated += 1
      vm.$nextTick(async function () {
        await vm.$bvModal.show("assay-modal")
        vm.$nextTick(function () {
          var modalBody = document.getElementsByClassName('modal-body')[0]
          modalBody.addEventListener('scroll', () => {
            vm.width = modalBody.scrollWidth;
          })
        })
        vm.$root.$emit('finish-assays');
      });
    });
    vm.$root.$on('tablelink', function(cluster_id, rank) {
      vm.tabIndex = 1;
      window.location.href = '#table-' + cluster_id + '-' + rank;
    });
    vm.$root.$on('vizlink', function(cluster_id, rank) {
      vm.tabIndex = 0;
      window.location.href = '#anchor-' + cluster_id + '-' + rank;
    });
  },
  methods: {
    async download_file(endpoint) {
      const vm = this
      if (vm.$root.$data.runid==''){
        for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
            this.$plausible.trackEvent(endpoint, {props: {"pk": taxon_and_name[0], "name": taxon_and_name[1]}});
          }
        if (endpoint=='download') {
          let obj = {}
          for (let label of vm.labels) {
            obj[label[1]] = vm.$root.$data.resulttable[label[0]]
          }
          let json = JSON.stringify(obj);
          let url = "data:text/plain;charset=utf-8," + encodeURIComponent(json);
          let filename = 'designs.json'
          let link = document.createElement('a')
          link.href = url
          link.setAttribute('download', filename)
          link.click()
        } else {
          let pks = vm.labels.filter(function (label) {
            return label[0] in vm.aln_sum
          }).map(function (label) {
            return vm.aln_sum[label[0]].pk
          }).join()
          window.open('/api/assayset/' + endpoint + '/?pk=' + pks, '_blank').focus();
        }
      } else {
        window.open('/api/adaptrun/id_prefix/' + vm.$root.$data.runid + '/' + endpoint + '/', '_blank').focus();
      }
    },
    linkToTable(cluster_id, rank) {
      this.tabIndex = 1;
      window.location.href = '#table-' + cluster_id + '-' + rank;
    },
  }
}
</script>
<style>
.modal-footer {
  box-shadow: 0 6px 10px 2px rgba(0,0,0,0.2);
}
</style>
