<template>
  <div class="adapt">
    <h1>{{ msg }}</h1>
    <button @click="count++">
      You clicked me {{ count }} times.
    </button>`
    <button @click="greet">Greet</button>
  </div>
</template>

<script>
const axios = require("axios");

export default {
  name: 'ADAPT',
  props: {
    msg: String
  },
  data () {
    return {
      count: 0,
      name: 'ADAPT'
    }
  },
  methods: {
    async greet(event) {
      const { data } = await axios.get("https://api.agify.io/?name=Priya")
      // `this` inside methods points to the current active instance
      alert('Hello ' + data.name + '!')
      // `event` is the native DOM event
      if (event) {
        alert(event.target.tagName)
      }
    }
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
