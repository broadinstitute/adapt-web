<template>
  <div id="app" class="mx-3 mt-4 mb-5">
    <Design
      v-for="virus in viruses"
      :key="virus.taxid"
      :family="virus.family"
      :genus="virus.genus"
      :species="virus.species"
      :subspecies="virus.subspecies"
    ></Design>
  </div>
</template>

<script>
import Design from '@/components/Design.vue'
const Cookies = require('js-cookie')
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'App',
  components: {
    Design
  },
  data () {
    return {
      viruses: {}
    }
  },
  created () {
    this.fetchData()
  },
  methods : {
    async fetchData () {
      let response = await fetch('/api/virus/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        this.viruses = await response.json()
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    }
  }
}
</script>
