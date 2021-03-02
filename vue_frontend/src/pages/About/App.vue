<template>
  <div id="app" class="mb-5">
  <Header/>
  <b-row class="mt-5">
    <b-col cols=0 md=2></b-col>
    <b-col>
      <About/>
    </b-col>
    <b-col cols=0 md=2></b-col>
  </b-row>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import About from '@/components/About.vue'

export default {
  name: 'App',
  components: {
    Header,
    About
  }
}
</script>
