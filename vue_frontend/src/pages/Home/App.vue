<template>
  <div id="app" class="mx-3 mt-4 mb-5">
    <Header/>
    <Home/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Home from '@/components/Home.vue'

export default {
  name: 'App',
  components: {
    Header,
    Home
  }
}
</script>
