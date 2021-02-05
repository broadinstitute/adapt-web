<template>
  <div class="runadapt">
    <form id="full-form">
      <div v-for="(sec, i) in Object.keys(inputs)" :key="i">
        <h2>{{ inputs[sec].label }}</h2>
        <div v-for="(subsec, j) in get_sub(Object.keys(inputs[sec]))" :key="j">
          <h3 v-if="inputs[sec][subsec].label">{{ inputs[sec][subsec].label }}</h3>
          <div class="field" v-for="(input_var, k) in get_sub(Object.keys(inputs[sec][subsec]))" :key="k">
            <label class="label" :for="input_var">{{ inputs[sec][subsec][input_var].label + ": "}}</label>
            <input v-if="inputs[sec][subsec][input_var].type == 'file'" type="button" :id="input_var + '_button'" value="Upload Files" @click="fileclick(input_var)">
            <input v-if="inputs[sec][subsec][input_var].type == 'file'" :type="inputs[sec][subsec][input_var].type" :id="input_var" :ref="input_var" multiple v-on:change="handleFilesUpload(sec,subsec,input_var)">
            <span v-if="inputs[sec][subsec][input_var].type == 'file' && inputs[sec][subsec][input_var].value">&emsp;Files:
              <span v-for="(file, index) in inputs[sec][subsec][input_var].value" :key="file.name">{{ file.name }}<span v-if="index+1 < inputs[sec][subsec][input_var].value.length">, </span></span>
            </span>
            <input v-if="inputs[sec][subsec][input_var].type == 'number'" :type="inputs[sec][subsec][input_var].type" :id="input_var" v-model="inputs[sec][subsec][input_var].value" :min="inputs[sec][subsec][input_var].min" :max="inputs[sec][subsec][input_var].max" :step="inputs[sec][subsec][input_var].step">
            <input v-if="inputs[sec][subsec][input_var].type == 'text'" :type="inputs[sec][subsec][input_var].type" :id="input_var" v-model="inputs[sec][subsec][input_var].value">
          </div>
        </div>
      </div>
      <!-- submit button -->
      <div class="field has-text-right">
        <button v-on:click.prevent="adapt_run" type="submit" class="button is-danger">Submit</button>
      </div>
    </form>
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
          autoinput: {
            label: 'Auto Download from NCBI',
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
            fasta: {
              label: 'FASTA',
              type: 'file',
              value: '',
            },
          },
        },
        sp: {
          label: 'Specificity',
          fasta: {
            label: 'FASTA',
            specificity_fasta: {
              label: 'FASTA',
              type: 'file',
              value: '',
            },
          },
        },
        opts: {
          label: 'Options',
          all: {
            obj: {
              label: 'Objective',
              type: 'text',
              value: '',
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
