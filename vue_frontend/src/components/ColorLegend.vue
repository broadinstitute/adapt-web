<template>
  <transition appear name="fade">
    <div :style="{'background-color': 'white'}">
      <b-row align-v="center" style="margin-left: 15px; margin-right: 15px;">
        <b-col class="text-center f-7">
          <b-row align-v="center">
            <b-col>Score <span aria-label="Info on Score" v-b-tooltip.top.html="{ customClass: 'f-7', variant: 'info'}" title="<small>Quality based on activity, number of primers, and amplicon length (high is better)</small>" tabindex="0"><b-icon-info-circle font-scale="0.9"/></span></b-col>
          </b-row>
          <div class="score-legend" id="score-legend">
          </div>
        </b-col>
        <b-col class="text-center f-7">
          <b-row align-v="center">
            <b-col>Activity <span aria-label="Info on Activity" v-b-tooltip.top.html="{ customClass: 'f-7', variant: 'info'}" title="<small>Average crRNA activity across sequences; correlates with fluorescence (high is better)</small>" tabindex="0"><b-icon-info-circle font-scale="0.9"/></span></b-col>
          </b-row>
          <div class="activity-legend" id="activity-legend">
          </div>
        </b-col>
        <b-col v-show="genome" class="text-center f-7">
          <b-row align-v="center">
            <b-col>Entropy <span aria-label="Info on Score" v-b-tooltip.top.html="{ customClass: 'f-7', variant: 'info'}" title="<small>How much variation there is at this base in the alignment (low is better)</small>" tabindex="0"><b-icon-info-circle font-scale="0.9"/></span></b-col>
          </b-row>
          <div class="entropy-legend" id="entropy-legend">
          </div>
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
    objectiveColorScale: Function,
    entropyColorScale: Function,
  },
  data() {
    return {
      barHeight: 7,
      width: 130,
      marginX: 5,
      tickHeight: 7,
      tickStrokeThickness: 0.5,
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
      vm.legend(vm.entropyColorScale, '#entropy-legend', [0, 2], [0, .5, 1, 1.5, 2], 1)
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

      vm.ramp(colorScale, svg, vm.marginX, 0, domain[0], domain[1]);

      let xAxisGenerator = d3
        .axisBottom()
        .scale(d3.scaleLinear()
          .domain(domain)
          .range([0, vm.width-2*vm.marginX]))
        .tickValues(tickValues)
        .tickFormat((i) => i.toFixed(roundTicks));

      let xAxis = svg
        .append("g")
        .attr("transform", "translate("+vm.marginX+","+vm.tickHeight+")")
        .call(xAxisGenerator)
        .call(g => g.select(".domain")
          .remove());
      xAxis.selectAll(".tick text")
        .style("font-size","0.2rem")
        .attr("y", vm.tickHeight/2);
      xAxis.selectAll(".tick line")
        .attr("y2", vm.tickHeight/2 - 1)
        .style("stroke-width", vm.tickStrokeThickness+"px");
    },
    ramp(colorScale, svg, x, y, min, max, n = 512) {
      const foreignObj = svg.append('foreignObject')
        .attr("transform", "translate("+x+","+y+")")
        .attr("width", (this.width-this.marginX*2+this.tickStrokeThickness) + "px")
        .attr("height", this.barHeight + "px");
      const canvasContainer = foreignObj.append('xhtml:canvas')
        .attr('xmlns', 'http://www.w3.org/1999/xhtml');
      const canvas = canvasContainer;
      const context = canvas.node().getContext("2d");
      canvas
        .attr("width", n)
        .attr("height", 1)
        .style("width", "100%")
        .style("height", "10px")
        .style("imageRendering", "-moz-crisp-edges")
        .style("imageRendering", "pixelated");
      for (let i = 0; i <= n; ++i) {
        context.fillStyle = colorScale(min+(i / (n - 1))*(max-min));
        context.fillRect(i, 0, 1, 1);
      }
      return canvas;
    }
  },
}
</script>
