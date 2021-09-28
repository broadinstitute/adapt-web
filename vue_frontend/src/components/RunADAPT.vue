<template>
  <transition appear name="fade">
    <div class="runadapt">
      <!-- Form created dynamically with 3 loops - one for sections, one for subsections, one for the fields -->
      <ValidationObserver ref="full-form" v-slot="{ handleSubmit, validate }" slim>
        <b-form id="full-form" :disabled="loading">
          <!-- Section loop -->
          <b-form-group
            class="sec"
            v-for="sec in get_sub(inputs)"
            :key="inputs[sec].order"
            :id="sec"
            :aria-describedby="sec + '-help '"
          >
          <!-- Make collapsible section, if it is one -->
          <legend :class="[{ 'pb-0': inputs[sec].description, 'pb-2': !inputs[sec].description }, 'my-0 col-form-label-lg pt-0 font-weight-bold']">
            {{ inputs[sec].label }}
            <b-button
              :id="sec+'-arrow'"
              :class="'px-0'"
              v-if="inputs[sec].collapsible"
              @click.prevent
              v-b-toggle
              :href="'#' + sec + '-toggle'"
              variant="link"
            >
              <b-icon-chevron-down class="arrow" font-scale="1.5" :aria-label="'Toggle ' + inputs[sec].label"/>
            </b-button>
          </legend>
          <b-form-text v-if="inputs[sec].description" v-html="inputs[sec].description" :id="sec + '-help'" class="m-0 pb-2 f-5"></b-form-text>
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
                :label-class="[{ 'py-0': inputs[sec][subsec].description || inputs[sec][subsec].predescription || inputs[sec][subsec].dynamic_description, 'pb-2': !(inputs[sec][subsec].description || inputs[sec][subsec].predescription || inputs[sec][subsec].dynamic_description)}, 'h3']"
                :key="inputs[sec][subsec].order"
                :id="sec + '-' + subsec"
                :aria-describedby="(inputs[sec][subsec].description || inputs[sec][subsec].predescription || inputs[sec][subsec].dynamic_description)? sec + '-' + subsec  + '-help': ''"
              >
                <b-form-row
                  v-show="inputs[sec][subsec].show"
                  v-if="inputs[sec][subsec].type != 'multi'"
                >
                  <b-form-text v-if="inputs[sec][subsec].description" v-html="inputs[sec][subsec].description" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 pl-1 f-6"></b-form-text>
                  <b-form-text v-else-if="inputs[sec][subsec].predescription" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 pl-1 f-6">
                    <span v-html="inputs[sec][subsec].predescription"/>
                    <b>{{ inputs[sec][subsec][inputs[sec][subsec].ref_var].value==""? inputs[sec][subsec][inputs[sec][subsec].ref_var].placeholder : inputs[sec][subsec][inputs[sec][subsec].ref_var].value }}</b>
                    <span v-html="inputs[sec][subsec].postdescription"/>
                  </b-form-text>
                  <b-form-text v-else-if="inputs[sec][subsec].dynamic_description" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 pl-1 f-6">
                    <span v-html="inputs[sec][subsec].dynamic_description[inputs[sec][subsec][inputs[sec][subsec].ref_var].value]"/>
                  </b-form-text>
                  <!-- Field loop -->
                  <b-col
                    v-for="input_var in get_sub(inputs[sec][subsec])"
                    :key="inputs[sec][subsec][input_var].order"
                    :sm="inputs[sec][subsec][input_var].cols ? inputs[sec][subsec][input_var].cols : 12"
                    :align-self="inputs[sec][subsec][input_var].type == 'boolean'? 'center' : 'start'"
                  >
                    <b-form-group
                      class="field"
                      v-show="inputs[sec][subsec][input_var].show == false? false : true"
                      :label="inputs[sec][subsec][input_var].label"
                      :label-for="input_var"
                      label-align=left
                      :id="sec + '-' + subsec + '-' + input_var"
                    >
                      <!-- ValidationProvider allows VeeValidate to put rules on a field -->
                      <ValidationProvider
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
                          :id="subsec + '-' + input_var"
                          :file-name-formatter="formatNames"
                          :placeholder="inputs[sec][subsec][input_var].multiple? 'Choose files or drop them here...' : 'Choose file or drop one here...'"
                          :drop-placeholder="inputs[sec][subsec][input_var].multiple? 'Drop files here...' : 'Drop file here...'"
                          accept=".fasta, .fa, .fna, .ffn, .faa, .frn, .aln, .txt"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          :state="getValidationState(validationContext)"
                          @change="validationContext.validate"
                          :multiple="inputs[sec][subsec][input_var].multiple"
                          :disabled="loading"
                        ></b-form-file>
                        <b-form-checkbox-group
                          v-if="inputs[sec][subsec][input_var].type == 'checkbox'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :id="subsec + '-' + input_var"
                          :options="inputs[sec][subsec][input_var].fields"
                          :disabled="loading"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          switches
                          class="text-center"
                        ></b-form-checkbox-group>
                        <b-form-checkbox
                          v-if="inputs[sec][subsec][input_var].type == 'boolean'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :id="subsec + '-' + input_var"
                          :disabled="loading"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          switch
                          class="text-center"
                        >{{ inputs[sec][subsec][input_var].fields }}</b-form-checkbox>
                        <b-form-input
                          v-if="inputs[sec][subsec][input_var].type == 'number'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :placeholder="inputs[sec][subsec][input_var].placeholder ? inputs[sec][subsec][input_var].placeholder.toString() : ''"
                          :id="subsec + '-' + input_var"
                          :type="inputs[sec][subsec][input_var].type"
                          :step="inputs[sec][subsec][input_var].step"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          :state="getValidationState(validationContext)"
                          :disabled="loading"
                        ></b-form-input>
                        <b-form-select
                          v-if="inputs[sec][subsec][input_var].type == 'options'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :id="subsec + '-' + input_var"
                          :options="inputs[sec][subsec][input_var].options"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          :state="getValidationState(validationContext)"
                          :disabled="loading"
                        >
                        </b-form-select>
                        <b-form-radio-group
                          v-if="inputs[sec][subsec][input_var].type == 'radio'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :id="subsec + '-' + input_var"
                          :options="inputs[sec][subsec][input_var].options"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          button-variant="outline-secondary"
                          buttons
                          :disabled="loading"
                        >
                        </b-form-radio-group>
                        <b-form-input
                          v-if="inputs[sec][subsec][input_var].type == 'text'"
                          v-model="inputs[sec][subsec][input_var].value"
                          :placeholder="inputs[sec][subsec][input_var].placeholder ? inputs[sec][subsec][input_var].placeholder.toString() : ''"
                          :id="subsec + '-' + input_var"
                          :type="inputs[sec][subsec][input_var].type"
                          :aria-describedby="subsec + '-' + input_var + '-help ' + subsec + '-' + input_var + '-feedback'"
                          :state="getValidationState(validationContext)"
                          :disabled="loading"
                        ></b-form-input>
                        <b-form-text v-if="inputs[sec][subsec][input_var].description" :id="subsec + '-' + input_var + '-help'" v-html="inputs[sec][subsec][input_var].description"></b-form-text>
                        <b-form-text v-else-if="inputs[sec][subsec][input_var].predescription" :id="subsec + '-' + input_var + '-help'" class="m-0 pb-2 f-6">
                          <span v-html="inputs[sec][subsec][input_var].predescription"/>
                          <b>{{ inputs[sec][subsec][input_var].value==""? inputs[sec][subsec][input_var].placeholder : inputs[sec][subsec][input_var].value }}</b>
                          <span v-html="inputs[sec][subsec][input_var].postdescription"/>
                        </b-form-text>
                        <b-form-text v-else-if="inputs[sec][subsec][input_var].dynamic_description" :id="subsec + '-' + input_var + '-help'" class="m-0 pb-2 f-6">
                          <span v-html="inputs[sec][subsec][input_var].dynamic_description[inputs[sec][subsec][input_var].value]"/>
                        </b-form-text>
                        <b-form-invalid-feedback :id="subsec + '-' + input_var + '-feedback'" :state="getValidationState(validationContext)">{{ validationContext.errors[0] }}</b-form-invalid-feedback>
                      </ValidationProvider>
                    </b-form-group>
                  </b-col>
                </b-form-row>
                <b-form
                  :id="sec + '-' + subsec"
                  v-show="inputs[sec][subsec].show"
                  v-if="inputs[sec][subsec].type == 'multi'"
                >
                  <b-form-row>
                    <b-col sm=11>
                      <b-form-row>
                        <b-col
                          v-for="input_var in get_sub(inputs[sec][subsec])"
                          :key="subsec + '-' + input_var"
                          :sm="inputs[sec][subsec][input_var].cols ? inputs[sec][subsec][input_var].cols : 12"
                        >
                          <b-form-group
                            :label="inputs[sec][subsec][input_var].label"
                            :label-for="subsec + '-' + input_var"
                            v-show="inputs[sec][subsec][input_var].show == false? false : true"
                            label-align=left
                          >
                            <b-form-input
                              v-if="inputs[sec][subsec][input_var].type == 'number'"
                              v-model="inputs[sec][subsec][input_var].value"
                              :id="subsec + '-' + input_var"
                              :type="inputs[sec][subsec][input_var].type"
                              :step="inputs[sec][subsec][input_var].step"
                              :aria-describedby="subsec + '-' + input_var + '-feedback'"
                              :state="inputs[sec][subsec][input_var].valid"
                              :disabled="loading"
                            ></b-form-input>
                            <b-form-input
                              v-if="inputs[sec][subsec][input_var].type == 'text'"
                              v-model="inputs[sec][subsec][input_var].value"
                              :id="subsec + '-' + input_var"
                              :type="inputs[sec][subsec][input_var].type"
                              :placeholder="inputs[sec][subsec][input_var].placeholder"
                              :aria-describedby="subsec + '-' + input_var + '-feedback'"
                              :state="inputs[sec][subsec][input_var].valid"
                              :disabled="loading"
                            ></b-form-input>
                            <b-form-checkbox-group
                              v-if="inputs[sec][subsec][input_var].type == 'checkbox'"
                              v-model="inputs[sec][subsec][input_var].value"
                              :id="subsec + '-' + input_var"
                              :options="inputs[sec][subsec][input_var].fields"
                              :disabled="loading"
                              switches
                              class="text-center"
                            ></b-form-checkbox-group>
                            <b-form-checkbox
                              v-if="inputs[sec][subsec][input_var].type == 'boolean'"
                              v-model="inputs[sec][subsec][input_var].value"
                              :id="subsec + '-' + input_var"
                              :disabled="loading"
                              switch
                              class="text-center"
                            >{{ inputs[sec][subsec][input_var].fields }}</b-form-checkbox>
                            <b-form-text v-if="inputs[sec][subsec][input_var].description" :id="subsec + '-' + input_var + '-help'" v-html="inputs[sec][subsec][input_var].description"></b-form-text>
                            <b-form-text v-else-if="inputs[sec][subsec][input_var].predescription" :id="subsec + '-' + input_var + '-help'" class="m-0 pb-2 f-6">
                              <span v-html="inputs[sec][subsec][input_var].predescription"/>
                              <b>{{ inputs[sec][subsec][input_var].value==""? inputs[sec][subsec][input_var].placeholder : inputs[sec][subsec][input_var].value }}</b>
                              <span v-html="inputs[sec][subsec][input_var].postdescription"/>
                            </b-form-text>
                            <b-form-invalid-feedback
                              v-if="inputs[sec][subsec][input_var].valid==false"
                              :key="inputs[sec][subsec][input_var].valid"
                              :id="subsec + '-' + input_var + '-feedback'"
                              :state="inputs[sec][subsec][input_var].valid"
                            >
                              The {{ inputs[sec][subsec][input_var].label }} is required
                            </b-form-invalid-feedback>
                          </b-form-group>
                        </b-col>
                      </b-form-row>
                    </b-col>
                    <b-col sm=1 cols=4 class="mx-auto mt-sm-4">
                      <b-button pill v-on:click.prevent="updateList(sec, subsec)" variant="success" class="add" :disabled="loading"><b-icon-plus aria-label="Add" font-scale="1.5"></b-icon-plus></b-button>
                    </b-col>
                  </b-form-row>
                  <div v-if="!checkEmpty(inputs[sec][subsec].value)">
                    <br>
                    <b-form-text v-if="inputs[sec][subsec].description" v-html="inputs[sec][subsec].description" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 f-5"></b-form-text>
                    <b-form-text v-else-if="inputs[sec][subsec].predescription" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 f-5">
                      <span v-html="inputs[sec][subsec].predescription"/>
                      <b>{{ inputs[sec][subsec][inputs[sec][subsec].ref_var].value==""? inputs[sec][subsec][inputs[sec][subsec].ref_var].placeholder : inputs[sec][subsec][inputs[sec][subsec].ref_var].value }}</b>
                      <span v-html="inputs[sec][subsec].postdescription"/>
                    </b-form-text>
                    <b-form-text v-else-if="inputs[sec][subsec].dynamic_description" :id="sec + '-' + subsec  + '-help'" class="m-0 pb-2 f-5">
                      <span v-html="inputs[sec][subsec].dynamic_description[inputs[sec][subsec][inputs[sec][subsec].ref_var].value]"/>
                    </b-form-text>
                    <b-table :items="inputs[sec][subsec].value" :fields="createFields(sec, subsec)" small>
                      <template #cell(delete)="data">
                        <b-button pill v-on:click.prevent="deleteRow(inputs[sec][subsec].value, data.index)" variant="outline-danger" class="delete" :disabled="loading"><b-icon-dash aria-label="Delete" font-scale="1"></b-icon-dash></b-button>
                      </template>
                    </b-table>
                  </div>
                  <b-form-invalid-feedback
                    v-else-if="inputs[sec][subsec].valid==false"
                    :key="inputs[sec][subsec].value.length"
                    :id="subsec + '-feedback'"
                    :state="!checkEmpty(inputs[sec][subsec].value)"
                  >
                    At least one {{ inputs[sec][subsec][inputs[sec][subsec].ref_var].label }} is required
                  </b-form-invalid-feedback>
                </b-form>
              </b-form-group>
            </b-collapse>
            <hr v-if="inputs[sec].order != 3">
          </b-form-group>
          <!-- submit button -->
          <b-overlay
            :show="loading"
            rounded="pill"
            opacity="0.7"
            blur="5px"
            spinner-variant="secondary"
          >
            <b-button pill block v-on:click.prevent="validateMultiParts().then(valid => {if (valid) {handleSubmit(adapt_run)} else {validate()}})" size="lg" type="submit" variant="outline-secondary" :disabled="loading">Submit a Run</b-button>
          </b-overlay>
        </b-form>
      </ValidationObserver>
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
const csrfToken = Cookies.get('csrftoken');

export default {
  name: 'RunADAPT',
  components: {
    ValidationProvider,
    ValidationObserver,
  },
  mounted () {
    // Makes VeeValidate check only on change events if the field is untouched or valid,
    // but on input events if the field is invalid
    setInteractionMode('eager');
    // Direct reference to checkEmpty needed for extend to access it within validate
    let checkEmpty = this.checkEmpty
    let vm = this
    // 'extend' creates rules for validation. In theory VeeValidate should come with many
    // of these preimplemented (such as 'required' and 'integer'), but preimplemented versions
    // don't work for anything with named parameters for some reason
    extend('required', {
      ...required,
      message: "The {_field_} is required"
    });
    // Sets field to be required if another field (args[0]) is/has any of the values (args[1:])
    extend('required_if', {
      computesRequired: true,
      validate(value, args) {
        let required;
        if (args.length > 1) {
          if (Array.isArray(args[0])) {
            required = args.slice(1).some((arg) => args[0].includes(arg));
          } else {
            required = args.slice(1).includes(String(args[0]).trim());
          }
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
      // Sets the message to say less than a specified string if one is supplied; otherwise, just says number
      message: (fieldName, placeholders) => {
        if (placeholders[1]) {
          return `The ${fieldName} must be less than or equal to the ${placeholders[1]}`;
        }
        return `The ${fieldName} must be at most ${placeholders[0]}`;
      }
    });
    extend('max_length', {
      validate(value, args) {
        return checkEmpty(args[0])? true : value.length <= Number(args[0]);
      },
      message: (fieldName, placeholders) => {
        return `The ${fieldName} must be at most ${placeholders[0]} characters`;
      }
    });
    // Specific rule for amplicon length
    extend('amplicon', {
      validate(value) {
        let primer_length = vm.inputs.advopts.all.pl.placeholder
        if (vm.inputs.advopts.all.pl.value) {
          primer_length = vm.inputs.advopts.all.pl.value
        }
        let guide_length = vm.inputs.advopts.all.gl.placeholder
        if (vm.inputs.advopts.all.gl.value) {
          guide_length = vm.inputs.advopts.all.gl.value
        }
        return (value >= primer_length & value >= guide_length);
      },
      message: "The {_field_} must be greater than the primer length and the guide length",
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
          collapsible: false,
          inputchoices: {
            show: true,
            inputchoice: {
              order: 0,
              label: 'Input Type',
              type: 'radio',
              value: '',
              options: [
                { value: 'auto-from-args', text: 'NCBI Taxonomy Identifier' },
                { value: 'fasta', text: 'Prealigned FASTA' },
              ],
              rules: 'required',
              exclude: true,
            },
          },
          autoinput: {
            order: 1,
            show: false,
            taxid: {
              order: 0,
              label: 'NCBI Taxonomy Identifier',
              type: 'number',
              value: '',
              description: 'Sequences will be downloaded from NCBI and aligned. Taxonomy Identifier can be determined <a href=https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Undef&id=10239&lvl=3&p=7&lin=f&keep=1&srchmode=1&unlock target="_blank" rel="noreferrer">here</a>.',
              rules: 'required_if:@inputchoice,auto-from-args|min_value:0',
              cols: 12,
            },
            segment: {
              order: 1,
              show: false,
              label: 'Segment',
              type: 'text',
              value: '',
              description: 'Segment required for segmented genomes.',
              rules: 'required_if:@segmented,true',
              cols: 0,
            },
            segmented: {
              order: 2,
              type: 'boolean',
              value: false,
              fields: 'Segmented Genome',
              rules: '',
              cols: 12,
              exclude: true,
            },
          },
          fileinput: {
            order: 2,
            show: false,
            fasta: {
              order: 0,
              label: 'Prealigned FASTA File',
              type: 'file',
              multiple: false,
              value: [],
              description: 'Sequence <i>must</i> be aligned. You can use <a href="https://mafft.cbrc.jp/alignment/server/" rel="noreferrer" target="_blank">MAFFT</a> to align FASTAs.',
              rules: 'required_if:@inputchoice,fasta',
            },
          },
          all: {
            order: 3,
            show: true,
            bestntargets: {
              order: 0,
              label: 'Number of Assays',
              type: 'number',
              value: 10,
              placeholder: 10,
              predescription: 'The ',
              postdescription: ' best assay designs will be outputted.',
              rules: 'between:1,20|integer',
            },
          },
        },
        sp: {
          order: 1,
          label: 'Specificity',
          collapsible: false,
          description: 'Sequences that should not be detected (optional)',
          all: {
            order: 0,
            show: true,
            sp_types: {
              order: 2,
              label: 'Input Types',
              type: 'checkbox',
              value: [],
              fields: [
                { text: 'Taxa', value: 'specificity_taxa' },
                { text: 'FASTAs', value: 'specificity_fasta' },
              ],
              rules: '',
              cols: 12,
              exclude: true,
            },
          },
          specificity_taxa: {
            order: 1,
            show: false,
            type: 'multi',
            value: [],
            ref_var: "sp_taxid",
            description: 'The assays designed will show up negative when tested against these taxons:',
            rules: 'required_if:@sp_types,specificity_taxa',
            valid: null,
            sp_taxid: {
              order: 0,
              label: 'NCBI Taxonomy Identifier',
              type: 'number',
              value: '',
              description: 'Sequences will be downloaded from NCBI. Taxonomy Identifier can be determined <a href=https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Undef&id=10239&lvl=3&p=7&lin=f&keep=1&srchmode=1&unlock target="_blank" rel="noreferrer">here</a>.',
              rules: 'required',
              valid: null,
              cols: 12,
            },
            sp_segment: {
              order: 1,
              show: false,
              label: 'Segment',
              type: 'text',
              value: '',
              description: 'Segment required for segmented genomes.',
              valid: null,
              rules: '',
              cols: 0,
            },
            sp_segmented: {
              order: 2,
              type: 'boolean',
              value: false,
              fields: 'Segmented Genome',
              rules: '',
              cols: 12,
              exclude: true,
            },
          },
          specificity_fasta: {
            order: 2,
            show: false,
            specificity_fasta: {
              order: 0,
              type: 'file',
              multiple: true,
              label: 'FASTA Files',
              description: 'Sequences do not need to be aligned.<br>The assays designed will show up negative when tested against the sequences in these FASTAs.',
              value: [],
              rules: 'required_if:@sp_types,specificity_fasta',
            },
          },
        },
        advopts: {
          order: 2,
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
              predescription: 'crRNAs will be precisely ',
              postdescription: ' bases long.',
              rules: 'min_value:1|integer',
              cols: 6,
            },
            pl: {
              order: 1,
              label: 'Primer Length',
              type: 'number',
              value: '',
              placeholder: 30,
              predescription: 'Primers will be precisely ',
              postdescription: ' bases long.',
              rules: 'min_value:1|integer',
              cols: 6,
            },
            max_target_length: {
              order: 2,
              label: 'Maximum Amplicon Length',
              type: 'number',
              value: '',
              placeholder: 250,
              predescription: 'The amplified region will be at most ',
              postdescription: ' bases long.',
              rules: 'amplicon|integer',
            },
          },
          primer: {
            order: 1,
            show: true,
            label: 'Primers',
            pm: {
              order: 0,
              label: 'Primer Mismatches',
              type: 'number',
              value: '',
              placeholder: 3,
              predescription: 'Classify primers with ',
              postdescription: ' mismatches as inactive.',
              rules: 'min_value:0|integer',
              cols: 4,
            },
            pp: {
              order: 1,
              label: 'Primer Coverage Fraction',
              type: 'number',
              value: '',
              placeholder: 0.98,
              step: 0.01,
              predescription: ' ',
              postdescription: ' is the fraction of sequences required to have active primers.',
              rules: 'between:0,1|double',
              cols: 4,
            },
            max_primers_at_site: {
              order: 2,
              label: 'Maximum Primers at Site',
              type: 'number',
              value: '',
              placeholder: 10,
              predescription: 'No more than ',
              postdescription: ' primers will be placed at a site',
              rules: 'min_value:1|integer',
              cols: 4,
            },
            primer_gc_lo: {
              order: 3,
              label: 'Low GC Fraction Content',
              type: 'number',
              value: '',
              placeholder: 0.35,
              step: 0.01,
              predescription: 'Classify primers with less than a fraction of ',
              postdescription: ' of bases in the primer that are either G or C as inactive.',
              rules: 'required_if_less:@primer_gc_hi,0.35|max_value:@primer_gc_hi,High GC Percent Content in Primer|between:0,1|double',
              cols: 6
            },
            primer_gc_hi: {
              order: 4,
              label: 'High GC Fraction Content',
              type: 'number',
              value: '',
              placeholder: 0.65,
              step: 0.01,
              predescription: 'Classify primers with more than a fraction of ',
              postdescription: ' of bases in the primer that are either G or C as inactive.',
              rules: 'required_if_greater:@primer_gc_lo,0.65|min_value:@primer_gc_lo,Low GC Percent Content in Primer|between:0,1|double',
              cols: 6
            },
          },
          autoadv: {
            order: 2,
            show: false,
            label: 'Alignment',
            cluster_threshold: {
              order: 0,
              label: 'Cluster Threshold',
              type: 'number',
              value: '',
              placeholder: 0.3,
              step: 0.01,
              description: 'A measure of how similar sequences need to be for them to be aligned.',
              rules: 'double',
              cols: 8
            },
            write_aln: {
              order: 1,
              type: 'boolean',
              value: true,
              fields: 'Output Alignment',
              rules: '',
              cols: 4
            },
          },
          obj: {
            order: 3,
            show: true,
            label: 'Objective',
            ref_var: 'obj',
            dynamic_description: {
              'maximize-activity': '<b>Maximize Activity</b> uses a machine learning model to optimize the fluorescence of crRNA assay set across all the sequences.',
              'minimize-guides': '<b>Minimize Guides</b> uses heuristics to determine if the crRNA is active and adds crRNAs to the assay until a certain percentage of all the sequences have an active crRNA.'
            },
            obj: {
              order: 0,
              type: 'radio',
              value: 'maximize-activity',
              options: [
                { value: 'maximize-activity', text: 'Maximize Activity' },
                { value: 'minimize-guides', text: 'Minimize Guides' },
              ],
              rules: 'required',
            },
          },
          minguides: {
            order: 4,
            show: false,
            gm: {
              order: 0,
              label: 'Guide Mismatches',
              type: 'number',
              value: '',
              placeholder: 3,
              predescription: 'Classify crRNAs with ',
              postdescription: ' mismatches or more as inactive.',
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
              predescription: ' ',
              postdescription: ' is the fraction of sequences required to have an active crRNA.',
              cols: 6,
            },
          },
          maxact: {
            order: 5,
            show: true,
            soft_guide_constraint: {
              order: 0,
              label: 'Soft Guide Constraint',
              type: 'number',
              value: '',
              placeholder: 1,
              predescription: 'Penalize each extra crRNA above ',
              postdescription: '.',
              rules: 'max_value:@hard_guide_constraint,Hard Guide Constraint|min_value:1|integer',
              cols: 6,
            },
            hard_guide_constraint: {
              order: 1,
              label: 'Hard Guide Constraint',
              type: 'number',
              value: '',
              placeholder: 5,
              predescription: 'Prevent the assay from having more than ',
              postdescription: ' crRNAs.',
              rules: 'required_if_greater:@soft_guide_constraint,5|min_value:@soft_guide_constraint,Soft Guide Constraint|integer',
              cols: 6,
            },
          },
          objw: {
            order: 6,
            show: true,
            objfnweights_a: {
              order: 1,
              label: 'Number of Primers Penalty',
              type: 'number',
              value: '',
              placeholder: 0.5,
              step: 0.01,
              predescription: ' ',
              postdescription: ' is the penalty imposed per extra primer.',
              rules: 'double',
              cols: 6
            },
            objfnweights_b: {
              order: 2,
              label: 'Amplicon Length Penalty',
              type: 'number',
              value: '',
              placeholder: 0.25,
              step: 0.01,
              predescription: ' ',
              postdescription: ' is the multiplier of the penalty imposed by the log of the amplicon length.',
              rules: 'double',
              cols: 6
            },
          },
          sp: {
            order: 7,
            show: false,
            label: 'Specificity',
            idm: {
              order: 0,
              label: 'Number of Mismatches to be Identical',
              type: 'number',
              value: '',
              placeholder: 4,
              predescription: 'If the guide matches a sequence it shouldn\'t (up to ',
              postdescription: ' mismatches), it will be classified as binding to it.',
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
              predescription: 'If the guide binds to a fraction of ',
              postdescription: ' of a nonspecific taxa/FASTA, it will be classified nonspecific.',
              rules: 'between:0,1|double',
              cols: 6,
            },
          },
          job: {
            order: 8,
            show: true,
            label: 'Computation',
            memory: {
              order: 0,
              label: 'Memory (GB)',
              type: 'number',
              value: '',
              placeholder: 2,
              predescription: 'The job will be given ',
              postdescription: ' GB of memory to run.',
              rules: 'between:1,200|integer',
            },
          },
        },
        postopts: {
          order: 3,
          collapsible: false,
          runopts: {
            show: true,
            nickname: {
              order: 0,
              label: 'Job Nickname',
              type: 'text',
              value: '',
              description: 'An optional, short (<50 characters) description of the run for your reference',
              rules: 'max_length:50'
            }
          }
        },
      },
      loading: false,
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
      return this.inputs.advopts.obj.obj.value
    },
    spval() {
      return this.inputs.sp.all.sp_types.value
    },
    sptaxaval() {
      return !this.checkEmpty(this.inputs.sp.specificity_taxa.value)
    },
    sptaxidval() {
      return !this.checkEmpty(this.inputs.sp.specificity_taxa.sp_taxid.value)
    },
    segmentedval() {
      return this.inputs.opts.autoinput.segmented.value
    },
    spsegmentedval() {
      return this.inputs.sp.specificity_taxa.sp_segmented.value
    },
    spsegmentval() {
      return (this.spsegmentedval & this.checkEmpty(this.inputs.sp.specificity_taxa.sp_segment.value))
    }
  },
  watch: {
    inputchoiceval(val) {
      this.inputs.opts.autoinput.show = val == 'auto-from-args';
      this.inputs.opts.fileinput.show = val == 'fasta';
      this.inputs.advopts.autoadv.show = val == 'auto-from-args';
    },
    objval(val) {
      this.inputs.advopts.minguides.show = val == 'minimize-guides';
      this.inputs.advopts.maxact.show = val == 'maximize-activity';
    },
    spval(val) {
      this.inputs.advopts.sp.show = (val.length > 0)
      this.inputs.sp.specificity_fasta.show = val.includes('specificity_fasta')
      this.inputs.sp.specificity_taxa.show = val.includes('specificity_taxa')
    },
    sptaxaval(val) {
      if (val) {
        this.inputs.sp.specificity_taxa.valid = null
      }
    },
    sptaxidval(val) {
      if (val) {
        this.inputs.sp.specificity_taxa.sp_taxid.valid = null
      }
    },
    spsegmentval(val) {
      this.inputs.sp.specificity_taxa.sp_segment.rules = val? 'required' : ''
      if (!val) {
        this.inputs.sp.specificity_taxa.sp_segment.valid = null
      }
    },
    segmentedval(val) {
      this.inputs.opts.autoinput.segment.show = val
      this.inputs.opts.autoinput.segment.cols = val? 6 : 0
      this.inputs.opts.autoinput.taxid.cols = val? 6 : 12
    },
    spsegmentedval(val) {
      this.inputs.sp.specificity_taxa.sp_segment.show = val
      this.inputs.sp.specificity_taxa.sp_segment.cols = val? 6 : 0
      this.inputs.sp.specificity_taxa.sp_taxid.cols = val? 6 : 12
    },
  },
  methods: {
    checkEmpty(val) {
      // Helper function
      return (Array.isArray(val) && val.length === 0) ||
             [false, null, undefined].includes(val) ||
             !String(val).trim().length
    },
    async validateMultiParts() {
      if (this.inputs.sp.specificity_taxa.show != false & this.checkEmpty(this.inputs.sp.specificity_taxa.value)) {
        this.inputs.sp.specificity_taxa.valid = false;
        return false;
      }
      this.inputs.sp.specificity_taxa.sp_taxid.valid = null;
      this.inputs.sp.specificity_taxa.sp_segment.valid = null;
      return true;
    },
    async adapt_run() {
      // Handles submission
      // Relies on innermost input field names matching adapt_web.wdl's input variable names.
      this.loading = true
      let response = null
      try {
        let form_data = new FormData()
        for (let sec of this.get_sub(this.inputs)) {
          for (let subsec of this.get_sub(this.inputs[sec])) {
            if (this.inputs[sec][subsec].show != false) {
              if (this.inputs[sec][subsec].type == 'multi') {
                form_data.append(subsec, JSON.stringify(this.inputs[sec][subsec].value));
              } else {
                for (let input_var of this.get_sub(this.inputs[sec][subsec])) {
                  if (this.inputs[sec][subsec][input_var].show != false & !this.checkEmpty(this.inputs[sec][subsec][input_var].value)) {
                    if (input_var.includes('fasta')) {
                      if (Array.isArray(this.inputs[sec][subsec][input_var].value)) {
                        for (let file of this.inputs[sec][subsec][input_var].value) {
                          form_data.append(input_var + '[]', file, file.name);
                        }
                      } else {
                        form_data.append(input_var + '[]',
                                         this.inputs[sec][subsec][input_var].value,
                                         this.inputs[sec][subsec][input_var].value.name);
                      }
                    } else if (!this.inputs[sec][subsec][input_var].exclude){
                      form_data.append(input_var, this.inputs[sec][subsec][input_var].value)
                    }
                  }
                }
              }
            }
          }
        }

        response = await fetch('/api/adaptrun/', {
          method: 'POST',
          headers: {
            "X-CSRFToken": csrfToken
          },
          body: form_data,
        })

        if (response.ok) {
          let responsejson = await response.json()
          let runid = responsejson.cromwell_id.slice(0,8) + ';' + responsejson.submit_time + ';' + form_data.get('nickname')
          let prev_runids = Cookies.get('runid')
          if (prev_runids == null) {
            Cookies.set('runid', runid)
          }
          else {
            Cookies.set('runid', prev_runids + ',' + runid)
          }
          Cookies.set('submitted', true)
          window.location.href = '/results'
        }
        else {
          let contentType = response.headers.get("content-type");
          if (contentType && contentType.indexOf("application/json") !== -1) {
            let responsejson = await response.json()
            this.$root.$data.modaltitle = Object.keys(responsejson)[0]
            this.$root.$data.modalmsg = responsejson[this.$root.$data.modaltitle]
          }
          else {
            this.$root.$data.modaltitle = 'Error'
            this.$root.$data.modalmsg = await response.text()
          }
          this.$root.$data.modalvariant = 'danger'
          this.$root.$emit('show-msg');
        }
      }
      catch (error) {
        this.$root.$data.modaltitle = 'Error'
        this.$root.$data.modalmsg = error.message
        this.$root.$data.modalvariant = 'danger'
        this.$root.$emit('show-msg');
      }
      finally {
        this.loading = false
      }
      return response
    },
    get_sub(sec) {
      // Helper function to get children of section
      return Object.keys(sec).filter(item => {
        return !(['order', 'label', 'collapsible', 'show', 'value', 'type', 'rules', 'fields', 'exclude', 'description', 'predescription', 'postdescription', 'dynamic_description', 'ref_var', 'multiple', 'valid'].includes(item));
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
    multiValidate(sec, subsec) {
      for (let input_var of this.get_sub(this.inputs[sec][subsec])) {
        if (this.inputs[sec][subsec][input_var].show != false) {
          if (this.inputs[sec][subsec][input_var].rules.includes('required')) {
            if (this.checkEmpty(this.inputs[sec][subsec][input_var].value)) {
              this.inputs[sec][subsec][input_var].valid = false;
              return false
            }
          }
        }
      }
      return true
    },
    async updateList(sec, subsec) {
      if (this.multiValidate(sec, subsec)) {
        let obj = {}
        for (let input_var of this.get_sub(this.inputs[sec][subsec])) {
          if (!this.inputs[sec][subsec][input_var].exclude) {
            if (this.inputs[sec][subsec][input_var].value) {
              obj[input_var] = this.inputs[sec][subsec][input_var].value;
            }
            else {
              obj[input_var] = this.inputs[sec][subsec][input_var].placeholder;
            }
            this.inputs[sec][subsec][input_var].value = '';
          }
        }
        this.inputs[sec][subsec].value.push(obj);
      }
    },
    createFields(sec, subsec) {
      let fields = [];
      for (let input_var of this.get_sub(this.inputs[sec][subsec])) {
        if (!this.inputs[sec][subsec][input_var].exclude) {
          fields.push({
            key: input_var,
            label: this.inputs[sec][subsec][input_var].label,
            thClass: 'f-5',
            thStyle: 'width: 45.8333%; padding: 5px'
          });
        }
      }
      fields.push({key: 'delete', label: '', tdClass: 'text-right delete-col', thStyle: 'width: 8.333%; padding: 5px'});
      return fields;
    },
    deleteRow(table, index) {
      table.splice(index, 1);
    },
  },
}
</script>
