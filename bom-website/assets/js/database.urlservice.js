/**
 * database.urlservice.js
 * Handles URL parameter parsing and updating
 */

const URLService = {
  /**
   * Gets parameters from the current URL
   * @returns {Object} - Object containing the parsed parameters
   */
  getParams() {
    const params = new URLSearchParams(window.location.search);

    return {
      startYear: params.has("start-year")
        ? parseInt(params.get("start-year"))
        : 1636,
      endYear: params.has("end-year") ? parseInt(params.get("end-year")) : 1754,
      countType: params.get("count-type") || "",
      parishes: params.has("parish")
        ? params
            .get("parish")
            .split(",")
            .filter((p) => p.trim() !== "")
        : [],
      page: params.has("page") ? Math.max(1, parseInt(params.get("page"))) : 1,
      billType: params.has("bill-type")
        ? params.get("bill-type")
        : "weekly",
      tab: params.has("tab") ? parseInt(params.get("tab")) : 1,
      causesOfDeath: params.has("causes")
        ? params
            .get("causes")
            .split(",")
            .filter((c) => c.trim() !== "")
        : [],
      christenings: params.has("christenings")
        ? params
            .get("christenings")
            .split(",")
            .filter((c) => c.trim() !== "")
        : [],
    };
  },

  /**
   * Updates the URL with new parameters without page reload
   * @param {Object} params - Parameters to update
   * @param {boolean} [replace=false] - Whether to replace or push state
   */
  updateParams(params, replace = false) {
    const urlParams = new URLSearchParams();

    // Add parameters if they have values
    if (params.startYear) urlParams.set("start-year", params.startYear);
    if (params.endYear) urlParams.set("end-year", params.endYear);
    if (params.countType && params.countType !== "All" && params.countType !== "all") urlParams.set("count-type", params.countType);

    if (params.parishes && params.parishes.length > 0) {
      urlParams.set("parish", params.parishes.join(","));
    }

    if (params.causesOfDeath && params.causesOfDeath.length > 0) {
      urlParams.set("causes", params.causesOfDeath.join(","));
    }

    if (params.christenings && params.christenings.length > 0) {
      urlParams.set("christenings", params.christenings.join(","));
    }

    if (params.page && params.page > 1) urlParams.set("page", params.page);
    if (params.billType) urlParams.set("bill-type", params.billType);
    if (params.tab) urlParams.set("tab", params.tab);

    // Update browser history
    const newUrl = `${window.location.pathname}?${urlParams}`;

    if (replace) {
      history.replaceState({}, "", newUrl);
    } else {
      history.pushState({}, "", newUrl);
    }
  },

  /**
   * Converts filters object to URL parameters format
   * @param {Object} filters - Filters object from Alpine state
   * @param {Object} pagination - Pagination object
   * @param {number} tab - Current tab
   * @returns {Object} - URL parameters object
   */
  filtersToParams(filters, pagination, tab) {
    return {
      startYear: filters.selectedStartYear,
      endYear: filters.selectedEndYear,
      countType: filters.selectedCountType,
      parishes: filters.selectedParishes,
      causesOfDeath: filters.selectedCausesOfDeath,
      christenings: filters.selectedChristenings,
      billType: filters.selectedBillType,
      page: pagination.page,
      tab: tab,
    };
  },

  /**
   * Updates filters object based on URL parameters
   * @param {Object} filters - Filters object to update
   * @param {Object} pagination - Pagination object to update
   * @returns {number} - Active tab from URL
   */
  updateFiltersFromURL(filters, pagination) {
    const params = this.getParams();

    // Update filters
    filters.selectedStartYear = params.startYear;
    filters.selectedEndYear = params.endYear;
    filters.selectedCountType = params.countType;
    filters.selectedParishes = params.parishes;
    filters.selectedCausesOfDeath = params.causesOfDeath;
    filters.selectedChristenings = params.christenings;
    filters.selectedBillType = params.billType;

    // Update pagination
    pagination.page = params.page;

    return params.tab;
  },
};

// Export the service
window.URLService = URLService;
