<template>
  <div id="app" class="mb-5">
  <Header page="Assays"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
        <transition appear name="fade">
        <b-row class="mb-2 px-3">
          <b-col cols=12 sm=6 offset-sm=3>
            <div class="pb-2"><b-button pill block v-on:click.prevent="display()" size="lg" type="submit" variant="outline-secondary" name="display_submit" :disabled="selectedDesigns.length==0">Show Assays</b-button></div>
          </b-col>
        </b-row>
        </transition>
        <transition appear name="fade">
          <Design class="px-3" parent="pknull"></Design>
        </transition>
       <AssayModal/>
      </b-col>
      <b-col cols=0 md=1></b-col>
    </b-row>
  </b-container>
  <Footer/>
  </div>
</template>

<script>
import Vue from 'vue'
import Header from '@/components/Header.vue'
import Design from '@/components/Design.vue'
import AssayModal from '@/components/AssayModal.vue'
import Footer from '@/components/Footer.vue'
const Cookies = require('js-cookie')
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'App',
  components: {
    Header,
    Design,
    AssayModal,
    Footer
  },
  data() {
    this.$root.$data.selectedDesigns = []
    return {
      selectedDesigns: this.$root.$data.selectedDesigns
    }
  },
  methods : {
    async display() {
      var vm = this
      vm.$root.$data.labels = vm.$root.$data.selectedDesigns
      for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
        var taxon = taxon_and_name[0]
        var cluster = 0
        Vue.set(vm.$root.$data.resulttable, taxon, [])
        while (cluster >= 0) {
          let response = await fetch('/api/assay?taxonrank=' + taxon.slice(2) + '&cluster=' + cluster, {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (response.ok) {
            let resultjson = await response.json()
            if (resultjson.length > 0) {
              vm.$root.$data.resulttable[taxon].push([]);
              for (let rank in resultjson) {
                vm.$root.$data.resulttable[taxon][cluster].push(resultjson[rank]);
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
      this.$root.$emit('show-assays');
    }
  }
}
</script>
