import * as d3 from "d3";
import PlagueBillsBarChart from "./counts-bar-chart";
import PlagueBillsBarChartWeekly from "./counts-bar-chart-multiple";

// Load data
const urls = [
  "https://data.chnm.org/bom/bills?start-year=1602&end-year=1754&bill-type=All&count-type=All&limit=300000&offset=0",
];
const promises = [];
urls.forEach((url) => promises.push(d3.json(url)));

// Once the data is loaded, initialize the visualization.
Promise.all(urls.map((url) => d3.json(url)))
  .then((data) => {
    // First, we need to convert the data into the format we want.
    // We want to group the data by year, and then count the number of bills
    // in each year.
    const groupedData = {};
    data[0].forEach((bill) => {
      if (groupedData[bill.year]) {
        groupedData[bill.year] += 1;
      } else {
        groupedData[bill.year] = 1;
      }
    });

    // Now we need to convert the grouped data into an array of objects
    // with a year and count property. The count here is the number of bills
    // in that year. We also need to sort the data by year.
    const dataArray = [];
    for (const year in groupedData) {
      dataArray.push({ year: year, count: groupedData[year] });
    }
    dataArray.sort((a, b) => a.year - b.year);

    // Let's create a second grouping. This will group by week_id, which is
    // the week of the year. We'll use this to create a second visualization. We
    // need the week_id, count, and year.
    const groupedDataByWeek = {};
    data[0].forEach((bill) => {
      if (groupedDataByWeek[bill.week_id]) {
        groupedDataByWeek[bill.week_id].rows_count += 1;
      } else {
        groupedDataByWeek[bill.week_id] = {
          rows_count: 1,
          year: bill.year,
        };
      }
    });

    // Now we need to convert the grouped data into an array of objects
    // with a year and count property. The count here is the number of bills
    // in that year. We also want to count the number of weeks that are in a year.
    // We then sort the data by year.
    const dataArrayByWeek = [];
    for (const week_id in groupedDataByWeek) {
      dataArrayByWeek.push({
        week_id: week_id,
        rows_count: groupedDataByWeek[week_id].rows_count,
        year: groupedDataByWeek[week_id].year,
      });
    }
    dataArrayByWeek.sort((a, b) => a.week_id - b.week_id);

    // Then, we group the data by year.
    const groupedDataByYear = {};
    dataArrayByWeek.forEach((bill) => {
      if (groupedDataByYear[bill.year]) {
        groupedDataByYear[bill.year].push(bill);
      } else {
        groupedDataByYear[bill.year] = [bill];
      }
    });
    console.log(groupedDataByYear);


    // We need to create a data structure that looks like: 
    // { year: 1638, weeksCompleted: 1, rowsCount: 153 }
    // { year: 1639, weeksCompleted: 24, rowsCount: 232 }
    // To do this, we need to count the number of week_ids in each year. 
    // We also need to count the number of rows in each year.
    const sums = [];
    for (const year in groupedDataByYear) {
      const weeksCompleted = groupedDataByYear[year].length;
      let rowsCount = 0;
      groupedDataByYear[year].forEach((week) => {
        rowsCount += week.rows_count;
      });
      sums.push({ year: year, weeksCompleted: weeksCompleted, rowsCount: rowsCount , totalCount: 53 });
    }
    console.log('sums', sums);



    // Now we can initialize the visualization.
    // const chart = new PlagueBillsBarChart(
    //   "#barchart",
    //   { plague: dataArray },
    //   { width: 960, height: 500 }
    // );
    // chart.render();

    const multiplechart = new PlagueBillsBarChartWeekly(
      "#barchart-multiple",
      { plagueByWeek: sums },
      { width: 960, height: 500 }
    );
    multiplechart.render();
  })
  .catch((error) => {
    console.error("There was an error fetching the data.", error);
  });
