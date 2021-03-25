<template>
  <div id="app" class="mb-5">
  <Header page="Home"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=2></b-col>
      <b-col cols=12 md=8>
        <Home class="px-4"/>
      </b-col>
      <b-col cols=0 md=2></b-col>
    </b-row>
  </b-container>
  <Footer/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Home from '@/components/Home.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    Home,
    Footer
  }
}
</script>
