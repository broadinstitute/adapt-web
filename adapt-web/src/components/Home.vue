<template>
  <div class="home">
    <button>About ADAPT</button>
    <button>Premade Diagnostic Assay Designs</button>
    <button>Run ADAPT on Your Own Data</button>
    <button>Check Your Results</button>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home{
  text-align: center;
}

.home button {
  font-size: 1.2em;
  padding: 1em;
  margin: 0 0.2vw 0.2em 0.2vw;
  background-color: rgba(var(--navy), .8);
  color: #ffffff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
}

.home button:hover {
  background-color: #0099cc;
}

</style>
