<template>
  <transition appear name="fade">
    <div class="scrolling-sticky genome" :style="{'top': '-20px'}">
      <div class="genome-viz" :id="'genome-' + cluster_id"  style="background-color:white">
      </div>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'Genome',
  props: {
    cluster_id: String,
    alignmentLength: Number,
    assays: Array,
    annotations: Array,
  },
  data() {
    return {
      width: 800,
      height: 20 + 20*this.assays.length,
      margin: {
        top: 0,
        right: 50,
        left: 50,
        bottom: 0,
      },
      baseline: 30,
      yspace: 33,
      assayLinks: [],
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

      if (vm.annotations.length > 0) {
        vm.height += 80
      }

      const svg = d3
        .select('#genome-' + vm.cluster_id)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + vm.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${vm.margin.left}px, ${vm.height/2}px)`
        )
        .style("font-family", "Overpass Mono")
        .style("letter-spacing", '0.04em');

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
      let closeTick = ((t[t.length-1] - t[t.length-2])/interval) < .3
      const line = d3
        .line()
        .x((d) => d[0])
        .y((d) => d[1])

      var i = 1
      var assayY = this.baseline - (this.yspace*2) - 12
      if (this.annotations.length == 0) {
        assayY = this.baseline - this.yspace*.75
      }

      // From Assay.vue
      let baseline = 20
      let oligoHeight = 10
      let shift = 6.5
      let marginTopBottom = 110

      var assayHeight = []

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

        let numOligos = assay.left_primers.primers.length +
                        assay.right_primers.primers.length +
                        assay.guide_set.guides.length
        assayHeight.push((baseline + numOligos*oligoHeight + (numOligos-1)*shift + marginTopBottom))

        let href = '#anchor-' + vm.cluster_id + '-' + (i-1).toString()
        vm.assayLinks.push(svg
          .append("a")
          .attr("href", href)
          .append("text")
          .attr("text-anchor", "middle")
          .style("fill", "#000d54AA")
          .style("font-size", "0.8rem")
          .attr("y", assayY)
          .attr("x", ampliconCenter)
          .text(i));
        i++
        assayY -= 10
      }

      var modalBody = document.getElementsByClassName('modal-body')[0]
      modalBody.addEventListener('scroll', () => {
        let pageWidth = document.getElementsByClassName('genome-viz')[0].scrollWidth;
        let scaledGenomeHeight = vm.height*pageWidth/vm.width;
        let scrollY = modalBody.scrollTop;
        let scrollTop = scrollY + scaledGenomeHeight
        let scrollBottom = scrollY + modalBody.clientHeight;
        for (let assayIndex in vm.assays) {
          if (scrollY == 0) {
            vm.assayLinks[assayIndex]
              .transition()
              .duration(200)
              .style("font-size", "0.8rem")
              .style("font-weight", "300");
          } else {
            let assayElement = document.getElementById('visualization-' + vm.cluster_id + '-' + assayIndex.toString())
            let assayTop = assayElement.offsetTop;
            let assayBottom = assayElement.offsetTop + assayElement.offsetHeight;
            if ((assayTop >= scrollTop) && (assayBottom <= scrollBottom)) {
              vm.assayLinks[assayIndex]
                .transition()
                .duration(200)
                .style("font-size", "1.2rem")
                .style("font-weight", "700");
            } else {
              vm.assayLinks[assayIndex]
                .transition()
                .duration(200)
                .style("font-size", "0.8rem")
                .style("font-weight", "300");
            }
          }
        }
      })

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
        .style("font-size","0.5rem");

      if (closeTick) {
        xAxis.select(".tick:nth-last-child(2) text")
          .attr("transform", "translate(-6,0)");
      }

      xAxis.select(".tick:last-of-type line")
        .attr("y2","16");
      xAxis.select(".tick:last-of-type text")
        .attr("y","19")
        .style("font-size","0.6rem");
      xAxis.select(".tick:first-of-type line")
        .attr("y2","16");
      xAxis.select(".tick:first-of-type text")
        .attr("y","19")
        .style("font-size","0.6rem");
    },
  },
}
</script>
