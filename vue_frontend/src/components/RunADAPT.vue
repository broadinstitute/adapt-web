<template>
  <transition appear name="fade">
    <div class="runadapt">
      <!-- Form created dynamically with 3 loops - one for sections, one for subsections, one for the fields -->
      <ValidationObserver ref="full-form" v-slot="{ handleSubmit }" slim>
        <b-form id="full-form">
          <!-- Section loop -->
          <b-form-group
            class="sec"
            v-for="sec in get_sub(inputs)"
            :key="inputs[sec].order"
            :id="sec"
          >
          <!-- Make collapsible section, if it is one -->
          <legend class="my-0 col-form-label-lg pt-0 font-weight-bold"
          >{{ inputs[sec].label }}
            <b-link
              v-if="inputs[sec].collapsible"
              @click.prevent
              v-b-toggle
              :href="'#' + sec + '-toggle'"
              class="col-form-label-lg pt-0 font-weight-bold"
            >
              <b-icon-chevron-down class="when-closed"/><b-icon-chevron-up class="when-open"/>
            </b-link>
          </legend>
            <b-collapse
              :id="sec + '-toggle'"
              :visible="inputs[sec].collapsible ? false : true"
            >
              <!-- Subsection loop -->
              <b-form-group
                class="subsec"
                v-for="subsec in get_sub(inputs[sec])"
                v-show="inputs[sec][subsec].show"
                :label="inputs[sec][subsec].label ? inputs[sec][subsec].label : ''"
                label-class="h3"
                :key="inputs[sec][subsec].order"
                :id="sec + '-' + subsec"
              >
                <b-form-row v-show="inputs[sec][subsec].show">
                  <!-- Field loop -->
                  <b-col
                    v-for="input_var in get_sub(inputs[sec][subsec])"
                    :key="inputs[sec][subsec][input_var].order"
                    :sm="inputs[sec][subsec][input_var].cols ? inputs[sec][subsec][input_var].cols : 12"
                  >
                  <b-form-group
                    class="field"
                    :label="inputs[sec][subsec][input_var].label"
                    :label-for="input_var"
                    label-align=left
                  >
                    <!-- ValidationProvider allows VeeValidate to put rules on a field -->
                    <ValidationProvider
                      v-if="inputs[sec][subsec][input_var].type != 'multi'"
                      :vid="input_var"
                      :rules="inputs[sec][subsec][input_var].rules"
                      v-slot="validationContext"
                      :name="inputs[sec][subsec][input_var].label"
                      mode="eager"
                    >
                      <!-- v-if only produces the input depending on the type -->
                      <b-form-file
                        v-if="inputs[sec][subsec][input_var].type == 'file'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :file-name-formatter="formatNames"
                        placeholder="Choose files or drop them here..."
                        drop-placeholder="Drop files here..."
                        accept=".fasta, .fa, .fna, .ffn, .faa, .frn, .aln"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext)"
                        multiple
                      ></b-form-file>
                      <b-form-input
                        v-if="inputs[sec][subsec][input_var].type == 'number'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :placeholder="inputs[sec][subsec][input_var].placeholder ? inputs[sec][subsec][input_var].placeholder.toString() : ''"
                        :id="input_var"
                        :type="inputs[sec][subsec][input_var].type"
                        :step="inputs[sec][subsec][input_var].step"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext)"
                      ></b-form-input>
                      <b-form-select
                        v-if="inputs[sec][subsec][input_var].type == 'options'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :options="inputs[sec][subsec][input_var].options"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext)"
                      >
                      </b-form-select>
                      <b-form-radio-group
                        v-if="inputs[sec][subsec][input_var].type == 'radio'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :id="input_var"
                        :options="inputs[sec][subsec][input_var].options"
                        :aria-describedby="input_var + '-feedback'"
                        button-variant="outline-secondary"
                        buttons
                      >
                      </b-form-radio-group>
                      <b-form-input
                        v-if="inputs[sec][subsec][input_var].type == 'text'"
                        v-model="inputs[sec][subsec][input_var].value"
                        :placeholder="inputs[sec][subsec][input_var].placeholder ? inputs[sec][subsec][input_var].placeholder.toString() : ''"
                        :id="input_var"
                        :type="inputs[sec][subsec][input_var].type"
                        :aria-describedby="input_var + '-feedback'"
                        :state="getValidationState(validationContext)"
                      ></b-form-input>
                      <b-form-invalid-feedback :id="input_var + '-feedback'" :state="getValidationState(validationContext)">{{ validationContext.errors[0] }}</b-form-invalid-feedback>
                    </ValidationProvider>
                    <b-form
                      v-if="inputs[sec][subsec][input_var].type == 'multi'"
                      :id="input_var"
                    >
                      <b-form-row>
                        <b-col>
                          <b-form-row>
                          <b-col
                            v-for="part in get_sub(inputs[sec][subsec][input_var])"
                            :key="input_var + '-' + part"
                            :sm="inputs[sec][subsec][input_var][part].cols ? inputs[sec][subsec][input_var][part].cols : 12"
                          >
                            <b-form-group
                              :key="input_var + '-' + part + '0'"
                              :label="inputs[sec][subsec][input_var][part].label"
                              :label-for="input_var + '-' + part"
                              label-class="f-5"
                              label-align=left
                            >
                              <b-form-input
                                :key="input_var + '-' + part + '2'"
                                v-model="inputs[sec][subsec][input_var][part].value"
                                :id="input_var + '-' + part"
                                :type="inputs[sec][subsec][input_var][part].type"
                                :placeholder="inputs[sec][subsec][input_var][part].placeholder"
                                :aria-describedby="input_var + '-' + part + '-feedback'"
                                :state="inputs[sec][subsec][input_var][part].valid"
                              ></b-form-input>
                            </b-form-group>
                          </b-col>
                          </b-form-row>
                        </b-col>
                        <b-col sm=1 align-self="center" class="text-center">
                          <b-button pill v-on:click.prevent="updateList(sec, subsec, input_var)" variant="success" class="font-weight-bold"><b-icon-plus aria-label="Add" font-scale="2"></b-icon-plus></b-button>
                        </b-col>
                      </b-form-row>
                      <template v-for="part in get_sub(inputs[sec][subsec][input_var])">
                        <b-form-invalid-feedback v-if="inputs[sec][subsec][input_var][part].valid==false" :key="inputs[sec][subsec][input_var][part].valid" :id="input_var + '-' + part + '-feedback'" :state="inputs[sec][subsec][input_var][part].valid">
                          The {{ inputs[sec][subsec][input_var][part].label }} is required
                        </b-form-invalid-feedback>
                      </template>
                      <div v-show="!checkEmpty(inputs[sec][subsec][input_var].value)">
                        <b-table :items="inputs[sec][subsec][input_var].value" :fields="createFields(sec, subsec, input_var)">
                          <template #cell(delete)="data">
                            <b-button pill v-on:click.prevent="deleteRow(inputs[sec][subsec][input_var].value, data.index)" variant="outline-danger" class="font-weight-bold"><b-icon-dash aria-label="Delete" font-scale="1"></b-icon-dash></b-button>
                          </template>
                        </b-table>
                      </div>
                    </b-form>
                  </b-form-group>
                  </b-col>
                </b-form-row>
              </b-form-group>
            </b-collapse>
          </b-form-group>
          <!-- submit button -->
          <b-button pill block v-on:click.prevent="clearMultiParts().then(handleSubmit(adapt_run))" size="lg" type="submit" variant="outline-secondary" class="font-weight-bold">Submit a Run</b-button>
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
  setInteractionMode
} from 'vee-validate';
import {
  required,
  integer,
} from 'vee-validate/dist/rules';
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'RunADAPT',
  components: {
    ValidationProvider,
    ValidationObserver
  },
  mounted () {
    // Makes VeeValidate check only on change events if the field is untouched or valid,
    // but on input events if the field is invalid
    setInteractionMode('eager');
    // Direct reference to checkEmpty needed for extend to access it within validate
    let checkEmpty = this.checkEmpty
    // 'extend' creates rules for validation. In theory VeeValidate should come with many
    // of these preimplemented (such as 'required' and 'integer'), but preimplemented versions
    // don't work for anything with named parameters for some reason
    extend('required', {
      ...required,
      message: "The {_field_} is required"
    });
    // Sets field to ge required if another field (args[0]) is a value (args[1:])
    extend('required_if', {
      computesRequired: true,
      validate(value, args) {
        let required;
        if (args.length > 1) {
          required = args.slice(1).includes(String(args[0]).trim());
        } else {
          required = !checkEmpty(args[0]);
        }
        if (!required) {
          return {
            valid: true,
            required
          }
        }
        return {
          valid: !checkEmpty(value),
          required
        }
      },
      message: "The {_field_} is required"
    });
    // Sets field to ge required if another field (args[0]) is greater than a value (args[1])
    extend('required_if_greater', {
      computesRequired: true,
      validate(value, args) {
        let required = checkEmpty(args[0])? false : Number(args[0]) > Number(args[1]);
        if (!required) {
          return {
            valid: true,
            required
          }
        }
        return {
          valid: !checkEmpty(value),
          required
        }
      },
      message: "The {_field_} is required"
    });
    // Sets field to ge required if another field (args[0]) is less than a value (args[1])
    extend('required_if_less', {
      computesRequired: true,
      validate(value, args) {
        let required = checkEmpty(args[0])? false : Number(args[0]) < Number(args[1]);
        if (!required) {
          return {
            valid: true,
            required
          }
        }
        return {
          valid: !checkEmpty(value),
          required
        }
      },
      message: "The {_field_} is required"
    });
    extend('integer', {
      ...integer,
      message: "The {_field_} must be an integer"
    });
    extend('double', {
      validate(value) {
        const regex = new RegExp(`^-?(\\d+\\.?\\d*|\\.\\d+)`);
        return Array.isArray(value) ? value.every(val => regex.test(String(val))) : regex.test(String(value));
      },
      message: "The {_field_} must be a valid decimal"
    });
    extend('between', {
      validate(value, args) {
        return Number(value) >= Number(args[0]) && Number(value) <= Number(args[1]);
      },
      message: (fieldName, placeholders) => {
        return `The ${fieldName} must be at least ${placeholders[0]} and at most ${placeholders[1]}`;
      }
    });
    extend('min_value', {
      validate(value, args) {
        return checkEmpty(args[0])? true : Number(value) >= Number(args[0]);
      },
      // Sets the message to say greater than a specified string if one is supplied; otherwise, just says number
      message: (fieldName, placeholders) => {
        if (placeholders[1]) {
          return `The ${fieldName} must be greater than or equal to the ${placeholders[1]}`;
        }
        return `The ${fieldName} must be at least ${placeholders[0]}`;
      }
    });
    extend('max_value', {
      validate(value, args) {
        return checkEmpty(args[0])? true : Number(value) <= Number(args[0]);
      },
      // Sets the message to say greater than a specified string if one is supplied; otherwise, just says number
      message: (fieldName, placeholders) => {
        if (placeholders[1]) {
          return `The ${fieldName} must be less than or equal to the ${placeholders[1]}`;
        }
        return `The ${fieldName} must be at least ${placeholders[0]}`;
      }
    });
    // Specific rule for amplicon length
    extend('amplicon', {
      validate(value) {
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
      message: "The {_field_} must be greater than or equal to double the primer length plus the guide length",
    });
  },
  data () {
    return {
      // Fields of the form. Divided into sections, subsections, and fields,
      // Sections have a label and a true/false 'collapsible' value
      // Subsections have an optional label and a true/false 'show' value that is set
      // depending on input choices
      // Fields have a label, a type, a value, rules to validate it, and options if it is
      // an options or radio type
      inputs: {
        opts: {
          order: 0,
          label: 'Options',
          collapsible: false,
          inputchoices: {
            show: true,
            inputchoice: {
              order: 0,
              label: 'Input Type',
              type: 'radio',
              value: '',
              options: [
                { value: 'fasta', text: 'Prealigned FASTA' },
                { value: 'auto-from-args', text: 'Taxonomic ID' },
              ],
              rules: 'required',
            },
          },
          autoinput: {
            order: 1,
            label: 'Auto Download from NCBI',
            show: false,
            taxid: {
              order: 0,
              label: 'Taxonomic ID',
              type: 'number',
              value: '',
              rules: 'required_if:@inputchoice,auto-from-args',
              cols: 6,
            },
            segment: {
              order: 1,
              label: 'Segment',
              type: 'text',
              value: '',
              placeholder: 'None',
              rules: '',
              cols: 6,
            },
          },
          fileinput: {
            order: 2,
            label: 'Prealigned FASTA',
            show: false,
            fasta: {
              order: 0,
              label: 'FASTA Files',
              type: 'file',
              value: [],
              rules: 'required_if:@inputchoice,fasta',
            },
          },
          all: {
            order: 3,
            show: true,
            obj: {
              order: 0,
              label: 'Objective',
              type: 'radio',
              value: '',
              options: [
                { value: 'maximize-activity', text: 'Maximize Activity' },
                { value: 'minimize-guides', text: 'Minimize Guides' },
              ],
              rules: 'required',
            },
            bestntargets: {
              order: 4,
              label: 'Number of Assays',
              type: 'number',
              value: 10,
              placeholder: 10,
              rules: 'between:1,20|integer',
            },
          },
        },
        sp: {
          order: 2,
          label: 'Specificity',
          collapsible: true,
          all: {
            order: 0,
            show: true,
            sp_fasta: {
              order: 0,
              label: 'FASTA Files',
              type: 'file',
              value: [],
              rules: '',
            },
            sp_taxa: {
              order: 1,
              label: 'Taxa',
              type: 'multi',
              value: [],
              rules: '',
              taxid: {
                order: 0,
                label: 'Taxonomic ID',
                type: 'number',
                value: '',
                rules: 'required',
                valid: null,
                cols: 6,
              },
              segment: {
                order: 1,
                label: 'Segment',
                type: 'text',
                value: '',
                placeholder: 'None',
                rules: '',
                cols: 6,
              }
            },
          },
        },
        advopts: {
          order: 3,
          label: 'Advanced',
          collapsible: true,
          all: {
            order: 0,
            show: true,
            gl: {
              order: 0,
              label: 'Guide Length',
              type: 'number',
              value: '',
              placeholder: 28,
              rules: 'min_value:1|integer',
              cols: 6,
            },
            pl: {
              order: 1,
              label: 'Primer Length',
              type: 'number',
              value: '',
              placeholder: 30,
              rules: 'min_value:1|integer',
              cols: 6,
            },
            max_target_length: {
              order: 2,
              label: 'Maximum Amplicon Length',
              type: 'number',
              value: '',
              placeholder: 250,
              rules: 'amplicon|integer',
            },
            pm: {
              order: 3,
              label: 'Primer Mismatches',
              type: 'number',
              value: '',
              placeholder: 3,
              rules: 'min_value:0|integer',
              cols: 4,
            },
            pp: {
              order: 4,
              label: 'Primer Coverage Fraction',
              type: 'number',
              value: '',
              placeholder: 0.98,
              step: 0.01,
              rules: 'between:0,1|double',
              cols: 4,
            },
            max_primers_at_site: {
              order: 5,
              label: 'Maximum Primers at Site',
              type: 'number',
              value: '',
              placeholder: 10,
              rules: 'min_value:1|integer',
              cols: 4,
            },
            cluster_threshold: {
              order: 6,
              label: 'Cluster Threshold',
              type: 'number',
              value: '',
              placeholder: 0.3,
              step: 0.01,
              rules: 'double'
            },
          },
          gc: {
            order: 1,
            show: true,
            label: 'Percent GC Content Allowed in Primers',
            primer_gc_lo: {
              order: 0,
              label: 'Low GC Percent Content in Primer',
              type: 'number',
              value: '',
              placeholder: 0.35,
              step: 0.01,
              rules: 'required_if_less:@primer_gc_hi,0.35|max_value:@primer_gc_hi,High GC Percent Content in Primer|between:0,1|double',
              cols: 6
            },
            primer_gc_hi: {
              order: 1,
              label: 'High GC Percent Content in Primer',
              type: 'number',
              value: '',
              placeholder: 0.65,
              step: 0.01,
              rules: 'required_if_greater:@primer_gc_lo,0.65|min_value:@primer_gc_lo,Low GC Percent Content in Primer|between:0,1|double',
              cols: 6
            },
          },
          objw: {
            order: 2,
            show: true,
            label: 'Objective Function Weights',
            objfnweights_a: {
              order: 0,
              label: 'Penalty for Number of Primers',
              type: 'number',
              value: '',
              placeholder: 0.5,
              step: 0.01,
              rules: 'double',
              cols: 6
            },
            objfnweights_b: {
              order: 1,
              label: 'Penalty for Amplicon Length',
              type: 'number',
              value: '',
              placeholder: 0.25,
              step: 0.01,
              rules: 'double',
              cols: 6
            },
          },
          sp: {
            order: 3,
            show: false,
            label: 'Specificity',
            idm: {
              order: 0,
              label: 'Number of Mismatches to be Identical',
              type: 'number',
              value: '',
              placeholder: 4,
              rules: 'min_value:0|integer',
              cols: 6,
            },
            idfrac: {
              order: 1,
              label: 'Fraction of Group Hit to be Identical',
              type: 'number',
              value: '',
              placeholder: 0.01,
              step: 0.01,
              rules: 'between:0,1|double',
              cols: 6,
            },
          },
          minguides: {
            order: 4,
            label: 'Minimize Guides',
            show: false,
            gm: {
              order: 0,
              label: 'Guide Mismatches',
              type: 'number',
              value: '',
              placeholder: 3,
              rules: 'min_value:0|integer',
              cols: 6,
            },
            gp: {
              order: 1,
              label: 'Guide Coverage Fraction',
              type: 'number',
              value: '',
              placeholder: 0.98,
              step: 0.01,
              rules: 'between:0,1|double',
              cols: 6,
            },
          },
          maxact: {
            order: 5,
            label: 'Maximize Activity',
            show: false,
            soft_guide_constraint: {
              order: 0,
              label: 'Soft Guide Constraint',
              type: 'number',
              value: '',
              placeholder: 1,
              rules: 'max_value:@hard_guide_constraint,Hard Guide Constraint|min_value:1|integer',
              cols: 6,
            },
            hard_guide_constraint: {
              order: 1,
              label: 'Hard Guide Constraint',
              type: 'number',
              value: '',
              placeholder: 5,
              rules: 'required_if_greater:@soft_guide_constraint,5|min_value:@soft_guide_constraint,Soft Guide Constraint|integer',
              cols: 6,
            },
          },
        },
      },
      runid: '',
      status: '',
    }
  },
  // computed and watch are used to show certain sections of the form dependent on input choices
  // computed properties are reevalutated whenever their dependencies change
  // watch allows things to happen when those computed properties change
  // Nested data cannot otherwise be accessed by watch
  computed: {
    inputchoiceval() {
      return this.inputs.opts.inputchoices.inputchoice.value
    },
    objval() {
      return this.inputs.opts.all.obj.value
    },
    spval() {
      return !this.checkEmpty(this.inputs.sp.all.sp_fasta.value)
    },
    sptaxidval() {
      return !this.checkEmpty(this.inputs.sp.all.sp_taxa.taxid.value)
    }
  },
  watch: {
    inputchoiceval(val) {
      this.inputs.opts.autoinput.show = val == 'auto-from-args';
      this.inputs.opts.fileinput.show = val == 'fasta';
    },
    objval(val) {
      this.inputs.advopts.minguides.show = val == 'minimize-guides';
      this.inputs.advopts.maxact.show = val == 'maximize-activity';
    },
    spval(val) {
      this.inputs.advopts.sp.show = val
    },
    sptaxidval(val) {
      if (val) {
        this.inputs.sp.all.sp_taxa.taxid.valid = null
      }
    },
  },
  methods: {
    checkEmpty(val) {
      // Helper function
      return (Array.isArray(val) && val.length === 0) ||
             [false, null, undefined].includes(val) ||
             !String(val).trim().length
    },
    async clearMultiParts() {
      this.inputs.sp.all.sp_taxa.taxid.valid = null;
      return true;
    },
    async adapt_run() {
      // Handles submission
      // Relies on innermost input field names matching adapt_web.wdl's input variable names.
      this.status = "Loading..."
      let form_data = new FormData()
      for (let sec of this.get_sub(this.inputs)) {
        for (let subsec of this.get_sub(this.inputs[sec])) {
          for (let input_var of this.get_sub(this.inputs[sec][subsec])) {
            if (!this.checkEmpty(this.inputs[sec][subsec][input_var].value)) {
              if (input_var.includes('fasta')) {
                for (let file of this.inputs[sec][subsec][input_var].value) {
                  form_data.append(input_var + '[]', file, file.name);
                }
              } else if (input_var=='sp_taxa') {
                form_data.append(input_var, JSON.stringify(this.inputs[sec][subsec][input_var].value));
              } else {
                form_data.append(input_var, this.inputs[sec][subsec][input_var].value)
              }
            }
          }
        }
      }

      let response = await fetch('/api/adaptrun/', {
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
        let prev_runids = Cookies.get('runid')
        if (prev_runids == null) {
          Cookies.set('runid', this.runid)
        }
        else {
          Cookies.set('runid', prev_runids + ',' + this.runid)
        }
        Cookies.set('submitted', true)
        window.location.href = '/results'
      }
      else {
        // TODO better error handling
        this.status = await response.text()
      }
      return response
    },
    get_sub(sec) {
      // Helper function to get children of section
      return Object.keys(sec).filter(item => {
        return !(['order', 'label', 'collapsible', 'show', 'value', 'type', 'rules', 'fields'].includes(item));
      }).sort((a,b) => {
        return sec[a].order-sec[b].order
      })
    },
    formatNames(files) {
      // Produces the correct string to indicate file input
      return files.length === 1 ? files[0].name : `${files.length} files selected`
    },
    getValidationState({failed, valid = null }) {
      // Only show if field is invalid; don't show if valid
      return !failed ? null : valid;
    },
    getGeneralValidationState(errors, failed) {
      return !failed? null : (errors? false : null)
    },
    handleFilesUpload(sec, subsec, input_var) {
      this.inputs[sec][subsec][input_var].value = this.$refs[input_var].files;
    },
    multiValidate(sec, subsec, input_var) {
      for (let part of this.get_sub(this.inputs[sec][subsec][input_var])) {
        if (this.inputs[sec][subsec][input_var][part].rules.includes('required')) {
          if (this.checkEmpty(this.inputs[sec][subsec][input_var][part].value)) {
            this.inputs[sec][subsec][input_var][part].valid = false;
            return false
          }
        }
      }
      return true
    },
    async updateList(sec, subsec, input_var) {
      if (this.multiValidate(sec, subsec, input_var)) {
        let obj = {}
        for (let part of this.get_sub(this.inputs[sec][subsec][input_var])) {
          if (this.inputs[sec][subsec][input_var][part].value) {
            obj[part] = this.inputs[sec][subsec][input_var][part].value;
          }
          else {
            obj[part] = this.inputs[sec][subsec][input_var][part].placeholder;
          }
          this.inputs[sec][subsec][input_var][part].value = '';
        }
        this.inputs[sec][subsec][input_var].value.push(obj);
      }
    },
    createFields(sec, subsec, input_var) {
      let fields = [];
      for (let part of this.get_sub(this.inputs[sec][subsec][input_var])) {
        fields.push({
          key: part,
          label: this.inputs[sec][subsec][input_var][part].label,
        });
      }
      fields.push({key: 'delete', label: '', tdClass: 'text-right', thClass: ''});
      return fields;
    },
    deleteRow(table, index) {
      table.splice(index, 1);
    },
  },
}
</script>

<style scoped>
input[type=file] {
  display: none
}

.collapsed .when-open,
.not-collapsed .when-closed {
  display: none;
}
</style>
