<template>
  <transition appear name="fade">
    <div class="home">
      <div class="jumbo d-none d-sm-block">AD<img v-if="prod" class="logo" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" src="@/assets/img/logo.png" alt="A">PT</div>
      <p class="subtitle">Activity-informed Design with All-inclusive Patrolling of Targets</p>
      <b-button-group>
        <b-button variant="outline-secondary" href="/about">About ADAPT</b-button>
        <b-button variant="outline-secondary" href="/designs">Premade Assays</b-button>
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
.home {
  text-align: center;
}

.jumbo {
  font-size: min(15vw, 8rem);
  font-weight: bold;
}

.subtitle {
  font-size: min(6vw, 1.5rem);
}

</style>
