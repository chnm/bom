# API Reference

The Bills of Mortality API is organized around [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) and returns
JSON-encoded responses from our PostgreSQL database using standard HTTP
response codes and verbs. 

The API currently provides three endpoints for returning data. The first endpoint, `bills`, accepts two required parameters: the start year and the end year. This is built this way to operate the range slider that controls the table view on the web application. As you adjust the slider, the new year values are passed to the endpoint and new data is fetched and then displayed in the table. 

The `bills` data returns the following information: 

- Parish name: The name of the parish as recorded for a given date on a given bill. 
- Count type: There are two records for the weekly bills: how many people were buried and how many had the plague. This column indicates the `count` value for each of these.
- Count: These values correspond to the *Count Type* column. 
- Week Number: This is the week number for a given bill.
- Start Day and End Day / Start Month and End Month: This is the date range for a given period.
- Year: This is the year for a given bill.

The second endpoint, `generalbills`, accepts two required parameters: the start year and the end year. This is built this way to operate the range slider that controls the table view on the web application. As you adjust the slider, the new year values are passed to the endpoint and new data is fetched and then displayed in the table. The `generalbills` endpoint returns the following information: 

- Parish name: The name of the parish as recorded for a given date on a given bill. 
- Count type: There are three records for the general bills: total annual values for the number of people buried, how many people had plague, or simply the sum of people who died of plague.
- Count: These values correspond to the *Count Type* column. 
- Week Number: This is the week number for a given bill.
- Start Day and End Day / Start Month and End Month: This is the date range for a given period.
- Year: This is the year for a given bill.

The final endpoint is `christenings`, which powers the *Christenings* tab of the web application. Currently, this endpoint returns the following: 

- Description: A description as transcribed from the bills.
- Count: The number of christenings for a given parish.
- Week Number: The week number for a given bill.
- Year: The year of the given bill.

## Web Application

The web application currently has four ways of interacting with the table of data. 

- The table itself has a few built-in tools for interacting with the data. You can change the rows per page (to view 25, 50, or 100 rows at a time), you can page through the results, or you can search for parish names using the "Search for parish name" box in the Parish column.
- Parishes checkboxes: Displayed above the table, these allow you to select or unselect specific parishes you'd like to display within the table. 
- Years slider: This adjusts the years that are displayed by the table. By default the full extent of years is selected. As you drag the nodes for start and end years, you can see the year value tooltip change. After you let up on your mouse, the new value is then passed to the API and new data fetched for display. 
- Count type: This allows you to filter the data based on either the number of burials or number of those infected with the plague. The options are "All" (to display all data regardless of count type), "Buried" (to display burial counts), and "Plague" (to display infection counts).

## Technical Specifications

### Errors

The BoM API uses conventional HTTP response codes to indicate the success or failure of an API request. Codes in the `2xx` range indicate success. Codes in the `4xx` range indicate an error with the information provided. Codes in the `5xx` range indicate an error with our servers (these are very rare). 

HTTP Status Code Summary 

| Code  | Summary |
| ----- | ------- |
| 200 - OK | Everything worked as expected. |
| 400 - Bad Request | The request was not accepted due to a missing required parameter. |
| 402 - Request Failed | The parameters were valid but the request failed.
| 403 - Forbidden | The API doesn't have permissions to perform a request. |
| 404 - Not Found | The requested resource doesn't exist. |
| 500, 502, 503, 504 - Server Errors | Something went wrong on the BoM end. (These are rare.) |

### Endpoints

The current API has three endpoints, one for serving user interfaces and two for returning the data to an interactive table.

#### Unique parish names

This serves the user interface by populating the checkboxes for filtering parish names selected by a user. These are unique values each with their own unique ID, name as recorded from the primary sources, and the canonical name.

```js
GET /parishes
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

#### Weekly bills

This endpoint returns the entirety of the Weekly Bills data and populates the table under the `Weekly Bills` tab. This endpoint is the primary way for viewing and interacting with the full weekly dataset.

```js
GET /bills
```

Parameters: 
- startYear (required): A four digit number representing the start year.
- endYear (required): A four digit number representing the end year.

The `startYear` and `endYear` parameters are required and return the range of rows in the database that fall between the two years. 

<http://data.chnm.org/bom/bills?startYear=1669&endYear=1754>

Response JSON: 

```js
[
    {
        "name": "Alhallows Barking",
        "count_type": "Buried",
        "count": 2,
        "year": 1669,
        "start_month": "January",
        "start_day": "4",
        "end_month": "January",
        "end_day": "11"
        "week_no": 40,
        "week_id": "1668-1669-40"
    },
    . . .
]
```

#### General bills

This endpoint returns the entirety of the General Bills data and populates the table under the `General Bills` tab. This endpoint is the primary way for viewing and interacting with the full annual dataset.

```js
GET /generalbills
```

Parameters: 
- startYear (required): A four digit number representing the start year.
- endYear (required): A four digit number representing the end year.

The `startYear` and `endYear` parameters are required and return the range of rows in the database that fall between the two years. 

<http://data.chnm.org/bom/generalbills?startYear=1669&endYear=1754>

Response JSON: 

```js
[
    {
        "name": "All Hallows Barking",
        "count_type": "Total",
        "count": 57,
        "start_day": "",
        "start_month": "",
        "end_day": "",
        "end_month": "",
        "year":1749,
        "week_id": "1748-1749-90"},
    . . .
]
```

#### Christenings data

This endpoint returns the christenings data and populates the table under the `Christenings` tab.

```js
GET /christenings
```

Parameters: 
- startYear (required): A four digit number representing the start year.
- endYear (required): A four digit number representing the end year.

The `startYear` and `endYear` parameters are required and return the range of rows in the database that fall between the two years.

<http://data.chnm.org/bom/christenings?startYear=1669&endYear=1754>

Response JSON:

```js
[
    {
        "christenings_desc": "Christened in the 97 Parishes within the Walls",
        "count": 4,
        "week_no": 50,
        "week_id": "1668-1669-50",
        "year": 1669
    },
    . . .
]
```
