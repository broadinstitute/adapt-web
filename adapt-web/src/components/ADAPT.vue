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
    <form id="status-form">
      <div class="field">
        <label class="label">runid</label>
        <input type="text" class="input" name="runid" v-model="runid">
      </div>

      <span>Status: {{ status }}</span>
      <!-- submit button -->
      <div class="field has-text-right">
        <button v-on:click.prevent="run_status" type="submit" class="button is-danger" name="status_submit">Get Status</button>
      </div>

      <!-- submit button -->
      <div class="field has-text-right">
        <button v-on:click.prevent="get_results" type="submit" class="button is-danger" name="results_submit">Download Results</button>
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
      fasta: '',
      runid: '',
      status: '',
    }
  },
  methods: {
    async adapt_run(event) {
      let data = new FormData()
      data.append('taxid', this.taxid)
      data.append('segment', this.segment)
      data.append('obj', this.obj)
      data.append('fasta', this.fasta)

      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/', {
        method: 'POST',
        headers: {
          "X-CSRFToken": csrfToken
        },
        body: data,
      }).then(response =>
        response.json().then(data => ({
            data: data,
            status: response.status
        })
      ))
      return response
    },
    async run_status(event) {
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/status', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      }).then(response =>
        response.json().then(data => ({
            data: data,
            status: response.status
        })
      ))

      this.status = response.data.status
      return response
    },
    async get_results(event) {
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/outputs', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      }).then(response => {
        if (response.status == 200) {
          this.downloadGuides(response)
        } else {
          response
        }
      })

      return response
    },
    async downloadGuides(response){
      let blob = await response.blob()
      let url = window.URL.createObjectURL(new Blob([blob]))
      let link = document.createElement('a')
      link.href = url
      let filename = this.runid
      if (blob.type == "text/csv") {
        filename = filename + '.csv'
      }
      else {
        filename = filename + '.zip'
      }
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
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
