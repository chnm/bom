(window.webpackJsonp=window.webpackJsonp||[]).push([[15],{391:function(t,n,r){"use strict";r.r(n);r(50);var e=r(368),h=r(75),o={name:"BarChart",props:{title:{type:String,required:!0}},data:function(){return{chart:null,data:[],width:1e3,height:500,margin:{top:20,right:20,bottom:140,left:40},x:null,y:null,xValues:null,yValues:null,xAxis:null,yAxis:null,svg:null,g:null}},mounted:function(){this.drawChart()},methods:{createChart:function(){this.svg=e.f("#chart").append("svg").attr("width",this.width).attr("height",this.height).append("g").attr("transform","translate("+this.margin.left+","+this.margin.top+")")},updateChart:function(){var t=this;this.x=e.d().rangeRound([0,this.width-this.margin.left-this.margin.right]).padding(.1).domain(this.data.map((function(t){return t.death}))),this.y=e.e().rangeRound([this.height-this.margin.top-this.margin.bottom,0]).domain([0,e.c(this.data,(function(t){return t.count}))]),this.xAxis=e.a(this.x),this.yAxis=e.b(this.y),this.svg.append("g").attr("class","axis axis--x").attr("transform","translate(0,"+(this.height-this.margin.top-this.margin.bottom)+")").call(this.xAxis),this.svg.selectAll(".axis--x text").attr("transform","rotate(-90)").attr("y",0).attr("x",-9).attr("dy",".35em").style("text-anchor","end"),this.svg.append("g").attr("class","axis axis--y").call(this.yAxis).append("text").attr("transform","rotate(-90)").attr("y",6).attr("dy","0.71em").attr("text-anchor","end").text("Frequency"),this.svg.selectAll(".bar").data(this.data).enter().append("rect").attr("class","bar").attr("fill","#EF3054").attr("x",(function(n){return t.x(n.death)})).attr("y",(function(n){return t.y(n.count)})).attr("width",this.x.bandwidth()).attr("height",(function(n){return t.height-t.margin.top-t.margin.bottom-t.y(n.count)}))},updateData:function(){var t=this;h.get("https://data.chnm.org/bom/causes?start-year=1648&end-year=1754&limit=1500&offset=0").then((function(n){t.data=n.data,t.updateChart()})).catch((function(t){console.log(t)}))},drawChart:function(){this.createChart(),this.updateData(),this.updateChart()}}},l=r(60),component=Object(l.a)(o,(function(){var t=this,n=t.$createElement,r=t._self._c||n;return r("div",[r("h3",{staticClass:"text-xl font-bold"},[t._v(t._s(t.title))]),t._v(" "),r("div",{attrs:{id:"chart"}})])}),[],!1,null,"d19c424c",null);n.default=component.exports}}]);