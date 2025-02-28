document.addEventListener("alpine:init", () => {
  Alpine.data("billsData", () => ({
    bills: [],
    christenings: [],
    causes: [],
    parishYearlyData: {},
    all_causes: [],
    all_christenings: [],
    parishes: null,
    sort: false,
    modalOpen: false,
    instructionsOpen: false,
    modalBill: [],
    disabled: false,
    filters: {
      selectedParishes: [],
      selectedBillType: "Weekly",
      selectedCountType: "",
      selectedStartYear: 1636,
      selectedEndYear: 1754,
      selectedCausesOfDeath: [],
      selectedChristenings: [],
    },
    isMissing: false,
    isIllegible: false,
    messages: {
      loading: "Loading data...",
      error: "Error loading data. Please try again.",
      noResults: "No data available. Please try different filters.",
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
      total: 0,
      lastPage: 1,
      page: 1, 
      pageSize: 25, 
      pageOffset: 25, 
    },
    
    init() {
      // Parse URL parameters
      this.parseURLParams();
      
      // Initialize data
      this.fetchStaticData()
        .then(() => {
          this.fetchAllData();
        });
    },
    
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
    
    async fetchStaticData() {
      try {
        // Fetch parishes data
        const parishesResponse = await fetch("https://data.chnm.org/bom/parishes");
        if (!parishesResponse.ok) throw new Error("Failed to fetch parishes");
        this.parishes = await parishesResponse.json();
        
        // Fetch causes of death data
        const causesResponse = await fetch("https://data.chnm.org/bom/list-deaths");
        if (!causesResponse.ok) throw new Error("Failed to fetch causes of death");
        this.all_causes = await causesResponse.json();
        this.all_causes.forEach((d, i) => (d.id = i));
        
        // Fetch christenings data
        const christeningsResponse = await fetch("https://data.chnm.org/bom/list-christenings");
        if (!christeningsResponse.ok) throw new Error("Failed to fetch christenings");
        this.all_christenings = await christeningsResponse.json();
      } catch (error) {
        console.error("Error fetching static data:", error);
      }
    },
    
    async fetchAllData() {
      // Set loading state
      this.meta.loading = true;
      this.meta.fetching = true;
      
      try {
        // Calculate offset based on page
        this.server.offset = (this.page - 1) * this.pageSize;
        this.server.limit = this.pageSize;
        const offset = this.server.offset;
        
        // Get current tab from Alpine's state or DOM
        const currentTab = this.getOpenTab();
        
        // Fetch appropriate data based on current tab
        if (currentTab === 1 || currentTab === 2) {
          await this.fetchData(currentTab === 1 ? 'Weekly' : 'General');
        } else if (currentTab === 3) {
          await this.fetchDeaths();
        } else if (currentTab === 4) {
          await this.fetchChristenings();
        } else if (currentTab === 5) { // New tab for Yearly Parish Data
          await this.fetchParishYearly();
        }
        
        // Update URL after data is loaded
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    // Fixed getOpenTab function
    getOpenTab() {
      try {
        // Try to get from Alpine store if available
        if (window.Alpine && window.Alpine.store && window.Alpine.store('openTab')) {
          return window.Alpine.store('openTab');
        }
        
        // Fallback to reading from the DOM
        const tabElement = document.querySelector('[x-data*="openTab"]');
        if (tabElement) {
          // Read the state from Alpine's internal state tracker
          const alpineData = tabElement.__x && tabElement.__x.getUnobservedData 
            ? tabElement.__x.getUnobservedData() 
            : null;
            
          if (alpineData && typeof alpineData.openTab === 'number') {
            return alpineData.openTab;
          }
          
          // If unable to get from Alpine, parse the x-data attribute
          const xData = tabElement.getAttribute('x-data');
          const match = xData && xData.match(/openTab:\s*(\d+)/);
          if (match && match[1]) {
            return parseInt(match[1]);
          }
        }
        
        // Check for active tab marker in the DOM
        const activeTab = document.querySelector('[aria-selected="true"]');
        if (activeTab && activeTab.id) {
          if (activeTab.id === 'tab-weekly') return 1;
          if (activeTab.id === 'tab-general') return 2;
          if (activeTab.id === 'tab-deaths') return 3;
          if (activeTab.id === 'tab-christenings') return 4;
          if (activeTab.id === 'tab-parish-yearly') return 5;
        }
        
        return 1; // Default to tab 1
      } catch (e) {
        console.error("Error determining active tab:", e);
        return 1; // Default to tab 1 on error
      }
    },
    
    // This matches the function name used in the template
    async fetchData(billType) {
      try {
        this.meta.loading = true;
        this.meta.fetching = true;
        
        const url = new URL("https://data.chnm.org/bom/bills");
        
        // Add query parameters
        url.searchParams.append("start-year", this.filters.selectedStartYear);
        url.searchParams.append("end-year", this.filters.selectedEndYear);
        url.searchParams.append("bill-type", billType || this.filters.selectedBillType);
        url.searchParams.append("count-type", this.filters.selectedCountType);
        if (this.filters.selectedParishes.length > 0) {
          url.searchParams.append("parish", this.filters.selectedParishes.join(","));
        }
        url.searchParams.append("limit", this.pageSize);
        url.searchParams.append("offset", this.server.offset);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        // Process data
        data.forEach((d, i) => (d.id = i));
        this.bills = data;
        
        // After loading bills, prefetch yearly data for each parish
        if (data.length > 0) {
          this.prefetchParishYearlyData(data);
        }
        
        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
      } catch (error) {
        console.error("Error fetching bills data:", error);
        this.bills = [];
        this.messages.loading = this.messages.noResults;
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    // Prefetch parish yearly data for displayed parishes
    async prefetchParishYearlyData(bills) {
      try {
        // Get unique parish names from current bills
        const uniqueParishes = [...new Set(bills.map(bill => bill.name))];
        
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
    
    // Fetch yearly data for a single parish
    async fetchParishYearlyForSingle(parishName) {
      if (!parishName) return null;
      
      try {
        const url = new URL("https://data.chnm.org/bom/statistics?type=parish-yearly");
        url.searchParams.append("parish", parishName);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        
        // Cache the data
        this.parishYearlyData[parishName] = data;
        
        return data;
      } catch (error) {
        console.error(`Error fetching yearly data for parish ${parishName}:`, error);
        return null;
      }
    },
    
    // New method to fetch parish yearly data for the dedicated tab
    async fetchParishYearly() {
      try {
        this.meta.loading = true;
        this.meta.fetching = true;
        
        // For the dedicated tab, we'll get data for all selected parishes
        // or a default set if none selected
        const parishes = this.filters.selectedParishes.length > 0 
          ? this.filters.selectedParishes 
          : (this.parishes && this.parishes.length > 0 
              ? this.parishes.slice(0, 10).map(p => p.canonical_name) 
              : []);
        
        let allData = [];
        
        // Fetch data for each parish
        for (const parish of parishes) {
          const data = await this.fetchParishYearlyForSingle(parish);
          if (data) {
            allData = [...allData, ...data];
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
    
    async fetchChristenings() {
      if (this.meta.fetching) {
        return;
      }
      
      this.meta.loading = true;
      this.meta.fetching = true;
      
      try {
        // Calculate offset based on page
        const offset = (this.page - 1) * this.pageSize;
        
        const url = new URL("https://data.chnm.org/bom/christenings");
        
        // Add query parameters
        url.searchParams.append("start-year", this.filters.selectedStartYear);
        url.searchParams.append("end-year", this.filters.selectedEndYear);
        if (this.filters.selectedChristenings.length > 0) {
          url.searchParams.append("id", this.filters.selectedChristenings.join(","));
        }
        url.searchParams.append("limit", this.pageSize);
        url.searchParams.append("offset", offset);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        // Process data
        data.forEach((d, i) => (d.id = i));
        this.christenings = data;
        
        // Update pagination if data has totalrecords
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
        
        // Update URL after data is loaded
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching christenings data:", error);
        this.christenings = [];
        this.messages.loading = this.messages.noResults;
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    async fetchDeaths() {
      try {
        this.meta.loading = true;
        this.meta.fetching = true;
        
        const url = new URL("https://data.chnm.org/bom/causes");
        
        // Add query parameters
        url.searchParams.append("start-year", this.filters.selectedStartYear);
        url.searchParams.append("end-year", this.filters.selectedEndYear);
        if (this.filters.selectedCausesOfDeath.length > 0) {
          url.searchParams.append("id", this.filters.selectedCausesOfDeath.join(","));
        }
        url.searchParams.append("limit", this.pageSize);
        url.searchParams.append("offset", this.server.offset);
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        // Process data
        data.forEach((d, i) => (d.id = i));
        this.causes = data;
        
        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }
      } catch (error) {
        console.error("Error fetching deaths data:", error);
        this.causes = [];
        this.messages.loading = this.messages.noResults;
      } finally {
        this.meta.loading = false;
        this.meta.fetching = false;
      }
    },
    
    // Added setLimit function that was missing
    setLimit() {
      this.pageSize = parseInt(this.server.limit);
      this.pagination.pageSize = this.pageSize;
      this.updatePageSize();
    },
    
    changePage(page) {
      if (page < 1 || page > this.pagination.lastPage) {
        return;
      }
      
      this.page = page;
      this.pagination.page = page;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1 || currentTab === 2) {
        this.fetchData(currentTab === 1 ? 'Weekly' : 'General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
    sortData(col) {
      if (this.sortCol === col) {
        this.sort = !this.sort;
      } else {
        this.sortCol = col;
        this.sort = false;
      }
      
      // Create a copy to avoid modifying the original reference
      let dataToSort = [];
      
      // Determine which data array to sort based on active tab
      const currentTab = this.getOpenTab();
      if (currentTab === 1 || currentTab === 2) {
        dataToSort = [...this.bills];
      } else if (currentTab === 3) {
        dataToSort = [...this.causes];
      } else if (currentTab === 4) {
        dataToSort = [...this.christenings];
      } else if (currentTab === 5) {
        dataToSort = this.parishYearlyData.combined 
          ? [...this.parishYearlyData.combined]
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
    
    applyFilters() {
      // Reset pagination to first page when applying new filters
      this.page = 1;
      this.pagination.page = 1;
      
      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1 || currentTab === 2) {
        this.fetchData(currentTab === 1 ? 'Weekly' : 'General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
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
      if (currentTab === 1 || currentTab === 2) {
        this.fetchData(currentTab === 1 ? 'Weekly' : 'General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
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
      if (currentTab === 1 || currentTab === 2) {
        this.fetchData(currentTab === 1 ? 'Weekly' : 'General');
      } else if (currentTab === 3) {
        this.fetchDeaths();
      } else if (currentTab === 4) {
        this.fetchChristenings();
      } else if (currentTab === 5) {
        this.fetchParishYearly();
      }
    },
    
    getFirstDisplayedRow() {
      if (this.pagination.total === 0) return 0;
      return (this.page - 1) * this.pageSize + 1;
    },
    
    getLastDisplayedRow() {
      const lastItem = this.page * this.pageSize;
      return Math.min(lastItem, this.pagination.total);
    },
    
    goToFirstPage() {
      this.changePage(1);
    },
    
    goToLastPage() {
      this.changePage(this.pagination.lastPage);
    },
    
    getSummary(type = "bills") {
      // If data is loading, show loading message
      if (this.meta.loading) {
        return this.messages.loading;
      }
      
      // Handle different summary types
      if (type.toLowerCase() === "pages") {
        return `Showing page <strong>${this.page}</strong> of <strong>${this.pagination.lastPage}</strong>`;
      }
      
      // Handle empty results
      if (this.pagination.total === 0) {
        return this.messages.noResults;
      }
      
      // Show row count summary
      return `Showing <strong>${this.getFirstDisplayedRow()}</strong> to <strong>${this.getLastDisplayedRow()}</strong> of <strong>${this.pagination.total}</strong> records`;
    },
    
    updateUrl() {
      // Create URL with current filter state
      const url = new URL(window.location.href);
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
      history.pushState({}, "", `${location.pathname}?${params}`);
    },
    
    // Modal handling
    toggleInstructions() {
      this.instructionsOpen = !this.instructionsOpen;
    },
    
    openModal(bill) {
      this.modalBill = bill;
      this.modalOpen = true;
    },
    
    closeModal() {
      this.modalOpen = false;
    },
    
    // Debounced search implementation
    debounce(func, wait = 300) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },
    
    // Handle input validation
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
    
    // Helper to get the chart data for a parish
    getParishChartData(parishName) {
      return this.parishYearlyData[parishName] || [];
    }
  }));
});

