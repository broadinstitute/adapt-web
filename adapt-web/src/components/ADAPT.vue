<template>
  <div class="adapt">
    <form id="run-form">
      <div class="field">
        <label class="label">taxid</label>
        <input type="number" class="input" name="taxid" v-model="taxid">
      </div>

      <div class="field">
        <label class="label">segment</label>
        <input type="text" class="input" name="segment" v-model="segment">
      </div>

      <div id="v-model-select" class="field">
        <label class="label">objective</label>
        <select v-model="obj">
          <option disabled value="">Please select one</option>
          <option value="maximize-activity">maximize activity</option>
          <option value="minimize-guides">minimize guides</option>
        </select>
        <span>Objective: {{ obj }}</span>
      </div>

      <div class="large-12 medium-12 small-12 cell">
        <label>File
          <input type="file" id="fasta" ref="fasta" v-on:change="handleFileUpload()"/>
        </label>
      </div>

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
  name: 'ADAPT',
  props: {
    msg: String
  },
  data () {
    return {
      taxid: '',
      segment: '',
      obj: '',
      fasta: ''
    }
  },
  methods: {
    async adapt_run(event) {

      var data = new FormData()
      data.append('taxid', this.taxid)
      data.append('segment', this.segment)
      data.append('obj', this.obj)
      data.append('fasta', this.fasta)

      const csrfToken = Cookies.get('csrftoken')

      const response = await fetch('/api/adaptruns/', {
        method: 'POST',
        headers: {
          "X-CSRFToken": csrfToken
        },
        body: data,
      })
      return response.json()
    },
    handleFileUpload(){
      this.fasta = this.$refs.fasta.files[0];
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!-- <style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style> -->
