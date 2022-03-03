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
                  <b v-if="runid.nickname!=''" v-on:click.prevent.stop.self="setRunID(runid.id)" class='f-3'>{{ runid.nickname }}<br></b>
                  {{ runid.id }}<br>
                  <i v-on:click.prevent.stop.self="setRunID(runid.id)" class='f-5'>{{ runid.time.toLocaleString() }}</i>
                  <b-button pill v-on:click.prevent="deleteRunID(index)" variant="outline-danger" style="float: right;"><b-icon-dash aria-label="Delete" font-scale="1"></b-icon-dash></b-button>
                </b-list-group-item>
              </b-list-group>
              <b-button pill block v-on:click.prevent="clearRunID" v-show="runids.length" size="lg" type="button" variant="outline-secondary" class="mt-3" name="clear-ids">Clear Run IDs</b-button>
              <div class="text-center" v-show="runids.length == 0">
                <br>
                <h5>No previous runs</h5>
                <br>
                <p>Check out the <a href="/run">Run page</a> to try running ADAPT yourself.</p>
                <p>Type "<a href="" v-on:click.prevent.stop.self="setRunID('example-success')">example-success</a>" as a Run ID to see an example of what ADAPT's output looks like.</p>
              </div>
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
                aria-describedby="runid-help"
              >
                <b-form-text id="runid-help" class="text-md-right pb-1"><i>Type in "example-success" to see the output of a successful run.</i></b-form-text>
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
                <b-button pill block v-on:click.prevent="validate().then(valid => {if (valid) {callServerWrap()}})" :disabled="loading" size="lg" type="submit" variant="outline-secondary" class="mt-2" name="show_submit">Show Results</b-button>
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
      nickname: '',
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
          'time': new Date(runid_parts[1]),
          'nickname': runid_parts[2]
        })
      }
      this.runids.sort((a,b) => b.time-a.time)
      this.runid = this.runids[0].id
      this.nickname = this.runids[0].nickname
      if (Cookies.get('submitted') == 'true') {
        Cookies.remove('submitted')
        this.$root.$data.modaltitle = 'Job submitted!'
        this.$root.$data.modalmsg = 'Your run ID is <b>' + this.runid + '</b>. Store this for future reference.<br>Use this site to check for its status.'
        this.$root.$data.modalvariant = 'success'
        this.$nextTick(function() {
          this.$root.$emit('show-msg');
        })
      }
    }
  },
  methods: {
    async callServerWrap() {
      var vm = this
      vm.callServer().then(success => {
        if (success) {
          vm.$root.$emit('show-assays');
          vm.$root.$on('finish-assays', () => {vm.loading=false});
        } else {
          vm.loading=false
        }
      })
    },
    async callServer() {
      this.loading = true

      let detail_response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/detail/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      let response
      if (detail_response.ok) {
        let detail_response_json = await detail_response.json();
        if (detail_response_json.nickname != '') {
          this.nickname = detail_response_json.nickname
        } else {
          this.nickname = this.runid
        }
        switch(detail_response_json.status) {
          case 'Submitted':
            this.$root.$data.modaltitle = 'Job Submitted';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' has been submitted. It will start running soon; please check back later.';
            this.$root.$data.modalvariant = 'dark';
            this.$root.$emit('show-msg');
            this.updateRunIDs(detail_response_json.submit_time, detail_response_json.nickname);
            break;
          case 'Running':
            this.$root.$data.modaltitle = 'Job Running';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' is running. Jobs can take up to a day to finish running; please check back later.';
            this.$root.$data.modalvariant = 'dark';
            this.$root.$emit('show-msg');
            this.updateRunIDs(detail_response_json.submit_time, detail_response_json.nickname);
            break;
          case 'Succeeded':
            response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/results/', {
              headers: {
                "X-CSRFToken": csrfToken
              }
            })
            if (response.ok) {
              this.$root.$data.labels = [[this.runid, this.nickname]]
              let resultjson = await response.json();
              Vue.set(this.$root.$data.resulttable, this.runid, {})
              for (var cluster in resultjson) {
                Vue.set(this.$root.$data.resulttable[this.runid], cluster, [])
                for (var rank in resultjson[cluster]) {
                  this.$root.$data.resulttable[this.runid][cluster].push(resultjson[cluster][rank]);
                }
              }
              this.$root.$data.runid = this.runid;
              this.$root.$data.aln = false;
              if (detail_response_json.alignment) {
                await this.summarize_alignment()
                this.$root.$data.aln = true;
              }
              await this.get_annotation()
              this.updateRunIDs(detail_response_json.submit_time, detail_response_json.nickname);
              return true;
            } else {
              this.errorMsg(response);
            }
            this.updateRunIDs(detail_response_json.submit_time, detail_response_json.nickname);
            break;
          case 'Failed':
          case 'Aborted':
          case 'Aborting':
            this.$root.$data.modaltitle = 'Job Failed';
            this.$root.$data.modalmsg = 'Run ' + this.runid + ' has failed due to ';
            switch(detail_response_json.fail_caused_by) {
              case 'Memory':
                this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat('running out of memory. Try increasing the memory setting in the "Advanced" options on the Run page and then submitting again.')
              break;
              case 'No sequences':
                this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat('our database of viral sequences (<a href="https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10239">NCBI\'s Viral Genome Database</a>) not containing any complete genomes for this virus. Try uploading a FASTA of the sequences you would like to detect.')
              break;
              case 'Busy':
                this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat('our servers being busy. Try waiting for a few hours and then submitting again.')
              break;
              case 'No references':
                this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat('our database of viral sequences (<a href="https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10239">NCBI\'s Viral Genome Database</a>) not containing reference sequences for this virus, meaning we cannot automatically curate based on sequence quality. Try uploading a FASTA of the sequences you would like to detect.')
              break;
              default:
                this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat('an unknown reason. Please double check your input parameters; if you uploaded a file, this could be due to incorrect formatting.')
              break;
            }
            this.$root.$data.modalmsg = this.$root.$data.modalmsg.concat(' If you continue to have issues, contact adapt@broadinstitute.org with your run ID.')
            this.$root.$data.modalvariant = 'danger';
            this.$root.$emit('show-msg');
            this.updateRunIDs(detail_response_json.submit_time, detail_response_json.nickname)
            break;
        }
      } else {
        this.errorMsg(detail_response);
      }
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
      this.runids = []
    },
    setRunID(runid) {
      this.runid = runid
    },
    updateRunIDs(submit_time, nickname) {
      if (!this.runids.some((runid) => runid.id.includes(this.runid))) {
        this.runids.push({
          'id': this.runid,
          'time': new Date(submit_time),
          'nickname': nickname
        })
        this.runids.sort((a,b) => b.time-a.time)
        let prev_runids = Cookies.get('runid')
        if (prev_runids == null) {
          Cookies.set('runid', this.runid + ';' + submit_time + ';' + nickname)
        }
        else if (!prev_runids.includes(this.runid)) {
          Cookies.set('runid', prev_runids + ',' + this.runid + ';' + submit_time + ';' + nickname)
        }
      }
    },
    deleteRunID(index) {
      this.runids.splice(index, 1);
      if (this.runids.length > 0) {
        let runid_strs = []
        for (let runid of this.runids) {
          runid_strs.push(runid.id + ';' + runid.time.toISOString() + ';' + runid.nickname)
        }
        Cookies.set('runid', runid_strs.join())
      } else {
        Cookies.remove('runid')
      }
    },
    async summarize_alignment() {
      if (!(this.runid in this.$root.$data.aln_sum)) {
        let response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/alignment_summary/', {
          headers: {
            "X-CSRFToken": csrfToken
          }
        })
        if (response.ok) {
          this.$root.$data.aln_sum[this.runid] = await response.json()
        } else {
          this.errorMsg(response)
        }
      }
    },
    async get_annotation() {
      let response = await fetch('/api/adaptrun/id_prefix/' + this.runid + '/annotation/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        this.$root.$data.ann[this.runid] = await response.json()
        if (Object.keys(this.$root.$data.ann[this.runid]).length === 0) {
          this.$root.$data.ann[this.runid] = {0: []}
        }
      } else if (response.status != 400) {
        this.errorMsg(response)
      } else {
        this.$root.$data.ann[this.runid] = {0: []}
      }
    },
  }
}
</script>
