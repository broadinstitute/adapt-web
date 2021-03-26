<template>
  <transition appear name="fade">
    <div class="assay">
      <b-row align-v="center">
        <b-col cols=1 class="text-center">
          <h4>{{result.rank + 1}}</h4>
        </b-col>
        <b-col cols=11>
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
    cluster_id: String
  },
  data() {
    return {
      width: 750,
      height: 150,
      margin: {
        top: 50,
        right: 10,
        left: 10,
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
        )
        .style("font-family", "PT Mono")
        .style("letter-spacing", '0.03em');

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
      const info = getComputedStyle(document.documentElement)
        .getPropertyValue('--info');

      var activityColorScale = d3.scaleLinear()
        .domain([0, 1.5, 3, 4])
        .range([red, orange, lemon, mint]);

      var fracBoundColorScale = d3.scaleLinear()
        .domain([0, .375, .75, 1])
        .range([red, orange, lemon, mint]);

      const yAccessor = (d) => d[1];
      const xAccessor = (d) => d[0];
      const yScale = d3
        .scaleLinear()
        .domain([0, 20])
        .range([boundedHeight, 0]);

      const baseline = 15
      const height = 3
      const shift = 3
      const guideLine = [
        [vm.guide_start, baseline-height/2],
        [vm.guide_start, baseline+height/2],
        [vm.guide_start + vm.guide_seq.length, baseline+height/2],
        [vm.guide_start + vm.guide_seq.length, baseline-height/2]
      ]
      const leftPrimerLine = [
        [vm.target[0], baseline+shift],
        [vm.target[0] + vm.left_primer_seq.length, baseline+shift],
        [vm.target[0], baseline+shift+height],
      ]
      const rightPrimerLine = [
        [vm.target[1] - vm.right_primer_seq.length, baseline-shift],
        [vm.target[1], baseline-shift],
        [vm.target[1], baseline-shift-height],
      ]

      // const xScale = d3sB
      //   .scaleLinear()
      //   .domain([0, 1000], [900, 1100], [1100, 3000])
      //   .range([0, boundedWidth])
      //   .scope([0, .25], [.25, .75], [.75, 1]);

      const xScale = d3
        .scaleLinear()
        .domain([this.result.amplicon_start - 20, this.result.amplicon_end + 20])
        .range([0, boundedWidth]);

      const line = d3
        .line()
        .x((d) => xScale(xAccessor(d)))
        .y((d) => yScale(yAccessor(d)))

      var guidePath = svg
        .append("path")
        .attr("d", line(guideLine))

      var leftPrimerPath = svg
        .append("path")
        .attr("d", line(leftPrimerLine))

      var tooltipgroup = svg
        .append("g")

      var tooltipbox = tooltipgroup
        .append("rect")
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("stroke", "#00000000")
        .attr("stroke-width", 10)
        .style("fill", info);

      var tooltip = tooltipgroup
        .append("text")
        .style("fill", navy)
        .attr("class", "tooltip")
        .style("font-size", ".5rem");

      guidePath
        .attr("stroke", "none")
        .attr("fill", activityColorScale(vm.result.guide_set.expected_activity))
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.guide_seq)
            .style("font-family", "Overpass Mono")
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2
            .html("Start Position: " + guideLine[0][0])
            .style("font-family", "Montserrat");

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3
            .html("Expected Activity: " + vm.result.guide_set.expected_activity)
            .style("font-family", "Montserrat");

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

      leftPrimerPath
        .attr("stroke", "none")
        .attr("fill", fracBoundColorScale(vm.result.left_primers.frac_bound))
        // .attr("stroke-width", 2)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.left_primer_seq)
            .style("font-family", "Overpass Mono")
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2
            .html("Start Position: " + leftPrimerLine[0][0]);

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3
            .html("Fraction Bound: " + vm.result.left_primers.frac_bound)
            .style("font-family", "Montserrat");

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
        .attr("stroke", "none")
        .attr("fill", fracBoundColorScale(vm.result.left_primers.frac_bound))
        // .attr("stroke-width", 2)
        .on('mouseover', function () {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .8);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          tooltip
            .html(vm.right_primer_seq)
            .style("font-family", "Overpass Mono")
            .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let line2 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line2
            .html("Start Position: " + rightPrimerLine[0][0])
            .style("font-family", "Montserrat");

          let line3 = tooltip
            .append("tspan")
            .attr("pointer-events", "none");
          line3
            .html("Fraction Bound: " + vm.result.right_primers.frac_bound)
            .style("font-family", "Montserrat");

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

      const xAxisGenerator = d3
        .axisBottom()
        .scale(xScale)
        .ticks(5)

      svg
        .append("g")
        .call(xAxisGenerator)
        .style("transform", `translateY(${boundedHeight}px)`)
        .call(g => g.select(".domain")
          .remove());

    },
  },
}
</script>
