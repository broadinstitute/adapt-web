<template>
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
import Design from '@/components/Design.vue'

export default {
  name: 'App',
  components: {
    Design
  },
  data () {
    return {
      viruses: [
        { id: 1, family: 'Flaviviridae', genus: 'Flaviviridae', species: 'Zika virus', subspecies: 'None' },
        { id: 2, family: 'Coronaviridae', genus: 'Betacoronavirus', species: 'Severe acute respiratory syndrome-related coronavirus', subspecies: 'SARS-CoV-2' }
      ]
    }
  },
  // created: function() {
  //   // Alias the component instance as `vm`, so that we
  //   // can access it inside the promise function
  //   var vm = this;
  //   // Fetch our array of posts from an API
  //   fetch("/api/designs/")
  //     .then(function(response) {
  //       return response.json();
  //     })
  //     .then(function(data) {
  //       vm.posts = data;
  //     });
  // }
}
</script>
