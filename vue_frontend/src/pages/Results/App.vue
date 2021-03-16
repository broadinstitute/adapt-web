<template>
  <div id="app" class="mb-5">
  <Header/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=2></b-col>
      <b-col  cols=12 md=8>
        <Results class="px-4"/>
        <b-modal id="assay-modal" size="xl" title="Assay Options" hide-footer class="">
          <div id="clusters" v-if="resulttable" :key="updated">
            <div v-for="cluster in Object.keys(resulttable)" :key="cluster">
              <AssayTable :cluster="resulttable[cluster]" :cluster_id="cluster"/>
              <!-- <Assay v-for="result in cluster" :key="result.rank" :result="result" :cluster="cluster"/> -->
            </div>
          </div>
        </b-modal>
      </b-col>
      <b-col cols=0 md=2></b-col>
    </b-row>
  </b-container>
  <Footer/>
  </div>
</template>

<script>
import Vue from 'vue'
import Header from '@/components/Header.vue'
import Results from '@/components/Results.vue'
// import Assay from '@/components/Assay.vue'
import AssayTable from '@/components/AssayTable.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    Results,
    // Assay,
    AssayTable,
    Footer
  },
  data() {
    return {
      resulttable: {},
      updated: 0
    }
  },

  mounted() {
    var vm = this
    this.$root.$on('display-assays', async function() {
      for (var cluster in vm.$root.$data.resultjson) {
        Vue.set(vm.resulttable, cluster, [])
        for (var rank in vm.$root.$data.resultjson[cluster]) {
          vm.resulttable[cluster].push(vm.$root.$data.resultjson[cluster][rank]);
        }
      }
      vm.updated += 1
      this.$bvModal.show("assay-modal")
    })
  }
}
</script>
