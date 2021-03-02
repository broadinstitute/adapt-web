<template>
  <transition appear name="fade">
    <div class="about">
      ADAPT (Activity-informed Design with All-inclusive Patrolling of Targets) is a tool to design nucleic acid detection assays that are:
      <ul class="adapt-summary">
        <li><b>Comprehensive</b>: Designs are effective against variable targets because ADAPT considers the full spectrum of their known genomic diversity.</li>
        <li><b>Sensitive</b>: ADAPT uses a model to predict detection activity across targeted genomic diversity, trained from ~19,000 guide-target pairs (based on <i>Lwa</i>Cas13a activity only).</li>
        <li><b>Specific</b>: Designs have high predicted specificity to their species or subspecies, allowing them to be grouped into panels that are accurate in distinguishing related taxa.</li>
      </ul>
      <p class="more-info">More information on these designs, including a protocol, is available in our February, 2020 paper on <a href="https://doi.org/10.1101/2020.02.26.967026" target="_blank">bioRxiv</a>.</p>
      <p class="more-info">More information on ADAPT is available in our November, 2020 preprint on <a href="https://doi.org/10.1101/2020.11.28.401877" target="_blank">bioRxiv</a>. ADAPT is available on <a href="https://github.com/broadinstitute/adapt" target="_blank">GitHub</a>.</p>
      <p>The current version of ADAPT comes with a built-in machine learning based predictive model for <i>Lwa</i>Cas13a crRNAs and a rule based predictive model for RPA primers; the crRNAs (not primers) are designed to be specific because these perform the detection. Future versions will modify ADAPT's predictive models to work with other nucleic acid detection technologies.</p>
      <p><span class="disclaimer">These design options are generated computationally and fully automatically. We have not experimentally validated them, except for one SARS-CoV-2 assay. They are intended for research-use only.</span></p>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'About'
}
</script>
