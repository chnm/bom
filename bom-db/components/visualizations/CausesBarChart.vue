<template>
  <div>
    <h3 class="text-xl font-bold">{{ title }}</h3>
    <div id="chart"></div>
  </div>
</template>

<script>
import * as d3 from "d3";
import * as axios from "axios";

export default {
  name: "BarChart",
  props: {
    title: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      chart: null,
      data: [],
      width: 1000,
      height: 500,
      margin: { top: 20, right: 20, bottom: 140, left: 40 },
      x: null,
      y: null,
      xValues: null,
      yValues: null,
      xAxis: null,
      yAxis: null,
      svg: null,
      g: null,
    };
  },
  mounted() {
    this.drawChart();
  },
  methods: {
    createChart() {
      this.svg = d3
        .select("#chart")
        .append("svg")
        .attr("width", this.width)
        .attr("height", this.height)
        .append("g")
        .attr(
          "transform",
          "translate(" + this.margin.left + "," + this.margin.top + ")"
        );
    },
    updateChart() {
      this.x = d3
        .scaleBand()
        .rangeRound([0, this.width - this.margin.left - this.margin.right])
        .padding(0.1)
        .domain(
          this.data.map((d) => {
            return d.death;
          })
        );
      this.y = d3
        .scaleLinear()
        .rangeRound([this.height - this.margin.top - this.margin.bottom, 0])
        .domain([
          0,
          d3.max(this.data, function (d) {
            return d.count;
          }),
        ]);
      this.xAxis = d3.axisBottom(this.x);
      this.yAxis = d3.axisLeft(this.y);
      this.svg
        .append("g")
        .attr("class", "axis axis--x")
        .attr(
          "transform",
          "translate(0," +
            (this.height - this.margin.top - this.margin.bottom) +
            ")"
        )
        .call(this.xAxis);

      // rotate the x axis labels 90 degrees
      this.svg
        .selectAll(".axis--x text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("x", -9)
        .attr("dy", ".35em")
        .style("text-anchor", "end");

      this.svg
        .append("g")
        .attr("class", "axis axis--y")
        .call(this.yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Frequency");
      this.svg
        .selectAll(".bar")
        .data(this.data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("fill", "#EF3054")
        .attr("x", (d) => this.x(d.death))
        .attr("y", (d) => this.y(d.count))
        .attr("width", this.x.bandwidth())
        .attr(
          "height",
          (d) =>
            this.height - this.margin.top - this.margin.bottom - this.y(d.count)
        );
    },
    updateData() {
      axios
        .get(
          "https://data.chnm.org/bom/causes?start-year=1648&end-year=1754&limit=1500&offset=0"
        )
        .then((response) => {
          this.data = response.data;
          this.updateChart();
        })
        .catch((error) => {
          // eslint-disable-next-line no-console
          console.log(error);
        });
    },
    drawChart() {
      this.createChart();
      this.updateData();
      this.updateChart();
    },
  },
};
</script>

<style scoped></style>
