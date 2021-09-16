<template>
  <b-container fluid class="header sticky-top" :class="{ 'scroll-shade': scroll }" :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
    <b-row>
      <b-col cols=0 md=2></b-col>
      <b-col cols=12 md=8>
      <b-navbar toggleable="lg" class="px-4 py-2">
        <b-navbar-brand href="/">AD<img v-if="prod" class="logo" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" @load="onLoad" src="@/assets/img/logo.png" alt="A">PT</b-navbar-brand>
        <b-navbar-toggle target="nav-collapse">
        </b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav><b-navbar-nav :justified=true class="w-100 ml-auto pr-2">
        <b-nav-item disabled href=""></b-nav-item>
        <b-nav-item href="/about" :class="{ 'current-page': page=='About'}">ABOUT US</b-nav-item>
        <b-nav-item href="/designs" :class="{ 'current-page': page=='Assays'}">PRE-DESIGNED ASSAYS</b-nav-item>
        <b-nav-item href="/" :class="{ 'current-page': page=='Run'}">RUN ADAPT</b-nav-item>
        <b-nav-item href="/results" :class="{ 'current-page': page=='Results'}">RESULTS</b-nav-item>
        </b-navbar-nav></b-collapse>
      </b-navbar>
      </b-col>
      <b-col cols=0 md=2></b-col>
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
