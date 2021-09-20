<template>
  <transition appear name="fade">
    <div :class="[{'scroll-shade': scrollY > 150}, 'scrolling-sticky', 'genome']" :style="{'top': '-18px'}">
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
    const axesHeight = 40
    const yspace = 8
    return {
      width: 800,
      height: axesHeight + yspace*(this.assays.length+2.5),
      margin: {
        top: 0,
        right: 50,
        left: 50,
        bottom: 0,
      },
      "yspace": yspace,
      scrollY: 0,
      assayLinks: [],
      "axesHeight": axesHeight,
      annotationThickness: 5,
    };
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      const vm = this
      const numAnnRows = vm.setAnnotationRows()
      const color = d3.scaleOrdinal([
        d3.interpolateCool(0.6),
        d3.interpolateCool(0.1),
        d3.interpolateCool(0.4),
        d3.interpolateCool(0.9),
        d3.interpolateCool(0),
        d3.interpolateCool(0.5),
        d3.interpolateCool(0.2),
        d3.interpolateCool(0.3),
        d3.interpolateCool(0.7),
      ]);
      if (vm.annotations.length > 0) {
        vm.height += vm.yspace * numAnnRows;
      }
      vm.baseline = vm.height/2 - vm.axesHeight;

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

      var annotationPath = function (annotation, h) {
        return [
         [x(annotation.start), annotation.y],
         [x(annotation.start), annotation.y+h],
         [x(annotation.end), annotation.y+h],
         [x(annotation.end), annotation.y]
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
      var assayY = vm.baseline - vm.yspace * (numAnnRows+1)

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
          .style("stroke-width", .5)
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
          .style("font-size", "0.6rem")
          .attr("y", assayY)
          .attr("x", ampliconCenter)
          .text(i));
        i++
        assayY -= vm.yspace
      }

      var modalBody = document.getElementsByClassName('modal-body')[0]
      modalBody.addEventListener('scroll', () => {
        let pageWidth = document.getElementsByClassName('genome-viz')[0].scrollWidth;
        let scaledGenomeHeight = vm.height*pageWidth/vm.width;
        vm.scrollY = modalBody.scrollTop;
        let scrollTop = vm.scrollY + scaledGenomeHeight
        let scrollBottom = vm.scrollY + modalBody.clientHeight;
        for (let assayIndex in vm.assays) {
          if (vm.scrollY == 0) {
            vm.assayLinks[assayIndex]
              .transition()
              .duration(200)
              .style("font-size", "0.6rem")
              .style("font-weight", "300");
          } else {
            let assayElement = document.getElementById('visualization-' + vm.cluster_id + '-' + assayIndex.toString())
            let assayTop = assayElement.offsetTop;
            let assayBottom = assayElement.offsetTop + assayElement.offsetHeight;
            if ((assayTop >= scrollTop-50) && (assayBottom <= scrollBottom+50)) {
              vm.assayLinks[assayIndex]
                .transition()
                .duration(200)
                .style("font-size", "0.75rem")
                .style("font-weight", "700");
            } else {
              vm.assayLinks[assayIndex]
                .transition()
                .duration(200)
                .style("font-size", "0.6rem")
                .style("font-weight", "300");
            }
          }
        }
      })

      i = 0
      let annotationLines = []
      for (let annotation of vm.annotations) {
        annotation.y = this.baseline - (annotation.row+1)*this.yspace;
        let annotationLine = svg
          .append("path")
          .style("fill", color(i))
          .style("opacity", .8)
          .attr("d", line(annotationPath(annotation, vm.annotationThickness)));
        annotationLines.push(annotationLine)
        i++
      }
      i = 0
      let xpos = vm.width/2 - vm.margin.left
      for (let annotationLine of annotationLines) {
        let annotation = vm.annotations[i]
        let textanch = "middle"
        let annotationText = svg
          .append("text")
          .attr("text-anchor", textanch)
          .style("fill", d3.color(color(i)).darker(0.6))
          .style("font-size", "0.7rem")
          .attr("y", vm.height/2-10)
          .attr("x", xpos)
          .text(annotation.product)
          .attr("pointer-events", "none");
        annotationText.style("opacity", 0);
        annotationLine
        .on('mouseover', function () {
          annotationText.transition()
           .duration(200)
           .style("opacity", 1);
        })
        .on('mouseout', function () {
          annotationText.transition()
            .duration(200)
            .style("opacity", 0);
        });
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
    setAnnotationRows() {
      var rowEnds = [];
      this.annotations.sort(function (a, b){
        if (a.start == b.start) {
          return (b.end-b.start) - (a.end-a.start)
        }
        return a.start - b.start
      })
      for (let annotation of this.annotations) {
        annotation.start = parseInt(annotation.start)
        annotation.end = parseInt(annotation.end)
        let row = null;
        let i = 0;
        for (let rowEnd of rowEnds) {
          if (rowEnd <= annotation.start) {
            row = parseInt(i);
            rowEnds[i] = annotation.end;
            break;
          }
          i++;
        }
        if (row == null) {
          row = rowEnds.length;
          rowEnds.push(annotation.end);
        }
        annotation.row = row
      }
      return rowEnds.length
    },
  },
}
</script>
