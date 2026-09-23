import causeSparklines from "../sparklines-causes/causes";

// General bills only
causeSparklines(
  "https://data.chnm.org/bom/causes?start-year=1629&end-year=1754&bill-type=general",
  "name",
);
