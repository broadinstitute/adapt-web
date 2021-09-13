<template>
  <transition appear name="fade">
    <div class="about">
      <p><b>Activity-informed Design with All-inclusive Patrolling of Targets</b>
      ADAPT efficiently designs nucleic acid diagnostic assays with maximal predicted detection activity over genomic variation given constraints on the assay’s complexity, with a focus on viruses. Its designs are...</p>
      <ul class="adapt-summary">
        <li><b>Comprehensive</b>: Designs are effective against variable targets because ADAPT considers the full spectrum of their known genomic diversity.</li>
        <li><b>Sensitive</b>: ADAPT leverages predictive models of detection activity. It includes a pre-trained model of CRISPR-Cas13a activity, trained from ~19,000 guide-target pairs.</li>
        <li><b>Specific</b>: Designs can distinguish closely-related species or subspecies, allowing them to be grouped into panels that are accurate in identifying taxa.</li>
      </ul>
      <p>ADAPT is also <b>end-to-end</b>, automatically downloading, curating, and aligning sequences from public databases to provide designs rapidly at scale with input as simple as an <a href="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi" rel="noreferrer" target="_blank">NCBI taxonomy identifier</a>.</p>
      <p>We designed <b><a href="/designs">ready-made assay options</a></b> for >1,500 known vertebrate-infecting viruses, harnessing all the genomes for each virus in NCBI’s databases. If there is a virus we have not designed for, you have custom sequences, or you require control over design parameters, you can run ADAPT easily through our <b><a href="/">web interface</a></b>. ADAPT’s output includes a list of assay options ranked by predicted performance.</p>
      <p class="more-info">More information on these designs, including a protocol, is available in our February, 2020 paper on <a href="https://doi.org/10.1101/2020.02.26.967026" rel="noreferrer" target="_blank">bioRxiv</a>.</p>
      <p>ADAPT currently uses a pre-trained machine learning based model of collateral activity for detection with <i>Lwa</i>Cas13a CRISPR guide RNAs and heuristics for RPA primers; the crRNAs are taxon-specific as these perform detection. This makes ADAPT directly suited to Cas13a-based diagnostics, e.g., with the SHERLOCK, SHINE, or CARMEN platforms. Future versions will extend ADAPT's predictive models to work with other nucleic acid detection technologies.</p>
      <p class="more-info">More information on ADAPT is available in our April, 2021 preprint on <a href="https://doi.org/10.1101/2020.11.28.401877" rel="noreferrer" target="_blank">bioRxiv</a>.</p>
      <p>ADAPT is available on <a href="https://github.com/broadinstitute/adapt" rel="noreferrer" target="_blank">GitHub</a>.</p>
      <p>The current version of ADAPT comes with a built-in machine learning based predictive model for <i>Lwa</i>Cas13a crRNAs and a rule based predictive model for RPA primers; the crRNAs (not primers) are designed to be specific because these perform the detection. Future versions will modify ADAPT's predictive models to work with other nucleic acid detection technologies.</p>
      <p><span class="disclaimer">Note: ADAPT’s ready-made assays were generated fully automatically and we have not yet experimentally validated most of them; they are intended for research use only. They have gone through in silico checks of comprehensiveness and sensitivity to their species.</span></p>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'About'
}
</script>
