<template>
  <transition appear name="fade">
    <div class="results">
      <Modal :variant='variant' :title='modaltitle' :msg='modalmsg'></Modal>
      <ValidationObserver ref="status-form" v-slot="{ validate }">
        <b-form id="status-form">
          <b-row>
            <b-col cols=12 md=4>
              <div class="h4 font-weight-bold" v-show="runids.length">Previous Runs</div>
              <b-list-group>
                <b-list-group-item v-for="(runid, index) of runids" :key="runid.id" button v-on:click.prevent.stop.self="setRunID(runid.id)">
                  {{ runid.id }}<br>
                  <i class='f-5'>{{ runid.time.toLocaleString() }}</i>
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
                <b-button pill block v-on:click.prevent="validate().then(valid => {if (valid) {call_server('status')}})" :disabled="loading!=''" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="status_submit">Get Status</b-button>
              </b-overlay>
              <b-overlay
                :show="loading=='download'"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="validate().then(valid => {if (valid) {call_server('download')}})" :disabled="loading!=''" size="lg" type="button" variant="outline-secondary" class="font-weight-bold mt-2" name="download_submit">Download Results</b-button>
              </b-overlay>
              <b-overlay
                :show="loading=='show'"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="validate().then(valid => {if (valid) {call_server('results')}})" :disabled="loading!=''" size="lg" type="button" variant="outline-secondary" class="font-weight-bold mt-2" name="show_submit">Show Results</b-button>
              </b-overlay>
            </b-col>
          </b-row>
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
      modaltitle: '',
      modalmsg: '',
      loading: '',
      variant: '',
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
      for (let runid_str of runids_str.split(',')) {
        let runid_parts = runid_str.split(';')
        this.runids.push({
          'id': runid_parts[0],
          'time': new Date(runid_parts[1])
        })
      }
      this.runids.sort((a,b) => b.time-a.time)
      this.runid = this.runids[0].id
      if (Cookies.get('submitted') == 'true') {
        Cookies.remove('submitted')
        this.modaltitle = 'Job submitted!'
        this.modalmsg = 'Your run ID is <b>' + this.runid + '</b>. Store this for future reference.<br>Use this site to check for its status.'
        this.variant = 'success'
        this.$bvModal.show("msg-modal")
        }
    }
  },
  methods: {
    async call_server(action) {
      this.loading = action

      let response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/' + action, {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })

      if (response.ok) {
        if (!this.runids.some((runid) => runid.id.includes(this.runid))) {
          let detail_response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/detail', {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (detail_response.ok) {
            let date_str = await detail_response.json().then(data => data.submit_time)
            this.runids.push({
              'id': this.runid,
              'time': new Date(date_str)
            })
            this.runids.sort((a,b) => b.time-a.time)
            let prev_runids = Cookies.get('runid')
            if (prev_runids == null) {
              Cookies.set('runid', this.runid + ';' + date_str)
            }
            else if (!prev_runids.includes(this.runid)) {
              Cookies.set('runid', prev_runids + ',' + this.runid + ';' + date_str)
            }
          }
        }

        switch(action) {
          case 'status':
            response = await response.json().then(data => ({
              data: data,
              status: response.status
            }));
            switch(response.data.status) {
              case 'Succeeded':
                this.modaltitle = 'Job Succeeded';
                this.modalmsg = 'Run ' + this.runid + ' has finished running. Use "Show Results" to see the output.';
                this.variant = 'success';
                this.$bvModal.show("msg-modal");
                break;
              case 'Failed':
                this.modaltitle = 'Job Failed';
                this.modalmsg = 'Run ' + this.runid + ' has failed. Please double check your input and try again. If you continue to have issues, contact ppillai@broadinstitute.org.';
                this.variant = 'danger';
                this.$bvModal.show("msg-modal");
                break;
            }
            break;
          case 'results':
            this.$root.$data.resultjson = await response.json();
            this.$root.$data.runid = this.runid;
            this.$root.$emit('show-assays');
            break;
          case 'download':
            this.download_file(response)
            break;
        }
      } else {
        let contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          let responsejson = await response.json()
          this.modaltitle = Object.keys(responsejson)[0]
          this.modalmsg = responsejson[this.modaltitle]
        }
        else {
          this.modaltitle = 'Error'
          this.modalmsg = await response.text()
        }
        this.variant = 'danger'
        this.$bvModal.show("msg-modal")
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
    },
    setRunID(runid) {
      this.runid = runid
    },
    deleteRunID(index) {
      this.runids.splice(index, 1);
      if (this.runids.length > 0) {
        let runid_strs = []
        for (let runid of this.runids) {
          runid_strs.push(runid.id + ';' + runid.time.toISOString())
        }
        Cookies.set('runid', runid_strs.join())
      } else {
        Cookies.remove('runid')
      }
    },
  }
}
</script>
