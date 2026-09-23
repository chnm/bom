import causeSparklines from "./causes";

// Weekly bills only
causeSparklines(
  "https://data.chnm.org/bom/causes?start-year=1636&end-year=1754&bill-type=weekly",
  "death",
);
