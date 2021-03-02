<template>
  <transition appear name="fade">
    <div class="home">
      <b-button href="/about">About ADAPT</b-button><br>
      <b-button href="/designs">Premade Diagnostic Assay Designs</b-button><br>
      <b-button href="/run">Run ADAPT on Your Own Data</b-button><br>
      <b-button href="/results">Check Your Results</b-button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.home{
  text-align: left;
}

</style>
