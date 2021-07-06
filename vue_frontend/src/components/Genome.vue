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
      height: 400,
      margin: {
        top: 50,
        right: 50,
        left: 50,
        bottom: 50,
      },
      baseline: 100,
      yspace: 33,
      alignmentLength: 3184,
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
      assays: [
        {
          amplicon_start: 1500,
          amplicon_end: 1588
        },
        {
          amplicon_start: 500,
          amplicon_end: 588
        },
        {
          amplicon_start: 2500,
          amplicon_end: 2588
        },
        {
          amplicon_start: 1550,
          amplicon_end: 1638
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

      const svg = d3
        .select('#genome-' + vm.cluster_id)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + vm.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${vm.margin.left}px, ${vm.height/2}px)`
        )
        .style("font-family", "PT Mono")
        .style("letter-spacing", '0.03em');

      var x = d3.scaleLinear()
        .domain([0, vm.alignmentLength])
        .range([0, this.width-this.margin.right-this.margin.left])

      var annotationPath = function (annotation, y, h) {
        return [
         [x(annotation.start), y],
         [x(annotation.start), y+h],
         [x(annotation.end), y+h],
         [x(annotation.end), y]
        ]
      }
      let t = [0]
      let interval =  Math.max(Math.trunc(this.alignmentLength/5000)*500, 250)
      while (t[t.length-1] < this.alignmentLength) {
        t.push(t[t.length-1] + interval)
      }
      t[t.length-1] = this.alignmentLength
      const line = d3
        .line()
        .x((d) => d[0])
        .y((d) => d[1])

      var i = 1
      var assayY = this.baseline - (this.yspace*2) - 12
      if (this.annotations.length == 0) {
        assayY = this.baseline - this.yspace
      }
      for (let assay of vm.assays) {
        let ampliconCenter = x((assay.amplicon_start + assay.amplicon_end)/2)
        svg
          .append("line")
          .style("stroke", "#000d5455")
          .style("stroke-width", 1)
          .attr("x1", ampliconCenter)
          .attr("y1", assayY + 6)
          .attr("x2", ampliconCenter)
          .attr("y2", vm.baseline);

        svg
          .append("text")
          .attr("text-anchor", "middle")
          .style("fill", "#000d54AA")
          .style("font-size", "0.8rem")
          .attr("y", assayY)
          .attr("x", ampliconCenter)
          .text(i);
        i++
      }

      i = 0
      for (let annotation of vm.annotations) {
        var y = this.baseline - this.yspace;
        var textColor = "black";
        if (annotation.type != "CDS") {
            y = y - this.yspace;
            textColor = "white";
        }
        svg
          .append("path")
          .style("fill", color(i))
          .style("stroke", color(i))
          .style("stroke-width", 1)
          .style("opacity", .9)
          .attr("d", line(annotationPath(annotation, y, 25)));

        svg
          .append("text")
          .attr("text-anchor", "middle")
          .style("fill", textColor)
          .style("font-size", "0.7rem")
          .attr("y", y+17)
          .attr("x", x((annotation.start+annotation.end)/2))
          .text(annotation.product);
        i++
      }

      const xAxisGenerator = d3
        .axisBottom()
        .scale(x)
        .tickValues(t)

      var xAxis = svg
        .append("g")
        .call(xAxisGenerator)
        .style("transform", `translateY(${this.baseline}px)`)

      xAxis.selectAll(".tick text")
        .style("font-size","0.6rem");

      xAxis.select(".tick:last-of-type line")
        .attr("y2","14");
      xAxis.select(".tick:last-of-type text")
        .attr("y","18");
      xAxis.select(".tick:first-of-type line")
        .attr("y2","14");
      xAxis.select(".tick:first-of-type text")
        .attr("y","18");
    },
  },
}
</script>
