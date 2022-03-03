<template>
  <b-container fluid class="header sticky-top" :class="{ 'scroll-shade': scroll }" :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
    <a href="https://github.com/broadinstitute/adapt" rel="noreferrer" target="_blank" class="github-corner" aria-label="View source on GitHub">
      <svg width="min(3rem, 12vw)" height="min(3rem, 12vw)" viewBox="0 0 250 250" style="fill: #45e2ea; color:#fff; position: fixed; top: 0; border: 0; right: 0; left: auto;" aria-hidden="true" class="fixed-top">
        <path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path>
        <path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path>
        <path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path>
      </svg>
    </a>
    <b-row>
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
      <b-navbar toggleable="lg">
        <b-navbar-brand href="/">AD<img v-if="prod" class="logo" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" @load="onLoad" src="@/assets/img/logo.png" alt="A">PT</b-navbar-brand>
        <b-navbar-toggle target="nav-collapse">
        </b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav><b-navbar-nav :justified=true class="w-100 mx-auto">
        <b-nav-item disabled href="" class="d-none d-lg-block"></b-nav-item>
        <b-nav-item href="/designs" :class="{ 'current-page': page=='Assays'}">PRE-DESIGNED ASSAYS</b-nav-item>
        <b-nav-item href="/run" :class="{ 'current-page': page=='Run'}">RUN ADAPT</b-nav-item>
        <b-nav-item href="/results" :class="{ 'current-page': page=='Results'}">RESULTS</b-nav-item>
        </b-navbar-nav></b-collapse>
      </b-navbar>
      </b-col>
      <b-col cols=0 md=1></b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: 'Header',
  props: {
    page: String,
  },
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
      return this.scrollY > 0;
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
