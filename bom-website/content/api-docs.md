---
title: "API Documentation"
slug: /api/
layout: api-docs
---

## Overview

The Bills of Mortality API is organized around [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) and returns JSON-encoded responses from our PostgreSQL database using standard HTTP response codes and verbs. The data held by Death by Numbers are available in machine readable formats (currently JSON and CSV) to aid in research and data visualization.

The first API was released in 2021, and the second version in 2024. The 2024 version provides new functionality for searching, sorting, and filtering; provides additional endpoints for data; and a set of new documentation for a quick start in exploring the data.

If you are unfamiliar with working with REST APIs, we recommend consulting the _Programming Historian_ lesson [Introduction to Populating a Website with API Data](https://programminghistorian.org/en/lessons/introduction-to-populating-a-website-with-api-data).

To get started with the data API, please consult our [Getting Started with the Bills of Mortality Data API](https://observablehq.com/d/7adb8b95df5d51a9) notebook.

## Datasets

While the API provides an effective way to retrieve data, for bulk export it is less useful than data delivered through a single file. If you have a project where you want to examine large sets of data, you can find our CSV exports in [our Github repository](/downloads/).

The API currently provides [three main data endpoints](https://data.chnm.org) for returning full datasets.

The first endpoint, `/bills`, accepts three required parameters: the start year, the end year, and the bill type (Weekly or General). This is built this way to operate the year range slider and specific bills to display in the web application. As you adjust the year slider, the new year values are stored until "Apply Filters" is clicked, which then passes stored data to the endpoint and fetches the updated parameters. Optionally, you can include a count type parameter (Buried or Plague) to filter specific values.

The `bills` data returns the following information:

- Parish name: The name of the parish as recorded for a given date on a given bill.
- Bill type: Whether the bill is a Weekly or General bill.
- Count type: There are two records for the weekly bills: how many people were buried and how many had the plague. This column indicates the `count` value for each of these.
- Count: These values correspond to the _Count Type_ column.
- Week Number: This is the week number in a year.
- Start Day and End Day / Start Month and End Month: This is the date range for a given period.
- Year: This is the year for a given bill.
- Split Year: This is to account for the calendar change and indicates where split years are necessary.

The second endpoint is `/causes`, which powers the _Total Deaths_ tab of the web application. The endpoint requires a year range to return data. You can optionally return a specific cause of death to see values for a specific cause. Currently, this endpoint returns the following:

- Death ID: This is a unique ID for the `death` description.
- Death: A description of the cause of death.
- Count: The number of the cause for a given week.
- Week ID: The unique identifier for the week.
- Start Day and End Day / Start Month and End Month: This is the date range for a given period.
- Year: The year for a given cause of death.
- Split Year: The split year for the given cause of death.

The final endpoint is `/christenings`, which powers the _Christenings_ tab of the web application. The endpoint requires a year range to return data. Currently, this endpoint returns the following:

- Description (`christenings_desc`): A description as transcribed from the bills.
- Count: The number of christenings for a given parish.
- Week Number: The week number for a given bill.
- Year: The year of the given bill.
- Split Year: The split year for the given cause of death.
- Location ID: A unique identifier for the **Description** field.

## Citation

If you want to refer to our data or are using the API in an academic publication, you can cite as follows:

```bibtex
@software{dbn-2024-data-api,
    author       = {Death by Numbers},
    title        = {Death by Numbers API v2},
    year         = 2024,
    version      = {2},
    url          = {https://deathbynumbers.org},
}
```

## Web Application

The [web application](/database/) currently has four ways of interacting with the table of data.

- The table itself has built-in tools for interacting with the data. You can change the rows per page (to view 25, 50, or 100 rows at a time), you can page through the results, or you can filter parish names, causes of death, and christenings from the checkboxes.
- Parishes checkboxes and causes of death checkboxes: Displayed above the table, these allow you to select or unselect specific locations or causes of death you'd like to display within the table.
- Years slider: This adjusts the years that are displayed by the table. By default the full extent of years is selected. As you drag the nodes for start and end years, you can see the year value tooltip change. After you let up on your mouse, the new value is stored and waits to be passed to the API by clicking "Apply Filters" and new data fetched for display.
- Count type: This allows you to filter the data based on either the number of burials or number of those infected with the plague. The options for the Weekly bills are "All" (to display all data regardless of count type), "Buried" (to display burial counts), and "Plague" (to display infection counts). The only option currently available for the General bills is "Total" (to display the aggregate data as transcribed from the bills), but will include "Buried" and "Plague" as transcriptions continue.

## Technical Specifications

### Errors

The BOM API uses conventional HTTP response codes to indicate the success or failure of an API request. Codes in the `2xx` range indicate success. Codes in the `4xx` range indicate an error with the information provided. Codes in the `5xx` range indicate an error with our servers (these are very rare).

HTTP Status Code Summary

| Code                               | Summary                                                           |
| ---------------------------------- | ----------------------------------------------------------------- |
| 200 - OK                           | Everything worked as expected.                                    |
| 400 - Bad Request                  | The request was not accepted due to a missing required parameter. |
| 402 - Request Failed               | The parameters were valid but the request failed.                 |
| 403 - Forbidden                    | The API doesn't have permissions to perform a request.            |
| 404 - Not Found                    | The requested resource doesn't exist.                             |
| 500, 502, 503, 504 - Server Errors | Something went wrong on the BOM end. (These are rare.)            |

### Endpoints

The current API has five endpoints, two for serving user interfaces and three for returning the data to an interactive table.

The endpoints can accept `limit` and `offset` values. No `limit` or `offset` values are provided by default, meaning without them you are returning the entire dataset. We're using limit and offset to handle pagination in the web application. You can also provide `limit` (and `offset`) to return a greater number of records. If no limit or offset is provided, the endpoint will return all of the data in the database. Providing a limit of 500, for example, will give you the first five hundred rows from the database:

<https://data.chnm.org/bom/bills?start-year=1648&end-year=1754&bill-type=Weekly&limit=500&offset=0>

#### Unique parish names

This populates parish names checkboxes in the interface for filtering parish names selected by a user. These are unique values each with their own unique ID, name as recorded from the primary sources, and the canonical name determined by the BOM team. **If you'd like to look up a specific parish from the `bills` endpoint, you will need to find the unique parish ID from this list.**

```js
GET / parishes;
```

Parameters:

- none

<http://data.chnm.org/bom/parishes>

Response JSON (indexed by parish ID):

```js
[
    {
        "id": 1,
        "name": "Alhallows Barking",
        "canonical_name": "All Hallows Barking"
        . . .
    },
]
```

#### Bills

This endpoint returns the entirety of the Weekly or General Bills data and populates the table under the `Weekly Bills` and `General Bills` tab. This endpoint is the primary way for viewing and interacting with the full dataset.

```js
GET / bills;
```

Parameters:

- start-year (required): A four digit number representing the start year.
- end-year (required): A four digit number representing the end year.
- bill-type (required): Either "Weekly" or "General" to view specific bill types.
- count-type (optional): Either "Buried" or "Plague" to view specific count types.
- limit (optional): Limit the number of records.
- offset (optional): Offset the number of records.

The `start-year` and `end-year` parameters are required and return the range of rows in the database that fall between the two years. You must also set the `bill-type` parameter to Weekly or General.

<http://data.chnm.org/bom/bills?start-year=1669&end-year=1754&bill-type=Weekly>

Response JSON:

```js
[
    {
	    "name":"All Hallows Barking",
	    "bill_type":"Weekly",
	    "count_type":"Plague",
	    "count":null,
	    "start_day":21,
	    "start_month":"December",
	    "end_day":28,
	    "end_month":"December",
	    "year":1669,
	    "split_year":"1668/1669",
	    "week_no":1,
	    "week_id":"1669-1670-01"
    }
    . . .
]
```

Optionally, you can provide the `/bills` endpoint with the `parishes` parameter, which accepts an ID value for a parish name. You can find the corresponding parish ID value from the `/parishes` endpoint.

<http://data.chnm.org/bom/bills?start-year=1648&end-year=1754&bill-type=Weekly&parishes=1,3,17&limit=50&offset=0>

```js
[
	{
		"name":"All Hallows Barking",
		"bill_type":"Weekly",
		"count_type":"Plague",
		"count":null,
		"start_day":21,
		"start_month":"December",
		"end_day":28,
		"end_month":"December",
		"year":1669,
		"split_year":"1668/1669",
		"week_no":1,
		"week_id":"1669-1670-01"
	},
	...
	{
		"name":"St Mary Rotherhithe",
		"bill_type":"Weekly",
		"count_type":"Plague",
		"count":null,
		"start_day":21,
		"start_month":"December",
		"end_day":28,
		"end_month":"December",
		"year":1669,
		"split_year":"1668/1669",
		"week_no":1,
		"week_id":"1669-1670-01"
	},
	...
	{
		"name":"All Hallows the Great",
		"bill_type":"Weekly",
		"count_type":"Buried",
		"count":1,
		"start_day":28,
		"start_month":"December",
		"end_day":4,
		"end_month":"January",
		"year":1669,
		"split_year":"1668/1669",
		"week_no":2,
		"week_id":"1669-1670-02"
		},
		{
			...
		}
	...
]
```

#### Total bills

To return the entire dataset with both Weekly and General bills, simply leave off the parameters for `bill-type` and `count-type`.

<https://data.chnm.org/bom/bills?start-year=1648&end-year=1754&limit=50>

```js
[
    {
	    "name":"All Hallows Barking",
	    "bill_type":"Weekly",
	    "count_type":"Plague",
	    "count":null,
	    "start_day":21,
	    "start_month":"December",
	    "end_day":28,
	    "end_month":"December",
	    "year":1669,
	    "split_year":"1668/1669",
	    "week_no":1,
	    "week_id":"1669-1670-01"
    }
    . . .
]
```

If you wish to get the dataset without the `limit` and `offset` pagination parameters, you can set `limit` to the total number of records in the database using the `/totalbills` endpoint (see below).

#### The sum of total records

The pagination of the web application table requires knowing the sum of total records for a given dataset. This is provided as an endpoint, and could be used to set the `limit` to the max number of values in the database to return all values.

```js
GET / totalbills;
```

The `totalbills` endpoint requires the parameter `type`, which can be **Causes**, **Weekly**, **General**, or **Christenings**.

<https://data.chnm.org/bom/totalbills?type=Causes>

```js
[
  {
    total_records: 7752,
  },
];
```

#### Causes of death data

This endpoint returns the causes of death data and populates the table under the `Total Deaths` tab.

```js
GET / causes;
```

Parameters:

- start-year (required): A four digit number representing the start year.
- end-year (required): A four digit number representing the end year.
- id (optional): An ID for a specific cause of death.
- limit (optional): Limit the number of records.
- offset (optional): Offset the number of records.

The `start-year` and `end-year` parameters are required and return the range of rows in the database that fall between the two years.

<https://data.chnm.org/bom/causes?start-year=1648&end-year=1754>

```js
[
	{
		"death_id":1,
		"death":"Abortive",
		"count":1,
		"week_id":"1668-1669-01",
		"week_no":1,
		"start_day":22,
		"start_month":"December",
		"end_day":29,
		"end_month":"December",
		"year":1668,
		"split_year":"1667/1668"
		}
	...
]
```

You can optionally include `id` to return specific causes, which can either be a single value or a comma-separated set of values. The full list of `causes` can be found in `/list-deaths` (see below).

<https://data.chnm.org/bom/causes?start-year=1648&end-year=1754&id=Apoplexy>

```js
[
	{
		"death_id":4,
		"death":"Apoplexy",
		"count":2,
		"week_id":"1668-1669-01",
		"week_no":1,
		"start_day":22,
		"start_month":"December",
		"end_day":29,
		"end_month":"December",
		"year":1668,
		"split_year":"1667/1668"
	}
	...
]
```

The complete list of causes of death and their unique IDs can be found using the `/list-deaths` endpoint.

<https://data.chnm.org/bom/list-deaths>

```js
[
	{"name":"Abortive","id":1},
	{"name":"Aged","id":2},
	{"name":"Ague","id":3},
	{"name":"Apoplexy","id":4},
	{"name":"Bed-ridden","id":5},
	{"name":"Blasted","id":6},
	...
]
```

#### Christenings data

This endpoint returns the christenings data and populates the table under the `Christenings` tab.

```js
GET / christenings;
```

Parameters:

- start-year (required): A four digit number representing the start year.
- end-year (required): A four digit number representing the end year.
- id (optional): An ID for a specific christening location.
- limit (optional): Limit the number of records.
- offset (optional): Offset the number of records.

The `start-year` and `end-year` parameters are required and return the range of rows in the database that fall between the two years.

<https://data.chnm.org/bom/christenings?start-year=1640&end-year=1754>

Response JSON:

```js
[
    {
        "christenings_desc": "Christened in the 97 Parishes within the Walls",
        "count": 11,
        "week_no": 1,
        "week_id": "1668-1669-01",
        "year": 1669,
        "split_year": "1668/1669",
        "location_id": 4
    },
    . . .
]
```

You can optionally specify `id` parameters to return specific data.

<https://data.chnm.org/bom/christenings?start-year=1640&end-year=1754&id=3>

```js
[
	{
		"christenings_desc":"Christened in the 5 Parishes in the City and Liberties of Westminster",
		"count":45,
		"week_no":1,
		"year":1669,
		"split_year":"1668/1669",
		"location_id":3
	},
	{
		"christenings_desc":"Christened in the 5 Parishes in the City and Liberties of Westminster",
		"count":43,
		"week_no":2,
		"year":1669,
		"split_year":"1668/1669",
		"location_id":3
	},
	...
]
```

You can retrieve the list of unique christening descriptions using the `/list-christenings` endpoint. The IDs can be used as an optional parameter `id` for the `/list-christenings` endpoint to return specific data.

<https://data.chnm.org/bom/list-christenings>

```js
[
	{
		"name":"Christened in the 13 out-Parishes in Middlesex and Surrey",
		"id":1
	},
	{
		"name":"Christened in the 16 Parishes without the Walls",
		"id":2
	},
	...
]
```

#### Statistics endpoint

The `/statistics` endpoint provides aggregated data about the Bills of Mortality records for visualization and analytical purposes. This endpoint helps researchers understand data completion, coverage, and patterns across time periods.

```js
GET /statistics;
```

Parameters:

- type (required): The type of statistics to return. Valid values are:
  - `yearly`: Returns statistics grouped by year
  - `weekly`: Returns statistics grouped by week
  - `parish-yearly`: Returns statistics grouped by parish and year

Optional parameters:

- parish (optional, only for `parish-yearly` type): Filter results to a specific parish name

Example requests:

<https://data.chnm.org/bom/statistics?type=yearly>

Response JSON:

```js
[
  {
    "year": 1636,
    "weeksCompleted": 42,
    "rowsCount": 3780,
    "totalCount": 53
  },
  {
    "year": 1637,
    "weeksCompleted": 53,
    "rowsCount": 4770,
    "totalCount": 53
  },
  // ...
]
```

<https://data.chnm.org/bom/statistics?type=weekly>

Response JSON:

```js
[
  {
    "year": 1636,
    "weekNumber": 1,
    "rowsCount": 90
  },
  {
    "year": 1636,
    "weekNumber": 2,
    "rowsCount": 90
  },
  // ...
]
```

<https://data.chnm.org/bom/statistics?type=parish-yearly&parish=All%20Hallows%20Barking>

Response JSON:

```js
[
  {
    "year": 1639,
    "parish_name": "All Hallows Barking",
    "total_buried": 175,
    "total_plague": 23
  },
  {
    "year": 1640,
    "parish_name": "All Hallows Barking",
    "total_buried": 134,
    "total_plague": 0
  },
  // ...
]
```

The response data structure depends on the `type` parameter:

For `yearly` type:
- `year`: The year for the statistics
- `weeksCompleted`: The number of weeks with data in that year
- `rowsCount`: The total number of data rows for that year
- `totalCount`: The expected total number of weeks per year (typically 53)

For `weekly` type:
- `year`: The year for the statistics
- `weekNumber`: The week number (1-53)
- `rowsCount`: The number of data rows for that week

For `parish-yearly` type:
- `year`: The year for the statistics
- `parish_name`: The canonical name of the parish
- `total_buried`: The total number of burials recorded for that parish in that year
- `total_plague`: The total number of plague cases recorded for that parish in that year (null if none)

#### Parish geometries endpoint

The `/geometries` endpoint provides GeoJSON data for parish boundaries, which can be used for mapping and spatial analysis of the Bills of Mortality data.

```js
GET /geometries;
```

Parameters:

- year (optional): Filter results to parishes active in a specific year
- subunit (optional): Filter results to a specific administrative subunit
- city_cnty (optional): Filter results to a specific city or county

Example request:

<https://data.chnm.org/bom/geometries>

Response JSON:

```js
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": 1,
      "properties": {
        "par": "All Hallows Barking",
        "civ_par": "All Hallows Barking",
        "dbn_par": "All Hallows Barking",
        "omeka_par": "All Hallows Barking",
        "subunit": "City",
        "city_cnty": "London",
        "start_yr": 1563,
        "sp_total": 4.23,
        "sp_per": 0.12
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          // Coordinate arrays
        ]
      }
    },
    // More features
  ]
}
```

#### GeoJSON Geometries endpoint

The `/geojson` endpoint provides an integrated view of parish geometries and Bills of Mortality data, allowing for spatial analysis of mortality patterns.

```js
GET /geojson;
```

Parameters:

- start-year (required): A four-digit number representing the start year
- end-year (required): A four-digit number representing the end year
- parish (optional): Comma-separated list of parish IDs to include
- bill-type (optional): Type of bills to include ("Weekly" or "General")
- count-type (optional): Type of counts to include ("Buried" or "Plague")
- year (optional): Filter geometries to parishes active in a specific year
- subunit (optional): Filter geometries to a specific administrative subunit
- city_cnty (optional): Filter geometries to a specific city or county

Example request:

<https://data.chnm.org/bom/geojson?start-year=1665&end-year=1666&bill-type=Weekly&count-type=Plague>

Response JSON:

```js
{
  "type": "FeatureCollection",
  "metadata": {
    "start_year": 1665,
    "end_year": 1666,
    "bill_type": "Weekly",
    "count_type": "Plague"
  },
  "features": [
    {
      "type": "Feature",
      "id": 1,
      "properties": {
        "par": "All Hallows Barking",
        "civ_par": "All Hallows Barking",
        "dbn_par": "All Hallows Barking",
        "omeka_par": "All Hallows Barking",
        "subunit": "City",
        "city_cnty": "London",
        "start_yr": 1563,
        "sp_total": 4.23,
        "sp_per": 0.12,
        "weeklyData": [
          {
            "week_id": "1665-1666-01", 
            "count": 15,
            "year": 1665,
            "count_type": "Plague"
          },
          // More weekly data
        ],
        "totalDeaths": 356
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          // Coordinate arrays
        ]
      }
    },
    // More features
  ]
}
```
