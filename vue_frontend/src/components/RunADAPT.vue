<template>
  <div class="runadapt">
    <b-form id="full-form" @submit="adapt_run" class="mx-3 px-3">
      <b-form-group
        class="sec"
        v-for="(sec, i) in Object.keys(inputs)"
        :label="inputs[sec].label ? inputs[sec].label : ''"
        :key="i"
        :id="sec"
      >
        <b-form-group
          class="subsec"
          v-for="(subsec, j) in get_sub(Object.keys(inputs[sec]))"
          v-show="inputs[sec][subsec].show"
          :label="inputs[sec][subsec].label ? inputs[sec][subsec].label : ''"
          label-cols-lg=3
          :key="j"
          :id="subsec"
        >
          <div v-show="inputs[sec][subsec].show">
            <b-form-group
              class="field"
              v-for="(input_var, k) in get_sub(Object.keys(inputs[sec][subsec]))"
              :key="k"
              :label="inputs[sec][subsec][input_var].label"
              :label-for="input_var"
              label-cols-md=4
              content-cols-md=8
              label-align=left
              label-align-md=right
            >
              <b-form-file
                v-if="inputs[sec][subsec][input_var].type == 'file'"
                v-model="inputs[sec][subsec][input_var].value"
                :id="input_var"
                :file-name-formatter="formatNames"
                placeholder="Choose a file or drop it here..."
                drop-placeholder="Drop file here..."
                accept=".fasta"
                multiple
              ></b-form-file>
              <b-form-spinbutton
                v-if="inputs[sec][subsec][input_var].type == 'number'"
                v-model="inputs[sec][subsec][input_var].value"
                :id="input_var"
                :min="inputs[sec][subsec][input_var].min"
                :max="inputs[sec][subsec][input_var].max"
                :step="inputs[sec][subsec][input_var].step"
                :required="inputs[sec][subsec][input_var].required ? true : false"
                inline
              ></b-form-spinbutton>
              <b-form-select
                v-if="inputs[sec][subsec][input_var].type == 'options'"
                v-model="inputs[sec][subsec][input_var].value"
                :id="input_var"
                :options="inputs[sec][subsec][input_var].options"
              >
              </b-form-select>
              <b-form-input
                v-if="inputs[sec][subsec][input_var].type == 'text'"
                v-model="inputs[sec][subsec][input_var].value"
                :id="input_var"
                :type="inputs[sec][subsec][input_var].type"
                :required="inputs[sec][subsec][input_var].required ? true : false"
              ></b-form-input>
            </b-form-group>
          </div>
        </b-form-group>
      </b-form-group>
      <!-- submit button -->
      <b-button type="submit" variant="primary">Submit</b-button>
    </b-form>
    <p v-if="status">{{ status }}</p>
    <p v-if="runid">{{ "Run ID: " + runid }}</p>
  </div>
</template>

<script>
const Cookies = require('js-cookie')

export default {
  name: 'RunADAPT',
  data () {
    return {
      inputs: {
        inputtype: {
          label: 'Inputs',
          inputchoices: {
            show: true,
            inputchoice: {
              label: 'Input Type',
              type: 'options',
              value: '',
              options: [
                { value: 'fasta', text: 'Prealigned FASTA' },
                { value: 'auto-from-args', text: 'Taxonomic ID' },
              ],
              required: true,
            },
          },
          autoinput: {
            label: 'Auto Download from NCBI',
            show: false,
            taxid: {
              label: 'Taxonomic ID',
              type: 'text',
              value: ''
            },
            segment: {
              label: 'Segment',
              type: 'text',
              value: '',
            },
          },
          fileinput: {
            label: 'Custom FASTA File',
            show: false,
            fasta: {
              label: 'FASTA',
              type: 'file',
              value: [],
            },
          },
        },
        sp: {
          label: 'Specificity',
          fasta: {
            label: 'FASTA',
            show: true,
            specificity_fasta: {
              label: 'FASTA',
              type: 'file',
              value: [],
            },
          },
        },
        opts: {
          label: 'Options',
          all: {
            show: true,
            obj: {
              label: 'Objective',
              type: 'options',
              value: '',
              options: [
                { value: 'maximize-activity', text: 'Maximize Activity' },
                { value: 'minimize-guides', text: 'Minimize Guides' },
              ],
              required: true,
            },
            bestntargets: {
              label: 'Number of Assays',
              type: 'text',
              value: '',
            },
          },
        },
        advopts: {
          label: 'Advanced Options',
          all: {
            show: true,
            gl: {
              label: 'Guide Length',
              type: 'text',
              value: '',
            },
            pl: {
              label: 'Primer Length',
              type: 'text',
              value: '',
            },
            pm: {
              label: 'Primer Mismatches',
              type: 'text',
              value: '',
            },
            pp: {
              label: 'Primer Coverage Fraction',
              type: 'text',
              value: '',
            },
            cluster_threshold: {
              label: 'Cluster Threshold',
              type: 'text',
              value: '',
            },
            max_primers_at_site: {
              label: 'Maximum Primers at Site',
              type: 'text',
              value: '',
            },
            max_target_length: {
              label: 'Maximum Amplicon Length',
              type: 'text',
              value: '',
            },
          },
          gc: {
            show: true,
            label: 'GC Content',
            primer_gc_lo: {
              label: 'Low',
              type: 'text',
              value: '',
            },
            primer_gc_hi: {
              label: 'High',
              type: 'text',
              value: '',
            },
          },
          objw: {
            show: true,
            label: 'Objective Function Weights',
            objfnweights_a: {
              label: 'Penalty for Number of Primers',
              type: 'text',
              value: '',
            },
            objfnweights_b: {
              label: 'Penalty for Amplicon Length',
              type: 'text',
              value: '',
            },
          },
          sp: {
            show: false,
            label: 'Specificity',
            idm: {
              label: 'Number of Mismatches to be Identical',
              type: 'text',
              value: '',
            },
            idfrac: {
              label: 'Fraction of Group Hit to be Identical',
              type: 'text',
              value: '',
            },
          },
          minguides: {
            label: 'Minimize Guides',
            show: false,
            gm: {
              label: 'Guide Mismatches',
              type: 'text',
              value: '',
            },
            gp: {
              label: 'Guide Coverage Fraction',
              type: 'text',
              value: '',
            },
          },
          maxact: {
            label: 'Maximize Activity',
            show: false,
            soft_guide_constraint: {
              label: 'Soft Guide Constraint',
              type: 'text',
              value: '',
            },
            hard_guide_constraint: {
              label: 'Hard Guide Constraint',
              type: 'text',
              value: '',
            },
          },
        },
      },
      runid: '',
      status: '',
    }
  },
  methods: {
    async adapt_run(event) {
      this.status = "Loading..."
      let form_data = new FormData()
      for (let sec of Object.keys(this.inputs)) {
        for (let subsec of this.get_sub(Object.keys(this.inputs[sec]))) {
          for (let input_var of this.get_sub(Object.keys(this.inputs[sec][subsec]))) {
            if (this.inputs[sec][subsec][input_var].value != '') {
              if (input_var.includes('fasta')) {
                for (let file of this.inputs[sec][subsec][input_var].value) {
                  form_data.append(input_var + '[]', file, file.name);
                }
              } else {
                form_data.append(input_var, this.inputs[sec][subsec][input_var].value)
              }
            }
          }
        }
      }

      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/', {
        method: 'POST',
        headers: {
          "X-CSRFToken": csrfToken
        },
        body: form_data,
      })
      if (response.ok) {
        let responsejson = await response.json()
        this.status = "Submitted!"
        this.runid = responsejson.cromwell_id
        Cookies.set('runid', responsejson.cromwell_id)
        Cookies.set('submitted', true)
        window.location.href = '/results'
      }
      else {
        this.status = "Submission Error"
      }
      return response
    },
    // handleFASTAUpload(){
    //   this.inputs.fasta = this.$refs.fasta.files;
    // },
    // handleSpecificityFASTAUpload(){
    //   this.inputs.specificity_fasta = this.$refs.specificity_fasta.files;
    // }
    get_sub(sec_keys) {
      return sec_keys.filter(item => {
        return item != 'label';
      })
    },
    formatNames(files) {
      return files.length === 1 ? files[0].name : `${files.length} files selected`
    },
    fileclick(input_var) {
      this.$refs[input_var].click()
    },
    handleFilesUpload(sec, subsec, input_var){
      console.log(input_var)
      this.inputs[sec][subsec][input_var].value = this.$refs[input_var].files;
    }
  },
}
</script>

<style scoped>
input[type=file] {
  display: none
}
</style>
