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
    let width = 750
    let height = 150
    let margin= {
      "top": 0,
      "right": 10,
      "left": 10,
      "bottom": 50,
    }

    let boundedWidth = width - margin.left - margin.right
    let boundedHeight = height - margin.top - margin.bottom

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
      "width": width,
      "height": height,
      "boundedHeight": boundedHeight,
      "boundedWidth": boundedWidth,
      "margin": margin,
      "target": [this.result.amplicon_start, this.result.amplicon_end],
      "left_primer_seq": this.result.left_primers.primers[0].target,
      "right_primer_seq": this.result.right_primers.primers[0].target,
      "guide_start": this.result.guide_set.guides[0].start_pos[0],
      "guide_seq": this.result.guide_set.guides[0].target,
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

      var activityColorScale = d3.scaleLinear()
        .domain([0, 1.5, 3, 4])
        .range([vm.red, vm.orange, vm.lemon, vm.mint]);

      var fracBoundColorScale = d3.scaleLinear()
        .domain([0, .375, .75, 1])
        .range([vm.red, vm.orange, vm.lemon, vm.mint]);

      const baseline = 20
      const height = 10
      const shift = 8
      const leftPrimerLine = [
        [vm.target[0], baseline+2*shift+2*height-1],
        [vm.target[0] + vm.left_primer_seq.length, baseline+2*shift+2*height],
        [vm.target[0] + vm.left_primer_seq.length, baseline+2*shift+3*height],
        [vm.target[0], baseline+2*shift+3*height+1],
      ]
      const guideLine = [
        [vm.guide_start, baseline+shift+height],
        [vm.guide_start, baseline+shift+2*height],
        [vm.guide_start + vm.guide_seq.length, baseline+shift+2*height],
        [vm.guide_start + vm.guide_seq.length, baseline+shift+height]
      ]
      const rightPrimerLine = [
        [vm.target[1] - vm.right_primer_seq.length, baseline],
        [vm.target[1], baseline-1],
        [vm.target[1], baseline+height+1],
        [vm.target[1] - vm.right_primer_seq.length, baseline+height],
      ]

      var guidePath = svg
        .append("path")
        .attr("d", vm.line(guideLine))
        .style(
          "transform",
          `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        );

      var leftPrimerPath = svg
        .append("path")
        .attr("d", vm.line(leftPrimerLine))
        .style(
          "transform",
          `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        );

      var rightPrimerPath = svg
        .append("path")
        .attr("d", vm.line(rightPrimerLine))
        .style(
          "transform",
          `translate(${vm.xScale(0)-vm.xScale(.5)}px)`
        );

      vm.oligo_bases(vm.left_primer_seq, vm.target[0], baseline+shift*2+height*5/2, svg)
      vm.oligo_bases(vm.guide_seq, vm.guide_start, baseline+shift+height*3/2, svg)
      vm.oligo_bases(vm.right_primer_seq, vm.target[1]-vm.right_primer_seq.length, baseline+height/2, svg)

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

      vm.oligo_tooltip(guidePath, "Start Position: " + guideLine[0][0], tooltip, tooltipbox, activityColorScale(vm.result.guide_set.expected_activity), ["Expected Activity: " + vm.result.guide_set.expected_activity])

      vm.oligo_tooltip(leftPrimerPath, "Start Position: " + leftPrimerLine[0][0], tooltip, tooltipbox, fracBoundColorScale(vm.result.left_primers.frac_bound), ["Fraction Bound: " + vm.result.left_primers.frac_bound])

      vm.oligo_tooltip(rightPrimerPath, "Start Position: " + rightPrimerLine[0][0], tooltip, tooltipbox, fracBoundColorScale(vm.result.right_primers.frac_bound), ["Fraction Bound: " + vm.result.right_primers.frac_bound])

      tooltipbox
        .on('mouseover', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 1);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", .8);
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
          .html(seq[b])
          .style("font-family", "Overpass Mono")
          .attr("x", vm.xScale(x+parseInt(b)))
          .attr("y", vm.yScale(y))
          .attr("alignment-baseline", "central")
          .attr("pointer-events", "none");
      }
    },
    oligo_tooltip(oligoPath, line1Text, tooltip, tooltipbox, color, extraLinesText) {
      oligoPath
        .attr("stroke", "none")
        .attr("fill", color)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
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

          let tooltipX = bboxOligoLine.x + bboxOligoLine.width/2

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
