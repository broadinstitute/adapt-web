<template>
  <div id="app" class="mb-5">
  <Header page="Assays"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
        <transition appear name="fade">
          <b-row class="mb-2 px-3 pt-4 mt-2">
            <b-col cols=12 align="center" class="f-1 pb-5">Type in taxa to see crRNA/RPA primer assay designs.</b-col>
            <b-col cols=12><Design class="px-3"></Design></b-col>
          </b-row>
        </transition>
        <transition appear name="fade">
        <b-row class="mb-2 px-3 pt-4 mt-2">
          <b-col cols=12 sm=6 offset-sm=3>
            <b-overlay
              :show="loading"
              rounded="pill"
              opacity="0.7"
              blur="5px"
              spinner-variant="secondary"
            >
              <b-button pill block v-on:click.prevent="display()" size="lg" type="submit" variant="outline-secondary" name="display_submit" :disabled="selectedDesigns.length==0">Show Assays</b-button>
            </b-overlay>
          </b-col>
        </b-row>
        </transition>
       <AssayModal/>
       <Modal/>
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
import Modal from '@/components/Modal.vue'
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
    Modal,
    Footer
  },
  data() {
    this.$root.$data.selectedDesigns = []
    return {
      selectedDesigns: this.$root.$data.selectedDesigns,
      loading: false
    }
  },
  methods : {
    async display() {
      this.loading = true
      var vm = this
      vm.$root.$data.labels = vm.$root.$data.selectedDesigns
      for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
        var taxon = taxon_and_name[0]
        var cluster = 0
        Vue.set(vm.$root.$data.resulttable, taxon, [])
        while (cluster >= 0) {
          let set_response = await fetch('/api/assayset?taxonrank=' + taxon + '&cluster=' + cluster, {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (set_response.ok) {
            let set_resultjson = await set_response.json()
            if (set_resultjson.length > 0) {
              let response = await fetch('/api/assay?assay_set=' + set_resultjson[0]['pk'], {
                headers: {
                  "X-CSRFToken": csrfToken
                }
              })
              if (response.ok) {
                let resultjson = await response.json()
                vm.$root.$data.resulttable[taxon].push([]);
                for (let rank in resultjson) {
                  vm.$root.$data.resulttable[taxon][cluster].push(resultjson[rank]);
                }
              } else {
                this.$root.$data.modaltitle = 'Error'
                this.$root.$data.modalmsg = await response.text()
                this.$root.$data.modalvariant = 'danger'
                this.$root.$emit('show-msg');
              }
            }
            else {
              break;
            }
          } else {
            this.$root.$data.modaltitle = 'Error'
            this.$root.$data.modalmsg = await set_response.text()
            this.$root.$data.modalvariant = 'danger'
            this.$root.$emit('show-msg');
          }
          cluster += 1
        }
      }
      this.$root.$emit('show-assays');
      this.loading = false
    }
  }
}
</script>
