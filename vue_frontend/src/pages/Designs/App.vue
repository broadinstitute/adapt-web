<template>
  <div id="app" class="mb-5">
  <Header page="Assays"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
        <transition appear name="fade">
          <div class="pb-2 float bottom right">
            <b-overlay
              :show="loading"
              rounded="pill"
              opacity="0.7"
              blur="5px"
              spinner-variant="secondary"
            >
              <b-button pill block v-on:click.prevent="display()" type="submit" variant="secondary" name="display_submit" :class="[{'hide': selectedDesigns.length==0}, 'fade-enter-active', 'btn-xl']" :disabled="selectedDesigns.length==0 || loading">Show Assays</b-button>
            </b-overlay>
          </div>
        </transition>
        <transition appear name="fade">
          <b-row>
            <b-col cols=12 align="center" class="f-4 pb-5">Select taxa to see crRNA/RPA primer assay designs. Click on arrows to see subtaxa. Only taxa in purple have designs.</b-col>
            <b-col cols=12>
              <Design class="px-3" style="width: 100%"></Design>
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
    this.$root.$data.all_taxons = {}
    return {
      selectedDesigns: this.$root.$data.selectedDesigns,
      all_taxons: this.$root.$data.all_taxons,
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
          let set_response = await fetch('/api/assayset?taxonrank=' + taxon.slice(2) + '&cluster=' + cluster, {
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
