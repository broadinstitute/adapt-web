<template>
  <ADAPT msg="Welcome to Your Vue.js App"/>
  <Design
    v-for="virus in viruses"
    :key="virus.id"
    :family="virus.family"
    :genus="virus.genus"
    :species="virus.species"
    :subspecies="virus.subspecies"
  ></Design>
</template>

<script>
import ADAPT from '@/components/ADAPT.vue'
import Design from '@/components/Design.vue'

export default {
  name: 'App',
  components: {
    ADAPT,
    Design
  },
  data () {
    return {
      viruses: [
        { id: 1, family: 'Flaviviridae', genus: 'Flaviviridae', species: 'Zika virus', subspecies: 'None' },
        { id: 2, family: 'Coronaviridae', genus: 'Betacoronavirus', species: 'Severe acute respiratory syndrome-related coronavirus', subspecies: 'SARS-CoV-2' }
      ]
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
