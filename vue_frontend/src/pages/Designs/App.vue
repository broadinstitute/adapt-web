<template>
  <div id="app" class="mx-3 mt-4 mb-5">
    <Header/>
    <Design/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Design from '@/components/Design.vue'
const Cookies = require('js-cookie')
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'App',
  components: {
    Header,
    Design
  }
}
</script>
