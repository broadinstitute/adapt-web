<template>
  <transition appear name="fade">
    <div class="results">
      <div v-if="submitted">Job submitted!<br>
      Your run ID is {{runid}}. Store this for future reference.<br>
      Check below for status.</div>
      <ValidationObserver ref="status-form" v-slot="{ handleSubmit }">
        <b-form id="status-form">
          <!-- submit buttons -->
          <b-row>
            <b-col cols=12 md=5>
              <h4 v-show="runids.length">Previous Run IDs</h4>
              <b-list-group>
                <b-list-group-item v-for="runid in runids" :key="runid" button v-on:click.prevent="set_runid(runid)">
                  {{ runid }}
                </b-list-group-item>
              </b-list-group>
              <br>
              <b-button pill block v-on:click.prevent="clearRunID" v-show="runids.length" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="status_submit">Clear Run IDs</b-button>
              <br>
            </b-col>
            <b-col cols=12 md=7>
              <b-form-group
                class="field"
                label="Run ID"
                label-for="runid"
                label-align=left
                label-align-md=right
                label-class="h2"
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
                    :state="getValidationState(validationContext, runid)"
                    aria-describedby="runid-feedback"
                  ></b-form-input>
                  <b-form-invalid-feedback id="runid-feedback">{{ validationContext.errors[0] }}</b-form-invalid-feedback>
                </ValidationProvider>
              </b-form-group>
              <b-button pill block v-on:click.prevent="handleSubmit(run_status)" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="status_submit">Get Status</b-button>
              <b-button pill block v-on:click.prevent="handleSubmit(get_results)" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="download_submit">Download Results</b-button>
              <b-button pill block v-on:click.prevent="handleSubmit(display_results)" size="lg" type="submit" variant="secondary" class="font-weight-bold" name="display_submit">Display Results</b-button>
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
      status: '',
      submitted: false,
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
        this.submitted = true
      }
    }
  },
  methods: {
    async run_status(event) {
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
        let msg = await response.text()
        alert(msg);
      }
      return response
    },
    async display_results(event) {
      // Get results JSON from backend
      // TODO do something with them
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
        this.$root.$emit('display-assays');
      } else {
        let msg = await response.text()
        alert(msg);
      }
      return response
    },
    async get_results(event) {
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
        let msg = await response.text()
        alert(msg);
      }

      return response
    },
    async download_file(response){
      // Helper function to download files
      // i have no idea why this is so complicated but apparently this is how
      // to download a file?? may try to simplify at some point
      let blob = await response.blob()
      let url = window.URL.createObjectURL(new Blob([blob]))
      let link = document.createElement('a')
      link.href = url
      let filename = response.headers.get('content-disposition')
        .split(';')
        .find(n => n.includes('filename='))
        .replace('filename=', '')
        .trim()
      console.log(filename)
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
    },
    getValidationState({failed, valid = null }, input_var) {
      // Only show if field is invalid; don't show if valid
      return !failed ? null : valid;
    },
    clearRunID() {
      Cookies.remove('runid')
      this.runids=[]
      this.runid=''
    },
    set_runid(runid) {
      this.runid = runid
    }
  }
}
</script>
