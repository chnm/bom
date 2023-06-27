import * as d3 from 'd3';
import d3Cloud from 'd3-cloud';
import Visualization from '../common/visualization';

export default class WordCloudChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 0, right: 40, bottom: 40, left: 10,
    };
    super(id, data, dim, margin);
  }

  // Draw the plot
  render() {
    // causes needs to be an array of objects with a text and size property, 
    // which will group each word together and add together each of their d.count
    // values. To do this we'll loop through the data and create a new object
    // for each unique word, and add the count to the size property. We use
    // d3.rollups to do this.
    const causes = d3.rollups(
      this.data.causes,
      (v) => d3.sum(v, (d) => d.count),
      (d) => d.death,
    ).map(([text, size]) => ({ text, size }));

    const wordcloud = WordCloud(causes, {
      size: (group) => {
        return group.reduce((acc, cur) => acc + cur.size * 0.01, 0);
      },
      word: (d) => d.text,
    });

    d3.select(".loading_chart").remove();
    this.svg.node().append(wordcloud);
  }
}

// Word cloud generator
function WordCloud(text, {
  size = group => group.length, // Given a grouping of words, returns the size factor for that word
  word = d => d, // Given an item of the data array, returns the word
  marginTop = 0, // top margin, in pixels
  marginRight = 0, // right margin, in pixels
  marginBottom = 0, // bottom margin, in pixels
  marginLeft = 0, // left margin, in pixels
  width = 640, // outer width, in pixels
  height = 400, // outer height, in pixels
  maxWords = 1200, // maximum number of words to extract from the text
  fontFamily = "serif", // font family
  fontScale = 14, // base font size
  padding = 0, // amount of padding between the words (in pixels)
  rotate = 0, // a constant or function to rotate the words
} = {}) {
  const words = typeof text === "string" ? text.split(/\W+/g) : Array.from(text);

  const data = d3.rollups(words, size, w => w)
    .sort(([, a], [, b]) => d3.descending(a, b))
    .slice(0, maxWords)
    .map(([key, size]) => ({text: word(key), size}));
  
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("font-family", fontFamily)
      .attr("text-anchor", "middle")
      .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  const g = svg.append("g").attr("transform", `translate(${marginLeft},${marginTop})`);

  const cloud = d3Cloud()
      .size([width - marginLeft - marginRight, height - marginTop - marginBottom])
      .words(data)
      .padding(padding)
      .rotate(rotate)
      .font(fontFamily)
      .fontSize(d => Math.sqrt(d.size) * fontScale)
      .on("word", ({size, x, y, rotate, text}) => {
        g.append("text")
            .attr("font-size", size)
            .attr("transform", `translate(${x},${y}) rotate(${rotate})`)
            .text(text);
      });

  cloud.start();
  return svg.node();
}