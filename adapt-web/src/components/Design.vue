<template>
  <div class="design">
    <h1>{{ family }}</h1>
    <h2>{{ genus }}</h2>
    <h3>{{ species }}</h3>
    <h4>{{ subspecies }}</h4>
  </div>
</template>

<script>
export default {
  name: 'Design',
  props: {
    family: String,
    genus: String,
    species: String, 
    subspecies: String,
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
