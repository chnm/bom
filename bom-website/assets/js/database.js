import Alpine from "alpinejs";
import collapse from '@alpinejs/collapse';

// initialize Alpine
window.Alpine = Alpine;
Alpine.plugin(collapse);

document.addEventListener("alpine:init", () => {
  Alpine.data("billsData", () => ({
    bills: [],
    christenings: [],
    causes: [],
    parishes: null,
    sort: false,
    modalOpen: false,
    instructionsOpen: false,
    modalBill: [],
    disabled: false,
    openTab: 1,
    filters: {
      selectedParishes: [],
      selectedBillType: "Weekly",
      selectedCountType: "",
      selectedStartYear: 1636,
      selectedEndYear: 1754,
    },
    isMissing: false,
    isIllegible: false,
    messages: {
      loading: "Loading data...",
    },
    meta: {
      loading: false,
      fetching: false,
    },
    server: {
      limit: 25,
      offset: 0,
    },
    page: 1,
    pageSize: 25,
    pagination: {
      pageOffset: 25, // number of pages to show on either side of the current page
      total: null, // total number of records from /totalbills endpoint
    },
    init() {
      // Fetch the static data
      this.fetchStaticData();

      // Read URL parameters
      let params = new URLSearchParams(window.location.search);

      // Update filters and page based on URL parameters
      if (params.has('start-year')) this.filters.selectedStartYear = parseInt(params.get('start-year'));
      if (params.has('end-year')) this.filters.selectedEndYear = parseInt(params.get('end-year'));
      if (params.has('count-type')) this.filters.selectedCountType = params.get('count-type');
      if (params.has('parish')) this.filters.selectedParishes = params.get('parish').split(',');
      if (params.has('page')) this.page = parseInt(params.get('page'));
      // if (params.has('openTab')) this.openTab = parseInt(params.get('openTab'));

      this.fetchData();
    },
    async fetchStaticData() {
      // Data used for populating UI elements in the app.
      // These values do not change within the app as users make choices.
      fetch("https://data.chnm.org/bom/parishes")
        .then((response) => response.json())
        .then((data) => {
          this.parishes = data;
        })
        .catch((error) => {
          console.error("There was an error fetching parish data:", error);
        });
    },
    async fetchData(billType) {
      if (this.meta.fetching) {
        return;
      }
      // Data that will update with user selections.
      this.meta.loading = true;
      this.meta.fetching = true;
      // billType defaults to filters.selectedBillType unless one is provided by the app
      billType = billType || this.filters.selectedBillType;

      // 1. Bills data.
      let response = await fetch(
        `https://data.chnm.org/bom/bills?start-year=${this.filters.selectedStartYear}&end-year=${this.filters.selectedEndYear}&bill-type=${billType}&count-type=${this.filters.selectedCountType}&parish=${this.filters.selectedParishes}&limit=${this.server.limit}&offset=${this.server.offset}`,
      );
      let data = await response.json();
      if (data.error) {
        console.error("There was an error fetching weekly bills data:", data.error);
        this.meta.loading = false;
        this.meta.fetching = false;
        return;
      }
      data.forEach((d, i) => (d.id = i));

      console.log('filtered data url: ', 
      `https://data.chnm.org/bom/bills?start-year=${this.filters.selectedStartYear}&end-year=${this.filters.selectedEndYear}&bill-type=${billType}&count-type=${this.filters.selectedCountType}&parish=${this.filters.selectedParishes}&limit=${this.server.limit}&offset=${this.server.offset}`,
      )

      // After the data is ready, we set it to our bills object and the DOM updates
      this.bills = data;
      this.pagination.total = data[0].totalrecords;

      this.meta.loading = false;
      this.meta.fetching = false;
      this.updateUrl();
    },
    async fetchChristenings() {
      this.meta.loading = true;
      let response = await fetch(
        `https://data.chnm.org/bom/christenings?start-year=${this.filters.selectedStartYear}&end-year=${this.filters.selectedEndYear}&limit=${this.server.limit}&offset=${this.server.offset}`,
      );
      let data = await response.json();
      if (data.error) {
        console.log(
          "There was an error fetching the christenings data:",
          data.error,
        );
        this.meta.loading = false;
        return;
      }
      data.forEach((d, i) => (d.id = i));
      this.christenings = data;
      this.pagination.total = data[0].totalrecords;

      this.meta.loading = false;
      this.updateUrl();
    },
    async fetchDeaths() {
      this.meta.loading = true;
      let response = await fetch(
        `https://data.chnm.org/bom/causes?start-year=${this.filters.selectedStartYear}&end-year=${this.filters.selectedEndYear}`,
      );
      let data = await response.json();
      if (data.error) {
        console.log(
          "There was an error fetching the causes of death data:",
          data.error,
        );
        this.meta.loading = false;
        return;
      }
      data.forEach((d, i) => (d.id = i));
      this.causes = data;
      this.pagination.total = data[0].totalrecords;

      this.meta.loading = false;
      this.updateUrl();
    },
    toggleTabs(tabNum) {
      // toggle between interfaces for Weekly, General, Total Deaths, and Christenings
      // if a user selects a different tab, switch to that one
      this.openTab = tabNum;
    },
    getTotalPages() {
      return this.pagination.total;
    },
    setLimit() {
      if (this.server.limit < 25 || this.server.limit > 100) {
        this.server.limit = 25;
      }

      // Anytime the limit is changed, we need to keep the offset position in sync.
      this.server.offset = (this.page - 1) * this.server.limit;

      // After the new limit/offset is ready, we'll fetch the data again.
      this.fetchData();
    },
    setStartYear() {
      // store the start year in the filters object
      this.filters.selectedStartYear = parseInt(this.filters.selectedStartYear);
    },
    setEndYear() {
      // store the end year in the filters object
      this.filters.selectedEndYear = parseInt(this.filters.selectedEndYear);
    },
    setCountType() {
      // store the count type in the filters object
      this.filters.selectedCountType = this.filters.selectedCountType;
      if (this.filters.selectedCountType == "All") {
        this.filters.selectedCountType = "";
      }
    },
    changePage(page) {
      if (page < 1 || page > this.pagination.lastPage) {
        return;
      }
      this.page = page;

      // Anytime the page is changed, we need to rerun our fetch with the appropriate
      // offset value.
      this.server.offset = (page - 1) * this.server.limit;

      // After the new offset is ready, we'll fetch the data again.
      this.fetchData();
    },
    sort(col) {
      if (this.sortCol == col) this.sort = !this.sort;
      this.sortCol = col;
      this.bills.sort((a, b) => {
        if (a[this.sortCol] < b[this.sortCol]) return this.sort ? 1 : -1;
        if (a[this.sortCol] > b[this.sortCol]) return this.sort ? -1 : 1;
        return 0;
      });
    },
    applyFilters() {
      // after a user has made selections, we need to get their data
      // and re-query the API. We get the values in the filters object
      // and pass them to the API.
      this.filters.selectedParishes = this.filters.selectedParishes;
      this.filters.selectedStartYear = parseInt(this.filters.selectedStartYear);
      this.filters.selectedEndYear = parseInt(this.filters.selectedEndYear);
      this.filters.selectedCountType = this.filters.selectedCountType;

      // we reset pagination to the first page
      this.page = 1;
      this.server.offset = 0;

      this.fetchData();
    },
    updateLimitVal() {
      // If a user changes the dropdown to a new value, we need to update the limit value.
      this.server.limit = this.pageSize;
    },
    get resetFilters() {
      // Restore defaults and query to original view
      return () => {
        this.filters.selectedStartYear = 1636;
        this.filters.selectedEndYear = 1754;
        this.filters.selectedCountType = "";
        this.selectedBillType = "Weekly";
        this.filters.selectedParishes = [];
        this.fetchData();
      };
    },
    getCurrentPage() {
      if (this.server.offset == 0) {
        return 1;
      }
      return parseInt(
        parseInt(this.server.offset) / parseInt(this.server.limit) + 1,
      );
    },
    getFirstDisplayedRow: function () {
      return this.server.offset + 1;
    },
    // returns the index of last row on the page
    getLastDisplayedRow: function () {
      let int = parseInt(this.server.offset) + parseInt(this.server.limit);
      if (int > this.server.total) {
        int = this.server.total;
      }
      return int;
    },
    goToLastPage() {
      this.server.offset = this.getTotalPages() - this.server.limit;
      this.fetchData();
    },
    getTotalRows: function () {
      return parseInt(this.server.total);
    },
    getSummary: function (type = "bills", name = "rows") {
      // if data is loading, we'll show a loading message
      if (this.meta.loading) {
        return this.messages.loading;
      }

      if (type.toLowerCase() == "pages") {
        return (
          "Showing page <strong>" +
          this.getCurrentPage() +
          "</strong> of <strong>" +
          this.getTotalPages() +
          "</strong>"
        );
      }
      if (!this.bills.length) {
        return "No results";
      }
      return (
        "Showing <strong>" +
        this.getFirstDisplayedRow() +
        "</strong> to <strong>" +
        this.getLastDisplayedRow() +
        "</strong> of <strong>" +
        this.getTotalPages() +
        "</strong> " +
        name
      );
    },
    updateUrl() {
      // We want to provide URL parameters, so anytime a user updates a filter
      let url = new URL(window.location.href);
      let params = new URLSearchParams(url.search.slice(1));
      params.set("start-year", this.filters.selectedStartYear);
      params.set("end-year", this.filters.selectedEndYear);
      params.set("count-type", this.filters.selectedCountType);
      params.set("parish", this.filters.selectedParishes);
      params.set("page", this.getCurrentPage());
      // params.set("openTab", this.openTab);

      // Use the history API to update the URL
      history.pushState({}, "", `${location.pathname}?${params}`);
    },
  }));
});

Alpine.start();
