<template>
  <transition appear name="fade">
    <div class="genome">
      <div class="genome-viz" :id="'genome-' + cluster_id">
      </div>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'Genome',
  props: {
    // resulttable: Object,
    cluster_id: String
  },
  data() {
    return {
      width: 800,
      height: 800,
      margin: {
        top: 50,
        right: 50,
        left: 50,
        bottom: 50,
      },
      alignment: [
        {
          acc: "KM822128",
          seq: "CATGGGGCAGATTATTACATTCTTTCAAGAAGTGCCACATGTAATAGAGGAAGTCATGAACATTGTGCTAATTGCGCTTTCTCTATTGGCAATCTTGAAGGGCTTGTATAACATCGCTACATGTGGGATTATTGGATTGGTTGCCTTTTTATTCTTGTGTGGCAAGTCTTGTTCCCTAACCCTT---AAAGGGGGATATGAGCTGCAAACCTTAGAATTAAATATGGAGACCCTAAACATGACCATGCCCTTATCATGCACCAAGAACAGCAGTCATCATTACATAAGAGTGGGCAATGAGACTGGATTAGAATTGACTTTAACTAACACCAGCATTATAAATCACAAATTTTGCAACTTATCCGATGCTCACAAAAAGAATCTTTATGATCATGCTCTCATGAGCATCATCTCAACATTCCATCTATCCATTCCAAACTTCAATCAGTATGAAGCCATGAGTTGTGATTTCAATGGAGGGAAAATCAGTGTGCAATACAACCTCTCTCATTCCTATGCTGGGGATGCGGCCGAACACTGTGGGACAGTTGCCAACGGAGTGTTGCAAACATTTATGAGAATGGCCTGGGGTGGAAGATACATTGCATTAGACTCAGGAAAGGGAAACTGGGACTGTATAATGACCAGCTACCAGTACCTGATAATTCAAAATACAACATGGGAGGACCACTGCCAATTCTCAAGACCGTCTCCTATCGGGTACCTTGGCCTTTTGTCACAAAGGACAAGAGATATATATATAAGTAGGAGGCTCTTGGGGACCTTCACCTGGACATTGTCAGATTCTGAGGGCAATGAAACACCAGGTGGTTATTGTTTAACCAGGTGGATGCTAATTGAAGCAGAACTCAAGTGTTTTGGGAATACAGCTGTGGCAAAATGCAATGAGAAGCATGATGAGGAGTTTTGTGACATGCTGAGATTGTTTGATTTCAACAAGCAAGCAATCCGTAGGTTGAAGGCTGAGGCCCAGATGAGTATTCAATTAATAAATAAAGCCGTGAATGCCTTAATCAATGATCAATTAATCATGAAGAACCATTTAAGAGACATCATGGGCATTCCCTACTGCAATTACAGCAAGTATTGGTACCTTAATCATACTAGTAGCGGGAGAACATCACTACCAAAGTGTTGGCTTATATCCAATGGGTCATATCTAAATGAAACCCAGTTCTCTGATGACATAGAACAGCAAGCCGACAATATGATCACAGAGATGCTTCAGAAAGAATACATTGAAAGACAAGGGAAAACGCCCTTGGGACTAGTGGACATTTTCATCTTTAGCACAAGCTTTTATCTGATCAGCATTTTCTTGCATTTAATTAAAATCCCTACACATCGACACATCGTTGGGAAACCCTGTCCCAAACCCCATAGACTAAATCACATGGGAGTATGTTCCTGTGGACTGTACAAACACCCTGGTGTTCCAACAAAGTGGAAGAGAT-TACAGAACGACTTTAGGGGTGCTGGTCCTGAAGACCATGTCTCTGGGAAGTACTGCCCTCAGTGTTGTGATGTTCAAACTACCAGTAGTAGCTGCATCAAACATGATGCAGTCCAGTAAAGCGCAATGTGGGGTGATTTCCTCTTTTCCACCCCTCTTTTTCTTCTCAACGACTACTCCCGTGTGCATGTGACACAAGTCTTTGTATTGGTCCCACACAGCATTTTCAAACTTCCTTGAATCTGCTTTGCTCAAAGAAATATCAATCAATTTGATGTCTCTTCTCCCTTGAGACTCCAACAGCTTTTTGATGTCATCTGACCCCTGGCAGGTCAACACCATATTGCGGGGAAGTGCCTCTATGACAGCACTTGTCAGCCCGGGTTGTGTGGAAAAAAGATCTGTAACATCTATCCCATGTGAGTACTTAGCATCCTGTTTGAATTGCTTAAGGTCAGTAGGTTCTCTAAAAAAGTGTATGTAACAACCAGAGCTTGGTTGAAACAAAGCAATCTCCACTGGGTCTTCAGGCCTGCCCTCAATATCTATCCATGTTTTGCTACTTGGGTCCAACTGTAACATACAATCTTTTAGTGTCATCAGTTGAGAATAGGTCAACCCAGCATTTAGACCTGCAGCCTGCAAGCTTTTATTGGAACCAGCGCTATTTAGTTTCGGTGGTTTGTTGTCAGATTCCAAATCAACAAGAGTGTTTTCCCAAGCTCTCCCAGTAATTGATGTTCTTGATGCAATATACGGCCAACCTTCACCTGAAAGGCAGATCTTATAGAGGATGTTCTCATATGGGTTTCTTTCACCAGGAGTGTCAGAAATGAACATTCCCAGTGATCTTTTGACCTTCAGAATAGATTTCAAAATACCGTCCATTGTTTGTGGTGACACTTTTATTGTTTCCAACATGTTGCCCCCATCAAGCATGCAAGCACCAGCTTTAACTGCAGCCCCCAGACTGAAGTTGTAACCTGAGATGTTCAGGGAACTCTTTTTTGTGTCAACCATTCCTAGTATAGGGTGACTCTGAGTGAGCATGTCTAGATCTGAAGAGTTCGGGTACTTTGCTGTGTAAATCAAACCTAAATCTGTTAAAGCTTGCACAGCATCATTGAGGTCCACTTGCCCTTGTTTGGTGAGGCACGCCAAGGTGAGGCTTGGCATGGTTCCAAATTGGTTATTGAGTAATTCTGCATTTTTTACGTCCCAAACCCTGACGACACCATCCCCACCTGTCCTATTTCCTTGAGGTCCACCTGACATCCCAATCATGCTCAAGAGAGCCCTCCTTTGATCAAGCTGTTGTGAGCTTAAATTCCCCATGTAAACACCTGAGCTCAAAGGCCTTTCTGTCCTTATGACTTTGGACTTGAGTTTTTCCAGGTCCGCTGCCAAAGTTATTAGATCATCTGAACTCAAGGTGCCGACCCTTAAGACATTCTTCTGTTGAGTTGACTTCAGTTCAACAAGATTGTTGACAGCTTGATTCAGATCCCTCAGTCGCTTTAGGTCTGCATCATCTCTCTTCTGCTTGCGCATCAGCCTCTGCACATTGCTGACCTCAGAAAAGTCAAGGCCATGCAGGAGAGCCTGAGCATCTTTGACAACTTGCAACTTTATGTTAGAACAGTAACCAGATAGTTCCCTTCGTAAGGACTGAGTCCAAAGGAATGATTTGATTTCCTTGGAGTTGCTCA",
        },
      ],
      annotations: [
        {
          type: "CDS",
          gene: "GPC",
          product: "glycoprotein precursor",
          start: 71,
          end: 1543,
        },
        {
          type: "mat_peptide",
          gene: "GPC",
          product: "glycoprotein GP1",
          start: 71,
          end: 838,
        },
        {
          type: "mat_peptide",
          gene: "GPC",
          product: "glycoprotein GP2",
          start: 839,
          end: 1540,
        },
        {
          type: "CDS",
          gene: "NP",
          product: "nucleoprotein",
          start: 3314,
          end: 1605,
        },
      ],
      // target: (this.result.amplicon_start + this.result.amplicon_end)/2,
      // left_primer_seq: this.result.left_primers.primers[0].target,
      // right_primer_seq: this.result.right_primers.primers[0].target,
      // guide_start: this.result.guide_set.guides[0].start_pos[0],
      // guide_seq: this.result.guide_set.guides[0].target,
    };
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      const vm = this
      const color = d3.scaleOrdinal([
        d3.interpolateCool(0.6),
        d3.interpolateCool(0.1),
        d3.interpolateCool(0.4),
        d3.interpolateCool(0.9),
        d3.interpolateCool(0),
        d3.interpolateCool(0.5),
        d3.interpolateCool(0.2),
        d3.interpolateCool(1),
        d3.interpolateCool(0.3),
        d3.interpolateCool(0.7),
      ]);
      // const mint = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--mint');
      const svg = d3
        .select('#genome-' + vm.cluster_id)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + vm.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${vm.width/2}px, ${vm.height/2}px)`
        )
        .style("font-family", "PT Mono")
        .style("letter-spacing", '0.03em');

      var x = d3.scaleLinear()
        .domain([0, vm.alignment[0].seq.length])
        .range([0, 2*Math.PI])

      var arc = d3.arc()
        .innerRadius(function (d) {
          if (d.type == "CDS") {
            return 270
          } else {
            return 230
          }
        })
        .outerRadius(function (d) {
          if (d.type == "CDS") {
            return 300
          } else {
            return 260
          }
        })
        .startAngle(d => x(d.start))
        .endAngle(d => x(d.end))
        // .padAngle(0.01)
        // .padRadius(270)

      var i = 0
      for (let annotation of vm.annotations) {
        svg
          .append("path")
          .attr("d", arc(annotation))
          .attr("fill", color(i))
        i++
      }

        // arc(vm.annotations.filter(annotation => annotation.type == "CDS")))
      // const red = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--red');
      // const orange = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--orange');
      // const lemon = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--lemon');
      // const navy = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--navy');
      // const info = getComputedStyle(document.documentElement)
      //   .getPropertyValue('--info');

      // var activityColorScale = d3.scaleLinear()
      //   .domain([0, 1.5, 3, 4])
      //   .range([red, orange, lemon, mint]);

      // var fracBoundColorScale = d3.scaleLinear()
      //   .domain([0, .375, .75, 1])
      //   .range([red, orange, lemon, mint]);
    },
  },
}
</script>
