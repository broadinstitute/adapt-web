<template>
  <b-container fluid class="footer" :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
    <b-row>
      <b-col cols=0 md=2></b-col>
      <b-col cols=12 md=8>
        <b-navbar-brand href="/"><img v-if="prod" class="logo mx-auto" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo mx-auto" @load="onLoad" src="@/assets/img/logo.png" alt="A"></b-navbar-brand>
      </b-col>
      <b-col cols=0 md=2></b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: 'Footer',
  data () {
    return {
      imgsrc: process.env.BASE_URL,
      prod: false,
      slowshow: 0
    }
  },
  created () {
    if (!this.imgsrc.includes('localhost')) {
      this.prod = true;
    }
  },
  methods: {
    onLoad() {
      this.slowshow = 1;
    }
  }
}
</script>
