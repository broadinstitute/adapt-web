<template>
   <b-modal id="assay-modal" size="xl" title="Assay Options" hide-footer class="" scrollable>
    <b-tabs content-class="mt-4" justified pills>
      <b-tab title="Visualization" active>
        <div id="clusters-viz" :key="updated">
          <div v-for="label in labels" :key="label[0]">
            <h2 v-if="label[1]!=''" style="text-align: center;">{{ label[1] }}</h2>
            <div v-for="(cluster, index) in resulttable[label[0]]" :key="index">
              <template v-if='aln_sum[label[0]]'>
                <Genome :cluster_id="label[0] + index" :alignmentLength="aln_sum[label[0]][index].length" :assays="cluster" :annotations="[]"/>
                <Assay v-for="result in cluster" :key="result.rank" :result="result" :cluster_id="label[0] + index" :aln_sum="aln_sum[label[0]][index]" :genomeHeight="(20 + 20*cluster.length + (annotations.length>0)*80)*(width/800)" :activityColorScale="activityColorScale" :fracBoundColorScale="fracBoundColorScale" :objectiveColorScale="objectiveColorScale"/>
              </template>
              <template v-else>
                <Assay v-for="result in cluster" :key="result.rank" :result="result" :cluster_id="label[0] + index" :aln_sum="[]" :genomeHeight="0" :activityColorScale="activityColorScale" :fracBoundColorScale="fracBoundColorScale" :objectiveColorScale="objectiveColorScale"/>
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
              <AssayTable :cluster="cluster" :cluster_id="label[0] + index"/>
            </div>
          </div>
        </div>
      </b-tab>
       <template #tabs-end>
        <b-nav-item role="presentation" @click.prevent="download_file('download')" href="#">Results <b-icon-download aria-label="Download"></b-icon-download></b-nav-item>
        <b-nav-item v-if='alignment' role="presentation" @click.prevent="download_file('alignment')" href="#">Alignment <b-icon-download aria-label="Download"></b-icon-download></b-nav-item>
      </template>
    </b-tabs>
  </b-modal>
</template>

<script>
const Cookies = require('js-cookie')
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')
// import Vue from 'vue'
import Assay from '@/components/Assay.vue'
import Genome from '@/components/Genome.vue'
import AssayTable from '@/components/AssayTable.vue'
import * as d3 from "d3";

export default {
  name: 'AssayModal',
  components: {
    Assay,
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
      .domain([0, 1.95, 3.9, 5.2])
      .interpolate(d3.interpolateRgb.gamma(2.2))
      .range([red, orange, lemon, mint])

    return {
      resulttable: {},
      labels: [],
      updated: 0,
      alignment: false,
      aln_sum: {},
      width: 0,
      "activityColorScale": activityColorScale,
      "fracBoundColorScale": fracBoundColorScale,
      "objectiveColorScale": objectiveColorScale,
    }
  },
  mounted() {
    this.$root.$data.resulttable = {}
    this.$root.$data.labels = []
    this.$root.$data.runid = ''
    this.$root.$data.alignment = false
    this.$root.$data.annotations = []
    var vm = this
    vm.$root.$on('show-assays', async function() {
      vm.resulttable = vm.$root.$data.resulttable;
      vm.labels = vm.$root.$data.labels;
      vm.alignment = vm.$root.$data.alignment;
      if (vm.alignment) {
        await vm.summarize_alignment()
      }
      vm.annotations = vm.$root.$data.annotations;
      vm.updated += 1
      vm.$nextTick(async function () {
        await vm.$bvModal.show("assay-modal")
        vm.$nextTick(function () {
          document.getElementById('clusters-viz').addEventListener('click', () => {
            vm.width = document.getElementsByClassName('modal-body')[0].scrollWidth;
          })
        })
        vm.$root.$emit('finish-assays');
      });
    })
  },
  methods: {
    async download_file(endpoint) {
      let url
      let filename
      if (this.$root.$data.runid=='') {
        let obj = {}
        for (let label of this.labels) {
          obj[label[1]] = this.$root.$data.resulttable[label[0]]
        }
        let json = JSON.stringify(obj);
        url = "data:text/plain;charset=utf-8," + encodeURIComponent(json);
        filename = 'designs.json'
      } else {
        let response = await fetch('/api/adaptrun/id_prefix/' + this.$root.$data.runid + '/' + endpoint + '/', {
          headers: {
            "X-CSRFToken": csrfToken
          }
        })
        if (response.ok) {
          let blob = await response.blob()
          url = window.URL.createObjectURL(new Blob([blob]))
          filename = response.headers.get('content-disposition')
            .split(';')
            .find(n => n.includes('filename='))
            .replace('filename=', '')
            .trim()
        } else {
          let contentType = response.headers.get("content-type");
          if (contentType && contentType.indexOf("application/json") !== -1) {
            let response_json = await response.json()
            this.$root.$data.modaltitle = Object.keys(response_json)[0]
            this.$root.$data.modalmsg = response_json[this.$root.$data.modaltitle]
          }
          else {
            this.$root.$data.modaltitle = 'Error'
            this.$root.$data.modalmsg = await response.text()
          }
          this.$root.$data.modalvariant = 'danger'
          this.$bvModal.show("msg-modal")
          return
        }
      }
      let link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      link.click()
    },
    async summarize_alignment() {
      if (this.$root.$data.runid=='') {
        return
      } else {
        let response = await fetch('/api/adaptrun/id_prefix/' + this.$root.$data.runid + '/alignment_summary/', {
          headers: {
            "X-CSRFToken": csrfToken
          }
        })
        if (response.ok) {
          this.aln_sum[this.$root.$data.runid] = await response.json()
        } else {
          let contentType = response.headers.get("content-type");
          if (contentType && contentType.indexOf("application/json") !== -1) {
            let response_json = await response.json()
            this.$root.$data.modaltitle = Object.keys(response_json)[0]
            this.$root.$data.modalmsg = response_json[this.$root.$data.modaltitle]
          }
          else {
            this.$root.$data.modaltitle = 'Error'
            this.$root.$data.modalmsg = await response.text()
          }
          this.$root.$data.modalvariant = 'danger'
          this.$bvModal.show("msg-modal")
        }
      }
    },
  }
}
</script>
