<template>
  <transition appear name="fade">
    <div class="assay">
      {{result.rank + 1}}
      <div class="visualization" :id="'visualization-' + cluster_id + '-' + result.rank.toString()">
      </div>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'Assay',
  props: {
    result: Object,
    cluster_id: String
  },
  data() {
    return {
      width: 750,
      height: 120,
      margin: {
        top: 50,
        right: 50,
        left: 50,
        bottom: 50,
      },
      target: [this.result.amplicon_start, this.result.amplicon_end],
      left_primer_seq: this.result.left_primers.primers[0].target,
      right_primer_seq: this.result.right_primers.primers[0].target,
      guide_start: this.result.guide_set.guides[0].start_pos[0],
      guide_seq: this.result.guide_set.guides[0].target,
    };
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      const vm = this
      let boundedWidth = vm.width - vm.margin.left - vm.margin.right
      let boundedHeight = vm.height - vm.margin.top - vm.margin.bottom
      const svg = d3
        .select(`#visualization-${vm.cluster_id}-${vm.result.rank.toString()}`)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + vm.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${vm.margin.left}px, ${vm.margin.top}px)`
        );

      const red = getComputedStyle(document.documentElement)
        .getPropertyValue('--red');
      const orange = getComputedStyle(document.documentElement)
        .getPropertyValue('--orange');
      const lemon = getComputedStyle(document.documentElement)
        .getPropertyValue('--lemon');
      const mint = getComputedStyle(document.documentElement)
        .getPropertyValue('--mint');
      const navy = getComputedStyle(document.documentElement)
        .getPropertyValue('--navy');

      var activityColorScale = d3.scaleLinear()
        .domain([2.8, 3.1, 3.4, 3.7])
        .range([red, orange, lemon, mint]);

      var fracBoundColorScale = d3.scaleLinear()
        .domain([0, .3333, .6667, 1])
        .range([red, orange, lemon, mint]);

      const yAccessor = () => 10;
      const xAccessor = (d) => d;
      const yScale = d3
        .scaleLinear()
        .domain([0, 20])
        .range([boundedHeight, 0]);

      const guideLine = [vm.guide_start, vm.guide_start + vm.guide_seq.length]
      const leftPrimerLine = [vm.target[0], vm.target[0] + vm.left_primer_seq.length]
      const rightPrimerLine = [vm.target[1] - vm.right_primer_seq.length, vm.target[1]]

      // const xScale = d3sB
      //   .scaleLinear()
      //   .domain([0, 1000], [900, 1100], [1100, 3000])
      //   .range([0, boundedWidth])
      //   .scope([0, .25], [.25, .75], [.75, 1]);

      let extentX = d3.extent(vm.target, (d) => xAccessor(d))
      const xScale = d3
        .scaleLinear()
        .domain([extentX[0] - 50, extentX[1] + 50])
        .range([0, boundedWidth]);

      const line = d3
        .line()
        .x((d) => xScale(xAccessor(d)))
        .y((d) => yScale(yAccessor(d)))

      var tooltipgroup = svg
        .append("g")

      var tooltipbox = tooltipgroup
        .append("rect")
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("stroke", "#00000000")
        .attr("stroke-width", 10)
        .style("fill", navy);

      var tooltip = tooltipgroup
        .append("text")
        .style("fill", "white")
        .attr("class", "tooltip")
        .style("font-size", ".5rem");

      svg
        .append("path")
        .attr("d", line(guideLine))
        .attr("fill", "none")
        .attr("stroke", activityColorScale(vm.result.guide_set.expected_activity))
        .attr("stroke-width", 6)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.guide_seq)
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2.html("Start Position: " + guideLine[0].toString());

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3.html("Expected Activity: " + vm.result.guide_set.expected_activity);

          let bboxGuideLine = this.getBBox()

          tooltip
            .attr("x", bboxGuideLine.x)
            .attr("y", bboxGuideLine.y - 2*bboxTextLine.height - 10);

          line2
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

          line3
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

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

      svg
        .append("path")
        .attr("id", "leftPrimerLine")
        .attr("d", line(leftPrimerLine))
        .attr("fill", "none")
        .attr("stroke", fracBoundColorScale(vm.result.left_primers.frac_bound))
        .attr("stroke-width", 2)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.left_primer_seq)
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2.html("Start Position: " + leftPrimerLine[0].toString());

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3.html("Fraction Bound: " + vm.result.left_primers.frac_bound);

          let bboxGuideLine = this.getBBox()

          tooltip
            .attr("x", bboxGuideLine.x)
            .attr("y", bboxGuideLine.y - 2*bboxTextLine.height - 10);

          line2
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

          line3
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

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

      svg
        .append("path")
        .attr("d", line(rightPrimerLine))
        .attr("fill", "none")
        .attr("stroke", fracBoundColorScale(vm.result.right_primers.frac_bound))
        .attr("stroke-width", 2)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.right_primer_seq)
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2.html("Start Position: " + rightPrimerLine[0].toString());

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3.html("Fraction Bound: " + vm.result.right_primers.frac_bound);

          let bboxGuideLine = this.getBBox()

          tooltip
            .attr("x", bboxGuideLine.x)
            .attr("y", bboxGuideLine.y - 2*bboxTextLine.height - 10);

          line2
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

          line3
            .attr("x", bboxGuideLine.x)
            .attr("dy", bboxTextLine.height);

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
      // const yAxisGenerator = d3
      //   .axisLeft()
      //   .scale(yScale)
      //   .ticks(2);

      // svg.append("g").call(yAxisGenerator);

      const xAxisGenerator = d3.axisBottom().scale(xScale).ticks(5)

      svg
        .append("g")
        .call(xAxisGenerator)
        .style("transform", `translateY(${boundedHeight}px)`);

    },
  },
}
</script>
