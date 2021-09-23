<template>
  <b-container fluid class="footer" :style="'opacity: ' + slowshow.toString() + '; transition: 0.3s;'">
    <b-row>
      <b-col cols=0 md=1></b-col>
      <b-col cols=12 md=10>
        <b-row class="px-2">
          <b-col cols=12 md=4 class="my-auto f-4">
            Contact:<br>
            <a href = "mailto:adapt@broadinstitute.org" class="f-5">adapt@broadinstitute.org</a>
          </b-col>
          <b-col cols=12 md=7 class="my-auto f-7">
            <small>Genomic data from NCBI's GenBank informed all of these designs, and data from GISAID informed the SARS-CoV-2 designs. All of these designs rely heavily on sequencing that other groups have performed and the genomes they have shared, and we are thankful to them for sharing data.</small>
          </b-col>
          <b-col cols=12 md=1>
            <b-navbar-brand href="/"><img v-if="prod" class="logo m-auto" @load="onLoad" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo m-auto" @load="onLoad" src="@/assets/img/logo.png" alt="A"></b-navbar-brand>
          </b-col>
        </b-row>
      </b-col>
      <b-col cols=0 md=1></b-col>
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
