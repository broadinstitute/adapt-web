<template>
  <div id="app" class="mx-3 mt-4 mb-5">
    <Header/>
    <RunADAPT/>
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
