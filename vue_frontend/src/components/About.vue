<template>
  <transition appear name="fade">
    <div class="about text-center">
      <b-row align-v="center" class="pb-2">
        <b-col md=5>
          <div style="font-weight: 700; font-size: max(min(5vw, 5.5em),2.7em); line-height: 1.2;">AD<img v-if="prod" class="logo" :src="`${imgsrc}/static/vue/img/logo.png`" alt="A"><img v-else class="logo" src="@/assets/img/logo.png" alt="A">PT</div>
        </b-col>
        <b-col md=7>
          <i style="font-size: max(min(1.7vw, 1.4em),0.8em)">Activity-informed Design with All-inclusive Patrolling of Targets</i>
        </b-col>
      </b-row>
      <p class="pb-3 text-muted f-4">ADAPT efficiently designs nucleic acid diagnostic assays with maximal predicted detection activity over genomic variation, with a focus on viruses.</p>
      <b-card class="mt-5 mb-5">
        <b-card-text>
          <b-row align-v="center">
            <b-col md=9>
              <small><i>Preprint on bioRxiv:</i></small>
              <a href="https://doi.org/10.1101/2020.11.28.401877" rel="noreferrer" target="_blank"><h3>Designing viral diagnostics with model-based optimization</h3></a>
              <h6>Hayden C. Metsky, Nicole L. Welch, Priya P. Pillai, Nicholas J. Haradhvala, Laurie Rumker, Sreekar Mantena, Yibin B. Zhang, David K. Yang, Cheri M. Ackerman, Juliane Weller, Paul C. Blainey, Cameron Myhrvold, Michael Mitzenmacher, Pardis C. Sabeti</h6>
            </b-col>
            <b-col md=3>
              <div class="pb-2"><small><i>Code on GitHub:</i></small></div>
              <a href="https://github.com/broadinstitute/adapt" rel="noreferrer" target="_blank"><img width="70" alt="Octicons-mark-github" src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/512px-Octicons-mark-github.svg.png"></a>
            </b-col>
          </b-row>
        </b-card-text>
      </b-card>
      <b-row>
        <b-col sm=1></b-col>
        <b-col sm=10>
          <p class="pb-1 pt-5 f-1">ADAPT's designs are...</p>
        </b-col>
        <b-col sm=1></b-col>
      </b-row>
      <b-row>
        <b-col lg=6 xl=4 class="pb-3">
          <b-card style="height: 100%">
            <b-card-title class="f-3">Comprehensive</b-card-title>
            <b-card-text>
              <small>Designs are effective against variable targets because ADAPT analyzes the full spectrum of known genomic diversity from public databases or a given set of sequences.</small>
            </b-card-text>
          </b-card>
        </b-col>
        <b-col lg=6 xl=4 class="pb-3">
          <b-card style="height: 100%">
            <b-card-title class="f-3">Sensitive</b-card-title>
            <b-card-text>
              <small>ADAPT leverages predictive models of detection activity. It includes a pre-trained machine learning model of <i>Lwa</i>Cas13a CRISPR guide diagnostic activity, trained from ~19,000 guide-target pairs, and uses a heuristic model for RPA primers.</small>
            </b-card-text>
          </b-card>
        </b-col>
        <b-col lg=6 xl=4 class="pb-3 mx-md-auto">
          <b-card style="height: 100%">
            <b-card-title class="f-3">Specific</b-card-title>
            <b-card-text>
              <small>ADAPT designs CRISPR guides to distinguish closely-related species or subspecies, allowing them to be grouped into panels that are accurate in identifying taxa.</small>
            </b-card-text>
          </b-card>
        </b-col>
      </b-row>
      <p class="f-3 pt-2 pb-5">ADAPT runs <b>end-to-end</b>, automatically downloading and curating sequences from NCBI to provide designs rapidly at scale.</p>

      <b-row class="pt-5 pb-4">
        <b-col lg=4 class="h3 text-center my-auto pb-3">
          <a href="/designs" style="letter-spacing: inherit;">Pre-designed Assays</a>
        </b-col>
        <b-col>
          <p class="f-4 text-left">We pre-designed assays against >1,500 known vertebrate-infecting viruses, ready for experimental validation, by harnessing all the genomes for each virus in NCBI’s databases. ADAPT’s output includes a visualized list of assay options ranked by predicted performance.</p>
        </b-col>
      </b-row>
      <b-row class="pt-4 pb-5">
        <b-col class="d-none d-lg-block">
          <p class="f-4 text-right">If there is a virus we have not designed for, you have custom sequences, or you require control over design parameters, you can run ADAPT easily through our web interface.</p>
        </b-col>
        <b-col lg=4 class="h3 my-auto pb-3">
          <a href="/run" style="letter-spacing: inherit;">Run ADAPT</a>
        </b-col>
        <b-col class="d-lg-none">
          <p class="f-4 text-left">If there is a virus we have not designed for, you have custom sequences, or you require control over design parameters, you can run ADAPT easily through our web interface.</p>
        </b-col>
      </b-row>
      <p class="pt-5 f-5">Currently, ADAPT is directly suited to Cas13a-based diagnostics, e.g., with the <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5526198/" rel="noreferrer" target="_blank">SHERLOCK</a>, <a href="https://www.nature.com/articles/s41467-020-19097-x" rel="noreferrer" target="_blank">SHINE</a>, or <a href="https://www.nature.com/articles/s41586-020-2279-8" rel="noreferrer" target="_blank">CARMEN</a> platforms. Future versions will extend ADAPT's predictive models to work with other nucleic acid detection technologies.</p>
      <p class="f-5">This website is being developed and maintained by <a href="https://priyappillai.github.io/" rel="noreferrer" target="_blank">Priya Pillai</a> and <a href="https://hayden.bio" rel="noreferrer" target="_blank">Hayden Metsky</a>, in the Sabeti Lab at the Broad Institute of MIT and Harvard.</p>
      <br>
      <p><span class="disclaimer">Note: ADAPT’s pre-designed assays were generated fully automatically and we have not yet experimentally validated most of them; they are intended for research use only. They have gone through in silico checks of comprehensiveness and sensitivity to their species.</span></p>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'About',
  data() {
    return {
      imgsrc: process.env.BASE_URL,
      prod: false
    }
  },
  created() {
    if (!this.imgsrc.includes('localhost')) {
      this.prod = true;
    }
  }
}
</script>
