<template>
  <div :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
    <div class="header">
      <div class="title"><a href="/">AD<img v-if="prod" class="logo" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" @load="onLoad" src="@/assets/img/logo.png" alt="A">PT</a></div>
      <div class="desktop menu"><a href="/about">ABOUT</a></div>
      <div class="desktop menu"><a href="/designs">ASSAYS</a></div>
      <div class="desktop menu"><a href="/run">RUN</a></div>
      <div class="desktop menu"><a href="/results">RESULTS</a></div>
      <div class="menuset">
        <div class="mobile menu"><a href="/about">ABOUT<br></a></div>
        <div class="mobile menu"><a href="/designs">ASSAYS<br></a></div>
        <div class="mobile menu"><a href="/run">RUN<br></a></div>
        <div class="mobile menu"><a href="/results">RESULTS<br></a></div>
      </div>
    </div>
    <hr/>
  </div>
</template>

<script>
export default {
  name: 'Header',
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
