<template>
  <div id="app" class="mx-3 mt-4 mb-5">
  <Header/>
  <b-row class="mt-5">
    <b-col cols=0 md=2></b-col>
    <b-col>
      <RunADAPT/>
    </b-col>
    <b-col cols=0 md=2></b-col>
  </b-row>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import RunADAPT from '@/components/RunADAPT.vue'

export default {
  name: 'App',
  components: {
  Header,
  RunADAPT
  }
}
</script>
