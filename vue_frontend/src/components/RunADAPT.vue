<template>
  <transition appear name="fade">
    <div class="runadapt">
      <ValidationObserver v-slot="{ invalid, untouched }">
        <b-form id="full-form" @submit.prevent="adapt_run" class="mx-3 px-3">
          <b-form-group
            class="sec"
            v-for="(sec, i) in Object.keys(inputs)"
            :label="(inputs[sec].label && !inputs[sec].collapsible) ? inputs[sec].label : ''"
            :key="i"
            :id="sec"
          >
          <a
            v-if="inputs[sec].collapsible"
            @click.prevent
            v-b-toggle
            :href="'#' + sec + '-toggle'"
          >{{ inputs[sec].label }} <b-icon-chevron-down class="when-closed"/><b-icon-chevron-up class="when-open"/></a>
            <b-collapse
              :id="sec + '-toggle'"
              :visible="inputs[sec].collapsible ? false : true"
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
                    <ValidationProvider
                      :rules="inputs[sec][subsec][input_var].rules"
                      v-slot="validationContext"
                      :name="inputs[sec][subsec][input_var].label"
                    >
                      <b-form-file
                        v-if="inputs[sec][subsec][input_var].type == 'file'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :file-name-formatter="formatNames"
                        placeholder="Choose a file or drop it here..."
                        drop-placeholder="Drop file here..."
                        accept=".fasta"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext, inputs[sec][subsec][input_var].value)"
                        multiple
                      ></b-form-file>
                      <b-form-input
                        v-if="inputs[sec][subsec][input_var].type == 'number'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :placeholder="inputs[sec][subsec][input_var].placeholder ? inputs[sec][subsec][input_var].placeholder.toString() : ''"
                        :id="input_var"
                        :type="inputs[sec][subsec][input_var].type"
                        :min="inputs[sec][subsec][input_var].min"
                        :max="inputs[sec][subsec][input_var].max"
                        :step="inputs[sec][subsec][input_var].step"
                        :required="inputs[sec][subsec][input_var].required ? true : false"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext, inputs[sec][subsec][input_var].value)"
                      ></b-form-input>
                      <b-form-select
                        v-if="inputs[sec][subsec][input_var].type == 'options'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :options="inputs[sec][subsec][input_var].options"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext, inputs[sec][subsec][input_var].value)"
                      >
                      </b-form-select>
                      <b-form-input
                        v-if="inputs[sec][subsec][input_var].type == 'text'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :type="inputs[sec][subsec][input_var].type"
                        :required="inputs[sec][subsec][input_var].required ? true : false"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext, inputs[sec][subsec][input_var].value)"
                      ></b-form-input>
                      <b-form-invalid-feedback :id="input_var + '-feedback'">{{ validationContext.errors[0] }}</b-form-invalid-feedback>
                    </ValidationProvider>
                  </b-form-group>
                </div>
              </b-form-group>
            </b-collapse>
          </b-form-group>
          <!-- submit button -->
          <b-button type="submit" variant="primary" :disabled="invalid || untouched">Submit</b-button>
        </b-form>
      </ValidationObserver>
      <p v-if="status">{{ status }}</p>
      <p v-if="runid">{{ "Run ID: " + runid }}</p>
    </div>
  </transition>
</template>

<script>
import {
  ValidationProvider,
  ValidationObserver,
  extend,
} from 'vee-validate';
import * as rules from 'vee-validate/dist/rules';
import { messages } from 'vee-validate/dist/locale/en.json';
import { setInteractionMode } from 'vee-validate';
const Cookies = require('js-cookie');

export default {
  name: 'RunADAPT',
  components: {
    ValidationProvider,
    ValidationObserver
  },
  mounted () {
    setInteractionMode('eager');
    Object.keys(rules).forEach(rule => {
      extend(rule, {
        ...rules[rule],
        message: messages[rule]
      });
    });
    extend('amplicon', {
      validate: value => {
        let primer_length = this.inputs.advopts.all.pl.placeholder
        if (this.inputs.advopts.all.pl.value) {
          primer_length = this.inputs.advopts.all.pl.value
        }
        let guide_length = this.inputs.advopts.all.gl.placeholder
        if (this.inputs.advopts.all.gl.value) {
          guide_length = this.inputs.advopts.all.gl.value
        }
        return value >= 2*primer_length + guide_length;
      },
      message: "The {_field_} field must be greater than or equal to double the primer length plus the guide length",
    });
  },
  data () {
    return {
      inputs: {
        inputtype: {
          label: 'Inputs',
          collapsible: false,
          inputchoices: {
            show: true,
            inputchoice: {
              label: 'Input Type',
              type: 'options',
              value: '',
              options: [
                { value: 'fasta', text: 'Prealigned FASTA' },
                { value: 'auto-from-args', text: 'Auto Download from NCBI via Taxonomic ID' },
              ],
              required: true,
              rules: '',
            },
          },
          autoinput: {
            label: 'Auto Download from NCBI',
            show: false,
            taxid: {
              label: 'Taxonomic ID',
              type: 'text',
              value: '',
              rules: '',
            },
            segment: {
              label: 'Segment',
              type: 'text',
              value: '',
              rules: '',
            },
          },
          fileinput: {
            label: 'Prealigned FASTA',
            show: false,
            fasta: {
              label: 'FASTA',
              type: 'file',
              value: [],
              rules: '',
            },
          },
        },
        opts: {
          label: 'Settings',
          collapsible: false,
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
              rules: '',
            },
            bestntargets: {
              label: 'Number of Assays',
              type: 'number',
              value: '',
              required: true,
              rules: 'required|min_value:1|integer',
            },
          },
        },
        sp: {
          label: 'Specificity',
          collapsible: true,
          fasta: {
            label: 'FASTA',
            show: true,
            specificity_fasta: {
              label: 'FASTA',
              type: 'file',
              value: [],
              rules: '',
            },
          },
        },
        advopts: {
          label: 'Advanced Options',
          collapsible: true,
          all: {
            show: true,
            gl: {
              label: 'Guide Length',
              type: 'number',
              value: '',
              placeholder: 28,
              rules: 'min_value:1|integer',
            },
            pl: {
              label: 'Primer Length',
              type: 'number',
              value: '',
              placeholder: 30,
              rules: 'min_value:1|integer',
            },
            pm: {
              label: 'Primer Mismatches',
              type: 'number',
              value: '',
              placeholder: 3,
              rules: 'min_value:0|integer',
            },
            pp: {
              label: 'Primer Coverage Fraction',
              type: 'number',
              value: '',
              placeholder: 0.98,
              rules: 'min_value:0|max_value:1|double',
            },
            cluster_threshold: {
              label: 'Cluster Threshold',
              type: 'number',
              value: '',
              placeholder: 0.3,
              rules: 'double'
            },
            max_primers_at_site: {
              label: 'Maximum Primers at Site',
              type: 'number',
              value: '',
              placeholder: 10,
              rules: 'min_value:1|integer',
            },
            max_target_length: {
              label: 'Maximum Amplicon Length',
              type: 'number',
              value: '',
              placeholder: 250,
              rules: 'amplicon|integer',
            },
          },
          gc: {
            show: true,
            label: 'Percent GC Content Allowed in Primers',
            primer_gc_lo: {
              label: 'Low',
              type: 'number',
              value: '',
              placeholder: 0.35,
              rules: 'min_value:0|max_value:1|double',
            },
            primer_gc_hi: {
              label: 'High',
              type: 'number',
              value: '',
              placeholder: 0.65,
              rules: 'min_value:0|max_value:1|double',
            },
          },
          objw: {
            show: true,
            label: 'Objective Function Weights',
            objfnweights_a: {
              label: 'Penalty for Number of Primers',
              type: 'number',
              value: '',
              placeholder: 0.5,
              rules: 'double',
            },
            objfnweights_b: {
              label: 'Penalty for Amplicon Length',
              type: 'number',
              value: '',
              placeholder: 0.25,
              rules: 'double',
            },
          },
          sp: {
            show: false,
            label: 'Specificity',
            idm: {
              label: 'Number of Mismatches to be Identical',
              type: 'text',
              value: '',
              rules: '',
            },
            idfrac: {
              label: 'Fraction of Group Hit to be Identical',
              type: 'text',
              value: '',
              rules: '',
            },
          },
          minguides: {
            label: 'Minimize Guides',
            show: false,
            gm: {
              label: 'Guide Mismatches',
              type: 'text',
              value: '',
              rules: '',
            },
            gp: {
              label: 'Guide Coverage Fraction',
              type: 'text',
              value: '',
              rules: '',
            },
          },
          maxact: {
            label: 'Maximize Activity',
            show: false,
            soft_guide_constraint: {
              label: 'Soft Guide Constraint',
              type: 'text',
              value: '',
              rules: '',
            },
            hard_guide_constraint: {
              label: 'Hard Guide Constraint',
              type: 'text',
              value: '',
              rules: '',
            },
          },
        },
      },
      runid: '',
      status: '',
    }
  },
  computed: {
    inputchoiceval() {
      return this.inputs.inputtype.inputchoices.inputchoice.value
    },
    objval() {
      return this.inputs.opts.all.obj.value
    }
  },
  watch: {
    inputchoiceval(val) {
      this.inputs.inputtype.autoinput.show = val == 'auto-from-args';
      this.inputs.inputtype.fileinput.show = val == 'fasta';
    },
    objval(val) {
      this.inputs.advopts.minguides.show = val == 'minimize-guides';
      this.inputs.advopts.maxact.show = val == 'maximize-activity';
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
    // dirty, validated, required, failed,
    getValidationState({pristine, valid = null }, input_var) {
      return pristine || valid ? null : valid;
      // if (!required && input_var.length == 0) {
      //   return null;
      // } else {
      //   return dirty || validated ? valid : null;
      // }
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
.collapsed > .when-open,
.not-collapsed > .when-closed {
  display: none;
}
</style>
