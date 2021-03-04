<template>
  <transition appear name="fade">
    <div class="home" style="text-align: center;">
      <div style="font-size: 8rem; font-weight: bold">AD<img v-if="prod" class="logo" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" src="@/assets/img/logo.png" alt="A">PT</div>
      <p style="font-size: 1.5rem;">Activity-informed Design with All-inclusive Patrolling of Targets</p>
      <b-button-group>
        <b-button variant="outline-secondary" href="/about">About ADAPT</b-button>
        <b-button variant="outline-secondary" href="/designs">Premade Diagnostic Assays</b-button>
        <b-button variant="outline-secondary" href="/run">Run ADAPT</b-button>
        <b-button variant="outline-secondary" href="/results">See Results</b-button>
      </b-button-group>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Home',
  data () {
    return {
      imgsrc: process.env.BASE_URL,
      prod: false,
    }
  },
  created () {
    if (!this.imgsrc.includes('localhost')) {
      this.prod = true;
    }
  },
}
</script>

<style scoped>
.home{
  text-align: left;
}

</style>
