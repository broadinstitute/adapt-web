<template>
  <transition appear name="fade">
    <div class="assay">
        <a class="anchor" :id="'anchor-' + cluster_id + '-' + result.rank.toString()" :style="{'top': (-genomeHeight).toString()+'px'}"></a>
        <div class="visualization" :id="'visualization-' + cluster_id + '-' + result.rank.toString()"></div>
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
    genomeHeight: Number,
    activityColorScale: Function,
    fracBoundColorScale: Function,
  },
  data() {
    let margin= {
      "top": 60,
      "right": 0,
      "left": 0,
      "bottom": 50,
    }

    let width = 750
    let boundedWidth = width - margin.left - margin.right

    let numOligos = this.result.left_primers.primers.length +
                    this.result.right_primers.primers.length +
                    this.result.guide_set.guides.length

    let baseline = 20
    let oligoHeight = 10
    let shift = 6.5

    let boundedHeight = baseline + numOligos*oligoHeight + (numOligos-1)*shift
    let height = boundedHeight + margin.top + margin.bottom

    let xDomain = [this.result.amplicon_start - 10, this.result.amplicon_end + 9]
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
      "primerShift": 4,
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
      "violet": getComputedStyle(document.documentElement)
        .getPropertyValue('--violet'),
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
        .style("font-family", "Overpass Mono")
        .style("letter-spacing", '0.03em');

      let t = [vm.target[0]]
      let ampliconLength = vm.target[1]-vm.target[0]
      let interval =  Math.max(Math.trunc(ampliconLength/50)*10, 20)
      while (t[t.length-1] < vm.target[1]) {
        t.push(t[t.length-1] + interval)
      }
      t[t.length-1] = vm.target[1]-1
      let closeTick = ((t[t.length-1] - t[t.length-2])/interval) < .2

      var darkInfo = d3.color(vm.info).darker(.6)
      var lightInfo = d3.color(vm.info).brighter(.25)

      svg
        .append("text")
        .attr("text-anchor", "middle")
        .style("font-weight", "700")
        .style("fill", darkInfo)
        .style("font-family", "Montserrat")
        .style("font-size", "1rem")
        .html((vm.result.rank+1).toString())
        .attr("x", vm.xScale(this.result.amplicon_start - 5))
        .attr("y", -15);

      var startLine = svg
        .append("line")
        .style("stroke", vm.info)
        .style("stroke-width", 1)
        .style("opacity", 0);

      var startTextBox = svg
        .append("text")
        .attr("text-anchor", "middle")
        .style("font-weight", "700")
        .style("fill", darkInfo)
        .style("font-size", ".5rem")
        .style("opacity", 0);

      var endLine = svg
        .append("line")
        .style("stroke", vm.info)
        .style("stroke-width", 1)
        .style("opacity", 0);

      var endTextBox = svg
        .append("text")
        .attr("text-anchor", "middle")
        .style("font-weight", "700")
        .style("fill", darkInfo)
        .style("font-size", ".5rem")
        .style("opacity", 0);

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


      let bottomOligo = vm.baseline
      let rightPrimerLines = []
      let rightPrimerPaths = []
      for (let rightPrimer of vm.rightPrimers) {
        let rightPrimerLine = [
          [vm.target[1] - rightPrimer.target.length, bottomOligo],
          [vm.target[1] - rightPrimer.target.length, bottomOligo+vm.oligoHeight],
          [vm.target[1], bottomOligo+vm.oligoHeight+vm.primerShift],
          [vm.target[1], bottomOligo-vm.primerShift/2],
        ]
        rightPrimerLines.push(rightPrimerLine)
        rightPrimerPaths.push(svg
          .append("path")
          .attr("d", vm.line(rightPrimerLine))
          .attr("stroke", "#00000000")
          .attr("stroke-width", 20)
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
          .attr("stroke", "#00000000")
          .attr("stroke-width", 20)
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
          [vm.target[0], bottomOligo-vm.primerShift/2],
          [vm.target[0], bottomOligo+vm.oligoHeight+vm.primerShift],
          [vm.target[0] + leftPrimer.target.length, bottomOligo+vm.oligoHeight],
          [vm.target[0] + leftPrimer.target.length, bottomOligo],
        ]
        leftPrimerLines.push(leftPrimerLine)
        leftPrimerPaths.push(svg
          .append("path")
          .attr("d", vm.line(leftPrimerLine))
          .attr("stroke", "#00000000")
          .attr("stroke-width", 20)
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
        // .attr("pointer-events", "none")
        .style("fill", lightInfo);

      var tooltip = tooltipgroup
        .append("text")
        .attr("text-anchor", "middle")
        .style("fill", vm.navy)
        .attr("class", "tooltip")
        // .attr("pointer-events", "none")
        .style("font-size", ".5rem");

      for (let i in guidePaths) {
        var bases = vm.complement(vm.guides[i].target, true)
        var blast_link = '<a class=\'light\' href=\'https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&DATABASE=nt&WORD_SIZE=7&QUERY='+bases+'&CMD=Put\' target=\'_blank\'>BLAST</a>'

        if (vm.guides[i].start_pos.length > 1) {
          vm.oligo_tooltip(guidePaths[i], 'LwaCas13a crRNA:', tooltip, tooltipbox, vm.activityColorScale(vm.result.guide_set.guides[i].expected_activity), ['<a style="font-family: Overpass Mono">5\'-GAUUUAGACUACCCCAAAAACGAAGGGGACUAAAAC'+bases+'-3\'</a>', "Alternate Start Positions: " + vm.guides[i].start_pos.slice(1), "Expected Activity: " + vm.result.guide_set.guides[i].expected_activity, blast_link], startLine, startTextBox, guideLines[i][0][0], endLine, endTextBox, guideLines[i][2][0]-1)
        } else {
          vm.oligo_tooltip(guidePaths[i], 'LwaCas13a crRNA:',  tooltip, tooltipbox, vm.activityColorScale(vm.result.guide_set.guides[i].expected_activity), ['<a style="font-family: Overpass Mono">5\'-GAUUUAGACUACCCCAAAAACGAAGGGGACUAAAAC'+bases+'-3\'</a>', "Expected Activity: " + vm.result.guide_set.guides[i].expected_activity, blast_link], startLine, startTextBox, guideLines[i][0][0], endLine, endTextBox, guideLines[i][2][0]-1)
        }
      }

      for (let i in leftPrimerPaths) {
        bases = vm.complement(vm.result.left_primers.primers[i].target, false)
        blast_link = '<a class=\'light\' href=\'https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&DATABASE=nt&WORD_SIZE=7&QUERY='+bases+'&CMD=Put\' target=\'_blank\'>BLAST</a>'
        vm.oligo_tooltip(leftPrimerPaths[i], "With T7 Promoter:", tooltip, tooltipbox, vm.fracBoundColorScale(vm.result.left_primers.frac_bound), ['<a style="font-family: Overpass Mono">5\'-gaaatTAATACGACTCACTATAggg'+bases+'-3\'</a>', "Fraction Bound: " + vm.result.left_primers.frac_bound, blast_link], startLine, startTextBox, '', endLine, endTextBox, leftPrimerLines[i][2][0]-1)
      }

      for (let i in rightPrimerPaths) {
        blast_link = '<a class=\'light\' href=\'https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&DATABASE=nt&WORD_SIZE=7&QUERY='+vm.result.right_primers.primers[i].target+'&CMD=Put\' target=\'_blank\'>BLAST</a>'
        vm.oligo_tooltip(rightPrimerPaths[i], '<a style="font-family: Overpass Mono">5\'-'+vm.result.right_primers.primers[i].target+'-3\'</a>', tooltip, tooltipbox, vm.fracBoundColorScale(vm.result.right_primers.frac_bound), ["Fraction Bound: " + vm.result.right_primers.frac_bound, blast_link], startLine, startTextBox, rightPrimerLines[i][0][0], endLine, endTextBox, '')
      }

      tooltip
        .on('mouseover', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 1);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", .94);
        })
        .on('mouseout', function () {
          tooltip.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltip.html('');
            });
          tooltipbox.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltipbox
                .attr("width", 0)
                .attr("height", 0);
            });
        });

      tooltipbox
        .on('mouseover', function () {
          tooltip.transition()
           .duration(200)
           .style("opacity", 1);
          tooltipbox.transition()
           .duration(200)
           .style("opacity", .94);
        })
        .on('mouseout', function () {
          tooltip.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltip
                .html('');
            });
          tooltipbox.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltipbox
                .attr("width", 0)
                .attr("height", 0);
            });
        });

      if (vm.aln_sum.length != 0) {
        let total = 0
        for (let i in vm.aln_sum[0]) {
          total += vm.aln_sum[0][i]
        }
        var entropyColorScale =d3.scaleLinear()
          .domain([0, 1.7])
          .interpolate(d3.interpolateRgb.gamma(2.2))
          .range([vm.violet, vm.red])
        for (let b in Array(this.xDomain[1]+1-this.xDomain[0]).fill(this.xDomain[0])) {
          let bases = this.aln_sum[parseInt(b) + this.xDomain[0]]
          svg
            .append("text")
            .attr("text-anchor", "middle")
            .style("fill", entropyColorScale(vm.entropy(bases, total)))
            .style("font-size", ".5rem")
            .html(this.max_base(bases))
            .style("font-family", "Overpass Mono")
            .attr("x", this.xScale(parseInt(b) + this.xDomain[0]))
            .attr("y", `${this.boundedHeight}px`)
            .attr("alignment-baseline", "central")
            .attr("pointer-events", "none");
        }
      }
    },
    entropy(bases, total) {
      return Object.values(bases).map(x => {
        let p = x/total;
        if (p==0) {
          return 0
        }
        return -p * Math.log(p)
      }).reduce((a, b) => a+b)
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
    complement(bases, rna=false) {
      return Array.prototype.map.call(bases, x => {
        if (x == 'G') {
          return 'C'
        } else if (x == 'C') {
          return 'G'
        } else if (x == 'A') {
          if (rna) {
            return 'U'
          } else {
            return 'T'
          }
        } else {
          return 'A'
        }
      }).join('');
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
    oligo_tooltip(oligoPath, line1Text, tooltip, tooltipbox, color, extraLinesText, startLine, startTextBox, startText, endLine, endTextBox, endText) {
      let vm = this
      oligoPath
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
            // .attr("pointer-events", "none");

          let bboxTextLine = tooltip.node().getBBox()

          let extraLines = []
          for (let extraLineText in extraLinesText){
            let extraLine = tooltip
              .append("tspan")
              // .attr("pointer-events", "none")
              .attr("text-anchor", "middle")
              .html(extraLinesText[extraLineText]);
            extraLines.push(extraLine);
          }

          let bboxOligoLine = this.getBBox()
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
          if (bboxText.x < 5) {
            tooltipX += 5 - bboxText.x
            tooltip
              .attr("x", tooltipX)
            for (let extraLine in extraLines) {
              extraLines[extraLine]
                .attr("x", tooltipX)
            }
            bboxText = tooltip.node().getBBox();
          }

          tooltipbox
            .attr("x", bboxText.x - 5)
            .attr("y", bboxText.y - 5)
            .attr("width", bboxText.width + 10)
            .attr("height",  bboxText.height + 10)

          startLine.transition()
            .duration(200)
            .style("opacity", 1);
          startTextBox.transition()
            .duration(200)
            .style("opacity", 1);
          startLine
            .attr("x1", bboxOligoLine.x)
            .attr("y1", bboxOligoLine.y+bboxOligoLine.height/2)
            .attr("x2", bboxOligoLine.x)
            .attr("y2", vm.boundedHeight + 21.5);
          startTextBox
            .html(startText.toLocaleString())
            .attr("x", bboxOligoLine.x)
            .attr("y", vm.boundedHeight + 33);

          endLine.transition()
            .duration(200)
            .style("opacity", 1);
          endTextBox.transition()
            .duration(200)
            .style("opacity", 1);
          endLine
            .attr("x1", bboxOligoLine.x+bboxOligoLine.width+(vm.xScale(0)-vm.xScale(1)))
            .attr("y1", bboxOligoLine.y+bboxOligoLine.height/2)
            .attr("x2", bboxOligoLine.x+bboxOligoLine.width+(vm.xScale(0)-vm.xScale(1)))
            .attr("y2", vm.boundedHeight + 21.5);
          endTextBox
            .html(endText.toLocaleString())
            .attr("x", bboxOligoLine.x+bboxOligoLine.width+(vm.xScale(0)-vm.xScale(1)))
            .attr("y", vm.boundedHeight + 33);
        })
        .on('mouseout', function () {
          tooltip.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltip
                .html('');
            });
          tooltipbox.transition()
            .duration(200)
            .style("opacity", 0)
            .on("end", function() {
              tooltipbox
                .attr("width", 0)
                .attr("height", 0);
            });

          startLine.transition()
            .duration(200)
            .style("opacity", 0);
          startTextBox.transition()
            .duration(200)
            .style("opacity", 0);

          endLine.transition()
            .duration(200)
            .style("opacity", 0);
          endTextBox.transition()
            .duration(200)
            .style("opacity", 0);
        });
    },
  },
}
</script>
