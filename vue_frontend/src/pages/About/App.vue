<template>
  <div id="app" class="mb-5">
  <Header/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=2></b-col>
      <b-col cols=12 md=8>
        <About class="px-4"/>
      </b-col>
      <b-col cols=0 md=2></b-col>
    </b-row>
  </b-container>
  <Footer/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import About from '@/components/About.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    About,
    Footer
  }
}
</script>
