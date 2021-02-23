<template>
  <transition appear name="fade">
    <div class="results">
      <div v-if="submitted">Job submitted!<br>
      Your run ID is {{runid}}. Store this for future reference.<br>
      Check below for status.</div>
      <form id="status-form">
        <div class="field">
          <label class="label">Run ID: </label>
          <input type="text" name="runid" v-model="runid">
        </div>

        <span>Status: {{ status }}</span>
        <!-- submit button -->
        <div class="field has-text-right">
          <button v-on:click.prevent="run_status" type="submit" class="button is-danger" name="status_submit">Get Status</button>
        </div>

        <!-- submit button -->
        <div class="field has-text-right">
          <button v-on:click.prevent="get_results" type="submit" class="button is-danger" name="download_submit">Download Results</button>
        </div>

        <!-- submit button -->
        <div class="field has-text-right">
          <button v-on:click.prevent="display_results" type="submit" class="button is-danger" name="display_submit">Display Results</button>
        </div>
      </form>
      <p>{{ resultjson }}</p>
    </div>
  </transition>
</template>

<script>
const Cookies = require('js-cookie')

export default {
  name: 'Results',
  data () {
    return {
      runid: '',
      status: '',
      resultjson: '',
      submitted: false,
    }
  },
  mounted() {
    // Check if a job was just submitted based on cookies
    if (Cookies.get('runid') != null) {
      this.runid = Cookies.get('runid')
      if (Cookies.get('submitted') == 'true') {
        Cookies.remove('submitted')
        this.submitted = true
      }
    }
  },
  methods: {
    async run_status(event) {
      // Check the status of a job from backend
      Cookies.set('runid', this.runid)
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/status', {
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
      // Get results ad JSON from backend
      // TODO do something with them
      Cookies.set('runid', this.runid)
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/results', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        this.resultjson = await response.json()
      } else {
        let msg = await response.text()
        alert(msg);
      }
      return response
    },
    async get_results(event) {
      // Download results as a TSV or ZIP from backend
      Cookies.set('runid', this.runid)
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/download', {
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
  }
}
</script>
