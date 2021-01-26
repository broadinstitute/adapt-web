<template>
  <div class="results">
    <form id="status-form">
      <div class="field">
        <label class="label">runid</label>
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
  </div>
</template>

<script>
const Cookies = require('js-cookie')

export default {
  name: 'Results',
  data () {
    return {
      runid: '',
      status: '',
    }
  },
  methods: {
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
    async display_results(event) {
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/results', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })

      return response
    },
    async get_results(event) {
      const csrfToken = Cookies.get('csrftoken')

      let response = await fetch('/api/adaptruns/' + this.runid + '/download', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      }).then(response => {
        if (response.status == 200) {
          this.download_file(response)
        } else {
          response
        }
      })

      return response
    },
    async download_file(response){
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
