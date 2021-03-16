<template>
  <div id="app" class="mb-5">
  <Header/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=2></b-col>
      <b-col cols=12 md=8>
        <transition appear name="fade">
          <div class="pb-4 px-3"><b-button pill block v-on:click.prevent="display" size="lg" type="submit" variant="outline-secondary" class="font-weight-bold" name="display_submit" :disabled="selectedDesigns.length==0">Display Assay Designs</b-button></div>
        </transition>
        <transition appear name="fade">
          <Design class="px-3" parent="pknull"></Design>
        </transition>
        <b-modal id="assay-modal" size="xl" title="Assay Options" hide-footer class="">
          <div id="clusters" v-if="resulttable" :key="updated">
            <div v-for="taxon_and_name in selectedDesigns" :key="taxon_and_name[0]">
              <h2>{{ taxon_and_name[1] }}</h2>
              <div v-for="(cluster, index) in resulttable[taxon_and_name[0]]" :key="index">
                <AssayTable :cluster="cluster" :cluster_id="taxon_and_name[0] + index"/>
              </div>
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
import Design from '@/components/Design.vue'
import AssayTable from '@/components/AssayTable.vue'
import Footer from '@/components/Footer.vue'
const Cookies = require('js-cookie')
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'App',
  components: {
    Header,
    Design,
    AssayTable,
    Footer
  },
  data() {
    this.$root.$data.selectedDesigns = []
    return {
      resulttable: {},
      updated: 0,
      selectedDesigns: this.$root.$data.selectedDesigns
    }
  },
  methods : {
    async display() {
      var vm = this
      vm.resulttable = {}
      for (var taxon_and_name of vm.selectedDesigns) {
        var taxon = taxon_and_name[0]
        var cluster = 0
        Vue.set(vm.resulttable, taxon, [])
        while (cluster >= 0) {
          let response = await fetch('/api/assay?taxonrank=' + taxon.slice(2) + '&cluster=' + cluster, {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (response.ok) {
            let resultjson = await response.json()
            if (resultjson.length > 0) {
              vm.resulttable[taxon].push([]);
              for (let rank in resultjson) {
                vm.resulttable[taxon][cluster].push(resultjson[rank]);
              }
            }
            else {
              break;
            }
          } else {
            let msg = await response.text()
            alert(msg);
          }
          cluster += 1
        }
      }
      vm.updated += 1
      this.$bvModal.show("assay-modal")
    }
  }
}
</script>
