<template>
  <transition appear name="fade">
    <div class="assay">
      {{result.rank + 1}}
      <div class="visualization" :id="'visualization' + result.rank.toString()">
      </div>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'Assay',
  props: {
    result: Object
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
      let boundedWidth = this.width - this.margin.left - this.margin.right
      let boundedHeight = this.height - this.margin.top - this.margin.bottom
      const svg = d3
        .select("#visualization" + this.result.rank.toString())
        .append("svg")
        .attr("viewBox", '0 0 ' + this.width.toString() + ' ' + this.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${this.margin.left}px, ${this.margin.top}px)`
        );
      const yAccessor = (d) => 10;
      const xAccessor = (d) => d;
      const yScale = d3
        .scaleLinear()
        .domain([0, 20])
        .range([boundedHeight, 0]);

      const guideLine = [this.guide_start, this.guide_start + this.guide_seq.length]
      const leftPrimerLine = [this.target[0], this.target[0] + this.left_primer_seq.length]
      const rightPrimerLine = [this.target[1] - this.right_primer_seq.length, this.target[1]]

      // const xScale = d3sB
      //   .scaleLinear()
      //   .domain([0, 1000], [900, 1100], [1100, 3000])
      //   .range([0, boundedWidth])
      //   .scope([0, .25], [.25, .75], [.75, 1]);

      let extentX = d3.extent(this.target, (d) => xAccessor(d))
      let left_primer_seq = this.left_primer_seq
      const xScale = d3
        .scaleLinear()
        .domain([extentX[0] - 50, extentX[1] + 50])
        .range([0, boundedWidth]);

      const line = d3
        .line()
        .x((d) => xScale(xAccessor(d)))
        .y((d) => yScale(yAccessor(d)))

      const violet = getComputedStyle(document.documentElement)
        .getPropertyValue('--violet');
      const mint = getComputedStyle(document.documentElement)
        .getPropertyValue('--mint');

      var tooltipbox = svg
        .append("rect")
        .attr("rx", 5)
        .attr("ry", 5)
        .style("fill", "black")
        .style("opacity", 0);

      var tooltip = tooltipbox
        .append("text")
        .style("fill", "white")
        .attr("class", "tooltip")
        .style("opacity", 0);

      svg
        .append("path")
        .attr("d", line(guideLine))
        .attr("fill", "none")
        .attr("stroke", violet)
        .attr("stroke-width", 1);

      svg
        .append("path")
        .attr("id", "leftPrimerLine")
        .attr("d", line(leftPrimerLine))
        .attr("fill", "none")
        .attr("stroke", mint)
        .attr("stroke-width", 5)
        .on('mouseover', function (d, i) {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .75);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
          let bbox = this.getBBox()
          tooltip.html(left_primer_seq)
            .attr("x",  bbox.x)
            .attr("y",  -20)
          tooltip
            .append("tspan")
            .html("Start Position: " + leftPrimerLine[0].toString())
            .attr("x",  bbox.x)
            .attr("y",  -5)
            .attr("z", 1)
          console.log(tooltip.node().getComputedTextLength())
          tooltipbox
            .attr("x", this.getBBox().x - 5)
            .attr("y",  -40)
            .attr("width", tooltip.node().getBoundingClientRect().width + 10)
            .attr("height",  45)
        })
        .on('mouseout', function (d, i) {
          tooltip.transition()
           .duration(200)
           .style("opacity", 0);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", 0);
        });
      tooltip.on('mouseover', function (d, i) {
          tooltipbox.transition()
            .duration(200)
            .style("opacity", .75);
          tooltip.transition()
            .duration(200)
            .style("opacity", 1);
        })
        .on('mouseout', function (d, i) {
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
        .attr("stroke", mint)
        .attr("stroke-width", 1);
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
