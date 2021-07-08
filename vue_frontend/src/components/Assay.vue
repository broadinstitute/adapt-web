<template>
  <transition appear name="fade">
    <div class="assay">
      <b-row align-v="center">
        <b-col cols=1 class="text-center">
          <h4>{{result.rank + 1}}</h4>
        </b-col>
        <b-col cols=12>
          <div class="visualization" :id="'visualization-' + cluster_id + '-' + result.rank.toString()">
          </div>
        </b-col>
      </b-row>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'Assay',
  props: {
    result: Object,
    cluster_id: String,
    aln_sum: Array,
  },
  data() {
    let margin= {
      "top": 35,
      "right": 10,
      "left": 10,
      "bottom": 50,
    }

    let width = 750
    let boundedWidth = width - margin.left - margin.right

    let numOligos = this.result.left_primers.primers.length +
                    this.result.right_primers.primers.length +
                    this.result.guide_set.guides.length

    let baseline = 20
    let oligoHeight = 10
    let shift = 4

    let boundedHeight = baseline + numOligos*oligoHeight + (numOligos-1)*shift
    let height = boundedHeight + margin.top + margin.bottom

    let xDomain = [this.result.amplicon_start - 10, this.result.amplicon_end + 10]
    let xRange = [0, boundedWidth]

    let xScale = d3
      .scaleLinear()
      .domain(xDomain)
      .range(xRange);
    let yScale = function (d) {
      return boundedHeight-d
    };
    let line = d3
      .line()
      .x((d) => xScale(d[0]))
      .y((d) => yScale(d[1]))
    return {
      "baseline": baseline,
      "oligoHeight": oligoHeight,
      "shift": shift,
      "width": width,
      "height": height,
      "boundedHeight": boundedHeight,
      "boundedWidth": boundedWidth,
      "margin": margin,
      "target": [this.result.amplicon_start, this.result.amplicon_end],
      "leftPrimers": this.result.left_primers.primers,
      "rightPrimers": this.result.right_primers.primers,
      "guides": this.result.guide_set.guides,
      "xDomain": xDomain,
      "xRange": xRange,
      "xScale": xScale,
      "yScale": yScale,
      "line": line,
      "red": getComputedStyle(document.documentElement)
        .getPropertyValue('--red'),
      "orange": getComputedStyle(document.documentElement)
        .getPropertyValue('--orange'),
      "lemon": getComputedStyle(document.documentElement)
        .getPropertyValue('--lemon'),
      "mint": getComputedStyle(document.documentElement)
        .getPropertyValue('--mint'),
      "navy": getComputedStyle(document.documentElement)
        .getPropertyValue('--navy'),
      "info": getComputedStyle(document.documentElement)
        .getPropertyValue('--info'),
    };
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      const vm = this
      const svg = d3
        .select(`#visualization-${vm.cluster_id}-${vm.result.rank.toString()}`)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + vm.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${vm.margin.left}px, ${vm.margin.top}px)`
        )
        .style("font-family", "PT Mono")
        .style("letter-spacing", '0.03em');

      let t = [vm.target[0]]
      let ampliconLength = vm.target[1]-vm.target[0]
      let interval =  Math.max(Math.trunc(ampliconLength/50)*10, 20)
      while (t[t.length-1] < vm.target[1]) {
        t.push(t[t.length-1] + interval)
      }
      t[t.length-1] = vm.target[1]
      let closeTick = ((t[t.length-1] - t[t.length-2])/interval) < .2

      const xAxisGenerator = d3
        .axisBottom()
        .scale(vm.xScale)
        .tickValues(t)

      let xAxis = svg
        .append("g")
        .call(xAxisGenerator)
        .style("transform", `translateY(calc(${vm.boundedHeight}px + 0.5rem))`)
        .call(g => g.select(".domain")
          .remove());

      xAxis.selectAll(".tick text")
        .style("font-size","0.4rem");

      if (closeTick) {
        xAxis.select(".tick:nth-last-child(2) text")
          .attr("transform", "translate(-6,0)");
      }

      xAxis.select(".tick:last-of-type line")
        .attr("y2","14");
      xAxis.select(".tick:last-of-type text")
        .attr("y","17")
        .style("font-size","0.5rem");
      xAxis.select(".tick:first-of-type line")
        .attr("y2","14");
      xAxis.select(".tick:first-of-type text")
        .attr("y","17")
        .style("font-size","0.5rem");

      var colorScale = d3.piecewise(d3.interpolateRgb.gamma(2.2), [vm.red, vm.orange, vm.lemon, vm.mint])
      var activityScale = d3.scaleLinear()
        .domain([0, 1.5, 3, 4])
        .range([0, 1/3, 2/3, 1]);
      var activityColorScale = function (d) {
        return colorScale(activityScale(d))
      }
      var fracBoundScale = d3.scaleLinear()
        .domain([0, .375, .75, 1])
        .range([0, 1/3, 2/3, 1]);
      var fracBoundColorScale = function (d) {
        return colorScale(fracBoundScale(d))
      }

      let bottomOligo = vm.baseline
      let rightPrimerLines = []
      let rightPrimerPaths = []
      for (let rightPrimer of vm.rightPrimers) {
        let rightPrimerLine = [
          [vm.target[1] - rightPrimer.target.length, bottomOligo],
          [vm.target[1] - rightPrimer.target.length, bottomOligo+vm.oligoHeight],
          [vm.target[1], bottomOligo+vm.oligoHeight+1],
          [vm.target[1], bottomOligo-1],
        ]
        rightPrimerLines.push(rightPrimerLine)
        rightPrimerPaths.push(svg
          .append("path")
          .attr("d", vm.line(rightPrimerLine))
          .style(
            "transform",
            `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        ))
        vm.oligo_bases(rightPrimer.target, vm.target[1] - rightPrimer.target.length, bottomOligo+vm.oligoHeight/2, svg)
        bottomOligo += vm.shift + vm.oligoHeight
      }

      let guideLines = []
      let guidePaths = []
      for (let guide of vm.guides) {
        let guideLine = [
          [guide.start_pos[0], bottomOligo],
          [guide.start_pos[0], bottomOligo+vm.oligoHeight],
          [guide.start_pos[0] + guide.target.length, bottomOligo+vm.oligoHeight],
          [guide.start_pos[0] + guide.target.length, bottomOligo]
        ]
        guideLines.push(guideLine)
        guidePaths.push(svg
          .append("path")
          .attr("d", vm.line(guideLine))
          .style(
            "transform",
            `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        ))
        vm.oligo_bases(guide.target, guide.start_pos[0], bottomOligo+vm.oligoHeight/2, svg)
        bottomOligo += vm.shift + vm.oligoHeight
      }

      let leftPrimerLines = []
      let leftPrimerPaths = []
      for (let leftPrimer of vm.leftPrimers) {
        let leftPrimerLine = [
          [vm.target[0], bottomOligo-1],
          [vm.target[0], bottomOligo+vm.oligoHeight+1],
          [vm.target[0] + leftPrimer.target.length, bottomOligo+vm.oligoHeight],
          [vm.target[0] + leftPrimer.target.length, bottomOligo],
        ]
        leftPrimerLines.push(leftPrimerLine)
        leftPrimerPaths.push(svg
          .append("path")
          .attr("d", vm.line(leftPrimerLine))
          .style(
            "transform",
            `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        ))
        vm.oligo_bases(leftPrimer.target, vm.target[0], bottomOligo+vm.oligoHeight/2, svg)
        bottomOligo += vm.shift + vm.oligoHeight
      }

      var tooltipgroup = svg
        .append("g")

      var tooltipbox = tooltipgroup
        .append("rect")
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("stroke", "#00000000")
        .attr("stroke-width", 10)
        .style("fill", vm.info);

      var tooltip = tooltipgroup
        .append("text")
        .attr("text-anchor", "middle")
        .style("fill", vm.navy)
        .attr("class", "tooltip")
        .style("font-size", ".5rem");

      for (let i in guidePaths) {
        vm.oligo_tooltip(guidePaths[i], "Start Position: " + guideLines[i][0][0], tooltip, tooltipbox, activityColorScale(vm.result.guide_set.guides[i].expected_activity), ["Expected Activity: " + vm.result.guide_set.guides[i].expected_activity])
      }

      for (let i in leftPrimerPaths) {
        vm.oligo_tooltip(leftPrimerPaths[i], "Start Position: " + leftPrimerLines[i][0][0], tooltip, tooltipbox, fracBoundColorScale(vm.result.left_primers.frac_bound), ["Fraction Bound: " + vm.result.left_primers.frac_bound])
      }

      for (let i in rightPrimerPaths) {
        vm.oligo_tooltip(rightPrimerPaths[i], "Start Position: " + rightPrimerLines[i][0][0], tooltip, tooltipbox, fracBoundColorScale(vm.result.right_primers.frac_bound), ["Fraction Bound: " + vm.result.right_primers.frac_bound])
      }

      tooltipbox
        .on('mouseover', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 1);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", .9);
        })
        .on('mouseout', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 0);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", 0);
        });

      if (vm.aln_sum.length != 0) {
        for (let b in Array(this.xDomain[1]+1-this.xDomain[0]).fill(this.xDomain[0])) {
          svg
            .append("text")
            .attr("text-anchor", "middle")
            .style("fill", vm.navy)
            .style("font-size", ".5rem")
            .html(this.max_base(this.aln_sum[parseInt(b) + this.xDomain[0]]))
            .style("font-family", "Overpass Mono")
            .attr("x", this.xScale(parseInt(b) + this.xDomain[0]))
            .attr("y", `${this.boundedHeight}px`)
            .attr("alignment-baseline", "central")
            .attr("pointer-events", "none");
        }
      }
    },
    max_base(bases) {
      return Object.keys(bases).reduce((a, b) => bases[a] > bases[b] ? a : b);
    },
    get_bases(start, end) {
      let bases = ''
      for (let i in Array(end+1-start).fill(start)) {
        bases += this.max_base(this.aln_sum[i])
      }
      return bases
    },
    oligo_bases(seq, x, y, svg) {
      let vm = this
      for (let b in seq) {
        svg
          .append("text")
          .attr("text-anchor", "middle")
          .style("fill", vm.navy)
          .style("font-size", "0.35rem")
          .style("font-weight", "700")
          .html(seq[b])
          .style("font-family", "Overpass Mono")
          .attr("x", vm.xScale(x+parseInt(b)))
          .attr("y", vm.yScale(y))
          .attr("alignment-baseline", "central")
          .attr("pointer-events", "none");
      }
    },
    oligo_tooltip(oligoPath, line1Text, tooltip, tooltipbox, color, extraLinesText) {
      let vm = this
      oligoPath
        .attr("stroke", "none")
        .attr("fill", color)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .94);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(line1Text)
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let extraLines = []
          for (let extraLineText in extraLinesText){
            let extraLine = tooltip
              .append("tspan")
              .attr("pointer-events", "none")
              .attr("text-anchor", "middle")
              .html(extraLinesText[extraLineText]);
            extraLines.push(extraLine);
          }

          let bboxOligoLine = this.getBBox()
          console.log(bboxOligoLine)
          let tooltipX = bboxOligoLine.x + bboxOligoLine.width/2 + (vm.xScale(0)-vm.xScale(.5))

          tooltip
            .attr("x", tooltipX)
            .attr("y", bboxOligoLine.y - (extraLines.length * bboxTextLine.height) - 10);

          for (let extraLine in extraLines) {
            extraLines[extraLine]
              .attr("x", tooltipX)
              .attr("dy", bboxTextLine.height);
          }

          let bboxText = tooltip.node().getBBox();

          tooltipbox
            .attr("x", bboxText.x - 5)
            .attr("y", bboxText.y - 5)
            .attr("width", bboxText.width + 10)
            .attr("height",  bboxText.height + 10)
        })
        .on('mouseout', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 0);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", 0);
        });
    },
  },
}
</script>
