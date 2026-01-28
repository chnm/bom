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
    deathYearlyData: {},
    christeningYearlyData: {},

    // Tab state - Two-tiered system
    primaryTab: "annual", // annual, yearly, bread-death
    secondaryTab: "parishes", // parishes, deaths, christenings, foodstuffs, ages
    activeTab: 1, // Legacy support
    dragging: null,
    weekDragging: null,

    // UI state
    modalOpen: false,
    instructionsOpen: false,
    filtersOpen: false,
    modalBill: [],
    disabled: false,
    isMissing: false,
    isIllegible: false,
    initialized: false,
    initializationStage: "starting",

    // Filter state
    filters: {
      selectedParishes: [],
      selectedBillType: "weekly",
      selectedCountType: "",
      selectedStartYear: 1629,
      selectedEndYear: 1754,
      selectedStartWeek: 1,
      selectedEndWeek: 56,
      selectedCausesOfDeath: [],
      selectedChristenings: [],
      showIllegibleOnly: false,
    },

    // Status messages
    messages: {
      loading: "Loading data...",
      error: "Error loading data. Please try again.",
      noResults: "No data available. Please try different filters.",
      slowConnection: "Data is taking longer than usual to load...",
      connectionError: "Unable to load data. There may be a server issue.",
    },

    // Loading state
    meta: {
      loading: false,
      fetching: false,
      error: null,
      slowConnection: false,
      connectionTimeout: null,
    },

    // Pagination state
    page: 1,
    pageSize: 100,
    server: {
      limit: 100,
      offset: 0,
    },
    pagination: {
      total: 0,
      lastPage: 1,
      page: 1,
      pageSize: 100,
      pageOffset: 100,
      cursor: null,
      hasMore: false,
      cursors: [], // Stack of cursors for each page
      useCursor: true, // Flag to enable cursor-based pagination
    },

    /**
     * Initialize the component with progressive loading
     */
    init() {
      console.log("Initializing Bills of Mortality application");

      // Start with a lightweight initialization
      this.initializationStage = "parsing";
      this.parseURLParams();

      // Use requestAnimationFrame to defer heavy initialization
      requestAnimationFrame(() => {
        this.initializeAsync();
      });
    },

    /**
     * Async initialization to prevent blocking
     */
    async initializeAsync() {
      try {
        this.initializationStage = "loading_static";

        // Initialize static data with timeout
        const staticDataPromise = this.fetchStaticData();
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(
            () => reject(new Error("Static data loading timeout")),
            10000,
          );
        });

        await Promise.race([staticDataPromise, timeoutPromise]);

        this.initializationStage = "setting_up";

        // Get the initial tab from URL or default to tab 1
        const urlParams = window.URLService
          ? window.URLService.getParams()
          : {};
        const initialTab = urlParams.tab || 1;
        this.activeTab = initialTab;

        console.log("Initial tab is " + initialTab);

        // Set Alpine store if available
        if (window.Alpine && window.Alpine.store) {
          try {
            window.Alpine.store("openTab", initialTab);
          } catch (e) {
            console.warn("Unable to set active tab in Alpine store:", e);
          }
        }

        this.initializationStage = "ready";
        this.initialized = true;

        // Load data for the initial tab with a small delay
        setTimeout(() => {
          this.loadTabData();
        }, 100);

        // Listen for history navigation
        window.addEventListener("popstate", () => {
          if (this.initialized) {
            this.parseURLParams();
            this.loadTabData();
          }
        });
      } catch (error) {
        console.error("Initialization failed:", error);
        this.initializationStage = "error";
        this.meta.error =
          "Failed to initialize application. Please refresh the page.";
      }
    },

    /**
     * Parse URL parameters and update state
     */
    parseURLParams() {
      const params = new URLSearchParams(window.location.search);

      // Handle two-tiered tab system
      if (params.has("primary-tab")) {
        const primaryTab = params.get("primary-tab");
        if (["annual", "yearly", "bread-death"].includes(primaryTab)) {
          this.primaryTab = primaryTab;
        }
      }

      if (params.has("secondary-tab")) {
        const secondaryTab = params.get("secondary-tab");
        if (["parishes", "deaths", "christenings", "foodstuffs", "ages"].includes(secondaryTab)) {
          this.secondaryTab = secondaryTab;
        }
      }

      // Legacy tab support - convert old tab numbers to new system
      if (params.has("tab")) {
        const tabNum = parseInt(params.get("tab"));
        switch (tabNum) {
          case 1:
            this.primaryTab = "annual";
            this.secondaryTab = "parishes";
            break;
          case 2:
            this.primaryTab = "yearly";
            this.secondaryTab = "parishes";
            break;
          case 3:
            this.primaryTab = "annual";
            this.secondaryTab = "deaths";
            break;
          case 4:
            this.primaryTab = "annual";
            this.secondaryTab = "christenings";
            break;
        }
        this.activeTab = tabNum; // Keep legacy support
      }

      if (params.has("start-year"))
        this.filters.selectedStartYear = parseInt(params.get("start-year"));
      if (params.has("end-year"))
        this.filters.selectedEndYear = parseInt(params.get("end-year"));
      if (params.has("start-week"))
        this.filters.selectedStartWeek = parseInt(params.get("start-week"));
      if (params.has("end-week"))
        this.filters.selectedEndWeek = parseInt(params.get("end-week"));
      if (params.has("count-type"))
        this.filters.selectedCountType = params.get("count-type");
      if (params.has("parish")) {
        const parishParam = params.get("parish");
        if (parishParam) {
          const parishes = parishParam.split(",");
          this.filters.selectedParishes = parishes.filter(
            (p) => p.trim() !== "",
          );
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
        if (["weekly", "general", "total"].includes(billType)) {
          this.filters.selectedBillType = billType;
        }
      }
    },

    /**
     * Fetch static data for filters with optimized loading
     */
    async fetchStaticData() {
      try {
        // Fetch parishes first
        const parishes = await window.DataService.fetchParishes();
        this.parishes = parishes;

        // Fetch causes and christenings for the current bill type
        await this.fetchCausesAndChristeningsForBillType();

        console.log("Static data loaded successfully");
      } catch (error) {
        console.error("Error fetching static data:", error);
        throw error; // Re-throw to be caught by initialization
      }
    },

    /**
     * Fetch causes and christenings filtered by current bill type
     */
    async fetchCausesAndChristeningsForBillType() {
      try {
        const billType = this.filters.selectedBillType;

        // Fetch causes and christenings in parallel for the current bill type
        const [causes, christenings] = await Promise.all([
          window.DataService.fetchAllCauses(billType),
          window.DataService.fetchAllChristenings(billType),
        ]);

        // Process causes with IDs
        this.all_causes = causes;
        this.all_causes.forEach(function (d, i) {
          d.id = i;
        });

        // Process christenings
        this.all_christenings = christenings;

        // Clear selected filters if they're no longer valid for this bill type
        const validCauseNames = new Set(causes.map(c => c.name));
        this.filters.selectedCausesOfDeath = this.filters.selectedCausesOfDeath.filter(
          name => validCauseNames.has(name)
        );

        const validChristeningIds = new Set(christenings.map(c => c.id));
        this.filters.selectedChristenings = this.filters.selectedChristenings.filter(
          id => validChristeningIds.has(id)
        );

        console.log(`Loaded ${causes.length} causes and ${christenings.length} christenings for bill type: ${billType}`);
      } catch (error) {
        console.error("Error fetching causes and christenings:", error);
      }
    },

    /**
     * Get current active tab (legacy support)
     */
    getOpenTab() {
      try {
        // Try to get from Alpine store if available
        if (
          window.Alpine &&
          window.Alpine.store &&
          window.Alpine.store("openTab")
        ) {
          return window.Alpine.store("openTab");
        }

        // If we don't have a stored value, use a local property
        return this.activeTab || 1;
      } catch (e) {
        console.error("Error determining active tab:", e);
        return 1; // Default to tab 1 on error
      }
    },

    /**
     * Get current primary tab
     */
    getPrimaryTab() {
      return this.primaryTab;
    },

    /**
     * Get current secondary tab
     */
    getSecondaryTab() {
      return this.secondaryTab;
    },

    /**
     * Set primary tab and handle secondary tab defaults
     */
    setPrimaryTab(tab) {
      this.primaryTab = tab;
      
      // Set appropriate default secondary tab based on primary tab
      if (tab === "annual" || tab === "yearly") {
        this.secondaryTab = "parishes";
      } else if (tab === "bread-death") {
        this.secondaryTab = "foodstuffs";
      }
      
      // Load data for the new tab combination
      this.loadTabData();
      this.updateUrl();
    },

    /**
     * Set secondary tab and load appropriate data
     */
    setSecondaryTab(tab) {
      this.secondaryTab = tab;
      this.loadTabData();
      this.updateUrl();
    },

    /**
     * Load data based on current primary and secondary tab combination
     */
    loadTabData() {
      // Clear existing data first
      this.bills = [];
      this.causes = [];
      this.christenings = [];

      const combo = `${this.primaryTab}-${this.secondaryTab}`;
      const previousBillType = this.filters.selectedBillType;

      switch (combo) {
        case "annual-parishes":
          this.filters.selectedBillType = "weekly";
          if (previousBillType !== "weekly") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchData("weekly");
          break;
        case "annual-deaths":
          this.filters.selectedBillType = "weekly";
          if (previousBillType !== "weekly") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchDeaths();
          break;
        case "annual-christenings":
          this.filters.selectedBillType = "weekly";
          if (previousBillType !== "weekly") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchChristenings();
          break;
        case "yearly-parishes":
          this.filters.selectedBillType = "general";
          if (previousBillType !== "general") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchData("general");
          break;
        case "yearly-deaths":
          this.filters.selectedBillType = "general";
          if (previousBillType !== "general") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchDeaths();
          break;
        case "yearly-christenings":
          this.filters.selectedBillType = "general";
          if (previousBillType !== "general") {
            this.fetchCausesAndChristeningsForBillType();
          }
          this.fetchChristenings();
          break;
        case "bread-death-foodstuffs":
          // Placeholder for foodstuffs data
          console.log("Loading foodstuffs data - to be implemented");
          break;
        case "bread-death-ages":
          // Placeholder for ages data
          console.log("Loading ages data - to be implemented");
          break;
        default:
          console.warn("Unknown tab combination:", combo);
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
          window.Alpine.store("openTab", tabIndex);
        } catch (e) {
          console.warn("Unable to set active tab in Alpine store:", e);
        }
      }

      const previousBillType = this.filters.selectedBillType;

      // Load appropriate data based on tab
      if (tabIndex === 1) {
        // Clear other arrays first to avoid display issues
        this.causes = [];
        this.christenings = [];

        // Set filter state for weekly tab
        this.filters.selectedBillType = "weekly";

        // Refetch filter lists if bill type changed
        if (previousBillType !== "weekly") {
          this.fetchCausesAndChristeningsForBillType();
        }

        // weekly tab - fetch weekly data
        this.fetchData("weekly");
      } else if (tabIndex === 2) {
        // Clear other arrays first to avoid display issues
        this.causes = [];
        this.christenings = [];

        // Set filter state for general tab
        this.filters.selectedBillType = "general";

        // Refetch filter lists if bill type changed
        if (previousBillType !== "general") {
          this.fetchCausesAndChristeningsForBillType();
        }

        // general tab - fetch general data
        this.fetchData("general");
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

      // Cancel any ongoing requests and clear cache to prevent race conditions and stale data
      if (window.DataService) {
        if (window.DataService.cancelAllRequests) {
          window.DataService.cancelAllRequests();
        }
        if (window.DataService.clearCache) {
          window.DataService.clearCache("bills");
        }
      }

      this.meta.loading = true;
      this.meta.fetching = true;
      this.meta.error = null;
      this.meta.slowConnection = false;

      // Clear any existing timeout first
      if (this.meta.connectionTimeout) {
        clearTimeout(this.meta.connectionTimeout);
        this.meta.connectionTimeout = null;
      }

      // Set up slow connection detection (15 seconds)
      this.meta.connectionTimeout = setTimeout(() => {
        if (this.meta.fetching) {
          this.meta.slowConnection = true;
        }
      }, 15000);

      try {
        // Prepare pagination params - cursor-based is default and preferred
        const paginationParams = {};

        // Always prefer cursor-based pagination when available
        if (this.page === 1) {
          // First page - no cursor needed
          // Backend will return first 25 records
        } else if (
          this.page > 1 &&
          this.pagination.cursors.length >= this.page - 1
        ) {
          // Use cursor for subsequent pages
          paginationParams.cursor = this.pagination.cursors[this.page - 2];
        } else {
          // Fallback to page-based pagination if cursors not available
          paginationParams.page = this.page;
        }

        // Fetch data using the updated DataService
        const response = await window.DataService.fetchBills(
          billType || this.filters.selectedBillType,
          this.filters,
          paginationParams,
        );

        // Handle new paginated response structure
        let data, pagination;
        if (response && response.data && Array.isArray(response.data)) {
          // New paginated response
          data = response.data;
          pagination = {
            nextCursor: response.next_cursor,
            hasMore: response.has_more,
          };
        } else if (Array.isArray(response)) {
          // Legacy array response
          data = response;
          pagination = {
            nextCursor: null,
            hasMore: false,
          };
        } else {
          throw new Error("Unexpected response format");
        }

        // Process data
        data.forEach(function (d, i) {
          d.id = i;
        });

        // Update state
        this.bills = data;

        // Update pagination state
        if (this.pagination.useCursor) {
          this.pagination.hasMore = pagination.hasMore;

          // Build cursor stack for navigation
          if (pagination.nextCursor) {
            // Ensure cursor array is the right size for current page
            while (this.pagination.cursors.length < this.page) {
              this.pagination.cursors.push(null);
            }
            // Store cursor for the NEXT page
            this.pagination.cursors[this.page - 1] = pagination.nextCursor;
          }

          // For cursor-based pagination, use the actual total from backend
          if (data.length > 0 && data[0].totalrecords > 0) {
            // First page or legacy pagination - update the total count
            this.pagination.total = data[0].totalrecords;
            this.pagination.lastPage = Math.ceil(
              this.pagination.total / this.pagination.pageSize,
            );
          } else if (this.pagination.total > 0) {
            // Subsequent cursor pages - keep existing total, just update lastPage if needed
            this.pagination.lastPage = Math.ceil(
              this.pagination.total / this.pagination.pageSize,
            );
          } else {
            // Fallback estimate if no total available
            this.pagination.total = data.length * this.page;
            this.pagination.lastPage = pagination.hasMore
              ? this.page + 1
              : this.page;
          }
        } else {
          // Legacy pagination
          this.pagination.cursor = null;
          this.pagination.hasMore = false;

          if (data.length > 0 && data[0].totalrecords) {
            this.pagination.total = data[0].totalrecords;
            this.pagination.lastPage = Math.ceil(
              this.pagination.total / this.pagination.pageSize,
            );
          } else {
            this.pagination.total = data.length;
            this.pagination.lastPage = 1;
          }
        }

        // Skip prefetching to improve initial page load performance
        // Parish data will be loaded on-demand when charts are opened

        // Update URL after data is loaded
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching bills data:", error);
        this.bills = [];
        this.meta.error = error.message || this.messages.error;
      } finally {
        // Clear the timeout
        if (this.meta.connectionTimeout) {
          clearTimeout(this.meta.connectionTimeout);
          this.meta.connectionTimeout = null;
        }
        this.meta.loading = false;
        this.meta.fetching = false;
        this.meta.slowConnection = false;
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

        // Fetch data for each parish in parallel if not already in cache
        const promises = uniqueParishes
          .filter((parish) => !this.parishYearlyData[parish])
          .map((parish) => this.fetchParishYearlyForSingle(parish));

        if (promises.length > 0) {
          await Promise.all(promises);
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
        console.error(
          "Error fetching yearly data for parish " + parishName + ":",
          error,
        );
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
        const parishes =
          this.filters.selectedParishes.length > 0
            ? this.filters.selectedParishes
            : this.parishes && this.parishes.length > 0
              ? this.parishes.slice(0, 10).map(function (p) {
                  return p.canonical_name;
                })
              : [];

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
        this.pagination.lastPage = Math.ceil(
          this.pagination.total / this.pagination.pageSize,
        );
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
      this.meta.error = null;
      this.meta.slowConnection = false;

      // Clear any existing timeout first
      if (this.meta.connectionTimeout) {
        clearTimeout(this.meta.connectionTimeout);
        this.meta.connectionTimeout = null;
      }

      // Set up slow connection detection (15 seconds)
      this.meta.connectionTimeout = setTimeout(() => {
        if (this.meta.fetching) {
          this.meta.slowConnection = true;
        }
      }, 15000);

      try {
        // Calculate offset based on page
        const offset = (this.page - 1) * this.pageSize;

        // Prepare params for API
        const params = {
          "start-year": this.filters.selectedStartYear,
          "end-year": this.filters.selectedEndYear,
          "bill-type": this.filters.selectedBillType,
          limit: this.pageSize,
          offset: offset,
        };

        // Add death causes filter if selected
        if (
          this.filters.selectedCausesOfDeath &&
          this.filters.selectedCausesOfDeath.length > 0
        ) {
          params.id = this.filters.selectedCausesOfDeath.join(",");
        }

        // Fetch data
        const data = await window.DataService.fetchData("causes", params);

        // Process data
        data.forEach(function (d, i) {
          d.id = i;
        });

        // Update state
        this.causes = data;

        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(
            this.pagination.total / this.pagination.pageSize,
          );
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }

        // Update URL
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching deaths data:", error);
        this.causes = [];
        this.meta.error = error.message || this.messages.error;
      } finally {
        // Clear the timeout
        if (this.meta.connectionTimeout) {
          clearTimeout(this.meta.connectionTimeout);
          this.meta.connectionTimeout = null;
        }
        this.meta.loading = false;
        this.meta.fetching = false;
        this.meta.slowConnection = false;
      }
    },

    /**
     * Fetch christenings data
     */
    async fetchChristenings() {
      console.log("Fetching christenings data...");
      this.meta.loading = true;
      this.meta.fetching = true;
      this.meta.error = null;
      this.meta.slowConnection = false;

      // Clear any existing timeout first
      if (this.meta.connectionTimeout) {
        clearTimeout(this.meta.connectionTimeout);
        this.meta.connectionTimeout = null;
      }

      // Set up slow connection detection (15 seconds)
      this.meta.connectionTimeout = setTimeout(() => {
        if (this.meta.fetching) {
          this.meta.slowConnection = true;
        }
      }, 15000);

      try {
        // Calculate offset based on page
        const offset = (this.page - 1) * this.pageSize;

        // Prepare params for API
        const params = {
          "start-year": this.filters.selectedStartYear,
          "end-year": this.filters.selectedEndYear,
          "bill-type": this.filters.selectedBillType,
          limit: this.pageSize,
          offset: offset,
        };

        // Add selected christenings if any
        if (
          this.filters.selectedChristenings &&
          this.filters.selectedChristenings.length > 0
        ) {
          params.id = this.filters.selectedChristenings.join(",");
        }

        // Fetch data
        const data = await window.DataService.fetchData("christenings", params);

        // Process data
        data.forEach(function (d, i) {
          d.id = i;
        });

        // Update state
        this.christenings = data;

        // Update pagination
        if (data.length > 0 && data[0].totalrecords) {
          this.pagination.total = data[0].totalrecords;
          this.pagination.lastPage = Math.ceil(
            this.pagination.total / this.pagination.pageSize,
          );
        } else {
          this.pagination.total = 0;
          this.pagination.lastPage = 1;
        }

        // Update URL
        this.updateUrl();
      } catch (error) {
        console.error("Error fetching christenings:", error);
        this.christenings = [];
        this.meta.error = error.message || this.messages.error;
      } finally {
        // Clear the timeout
        if (this.meta.connectionTimeout) {
          clearTimeout(this.meta.connectionTimeout);
          this.meta.connectionTimeout = null;
        }
        this.meta.loading = false;
        this.meta.fetching = false;
        this.meta.slowConnection = false;
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
      if (page < 1) {
        return;
      }

      if (this.pagination.useCursor) {
        // Cursor-based pagination
        if (page === 1) {
          // Going to first page - reset everything
          this.pagination.cursor = null;
          this.pagination.cursors = [];
        } else if (page === this.page + 1) {
          // Going to next page - use the current cursor
          if (!this.pagination.hasMore) {
            return; // No more data available
          }
          // The cursor is already set from the previous response
        } else if (page === this.page - 1 && page > 1) {
          // Going back one page - use previous cursor
          if (this.pagination.cursors.length >= page - 1) {
            this.pagination.cursor = this.pagination.cursors[page - 2] || null;
          } else {
            // Can't go back efficiently, disable cursor temporarily
            this.pagination.useCursor = false;
          }
        } else {
          // Jumping to arbitrary page - fall back to page-based pagination
          this.pagination.useCursor = false;
          this.pagination.cursor = null;
        }
      }

      this.page = page;
      this.pagination.page = page;

      // Use the new two-tiered tab system to determine which data to fetch
      const combo = `${this.primaryTab}-${this.secondaryTab}`;

      // Set a loading state
      this.meta.loading = true;

      // Fetch new data for the page based on current tab combination
      switch (combo) {
        case "annual-parishes":
          this.fetchData(this.filters.selectedBillType);
          break;
        case "annual-deaths":
          this.fetchDeaths();
          break;
        case "annual-christenings":
          this.fetchChristenings();
          break;
        case "yearly-parishes":
          this.fetchData(this.filters.selectedBillType);
          break;
        case "yearly-deaths":
          this.fetchDeaths();
          break;
        case "yearly-christenings":
          this.fetchChristenings();
          break;
        case "bread-death-foodstuffs":
          // Future implementation
          console.log("Foodstuffs pagination - to be implemented");
          break;
        case "bread-death-ages":
          // Future implementation
          console.log("Ages pagination - to be implemented");
          break;
        default:
          console.warn("Unknown tab combination for pagination:", combo);
          // Fallback to legacy system for safety
          const currentTab = this.getOpenTab();
          if (currentTab === 1) {
            this.fetchData(this.filters.selectedBillType);
          } else if (currentTab === 2) {
            this.fetchData(this.filters.selectedBillType);
          }
      }

      // Re-enable cursor pagination after page-based fetch completes
      if (!this.pagination.useCursor && page === 1) {
        this.$nextTick(() => {
          this.pagination.useCursor = true;
        });
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
        if (typeof aVal === "string" && typeof bVal === "string") {
          return this.sort
            ? bVal.localeCompare(aVal)
            : aVal.localeCompare(bVal);
        }

        return this.sort ? bVal - aVal : aVal - bVal;
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
      this.pagination.cursor = null; // Reset cursor for new filters
      this.pagination.cursors = []; // Reset cursor stack
      this.pagination.useCursor = true; // Re-enable cursor pagination

      // Use new tab system for data fetching
      this.loadTabData();
      
      // Close the filter panel
      this.filtersOpen = false;
    },

    /**
     * Update page size and refetch data
     */
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
      this.pagination.cursor = null; // Reset cursor for new page size
      this.pagination.cursors = []; // Reset cursor stack
      this.pagination.useCursor = true; // Re-enable cursor pagination

      // Get current tab to determine which data to fetch
      const currentTab = this.getOpenTab();
      if (currentTab === 1) {
        this.fetchData(this.filters.selectedBillType);
      } else if (currentTab === 2) {
        this.fetchData(this.filters.selectedBillType);
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
      this.filters.selectedStartYear = 1629;
      this.filters.selectedEndYear = 1754;
      this.filters.selectedStartWeek = 1;
      this.filters.selectedEndWeek = 56;
      this.filters.selectedCountType = "";
      this.filters.selectedBillType = "weekly";
      this.filters.selectedParishes = [];
      this.filters.selectedCausesOfDeath = [];
      this.filters.selectedChristenings = [];
      this.filters.showIllegibleOnly = false;

      // Reset pagination
      this.page = 1;
      this.pagination.page = 1;
      this.pagination.cursor = null; // Reset cursor
      this.pagination.cursors = []; // Reset cursor stack
      this.pagination.useCursor = true; // Re-enable cursor pagination

      // Get current tab combination to determine which data to fetch
      const combo = `${this.primaryTab}-${this.secondaryTab}`;
      
      switch (combo) {
        case "annual-parishes":
          this.fetchData(this.filters.selectedBillType);
          break;
        case "annual-deaths":
          this.fetchDeaths();
          break;
        case "annual-christenings":
          this.fetchChristenings();
          break;
        case "yearly-parishes":
          this.fetchData(this.filters.selectedBillType);
          break;
        case "yearly-deaths":
          this.fetchDeaths();
          break;
        case "yearly-christenings":
          this.fetchChristenings();
          break;
        case "bread-death-foodstuffs":
          // Future implementation
          console.log("Foodstuffs reset - to be implemented");
          break;
        case "bread-death-ages":
          // Future implementation
          console.log("Ages reset - to be implemented");
          break;
        default:
          console.warn("Unknown tab combination for reset:", combo);
          // Fallback to legacy system for safety
          const currentTab = this.getOpenTab();
          if (currentTab === 1) {
            this.fetchData(this.filters.selectedBillType);
          } else if (currentTab === 2) {
            this.fetchData(this.filters.selectedBillType);
          }
      }
    },

    /**
     * Set the start year for filtering
     */
    setStartYear() {
      // Validate input
      const year = parseInt(this.filters.selectedStartYear);
      if (isNaN(year)) {
        this.filters.selectedStartYear = 1629;
      } else if (year < 1629) {
        this.filters.selectedStartYear = 1629;
      } else if (year > 1754) {
        this.filters.selectedStartYear = 1754;
      }

      // Ensure start year is not after end year
      if (
        parseInt(this.filters.selectedStartYear) >
        parseInt(this.filters.selectedEndYear)
      ) {
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
      } else if (year < 1629) {
        this.filters.selectedEndYear = 1629;
      } else if (year > 1754) {
        this.filters.selectedEndYear = 1754;
      }

      // Ensure end year is not before start year
      if (
        parseInt(this.filters.selectedEndYear) <
        parseInt(this.filters.selectedStartYear)
      ) {
        this.filters.selectedStartYear = this.filters.selectedEndYear;
      }
    },

    /**
     * Set the count type for filtering
     */
    setCountType() {
      // This function is needed for the filter to work with count type selections
      console.log("Count type set to:", this.filters.selectedCountType);
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
      // If there's an actual connection error (not just slow loading), show error message
      if (this.meta.error && !this.meta.loading) {
        return (
          this.messages.connectionError +
          ' <a href="https://github.com/YOUR_USERNAME/YOUR_REPO/tree/main/data" class="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener">Download CSV files instead</a>'
        );
      }

      // If data is loading, show appropriate loading message
      if (this.meta.loading) {
        if (this.meta.slowConnection) {
          return (
            this.messages.slowConnection +
            ' <a href="https://github.com/YOUR_USERNAME/YOUR_REPO/tree/main/data" class="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener">Download CSV files instead</a>'
          );
        }
        return this.messages.loading;
      }

      // Handle different summary types
      if (type && type.toLowerCase() === "pages") {
        return (
          "Showing page <strong>" +
          this.page +
          "</strong> of <strong>" +
          this.pagination.lastPage +
          "</strong>"
        );
      }

      // Handle empty results
      if (this.pagination.total === 0) {
        return this.messages.noResults;
      }

      // Show row count summary
      return (
        "Showing <strong>" +
        this.getFirstDisplayedRow() +
        "</strong> to <strong>" +
        this.getLastDisplayedRow() +
        "</strong> of <strong>" +
        this.pagination.total +
        "</strong> records"
      );
    },

    /**
     * Update URL with current state
     */
    updateUrl() {
      // Create URL with current filter state
      const params = new URLSearchParams();

      params.set("start-year", this.filters.selectedStartYear);
      params.set("end-year", this.filters.selectedEndYear);
      if (this.filters.selectedStartWeek !== 1) {
        params.set("start-week", this.filters.selectedStartWeek);
      }
      if (this.filters.selectedEndWeek !== 56) {
        params.set("end-week", this.filters.selectedEndWeek);
      }
      if (this.filters.selectedCountType && this.filters.selectedCountType !== "all") {
        params.set("count-type", this.filters.selectedCountType);
      }
      if (this.filters.selectedParishes.length > 0) {
        params.set("parish", this.filters.selectedParishes.join(","));
      }

      // Only include page in URL if not using cursor pagination or if on page 1
      if (!this.pagination.useCursor || this.page === 1) {
        if (this.page > 1) {
          params.set("page", this.page);
        }
      }

      params.set("bill-type", this.filters.selectedBillType);

      // Add two-tiered tab system to URL
      params.set("primary-tab", this.primaryTab);
      params.set("secondary-tab", this.secondaryTab);

      // Add legacy tab to URL for backward compatibility
      params.set("tab", this.getOpenTab());

      // Use the history API to update the URL without reloading
      history.pushState({}, "", location.pathname + "?" + params.toString());
    },

    /**
     * Open modal with chart
     */
    openModal(item) {
      this.modalBill = item;
      this.modalOpen = true;

      // Initialize chart only after modal is open and we have data
      this.$nextTick(() => {
        // Check for christening first (has 'christening' field)
        if (item && item.christening) {
          // Christening data
          this.initModalChart(item.christening, 'christening');
        } else if (item && item.death !== undefined) {
          // Death data (has 'death' field for original transcription, even if null)
          // Use 'name' field for the identifier since that's the standardized cause name
          this.initModalChart(item.name, 'death');
        } else if (item && item.name) {
          // Parish data (only has 'name', no 'death' field)
          this.initModalChart(item.name, 'parish');
        }
      });
    },

    /**
     * Initialize modal chart
     */
    initModalChart(identifier, dataType = 'parish') {
      if (!identifier) {
        console.error("No identifier provided for chart initialization");
        return;
      }

      // Get container IDs based on data type and bill type
      const suffixes = {
        'parish': this.filters.selectedBillType === 'general' ? '-general' : '',
        'death': this.filters.selectedBillType === 'general' ? '-deaths-general' : '-deaths',
        'christening': '-christenings'
      };

      const suffix = suffixes[dataType] || '';
      const chartContainer = document.getElementById(`modal-chart-container${suffix}`);
      const loadingIndicator = document.getElementById(`modal-loading-indicator${suffix}`);
      const errorMessage = document.getElementById(`modal-error-message${suffix}`);

      if (!chartContainer) {
        console.error(`Chart container not found: modal-chart-container${suffix}`);
        return;
      }

      // Show loading state
      if (loadingIndicator) loadingIndicator.style.display = "block";
      if (errorMessage) {
        errorMessage.style.display = "none";
        errorMessage.classList.add("hidden");
      }

      // Use ChartService to load the chart
      if (window.ChartService) {
        window.ChartService.loadPlotLibrary()
          .then(() => {
            // Get appropriate data based on type
            let dataPromise;
            const cacheKey = `${dataType}-${identifier}`;
            
            if (dataType === 'parish') {
              if (this.parishYearlyData[identifier]) {
                dataPromise = Promise.resolve(this.parishYearlyData[identifier]);
              } else {
                dataPromise = window.DataService.fetchParishYearly(identifier).then(
                  (data) => {
                    this.parishYearlyData[identifier] = data;
                    return data;
                  }
                );
              }
            } else if (dataType === 'death') {
              // Fetch real death cause yearly data from API
              if (this.deathYearlyData[identifier]) {
                dataPromise = Promise.resolve(this.deathYearlyData[identifier]);
              } else {
                const billType = this.filters.selectedBillType || 'weekly';
                dataPromise = window.DataService.fetchDeathCauseYearly(identifier, billType).then(
                  (data) => {
                    this.deathYearlyData[identifier] = data;
                    return data;
                  }
                );
              }
            } else if (dataType === 'christening') {
              // Fetch real christening yearly data from API
              if (this.christeningYearlyData[identifier]) {
                dataPromise = Promise.resolve(this.christeningYearlyData[identifier]);
              } else {
                const billType = this.filters.selectedBillType || 'weekly';
                dataPromise = window.DataService.fetchChristeningYearly(identifier, billType).then(
                  (data) => {
                    this.christeningYearlyData[identifier] = data;
                    return data;
                  }
                );
              }
            } else {
              dataPromise = Promise.reject(new Error(`Unknown data type: ${dataType}`));
            }
            
            return dataPromise;
          })
          .then((data) => {
            // Use ChartService to render the chart
            window.ChartService.createModalDetailChart(chartContainer, data, dataType);

            // Hide loading indicator
            if (loadingIndicator) loadingIndicator.style.display = "none";
          })
          .catch((error) => {
            console.error("Chart error:", error);

            // Show error message
            if (errorMessage) {
              errorMessage.textContent =
                error.message || "Error loading chart data";
              errorMessage.style.display = "block";
              errorMessage.classList.remove("hidden");
            }

            // Hide loading indicator
            if (loadingIndicator) loadingIndicator.style.display = "none";
          });
      } else {
        console.error("ChartService not available");
      }
    },

    /**
     * Generate mock chart data for deaths and christenings
     * TODO: Replace with real API calls when backend is ready
     */
    generateMockChartData(identifier, dataType) {
      return new Promise((resolve) => {
        // Generate sample data for demonstration
        const startYear = 1629;
        const endYear = 1754;
        const data = [];
        
        for (let year = startYear; year <= endYear; year += 5) {
          const baseCount = Math.floor(Math.random() * 100) + 20;
          const variation = Math.floor(Math.random() * 50) - 25;
          
          if (dataType === 'death') {
            data.push({
              year: year,
              total_deaths: Math.max(1, baseCount + variation),
              cause: identifier
            });
          } else if (dataType === 'christening') {
            data.push({
              year: year,
              total_christenings: Math.max(1, baseCount + variation),
              type: identifier
            });
          }
        }
        
        // Simulate async delay
        setTimeout(() => resolve(data), 300);
      });
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

      if (isNaN(startYear) || startYear < 1629) {
        this.filters.selectedStartYear = 1629;
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
        const clientX = e.type.includes("touch")
          ? e.touches[0].clientX
          : e.clientX;

        // Calculate position relative to the track
        const rect = track.getBoundingClientRect();
        const position = (clientX - rect.left) / rect.width;

        // Convert position to year value
        const minYear = 1629;
        const maxYear = 1754;
        const range = maxYear - minYear;

        // Calculate the new year based on position
        let newYear = Math.round(minYear + position * range);

        // Clamp the year to valid range
        newYear = Math.max(minYear, Math.min(maxYear, newYear));

        // Update the appropriate year based on which handle is being dragged
        if (this.dragging === "start") {
          // Ensure start year doesn't exceed end year
          this.filters.selectedStartYear = Math.min(
            newYear,
            this.filters.selectedEndYear,
          );
        } else if (this.dragging === "end") {
          // Ensure end year doesn't go below start year
          this.filters.selectedEndYear = Math.max(
            newYear,
            this.filters.selectedStartYear,
          );
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
        window.removeEventListener("mousemove", moveHandler);
        window.removeEventListener("touchmove", moveHandler);
        window.removeEventListener("mouseup", endHandler);
        window.removeEventListener("touchend", endHandler);

        // Validate the selected years
        this.validateYearInput();
      };

      // Add event listeners
      window.addEventListener("mousemove", moveHandler);
      window.addEventListener("touchmove", moveHandler);
      window.addEventListener("mouseup", endHandler);
      window.addEventListener("touchend", endHandler);
    },

    /**
     * Handle week range slider dragging
     */
    startWeekDrag(event, handle) {
      // Set the current handle being dragged
      this.weekDragging = handle;

      // Prevent text selection during drag
      event.preventDefault();

      // Get the slider track element
      const track = event.target.parentElement;

      // Calculate position and update week
      const updatePosition = (e) => {
        // Get event position (support both mouse and touch)
        const clientX = e.type.includes("touch")
          ? e.touches[0].clientX
          : e.clientX;

        // Calculate position relative to the track
        const rect = track.getBoundingClientRect();
        const position = (clientX - rect.left) / rect.width;

        // Convert position to week value (1-56)
        const minWeek = 1;
        const maxWeek = 56;
        const range = maxWeek - minWeek;

        // Calculate the new week based on position
        let newWeek = Math.round(minWeek + position * range);

        // Clamp the week to valid range
        newWeek = Math.max(minWeek, Math.min(maxWeek, newWeek));

        // Update the appropriate week based on which handle is being dragged
        if (this.weekDragging === "start") {
          // Ensure start week doesn't exceed end week
          this.filters.selectedStartWeek = Math.min(
            newWeek,
            this.filters.selectedEndWeek,
          );
        } else if (this.weekDragging === "end") {
          // Ensure end week doesn't go below start week
          this.filters.selectedEndWeek = Math.max(
            newWeek,
            this.filters.selectedStartWeek,
          );
        }
      };

      // Handle the initial position
      updatePosition(event);

      // Set up event listeners for dragging
      const moveHandler = (e) => updatePosition(e);
      const endHandler = () => {
        // Clear dragging state
        this.weekDragging = null;

        // Remove event listeners
        window.removeEventListener("mousemove", moveHandler);
        window.removeEventListener("touchmove", moveHandler);
        window.removeEventListener("mouseup", endHandler);
        window.removeEventListener("touchend", endHandler);

        // Validate the selected weeks
        this.validateWeekInput();
      };

      // Add event listeners
      window.addEventListener("mousemove", moveHandler);
      window.addEventListener("touchmove", moveHandler);
      window.addEventListener("mouseup", endHandler);
      window.addEventListener("touchend", endHandler);
    },

    /**
     * Validate week input range
     */
    validateWeekInput() {
      // Ensure weeks are within valid range
      this.filters.selectedStartWeek = Math.max(1, Math.min(56, this.filters.selectedStartWeek || 1));
      this.filters.selectedEndWeek = Math.max(1, Math.min(56, this.filters.selectedEndWeek || 56));

      // Ensure start week doesn't exceed end week
      if (this.filters.selectedStartWeek > this.filters.selectedEndWeek) {
        this.filters.selectedEndWeek = this.filters.selectedStartWeek;
      }
    },

    /**
     * Get count type options based on current tab context
     */
    getCountTypeOptions() {
      const secondaryTab = this.getSecondaryTab();
      let options = '<option value="all">All</option>';
      
      if (secondaryTab === 'parishes') {
        options += '<option value="buried">Buried</option>';
        options += '<option value="plague">Plague</option>';
      } else if (secondaryTab === 'deaths') {
        options += '<option value="total">Total</option>';
      } else if (secondaryTab === 'christenings') {
        options += '<option value="buried">Buried</option>';
        options += '<option value="plague">Plague</option>';
      }
      
      return options;
    },
  }));
});
