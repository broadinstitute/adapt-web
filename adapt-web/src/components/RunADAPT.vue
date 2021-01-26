<template>
  <div class="runadapt">
    <form id="run-form">
      <section id="input-form">
        <h2>Input</h2>
        <div class="field">
          <label class="label">Taxonomic ID: </label>
          <input type="number" name="taxid" v-model="form_input.taxid">
        </div>

        <div class="field">
          <label class="label">Segment: </label>
          <input type="text" name="segment" v-model="form_input.segment">
        </div>

        <div class="large-12 medium-12 small-12 cell">
          <label class="label">Input FASTAs: </label>
          <input type="file" id="fasta" ref="fasta" multiple v-on:change="handleFASTAUpload()"/>
        </div>
      </section>

      <section id="specificity-form">
        <h2>Specificity</h2>
        <div class="large-12 medium-12 small-12 cell">
          <label class="label">File</label>
          <input type="file" id="specificity_fasta" ref="specificity_fasta" multiple v-on:change="handleSpecificityFASTAUpload()"/>
        </div>
      </section>

      <section id="options-form">
        <h2>Options</h2>
        <div id="v-model-select" class="field">
          <label class="label">Objective: </label>
          <select v-model="form_input.obj">
            <option disabled value="">Please select one: </option>
            <option value="maximize-activity">maximize activity</option>
            <option value="minimize-guides">minimize guides</option>
          </select>
        </div>
        <div class="field">
          <label>Number of Assays</label>
          <input class="label" type="number" name="bestntargets" v-model="form_input.bestntargets">
        </div>
      </section>

      <section id="advoptions-form">
        <h2>Advanced Options</h2>
        <div class="field">
          <label class="label">Guide Length: </label>
          <input type="number" name="gl" v-model="form_input.gl">
        </div>
        <div class="field">
          <label class="label">Primer Length: </label>
          <input type="number" name="pl" v-model="form_input.pl">
        </div>
        <div class="field">
          <label class="label">Primer Mismatches: </label>
          <input type="number" name="pm" v-model="form_input.pm">
        </div>
        <div class="field">
          <label class="label">Primer Coverage Fraction</label>
          <input type="number" name="pp" v-model="form_input.pp" min="0" max="1" step=".000001">
        </div>
        <div class="field">
          <label class="label">Primer GC content</label>
          <label class="label">Low</label>
          <input type="number" name="gclo" v-model="form_input.primer_gc_lo" min="0" max="1" step=".000001">
          <label class="label">High</label>
          <input type="number" name="gchi" v-model="form_input.primer_gc_hi" min="0" max="1" step=".000001">
        </div>
        <div class="field">
          <label class="label">Maximum number of Primers at a site: </label>
          <input type="number" name="max_primers_at_site" v-model="form_input.max_primers_at_site">
        </div>
        <div class="field">
          <label class="label">Maximum Amplicon Length: </label>
          <input type="number" name="max_target_length" v-model="form_input.max_target_length">
        </div>
        <div class="field">
          <label class="label">Objective Function Weights: </label>
          <label class="label">Penalty for Number of Primers: </label>
          <input type="number" name="objfnweights_a" v-model="form_input.objfnweights_a" min="0" max="1" step=".000001">
          <label class="label">Penalty for Amplicon Length: </label>
          <input type="number" name="objfnweights_b" v-model="form_input.objfnweights_b" min="0" max="1" step=".000001">
        </div>
        <div class="field">
          <label class="label">Cluster Threshold: </label>
          <input type="number" name="cluster_threshold" v-model="form_input.cluster_threshold" min="0" max="1" step=".000001">
        </div>
        <h3>Advanced Specificity Options</h3>
        <div class="field">
          <label class="label">Number of Mismatches to be Identical: </label>
          <input type="number" name="idm" v-model="form_input.idm">
        </div>
        <div class="field">
          <label class="label">Fraction of Group Hit to be Identical: </label>
          <input type="number" name="idfrac" v-model="form_input.idfrac" min="0" max="1" step=".000001">
        </div>
        <h3>Advanced Minimize Guides Options</h3>
        <div class="field">
          <label class="label">Guide Mismatches: </label>
          <input type="number" name="gm" v-model="form_input.gm">
        </div>
        <div class="field">
          <label class="label">Guide Coverage Fraction: </label>
          <input type="number" name="gp" v-model="form_input.gp" min="0" max="1" step=".000001">
        </div>
        <h3>Advanced Maximize Activity Options</h3>
        <div class="field">
          <label class="label">Soft Guide Constraint: </label>
          <input type="number" name="soft_guide_constraint" v-model="form_input.soft_guide_constraint">
        </div>
        <div class="field">
          <label class="label">Hard Guide Constraint: </label>
          <input type="number" name="hard_guide_constraint" v-model="form_input.hard_guide_constraint">
        </div>
      </section>

      <!-- submit button -->
      <div class="field has-text-right">
        <button v-on:click.prevent="adapt_run" type="submit" class="button is-danger">Submit</button>
      </div>
    </form>
  </div>
</template>

<script>
const Cookies = require('js-cookie')

export default {
  name: 'RunADAPT',
  data () {
    return {
      form_input: {
        taxid: '',
        segment: '',
        obj: '',
        bestntargets: '',
        gl: '',
        pl: '',
        pm: '',
        pp: '',
        primer_gc_lo: '',
        primer_gc_hi: '',
        objfnweights_a: '',
        objfnweights_b: '',
        cluster_threshold: '',
        max_primers_at_site: '',
        max_target_length: '',
        idm: '',
        idfrac: '',
        gm: '',
        gp: '',
        soft_guide_constraint: '',
        hard_guide_constraint: '',
        fasta: '',
        specificity_fasta: '',
      },
    }
  },
  methods: {
    async adapt_run(event) {
      let form_data = new FormData()
      for (let input_var of Object.keys(this.form_input)) {
        if (this.form_input[input_var] != '') {
          form_data.append(input_var, this.form_input[input_var])
        }
      }
      // form_data.append('taxid', this.form_input.taxid)
      // form_data.append('segment', this.form_input.segment)
      // form_data.append('obj', this.form_input.obj)
      for (let file of this.form_input.fasta) {
        form_data.append('fasta[]', file, file.name);
      }
      for (let file of this.form_input.specificity_fasta) {
        form_data.append('specificity_fasta[]', file, file.name);
      }

      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/', {
        method: 'POST',
        headers: {
          "X-CSRFToken": csrfToken
        },
        body: form_data,
      }).then(response =>
        response.json().then(responsejson => ({
          data: responsejson,
          status: response.status
        })
      ))
      return response
    },
    handleFASTAUpload(){
      this.form_input.fasta = this.$refs.fasta.files;
    },
    handleSpecificityFASTAUpload(){
      this.form_input.specificity_fasta = this.$refs.specificity_fasta.files;
    }
  }
}
</script>
