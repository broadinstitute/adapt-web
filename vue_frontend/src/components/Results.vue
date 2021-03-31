<template>
  <transition appear name="fade">
    <div class="results">
      <ValidationObserver ref="status-form" v-slot="{ validate }">
        <b-form id="status-form">
          <b-row>
            <b-col cols=12 md=4>
              <div class="h4 font-weight-bold" v-show="runids.length">Previous Runs</div>
              <b-list-group>
                <b-list-group-item v-for="(runid, index) of runids" :key="runid.id" button v-on:click.prevent.stop.self="setRunID(runid.id)">
                  {{ runid.id }}<br>
                  <i v-on:click.prevent.stop.self="setRunID(runid.id)" class='f-5'>{{ runid.time.toLocaleString() }}</i>
                  <b-button pill v-on:click.prevent="deleteRunID(index)" variant="outline-danger" style="float: right;"><b-icon-dash aria-label="Delete" font-scale="1"></b-icon-dash></b-button>
                </b-list-group-item>
              </b-list-group>
              <br>
              <b-button pill block v-on:click.prevent="clearRunID" v-show="runids.length" size="lg" type="button" variant="outline-secondary" name="clear-ids">Clear Run IDs</b-button>
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
                :show="loading"
                rounded="pill"
                opacity="0.7"
                blur="5px"
                spinner-variant="secondary"
              >
                <b-button pill block v-on:click.prevent="validate().then(valid => {if (valid) {call_server('results')}})" :disabled="loading" size="lg" type="submit" variant="outline-secondary" class="mt-2" name="show_submit">Show Results</b-button>
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
import Vue from 'vue';

export default {
  name: 'Results',
  components: {
    ValidationObserver,
    ValidationProvider,
  },
  data () {
    return {
      runids: [],
      runid: '',
      loading: false,
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
        this.$root.$data.modaltitle = 'Job submitted!'
        this.$root.$data.modalmsg = 'Your run ID is <b>' + this.runid + '</b>. Store this for future reference.<br>Use this site to check for its status.'
        this.$root.$data.modalvariant = 'success'
        this.$bvModal.show("msg-modal")
      }
    }
  },
  methods: {
    async call_server() {
      this.loading = true

      let detail_response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/detail/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      let response
      if (detail_response.ok) {
        let detail_response_json = await detail_response.json();
        switch(detail_response_json.status) {
          case 'Succeeded':
            response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/results/', {
              headers: {
                "X-CSRFToken": csrfToken
              }
            })
            if (response.ok) {
              if (!this.runids.some((runid) => runid.id.includes(this.runid))) {
                this.runids.push({
                  'id': this.runid,
                  'time': new Date(detail_response_json.submit_time)
                })
                this.runids.sort((a,b) => b.time-a.time)
                let prev_runids = Cookies.get('runid')
                if (prev_runids == null) {
                  Cookies.set('runid', this.runid + ';' + detail_response_json.submit_time)
                }
                else if (!prev_runids.includes(this.runid)) {
                  Cookies.set('runid', prev_runids + ',' + this.runid + ';' + detail_response_json.submit_time)
                }
              }
              this.$root.$data.labels = [[this.runid, this.runid]]
              let resultjson = await response.json();
              Vue.set(this.$root.$data.resulttable, this.runid, {})
              for (var cluster in resultjson) {
                Vue.set(this.$root.$data.resulttable[this.runid], cluster, [])
                for (var rank in resultjson[cluster]) {
                  this.$root.$data.resulttable[this.runid][cluster].push(resultjson[cluster][rank]);
                }
              }
              this.$root.$data.runid = this.runid;
              this.$root.$emit('show-assays');
              this.loading = false;
              return response;
            } else {
              this.errorMsg(response);
              this.loading = false;
              return response;
            }
          case 'Failed':
          case 'Aborted':
          case 'Aborting':
            this.$root.$data.modaltitle = 'Job Failed';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' has failed. Please double check your input and try again. If you continue to have issues, contact ppillai@broadinstitute.org.';
            this.$root.$data.modalvariant = 'danger';
            this.$root.$emit('show-msg');
            break;
          case 'Submitted':
            this.$root.$data.modaltitle = 'Job Submitted';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' has been submitted. It will start running soon; please check back later.';
            this.$root.$data.modalvariant = 'dark';
            this.$root.$emit('show-msg');
            break;
          case 'Running':
            this.$root.$data.modaltitle = 'Job Running';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' is running. Jobs can take up to a day to finish running; please check back later.';
            this.$root.$data.modalvariant = 'dark';
            this.$root.$emit('show-msg');
            break;
        }
      } else {
        this.errorMsg(detail_response);
      }
      this.loading = false;
      return detail_response;
    },
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
