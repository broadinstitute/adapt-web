<template>
  <transition appear name="fade">
    <div class="results">
      <Modal :success='true' title='Job Submitted!' :msg='submittedmsg'></Modal>
      <Modal :success='false' :title='errortitle' :msg='errormsg'></Modal>
      <ValidationObserver ref="status-form" v-slot="{ handleSubmit }">
        <b-form id="status-form">
          <b-row>
            <b-col cols=12 md=4>
              <div class="h4 font-weight-bold" v-show="runids.length">Previous Runs</div>
              <b-list-group>
                <b-list-group-item v-for="(runid, index) in runids" :key="runid" button v-on:click.prevent.stop.self="setRunID(runid)">
                  {{ runid }}
                  <b-button pill v-on:click.prevent="deleteRunID(index)" variant="outline-danger" class="font-weight-bold" style="float: right;"><b-icon-dash aria-label="Delete" font-scale="1"></b-icon-dash></b-button>
                </b-list-group-item>
              </b-list-group>
              <br>
              <b-button pill block v-on:click.prevent="clearRunID" v-show="runids.length" size="lg" type="button" variant="outline-secondary" class="font-weight-bold" name="clear-ids">Clear Run IDs</b-button>
              <br>
            </b-col>
            <b-col cols=0 md=1>
            </b-col>
            <br>
            <b-col cols=12 md=7>
              <b-form-group
                class="field"
                label="Run ID"
                label-for="runid"
                label-align="left"
                label-align-md="right"
                label-class="h2 font-weight-bold"
              >
                <ValidationProvider
                  vid="runid"
                  rules="required"
                  v-slot="validationContext"
                  name="Run ID"
                  mode="passive"
                >
                  <b-form-input
                    v-model="runid"
                    id="runid"
                    type="text"
                    :state="getValidationState(validationContext)"
                    aria-describedby="runid-feedback"
                  ></b-form-input>
                  <b-form-invalid-feedback id="runid-feedback">{{ validationContext.errors[0] }}</b-form-invalid-feedback>
                </ValidationProvider>
              </b-form-group>
              <b-overlay
                :show="loading=='status'"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="handleSubmit(run_status)" :disabled="loading!=''" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="status_submit">Get Status</b-button>
              </b-overlay>
              <b-overlay
                :show="loading=='download'"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="handleSubmit(get_results)" :disabled="loading!=''" size="lg" type="button" variant="outline-secondary" class="font-weight-bold mt-2" name="download_submit">Download Results</b-button>
              </b-overlay>
              <b-overlay
                :show="loading=='show'"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="handleSubmit(show_results)" :disabled="loading!=''" size="lg" type="button" variant="outline-secondary" class="font-weight-bold mt-2" name="show_submit">Show Results</b-button>
              </b-overlay>
            </b-col>
          </b-row>
          <span v-show="status">Status: {{ status }}</span>
        </b-form>
      </ValidationObserver>
    </div>
  </transition>
</template>

<script>
const Cookies = require('js-cookie')
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')
import {
  ValidationObserver,
  ValidationProvider,
  extend,
} from 'vee-validate';
import {
  required,
} from 'vee-validate/dist/rules';
import Modal from '@/components/Modal.vue'

export default {
  name: 'Results',
  components: {
    ValidationObserver,
    ValidationProvider,
    Modal,
  },
  data () {
    return {
      runids: [],
      runid: '',
      status: '',
      errortitle: '',
      errormsg: '',
      loading: '',
    }
  },
  computed: {
    submittedmsg() {
      return 'Your run ID is <b>' + this.runid + '</b>. Store this for future reference.<br>Use this site to check for its status.'
    }
  },
  mounted () {
    extend('required', {
      ...required,
      message: "The {_field_} is required"
    });
    // Check if a job was just submitted based on cookies
    let runids_str = Cookies.get('runid')
    if (runids_str != null && runids_str != '') {
      this.runids = runids_str.split(',')
      this.runid = this.runids[this.runids.length - 1]
      if (Cookies.get('submitted') == 'true') {
        Cookies.remove('submitted')
        this.$bvModal.show("success-modal")
        }
    }
  },
  methods: {
    async run_status() {
      this.loading = 'status'
      // Check the status of a job from backend
      if (!this.runids.includes(this.runid)) {
        this.runids.push(this.runid)
      }
      let prev_runids = Cookies.get('runid')
      if (prev_runids == null) {
        Cookies.set('runid', this.runid)
      }
      else if (!prev_runids.includes(this.runid)) {
        Cookies.set('runid', prev_runids + ',' + this.runid)
      }

      let response = await fetch('/api/adaptrun/' + this.runid + '/status', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        response = await response.json().then(data => ({
          data: data,
          status: response.status
        }))
        this.status = response.data.status
      } else {
        let contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          let responsejson = await response.json()
          this.errortitle = Object.keys(responsejson)[0]
          this.errormsg = responsejson[this.errortitle]
        }
        else {
          this.errortitle = 'Error'
          this.errormsg = await response.text()
        }
        this.$bvModal.show("error-modal")
      }
      this.loading = ''
      return response
    },
    async show_results(loading) {
      this.loading = loading
      // Get results JSON from backend
      if (!this.runids.includes(this.runid)) {
        this.runids.push(this.runid)
      }
      let prev_runids = Cookies.get('runid')
      if (prev_runids == null) {
        Cookies.set('runid', this.runid)
      }
      else if (!prev_runids.includes(this.runid)) {
        Cookies.set('runid', prev_runids + ',' + this.runid)
      }

      let response = await fetch('/api/adaptrun/' + this.runid + '/results', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        this.$root.$data.resultjson = await response.json()
        this.$root.$data.runid = this.runid
        this.$root.$emit('show-assays');
      } else {
        let responsejson = await response.json()
        this.errortitle = Object.keys(responsejson)[0]
        this.errormsg = responsejson[this.errortitle]
        this.$bvModal.show("error-modal")
      }
      this.loading = ''
      return response
    },
    async get_results() {
      this.loading = 'download'
      // Download results as a TSV or ZIP from backend
      if (!this.runids.includes(this.runid)) {
        this.runids.push(this.runid)
      }
      let prev_runids = Cookies.get('runid')
      if (prev_runids == null) {
        Cookies.set('runid', this.runid)
      }
      else if (!prev_runids.includes(this.runid)) {
        Cookies.set('runid', prev_runids + ',' + this.runid)
      }

      let response = await fetch('/api/adaptrun/' + this.runid + '/download', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
          this.download_file(response)
      } else {
        let responsejson = await response.json()
        this.errortitle = Object.keys(responsejson)[0]
        this.errormsg = responsejson[this.errortitle]
        this.$bvModal.show("error-modal")
      }
      this.loading = ''
      return response
    },
    async download_file(response){
      // Helper function to download files
      let blob = await response.blob()
      let url = window.URL.createObjectURL(new Blob([blob]))
      let link = document.createElement('a')
      link.href = url
      let filename = response.headers.get('content-disposition')
        .split(';')
        .find(n => n.includes('filename='))
        .replace('filename=', '')
        .trim()
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
    },
    getValidationState({failed, valid = null }) {
      // Only show if field is invalid; don't show if valid
      return !failed ? null : valid;
    },
    clearRunID() {
      Cookies.remove('runid')
      this.runids=[]
      this.runid=''
    },
    setRunID(runid) {
      this.runid = runid
    },
    deleteRunID(index) {
      this.runids.splice(index, 1);
      if (this.runids.length > 0) {
        Cookies.set('runid', this.runids.join())
      } else {
        Cookies.remove('runid')
      }
    },
  }
}
</script>
