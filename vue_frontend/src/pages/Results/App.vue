<template>
  <div id="app" class="mx-3 mt-4 mb-5">
    <Header/>
    <Results/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Results from '@/components/Results.vue'

export default {
  name: 'App',
  components: {
    Header,
    Results
  }
}
</script>
