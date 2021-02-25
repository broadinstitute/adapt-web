<template>
  <transition appear name="fade">
    <div class="assay" id="assay">
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";
import * as d3sB from "d3-scale-break";

export default {
  name: 'Assay',
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
      dataset: [
        {
          xattr: 1023,
        },
        {
          xattr: 1051,
        },
      ]
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
        .select("#assay")
        .append("svg")
        .attr("viewBox", '0 0 ' + this.width.toString() + ' ' + this.height.toString())
        .append("g")
        .style(
          "transform",
          `translate(${this.margin.left}px, ${this.margin.top}px)`
        );
      const yAccessor = (d) => 10;
      const xAccessor = (d) => d.xattr;
      const yScale = d3
        .scaleLinear()
        .domain([0, 20])
        .range([boundedHeight, 0]);

      // const xScale = d3sB
      //   .scaleLinear()
      //   .domain([0, 1000], [900, 1100], [1100, 3000])
      //   .range([0, boundedWidth])
      //   .scope([0, .25], [.25, .75], [.75, 1]);

      const xScale = d3sB
        .scaleLinear()
        .domain([0, 3000])
        .range([0, boundedWidth]);

      const line = d3
        .line()
        .x((d) => xScale(xAccessor(d)))
        .y((d) => yScale(yAccessor(d)))

      const violet = getComputedStyle(document.documentElement)
        .getPropertyValue('--violet');
      svg
        .append("path")
        .attr("d", line(this.dataset))
        .attr("fill", "none")
        .attr("stroke", violet)
        .attr("stroke-width", 3);
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
