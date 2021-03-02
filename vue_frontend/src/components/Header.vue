<template>
    <div class="header sticky-top">
      <b-navbar toggleable="md" :sticky=true class="px-5 py-3" v-bind:class="{ 'scroll-shade': scroll }" :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
        <b-navbar-brand class="pl-2" href="/">AD<img v-if="prod" class="logo" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" @load="onLoad" src="@/assets/img/logo.png" alt="A">PT</b-navbar-brand>
        <b-navbar-toggle target="nav-collapse">
        </b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav><b-navbar-nav :justified=true class="w-100 ml-auto pr-2">
        <b-nav-item disabled href=""></b-nav-item>
        <b-nav-item href="/about">ABOUT</b-nav-item>
        <b-nav-item href="/designs">ASSAYS</b-nav-item>
        <b-nav-item href="/run">RUN</b-nav-item>
        <b-nav-item href="/results">RESULTS</b-nav-item>
        </b-navbar-nav></b-collapse>
      </b-navbar>
    </div>
</template>

<script>
export default {
  name: 'Header',
  data () {
    return {
      imgsrc: process.env.BASE_URL,
      prod: false,
      slowshow: 0,
      scrollY: window.scrollY
    }
  },
  computed: {
    scroll() {
      return this.scrollY > 5;
    }
  },
  created () {
    if (!this.imgsrc.includes('localhost')) {
      this.prod = true;
    }
  },
  mounted () {
    window.addEventListener('scroll', () => {
      this.scrollY = window.scrollY;    })
  },
  methods: {
    onLoad() {
      this.slowshow = 1;
    }
  }
}
</script>
