<template>
  <transition appear name="fade">
    <div :class="['py-2',]" :style="{'background-color': 'white'}">
      <b-row align-v="center">
        <b-col cols=2 class="text-center f-4">
          Legend
        </b-col>
        <b-col cols=10>
          <b-row style="margin-left: -45px; margin-right: 15px;">
            <b-col class="text-center f-5">
              <small><i>Score:</i></small>
              <div class="score-legend" id="score-legend">
              </div>
            </b-col>
            <b-col class="text-center f-5">
              <small><i>Activity:</i></small>
              <div class="activity-legend" id="activity-legend">
              </div>
            </b-col>
            <b-col class="text-center f-5">
              <small><i>Fraction Bound:</i></small>
              <div class="frac-bound-legend" id="frac-bound-legend">
              </div>
            </b-col>
            <b-col v-show="genome" class="text-center f-5">
              <small><i>Entropy:</i></small>
              <div class="entropy-legend" id="entropy-legend">
              </div>
            </b-col>
          </b-row>
        </b-col>
      </b-row>
    </div>
  </transition>
</template>

<script>
import * as d3 from "d3";

export default {
  name: 'ColorLegend',
  props: {
    genome: Boolean,
    activityColorScale: Function,
    fracBoundColorScale: Function,
    objectiveColorScale: Function,
    entropyColorScale: Function,
  },
  data() {
    return {
      barHeight: 10,
      width: 90,
      marginX: 5,
      tickHeight: 10,
    };
  },
  mounted() {
    this.init()
  },
  methods: {
    init() {
      const vm = this

      vm.legend(vm.objectiveColorScale, '#score-legend', [0, 5], [0, 1, 2, 3, 4, 5], 0)
      vm.legend(vm.activityColorScale, '#activity-legend', [0, 4], [0, 1, 2, 3, 4], 0)
      vm.legend(vm.fracBoundColorScale, '#frac-bound-legend', [0, 1], [0, .2, .4, .6, .8, 1], 1)
      vm.legend(vm.entropyColorScale, '#entropy-legend', [2, 0], [2, 1.5, 1, .5, 0], 1)

    },
    legend(colorScale, svgId, domain, tickValues, roundTicks) {
      const vm = this;
      const svg = d3
        .select(svgId)
        .append("svg")
        .attr("viewBox", '0 0 ' + vm.width.toString() + ' ' + (vm.barHeight+vm.tickHeight).toString())
        .append("g")
        .style("font-family", "Overpass Mono")
        .style("letter-spacing", '0.04em');

      let xAxisGenerator = d3
        .axisBottom()
        .scale(d3.scaleLinear()
          .domain(domain)
          .range([0, vm.width-2*vm.marginX]))
        .tickValues(tickValues)
        .tickFormat((i) => i.toFixed(roundTicks));

      let xAxis = svg
        .append("g")
        .attr("transform", "translate(3,10)")
        .call(xAxisGenerator)
        .call(g => g.select(".domain")
          .remove());
      xAxis.selectAll(".tick text")
        .style("font-size","0.2rem")
        .attr("y", "4");
      xAxis.selectAll(".tick line")
        .attr("y2", "3")
        .style("stroke-width", 0.3);

      vm.ramp(colorScale, svg, 3, 0, domain[0], domain[1]);
    },
    ramp(colorScale, svg, x, y, min, max, n = 512) {
      const foreignObj = svg.append('foreignObject')
        .attr("x", x)
        .attr("y", y)
        .attr("width", "80px")
        .attr("height", "10px");
      const canvasContainer = foreignObj.append('xhtml:canvas')
        .attr('xmlns', 'http://www.w3.org/1999/xhtml');
      const canvas = canvasContainer;
      const context = canvas.node().getContext("2d");
      canvas
        .attr("width", n)
        .attr("height", 1)
        .style("width", (this.width-2*this.marginX)+"px")
        .style("height", "10px")
        .style("imageRendering", "-moz-crisp-edges")
        .style("imageRendering", "pixelated");
      for (let i = 0; i < n; ++i) {
        context.fillStyle = colorScale(min+(i / (n - 1))*(max-min));
        context.fillRect(i, 0, 1, 1);
      }
      return canvas;
    }
  },
}
</script>
