<template>
   <b-modal id="assay-modal" size="xl" class="" scrollable :hide-footer="tabIndex > 0">
    <!--Header-->
    <template #modal-header>
      <div class="w-100">
        <b-row><b-col cols=12 lg=4><h5 class="modal-title">Assay Options</h5></b-col><b-col class="text-right pr-3 disclaimer" cols=12 lg=8 style="line-height: 1.1;">
          Assays made for RPA primers and LwaCas13a crRNAs<br>
          Positions based on a multiple sequence alignment of available genomes
        </b-col></b-row>
      </div>
    </template>
    <!--Tabs (Visualization, Table, Download Links)-->
    <b-tabs content-class="mt-4" justified pills v-model="tabIndex">
      <b-tab title="Visualization" active>
        <div id="clusters-viz" :key="updated">
          <!--Loop through either taxa or runs that are being displayed-->
          <div v-for="label in labels" :key="label[0]">
            <h2 v-if="label[1]!=''" style="text-align: center;">{{ label[1] }}</h2>
            <!--Loop through clusters-->
            <div v-for="(cluster, index) in resulttable[label[0]]" :key="index">
              <!--If there is an alignment, show the genome-->
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
          <!--Loop through either taxa or runs that are being displayed-->
          <div v-for="label in labels" :key="label[0]">
            <h2 v-if="label[1]!=''" style="text-align: center;">{{ label[1] }}</h2>
            <br/>
            <!--Loop through clusters-->
            <div v-for="(cluster, index) in resulttable[label[0]]" :key="index">
              <AssayTable :cluster="cluster" :cluster_id="label[0] + index" :complement="complement"/>
            </div>
          </div>
        </div>
      </b-tab>
       <template #tabs-end>
        <!--Download links for the results and alignment if it exists-->
        <b-nav-item role="presentation" @click.prevent="download_file('download')" href="#">Results <b-icon-download aria-label="Download Results"></b-icon-download></b-nav-item>
        <b-nav-item v-if='aln' role="presentation" @click.prevent="download_file('alignment')" href="#">Alignment <b-icon-download aria-label="Download Alignments"></b-icon-download></b-nav-item>
      </template>
    </b-tabs>
    <!--Footer (just color legend)-->
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
    // Set the color scales for the legend
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

    /**
     * Get the complement of a nucleic acid sequence
     *
     * Shared function between the assay table and the assay
     *
     * @param {String} bases - String of bases to complement
     * @param {Boolean} rna - Whether or not it is RNA
     * @param {String} reverse - Whether or not to alse reverse the string
     */
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
      // Identifies which tab is active
      tabIndex: 0,
      // Stores the assays for all the taxa/runs
      resulttable: {},
      // Stores the taxa/runs to display
      labels: [],
      // Makes sure the content of the modal is updated when the data is updated
      updated: 0,
      // Stores the alignment summaries
      aln_sum: {},
      // Stores the annotations
      ann: {},
      // Stores the width of the modal to size the visualizations
      width: 0,
      // Stores the color scales
      "activityColorScale": activityColorScale,
      "fracBoundColorScale": fracBoundColorScale,
      "objectiveColorScale": objectiveColorScale,
      "entropyColorScale": entropyColorScale,
      // Stores the complement functions
      "complement": complement,
    }
  },
  mounted() {
    var vm = this
    // Iniitalize these variables to make sure they can be updated by other components
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
      // Increase updated to make sure the content of the modal updates
      vm.updated += 1
      // Show modal after data is updated
      vm.$nextTick(async function () {
        await vm.$bvModal.show("assay-modal")
        vm.$nextTick(function () {
          var modalBody = document.getElementsByClassName('modal-body')[0]
          // Make sure the width updates depending on the width of the component
          modalBody.addEventListener('scroll', () => {
            vm.width = modalBody.scrollWidth;
          })
        })
        // Indicate the assays have finished loading so other components don't need to stay in the loading state
        vm.$root.$emit('finish-assays');
      });
    });
    // Listens when the 'More Details' link is clicked in the visualization to go to the table
    vm.$root.$on('tablelink', function(cluster_id, rank) {
      vm.tabIndex = 1;
      window.location.href = '#table-' + cluster_id + '-' + rank;
    });
    // Listens when the 'Visualization' link is clicked in the table to go to the visualization
    vm.$root.$on('vizlink', function(cluster_id, rank) {
      vm.tabIndex = 0;
      window.location.href = '#anchor-' + cluster_id + '-' + rank;
    });
  },
  methods: {
    async download_file(endpoint) {
      const vm = this
      if (vm.$root.$data.runid=='') {
        // If the run id is empty, these are taxa to download
        // Record when a taxa is downloaded
        for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
          this.$plausible.trackEvent(endpoint, {props: {"pk": taxon_and_name[0], "name": taxon_and_name[1]}});
        }
        // Download the results in a JSON
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
          // Download the alignment
          let pks = vm.labels.filter(function (label) {
            return label[0] in vm.aln_sum
          }).map(function (label) {
            return vm.aln_sum[label[0]].pk
          }).join()
          window.open('/api/assayset/' + endpoint + '/?pk=' + pks, '_blank').focus();
        }
      } else {
        // If it's a run, download from the API endpoint
        window.open('/api/adaptrun/id_prefix/' + vm.$root.$data.runid + '/' + endpoint + '/', '_blank').focus();
      }
    },
  }
}
</script>
<style>
.modal-footer {
  box-shadow: 0 6px 10px 2px rgba(0,0,0,0.2);
}
</style>
