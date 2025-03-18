/**
 * Main Alpine.js component for the Bills of Mortality application
 */
document.addEventListener("alpine:init", () => {
  Alpine.data("billsData", () => ({
    // Data state
    bills: [],
    christenings: [],
    causes: [],
    parishes: null,
    all_causes: [],
    all_christenings: [],
    parishYearlyData: {},
    
    // Tab state
    activeTab: 1,
    dragging: null,
    
    // UI state
    modalOpen: false,
    instructionsOpen: false,
    modalBill: [],
    disabled: false,
    isMissing: false,
    isIllegible: false,
    
    // Filter state
    filters: {
      selectedParishes: [],
      selectedBillType: "Weekly",
      selectedCountType: "",
      selectedStartYear: 1636,
      selectedEndYear: 1754,
      selectedCausesOfDeath: [],
      selectedChristenings: [],
    },
    
    // Status messages
    messages: {
      loading: "Loading data...",
      error: "Error loading data. Please try again.",
      noResults: "No data available. Please try different filters.",
    },
    
    // Loading state
    meta: {
      loading: false,
      fetching: false,
      error: null
    },
    
    // Pagination state
    page: 1,
    pageSize: 25,
    server: {
      limit: 25,
      offset: 0,
    },
    pagination: {
      total: 0,
      lastPage: 1,
      page: 1, 
      pageSize: 25, 
      pageOffset: 25, 
    },
    
    /**
     * Initialize the component
     */
    init() {
      console.log("Initializing Bills of Mortality application");
      
      // Parse URL parameters
      this.parseURLParams();
      
      // Initialize data
      this.fetchStaticData()
        .then(() => {
          // Get the initial tab from URL or default to tab 1
          const urlParams = window.URLService ? window.URLService.getParams() : {};
          const initialTab = urlParams.tab || 1;
          this.activeTab = initialTab;
          
          console.log("Initial tab is " + initialTab);
          
          // Set Alpine store if available
          if (window.Alpine && window.Alpine.store) {
            try {
              window.Alpine.store('openTab', initialTab);
            } catch (e) {
              console.warn('Unable to set active tab in Alpine store:', e);
            }
          }
          
          // Load data for the initial tab
          this.switchTab(initialTab);
        });
        
      // Listen for history navigation
      window.addEventListener('popstate', () => {
        this.parseURLParams();
        const currentTab = this.getOpenTab();
        this.switchTab(currentTab);
      });
    },
    
    /**
     * Parse URL parameters and update state
     */
    parseURLParams() {
      const params = new URLSearchParams(window.location.search);
      
      if (params.has("start-year"))
        this.filters.selectedStartYear = parseInt(params.get("start-year"));
      if (params.has("end-year"))
        this.filters.selectedEndYear = parseInt(params.get("end-year"));
      if (params.has("count-type"))
        this.filters.selectedCountType = params.get("count-type");
      if (params.has("parish")) {
        const parishParam = params.get("parish");
        if (parishParam) {
          const parishes = parishParam.split(",");
          this.filters.selectedParishes = parishes.filter(p => p.trim() !== "");
        }
      }
      if (params.has("page")) {
        const pageNum = parseInt(params.get("page"));
        if (!isNaN(pageNum) && pageNum > 0) {
          this.page = pageNum;
          this.pagination.page = pageNum;
        }
      }
      if (params.has("bill-type")) {
        const billType = params.get("bill-type");
        if (["Weekly", "General", "Total"].includes(billType)) {
          this.filters.selectedBillType = billType;
        }
      }
    },
    
    /**
     * Fetch static data for filters
     */
    async fetchStaticData() {
      try {
        // Fetch parishes data
        const parishes = await window.DataService.fetchParishes();
        this.parishes = parishes;
        
        // Fetch causes of death data
        const causes = await window.DataService.fetchAllCauses();
        this.all_causes = causes;
        this.all_causes.forEach(function(d, i) {
          d.id = i;
        });
        
        // Fetch christenings data
        const christenings = await window.DataService.fetchAllChristenings();
        this.all_christenings = christenings;
      } catch (error) {
        console.error("Error fetching static data:", error);
      }
    },
    
    /**
     * Get current active tab
     */
    getOpenTab() {
      try {
        // Try to get from Alpine store if available
        if (window.Alpine && window.Alpine.store && window.Alpine.store('openTab')) {
          return window.Alpine.store('openTab');
        }
        
        // If we don't have a stored value, use a local property
        return this.activeTab || 1;
      } catch (e) {
        console.error("Error determining active tab:", e);
        return 1; // Default to tab 1 on error
      }
    },
    
    /**
     * Switch to a different tab and load its data
     */
    switchTab(tabIndex) {
  // Store the active tab
  this.activeTab = tabIndex;
  
  // Update Alpine store
  if (window.Alpine && window.Alpine.store) {
    try {
      window.Alpine.store('openTab', tabIndex);
    } catch (e) {
      console.warn('Unable to set active tab in Alpine store:', e);
    }
  }
  
  // Load appropriate data based on tab
  if (tabIndex === 1) {
    // Clear other arrays first to avoid display issues
    this.causes = [];
    this.christenings = [];
    
    // Weekly tab
    this.fetchData('Weekly');
  } else if (tabIndex === 2) {
    // Clear other arrays first to avoid display issues
    this.causes = [];
    this.christenings = [];
    
    // General tab
    this.fetchData('General');
  } else if (tabIndex === 3) {
    // Clear other arrays first to avoid display issues
    this.bills = [];
    this.christenings = [];
    
    // Deaths tab
    this.fetchDeaths();
  } else if (tabIndex === 4) {
    // Clear other arrays first to avoid display issues
    this.bills = [];
    this.causes = [];
    
    // Christenings tab
    this.fetchChristenings();
  }
  
  // Update URL with the current tab
  this.updateUrl();
},
         
    /**
     * Fetch bills data
     */
    async fetchData(billType) {
      console.log("Fetching " + billType + " bills data...");
      this.meta.loading = true;
      this.meta.fetching = true;
      
      try {
        // Calculate offset based on current page and page size
        const offset = (this.page - 1) * this.pageSize;
        
        // Prepare direct params for API call
        const params = {
          'bill-type': billType || this.filters.selectedBillType,
          'start-year': this.filters.selectedStartYear,
          'end-year': this.filters.selectedEndYear,
          'count-type': this.filters.selectedCountType,
          'limit': this.pageSize,
          'offset': offset
        };
        
        // Add parish filter if selected
        if (this.filters.selectedParishes && this.filters.selectedParishes.length > 0) {
          params.parish = this.filters.selectedParishes.join(',');
        }
        
        // Fetch data
        const data = await window.DataService.fetchData('bills', params);
        
        // Process data
        data.forEach(function(d, i) {
          d.id = i;
        });
        
        // Update state
        this.bills = data;
        
        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
        
        // Prefetch parish yearly data for charts if we have bills
        if (data.length > 0) {
          this.prefetchParishYearlyData(data);
        }
        
        // Update URL after data is loaded
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching bills data:", error);
        this.bills = [];
        this.messages.loading = this.messages.noResults;
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    /**
     * Prefetch parish yearly data for charts
     */
    async prefetchParishYearlyData(bills) {
      try {
        // Get unique parish names from current bills
        const uniqueParishes = [];
        for (const bill of bills) {
          if (bill.name && !uniqueParishes.includes(bill.name)) {
            uniqueParishes.push(bill.name);
          }
        }
        
        // Fetch data for each parish if not already in cache
        for (const parish of uniqueParishes) {
          if (!this.parishYearlyData[parish]) {
            await this.fetchParishYearlyForSingle(parish);
          }
        }
      } catch (error) {
        console.error("Error prefetching parish yearly data:", error);
      }
    },
    
    /**
     * Fetch yearly data for a single parish
     */
    async fetchParishYearlyForSingle(parishName) {
      if (!parishName) return null;
      
      try {
        const data = await window.DataService.fetchParishYearly(parishName);
        
        // Cache the data
        this.parishYearlyData[parishName] = data;
        
        return data;
      } catch (error) {
        console.error("Error fetching yearly data for parish " + parishName + ":", error);
        return null;
      }
    },
    
    /**
     * Fetch yearly parish data
     */
    async fetchParishYearly() {
      try {
        this.meta.loading = true;
        this.meta.fetching = true;
        
        // For the dedicated tab, we'll get data for all selected parishes
        // or a default set if none selected
        const parishes = this.filters.selectedParishes.length > 0 
          ? this.filters.selectedParishes 
          : (this.parishes && this.parishes.length > 0 
              ? this.parishes.slice(0, 10).map(function(p) { return p.canonical_name; }) 
              : []);
        
        let allData = [];
        
        // Fetch data for each parish
        for (const parish of parishes) {
          const data = await this.fetchParishYearlyForSingle(parish);
          if (data) {
            allData = allData.concat(data);
          }
        }
        
        // Store the combined data
        this.parishYearlyData.combined = allData;
        
        // Update pagination for the combined data
        this.pagination.total = allData.length;
        this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        
      } catch (error) {
        console.error("Error fetching parish yearly data:", error);
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    /**
     * Fetch causes of death data
     */
    async fetchDeaths() {
      console.log("Fetching death causes data...");
      this.meta.loading = true;
      this.meta.fetching = true;
      
      try {
        // Calculate offset based on page
        const offset = (this.page - 1) * this.pageSize;
        
        // Prepare params for API
        const params = {
          'start-year': this.filters.selectedStartYear,
          'end-year': this.filters.selectedEndYear,
          'limit': this.pageSize,
          'offset': offset
        };
        
        // Add death causes filter if selected
        if (this.filters.selectedCausesOfDeath && this.filters.selectedCausesOfDeath.length > 0) {
          params.id = this.filters.selectedCausesOfDeath.join(',');
        }
        
        // Fetch data
        const data = await window.DataService.fetchData('causes', params);
        
        // Process data
        data.forEach(function(d, i) {
          d.id = i;
        });
        
        // Update state
        this.causes = data;
        
        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
        
        // Update URL
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching deaths data:", error);
        this.causes = [];
        this.messages.loading = this.messages.noResults;
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    /**
     * Fetch christenings data
     */
    async fetchChristenings() {
      console.log("Fetching christenings data...");
      this.meta.loading = true;
      this.meta.fetching = true;
      
      try {
        // Calculate offset based on page
        const offset = (this.page - 1) * this.pageSize;
        
        // Prepare params for API
        const params = {
          'start-year': this.filters.selectedStartYear,
          'end-year': this.filters.selectedEndYear,
          'limit': this.pageSize,
          'offset': offset
        };
        
        // Add selected christenings if any
        if (this.filters.selectedChristenings && this.filters.selectedChristenings.length > 0) {
          params.id = this.filters.selectedChristenings.join(',');
        }
        
        // Fetch data
        const data = await window.DataService.fetchData('christenings', params);
        
        // Process data
        data.forEach(function(d, i) {
          d.id = i;
        });
        
        // Update state
        this.christenings = data;
        
        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
        
        // Update URL
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching christenings:", error);
        this.christenings = [];
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    /**
     * Set items per page limit
     */
    setLimit() {
      this.pageSize = parseInt(this.server.limit);
      this.pagination.pageSize = this.pageSize;
      this.updatePageSize();
    },
    
    /**
     * Change page in pagination
     */
    changePage(page) {
      if (page < 1 || page > this.pagination.lastPage) {
        return;
      }
      
      this.page = page;
      this.pagination.page = page;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      
      // Set a loading state
      this.meta.loading = true;
      
      // Fetch new data for the page
      if (currentTab === 1) {
        this.fetchData('Weekly');
      } else if (currentTab === 2) {
        this.fetchData('General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
    /**
     * Sort data by column
     */
    sort(col) {
      // Initialize sort column if not set
      if (!this.sortCol) {
        this.sortCol = col;
        this.sort = false;
      } else if (this.sortCol === col) {
        // Toggle sort direction
        this.sort = !this.sort;
      } else {
        // Change sort column
        this.sortCol = col;
        this.sort = false;
      }
      
      // Create a copy to avoid modifying the original reference
      let dataToSort = [];
      
      // Determine which data array to sort based on active tab
      const currentTab = this.getOpenTab();
      if (currentTab === 1 || currentTab === 2) {
        dataToSort = this.bills.slice();
      } else if (currentTab === 3) {
        dataToSort = this.causes.slice();
      } else if (currentTab === 4) {
        dataToSort = this.christenings.slice();
      } else if (currentTab === 5) {
        dataToSort = this.parishYearlyData.combined 
          ? this.parishYearlyData.combined.slice()
          : [];
      }
      
      const sortedData = dataToSort.sort((a, b) => {
        const aVal = a[this.sortCol];
        const bVal = b[this.sortCol];
        
        // Handle null/undefined values
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return this.sort ? -1 : 1;
        if (bVal == null) return this.sort ? 1 : -1;
        
        // Sort based on data type
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return this.sort ? 
            bVal.localeCompare(aVal) : 
            aVal.localeCompare(bVal);
        }
        
        return this.sort ? 
          bVal - aVal : 
          aVal - bVal;
      });
      
      // Update the appropriate data array
      if (currentTab === 1 || currentTab === 2) {
        this.bills = sortedData;
      } else if (currentTab === 3) {
        this.causes = sortedData;
      } else if (currentTab === 4) {
        this.christenings = sortedData;
      } else if (currentTab === 5) {
        this.parishYearlyData.combined = sortedData;
      }
    },
    
    /**
     * Apply filters and fetch data
     */
    applyFilters() {
      // Reset pagination to first page when applying new filters
      this.page = 1;
      this.pagination.page = 1;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1) {
        this.fetchData('Weekly');
      } else if (currentTab === 2) {
        this.fetchData('General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      }
    },
    
    /**
     * Update page size and refetch data
     *      /
    updatePageSize() {
      // Update page size and refetch data
      this.pageSize = parseInt(this.pageSize);
      this.pagination.pageSize = this.pageSize;
      
      if (isNaN(this.pageSize) || this.pageSize < 10) {
        this.pageSize = 25;
        this.pagination.pageSize = 25;
      } else if (this.pageSize > 100) {
        this.pageSize = 100;
        this.pagination.pageSize = 100;
      }
      
      // Reset to first page when changing page size
      this.page = 1;
      this.pagination.page = 1;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1) {
        this.fetchData('Weekly');
      } else if (currentTab === 2) {
        this.fetchData('General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
    /**
     * Reset filters to default values
     */
    resetFilters() {
      // Restore defaults
      this.filters.selectedStartYear = 1636;
      this.filters.selectedEndYear = 1754;
      this.filters.selectedCountType = "";
      this.filters.selectedBillType = "Weekly";
      this.filters.selectedParishes = [];
      this.filters.selectedCausesOfDeath = [];
      this.filters.selectedChristenings = [];
      
      // Reset pagination
      this.page = 1;
      this.pagination.page = 1;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1) {
        this.fetchData('Weekly');
      } else if (currentTab === 2) {
        this.fetchData('General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
    /**
     * Set the start year for filtering
     */
    setStartYear() {
      // Validate input
      const year = parseInt(this.filters.selectedStartYear);
      if (isNaN(year)) {
        this.filters.selectedStartYear = 1636;
      } else if (year < 1636) {
        this.filters.selectedStartYear = 1636;
      } else if (year > 1754) {
        this.filters.selectedStartYear = 1754;
      }
      
      // Ensure start year is not after end year
      if (parseInt(this.filters.selectedStartYear) > parseInt(this.filters.selectedEndYear)) {
        this.filters.selectedEndYear = this.filters.selectedStartYear;
      }
    },
    
    /**
     * Set the end year for filtering
     */
    setEndYear() {
      // Validate input
      const year = parseInt(this.filters.selectedEndYear);
      if (isNaN(year)) {
        this.filters.selectedEndYear = 1754;
      } else if (year < 1636) {
        this.filters.selectedEndYear = 1636;
      } else if (year > 1754) {
        this.filters.selectedEndYear = 1754;
      }
      
      // Ensure end year is not before start year
      if (parseInt(this.filters.selectedEndYear) < parseInt(this.filters.selectedStartYear)) {
        this.filters.selectedStartYear = this.filters.selectedEndYear;
      }
    },
    
    /**
     * Set the count type for filtering
     */
    setCountType() {
      // This function is needed for the filter to work with count type selections
      console.log('Count type set to:', this.filters.selectedCountType);
    },
    
    /**
     * Get first row index displayed on current page
     */
    getFirstDisplayedRow() {
      if (this.pagination.total === 0) return 0;
      return (this.page - 1) * this.pageSize + 1;
    },
    
    /**
     * Get last row index displayed on current page
     */
    getLastDisplayedRow() {
      const lastItem = this.page * this.pageSize;
      return Math.min(lastItem, this.pagination.total);
    },
    
    /**
     * Go to first page in pagination
     */
    goToFirstPage() {
      this.changePage(1);
    },
    
    /**
     * Go to last page in pagination
     */
    goToLastPage() {
      this.changePage(this.pagination.lastPage);
    },
    
    /**
     * Get summary text for pagination
     */
    getSummary(type) {
      // If data is loading, show loading message
      if (this.meta.loading) {
        return this.messages.loading;
      }
      
      // Handle different summary types
      if (type && type.toLowerCase() === "pages") {
        return "Showing page <strong>" + this.page + "</strong> of <strong>" + this.pagination.lastPage + "</strong>";
      }
      
      // Handle empty results
      if (this.pagination.total === 0) {
        return this.messages.noResults;
      }
      
      // Show row count summary
      return "Showing <strong>" + this.getFirstDisplayedRow() + "</strong> to <strong>" + this.getLastDisplayedRow() + "</strong> of <strong>" + this.pagination.total + "</strong> records";
    },
    
    /**
     * Update URL with current state
     */
    updateUrl() {
      // Create URL with current filter state
      const params = new URLSearchParams();
      
      params.set("start-year", this.filters.selectedStartYear);
      params.set("end-year", this.filters.selectedEndYear);
      if (this.filters.selectedCountType) {
        params.set("count-type", this.filters.selectedCountType);
      }
      if (this.filters.selectedParishes.length > 0) {
        params.set("parish", this.filters.selectedParishes.join(","));
      }
      params.set("page", this.page);
      params.set("bill-type", this.filters.selectedBillType);
      
      // Add tab to URL
      params.set("tab", this.getOpenTab());
      
      // Use the history API to update the URL without reloading
      history.pushState({}, "", location.pathname + "?" + params.toString());
    },
    
    /**
     * Open modal with chart
     */
    openModal(bill) {
      this.modalBill = bill;
      this.modalOpen = true;
      
      // Initialize chart only after modal is open and we have data
      this.$nextTick(() => {
        if (bill && bill.name) {
          this.initModalChart(bill.name);
        }
      });
    },
    
    /**
     * Initialize modal chart
     */
    initModalChart(parishName) {
      if (!parishName) {
        console.error("No parish name provided for chart initialization");
        return;
      }
      
      // Use IDs to ensure we get the right elements
      const chartContainer = document.getElementById('modal-chart-container');
      const loadingIndicator = document.getElementById('modal-loading-indicator');
      const errorMessage = document.getElementById('modal-error-message');
      
      if (!chartContainer) {
        console.error("Chart container not found");
        return;
      }
      
      // Show loading state
      if (loadingIndicator) loadingIndicator.style.display = 'block';
      if (errorMessage) {
        errorMessage.style.display = 'none';
        errorMessage.classList.add('hidden');
      }
      
      // Use ChartService to load the chart
      if (window.ChartService) {
        window.ChartService.loadPlotLibrary()
          .then(() => {
            // Get data from cache if available, otherwise fetch
            if (this.parishYearlyData[parishName]) {
              return this.parishYearlyData[parishName];
            } else {
              return window.DataService.fetchParishYearly(parishName)
                .then(data => {
                  this.parishYearlyData[parishName] = data;
                  return data;
                });
            }
          })
          .then(data => {
            // Use ChartService to render the chart
            window.ChartService.createModalDetailChart(chartContainer, data);
            
            // Hide loading indicator
            if (loadingIndicator) loadingIndicator.style.display = 'none';
          })
          .catch(error => {
            console.error('Chart error:', error);
            
            // Show error message
            if (errorMessage) {
              errorMessage.textContent = error.message || 'Error loading chart data';
              errorMessage.style.display = 'block';
              errorMessage.classList.remove('hidden');
            }
            
            // Hide loading indicator
            if (loadingIndicator) loadingIndicator.style.display = 'none';
          });
      } else {
        console.error("ChartService not available");
      }
    },
    
    /**
     * Close the modal
     */
    closeModal() {
      this.modalOpen = false;
    },
    
    /**
     * Toggle instructions visibility
     */
    toggleInstructions() {
      this.instructionsOpen = !this.instructionsOpen;
    },
    
    /**
     * Validate year input values
     */
    validateYearInput() {
      // Ensure years are integers within valid range
      const startYear = parseInt(this.filters.selectedStartYear);
      const endYear = parseInt(this.filters.selectedEndYear);
      
      if (isNaN(startYear) || startYear < 1636) {
        this.filters.selectedStartYear = 1636;
      }
      
      if (isNaN(endYear) || endYear > 1754) {
        this.filters.selectedEndYear = 1754;
      }
      
      // Ensure start year is before end year
      if (startYear > endYear) {
        this.filters.selectedEndYear = startYear;
      }
    },
    
    /**
     * Get chart data for a parish
     */
    getParishChartData(parishName) {
      return this.parishYearlyData[parishName] || [];
    },

  /**
  * Start dragging a slider handle
  * @param {Event} event - Mouse or touch event
  * @param {string} handle - Which handle is being dragged ('start' or 'end')
  */
  startDrag(event, handle) {
    // Set the current handle being dragged
    this.dragging = handle;
    
    // Prevent text selection during drag
    event.preventDefault();
    
    // Get the slider track element
    const track = event.target.parentElement;
    
    // Calculate initial position
    const updatePosition = (e) => {
      // Get event position (support both mouse and touch)
      const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
      
      // Calculate position relative to the track
      const rect = track.getBoundingClientRect();
      const position = (clientX - rect.left) / rect.width;
      
      // Convert position to year value
      const minYear = 1636;
      const maxYear = 1754;
      const range = maxYear - minYear;
      
      // Calculate the new year based on position
      let newYear = Math.round(minYear + (position * range));
      
      // Clamp the year to valid range
      newYear = Math.max(minYear, Math.min(maxYear, newYear));
      
      // Update the appropriate year based on which handle is being dragged
      if (this.dragging === 'start') {
        // Ensure start year doesn't exceed end year
        this.filters.selectedStartYear = Math.min(newYear, this.filters.selectedEndYear);
      } else if (this.dragging === 'end') {
        // Ensure end year doesn't go below start year
        this.filters.selectedEndYear = Math.max(newYear, this.filters.selectedStartYear);
      }
    };
    
    // Handle the initial position
    updatePosition(event);
    
    // Set up event listeners for dragging
    const moveHandler = (e) => updatePosition(e);
    const endHandler = () => {
      // Clear dragging state
      this.dragging = null;
      
      // Remove event listeners
      window.removeEventListener('mousemove', moveHandler);
      window.removeEventListener('touchmove', moveHandler);
      window.removeEventListener('mouseup', endHandler);
      window.removeEventListener('touchend', endHandler);
      
      // Validate the selected years
      this.validateYearInput();
    };
    
    // Add event listeners
    window.addEventListener('mousemove', moveHandler);
    window.addEventListener('touchmove', moveHandler);
    window.addEventListener('mouseup', endHandler);
    window.addEventListener('touchend', endHandler);
  }  
}));
})
