<template>
  <div id="app" class="mb-5">
  <Header page="Assays"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
        <transition appear name="fade">
          <!--Extra row needed as Design needs to be in its own column (and helps with spacing)-->
          <b-row class="mb-2 px-3 pt-4 mt-2">
            <b-col cols=12><Design class="px-3"></Design></b-col>
          </b-row>
        </transition>
        <!--Button-->
        <transition appear name="fade">
          <div class="pb-2 float bottom right">
            <!--Loading overlay-->
            <b-overlay
              :show="loading"
              rounded="pill"
              opacity="0.7"
              blur="5px"
              spinner-variant="secondary"
            >
              <b-button pill block v-on:click.prevent="displayWrap()" type="submit" variant="secondary" name="display_submit" :class="[{'hide': selectedDesigns.length==0}, 'fade-enter-active', 'btn-xl']" :disabled="selectedDesigns.length==0 || loading">Show Assays</b-button>
            </b-overlay>
          </div>
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
    // Designs which have been selected for display (updated by Design component)
    this.$root.$data.selectedDesigns = []
    // List of taxons from which to select (filled in by Design component)
    this.$root.$data.all_taxons = {}
    return {
      // Allow root data to be accessible to this component in the HTML above
      selectedDesigns: this.$root.$data.selectedDesigns,
      all_taxons: this.$root.$data.all_taxons,
      // Note whether or not the page is loading
      loading: false,
    }
  },
  methods : {
    /**
     * Prepare to display the assay modal, then display the assay modal
     *
     * Emit 'show-assays' for AssayModal component to show up
     * Also, send a message to Plausible that this taxon was displayed
     */
    async displayWrap() {
      var vm = this
      vm.display().then(() => {
        vm.$root.$emit('show-assays');
        vm.loading = false;
        for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
          this.$plausible.trackEvent('display', {props: {pk: taxon_and_name[0], name: taxon_and_name[1]}});
        }
      });
    },
    /**
     * Load the assays for selected taxons
     *
     * Selected taxons in this.$root.$data.selectedDesigns as (taxonrank primary key, taxonrank latin name)
     */
    async display() {
      this.loading = true
      var vm = this
      vm.$root.$data.labels = vm.$root.$data.selectedDesigns
      vm.$root.$data.aln = false;
      // Loop through all the taxons selected and load the data
      for (var taxon_and_name of vm.$root.$data.selectedDesigns) {
        var taxon = taxon_and_name[0]
        var cluster = 0
        Vue.set(vm.$root.$data.resulttable, taxon, [])
        // Check clusters until one does not return any assays
        while (cluster >= 0) {
          // Fetch assay sets for this taxon/cluster
          let set_response = await fetch('/api/assayset?taxonrank=' + taxon + '&cluster=' + cluster, {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (set_response.ok) {
            let set_resultjson = await set_response.json()
            if (set_resultjson.length > 0) {
              // There is at least one assay set for this taxon/cluster; get the assays for the first (most recent) one
              let response = await fetch('/api/assay?assay_set=' + set_resultjson[0]['pk'], {
                headers: {
                  "X-CSRFToken": csrfToken
                }
              })
              if (response.ok) {
                let resultjson = await response.json()
                // Add a list to the result table for the cluster we are on.
                vm.$root.$data.resulttable[taxon].push([]);
                for (let rank in resultjson) {
                  // Add an assay to the taxon/cluster of the result table
                  vm.$root.$data.resulttable[taxon][cluster].push(resultjson[rank]);
                }
                // If there is an alignment, get it and store that information
                // Note: set_resultjson[0]['pk'] is the primary key of the assay set
                // TODO: summarize_alignment does not handle multiple clusters correctly
                if (set_resultjson[0]['s3_aln_path'] != "") {
                  await vm.summarize_alignment(set_resultjson[0]['pk'], taxon)
                  vm.$root.$data.aln = true;
                }
                // If there are annotations, get them and store that information
                // Note: set_resultjson[0]['pk'] is the primary key of the assay set
                // TODO: get_annotation does not handle multiple clusters correctly
                //       though the else condition does partially
                if (set_resultjson[0]['s3_ann_path'] != "") {
                  await vm.get_annotation(set_resultjson[0]['pk'], taxon)
                } else {
                  if (!(taxon in this.$root.$data.ann)) {
                    this.$root.$data.ann[taxon] = {}
                  }
                  this.$root.$data.ann[taxon][cluster] = []
                }
              } else {
                // Some error has occurred when getting the assays; report it
                vm.errorMsg(response)
              }
            }
            else {
              // This cluster doesn't have any assays; break out of the loop
              break;
            }
          } else {
            // Some error has occurred when getting the assay set; report it
            vm.errorMsg(set_response)
            break;
          }
          cluster += 1
        }
      }
    },
    /**
     * Get the annotations of the alignment
     *
     * Stored in this.$root.$data.ann[taxon]
     *
     * @param {Number} pk - The primary key of a assay set
     * @param {Number} taxon - The primary key of the taxonrank of that assay set
     */
    async get_annotation(pk, taxon) {
      let response = await fetch('/api/assayset/' + pk + '/annotation/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        if (!(taxon in this.$root.$data.ann)) {
          this.$root.$data.ann[taxon] = {}
        }
        this.$root.$data.ann[taxon] = await response.json()
      } else {
        this.errorMsg(response)
      }
    },
    /**
     * Get the summary of the alignment of an assay set
     *
     * Stored in this.$root.$data.aln_sum[taxon]
     *
     * @param {Number} pk - The primary key of a assay set
     * @param {Number} taxon - The primary key of the taxonrank of that assay set
     */
    async summarize_alignment(pk, taxon) {
      // Only get the alignment summary if it doesn't yet exist
      if (!(taxon in this.$root.$data.aln_sum)) {
        let response = await fetch('/api/assayset/' + pk + '/alignment_summary/', {
          headers: {
            "X-CSRFToken": csrfToken
          }
        })
        if (response.ok) {
          this.$root.$data.aln_sum[taxon] = await response.json()
          this.$root.$data.aln_sum[taxon].pk = pk
        } else {
          // This can time out, so don't raise an error, just show nothing for the alignment summary
          this.$root.$data.aln_sum[taxon] = {}
          this.$root.$data.aln_sum[taxon].pk = pk
        }
      }
    },
    /**
     * Show an error message
     *
     * @param {Response} response - HTML response with error message
     */
    async errorMsg(response) {
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
      this.$root.$emit('show-msg');
    },
  }
}
</script>
