/**
 * database.dataservice.js
 * Handles all data fetching and processing operations for the Bills of Mortality application
 */

const DataService = {
  baseUrl: 'https://data.chnm.org/bom',
  cache: {},
  
  /**
   * Generic method to fetch data from the API
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - Promise resolving to the fetched data
   */
  async fetchData(endpoint, params = {}) {
    try {
      const url = new URL(`${this.baseUrl}/${endpoint}`);
      
      // Add query parameters
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value) && value.length > 0) {
          url.searchParams.append(key, value.join(','));
        } else if (value !== undefined && value !== null && value !== '') {
          url.searchParams.append(key, value);
        }
      });
      
      // Check cache first if caching is enabled for this request
      if (params.useCache !== false) {
        const cacheKey = url.toString();
        if (this.cache[cacheKey]) {
          console.log('Using cached data for:', url.toString());
          return this.cache[cacheKey];
        }
      }
      
      console.log('Fetching data from:', url.toString());
      const response = await fetch(url);
      
      if (!response.ok) {
        console.error(`HTTP error ${response.status} for URL: ${url.toString()}`);
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        console.error(`API error for ${url.toString()}:`, data.error);
        throw new Error(data.error);
      }
      
      console.log(`Received ${data.length} items from ${endpoint}`);
      
      // Add IDs to the data if not present
      if (Array.isArray(data)) {
        data.forEach((item, index) => {
          if (!item.id) {
            item.id = index;
          }
        });
      }
      
      // Cache the results if caching is enabled
      if (params.useCache !== false) {
        const cacheKey = url.toString();
        this.cache[cacheKey] = data;
      }
      
      return data;
    } catch (error) {
      console.error(`Error fetching ${endpoint} data:`, error);
      return [];
    }
  },
  
  /**
   * Clears the data cache
   * @param {string} [endpoint] - Optional endpoint to clear specific cache
   */
  clearCache(endpoint) {
    if (endpoint) {
      const prefix = `${this.baseUrl}/${endpoint}`;
      Object.keys(this.cache).forEach(key => {
        if (key.startsWith(prefix)) {
          delete this.cache[key];
        }
      });
    } else {
      this.cache = {};
    }
  },
  
  /**
   * Fetches parish data
   * @returns {Promise<Array>} - List of parishes
   */
  async fetchParishes() {
    return this.fetchData('parishes');
  },
  
  /**
   * Fetches bills data
   * @param {string} billType - Type of bill (Weekly, General)
   * @param {Object} filters - Filter parameters
   * @param {Object} pagination - Pagination parameters
   * @returns {Promise<Array>} - List of bills
   */
  async fetchBills(billType, filters, pagination) {
    const params = {
      'bill-type': billType,
      'start-year': filters.selectedStartYear,
      'end-year': filters.selectedEndYear,
      'count-type': filters.selectedCountType,
      'parish': filters.selectedParishes,
      'limit': pagination.pageSize,
      'offset': (pagination.page - 1) * pagination.pageSize
    };
    
    return this.fetchData('bills', params);
  },
  
  /**
   * Fetches causes of death data
   * @param {Object} filters - Filter parameters
   * @param {Object} pagination - Pagination parameters
   * @returns {Promise<Array>} - List of causes of death
   */
  async fetchDeaths(filters, pagination) {
    const params = {
      'start-year': filters.selectedStartYear,
      'end-year': filters.selectedEndYear,
      'limit': pagination.pageSize,
      'offset': (pagination.page - 1) * pagination.pageSize
    };
    
    // Handle cause of death filter - API expects 'death' parameter
    if (filters.selectedCausesOfDeath && filters.selectedCausesOfDeath.length > 0) {
      params['id'] = filters.selectedCausesOfDeath;
    }
    
    return this.fetchData('causes', params);
  },
  
  /**
   * Fetches all causes of death for the filter dropdown
   * @returns {Promise<Array>} - List of all causes of death
   */
  async fetchAllCauses() {
    return this.fetchData('list-deaths');
  },
  
  /**
   * Fetches christening data
   * @param {Object} filters - Filter parameters
   * @param {Object} pagination - Pagination parameters
   * @returns {Promise<Array>} - List of christenings
   */
  async fetchChristenings(filters, pagination) {
    const params = {
      'start-year': filters.selectedStartYear,
      'end-year': filters.selectedEndYear,
      'id': filters.selectedChristenings,
      'limit': pagination.pageSize,
      'offset': (pagination.page - 1) * pagination.pageSize
    };
    
    return this.fetchData('christenings', params);
  },
  
  /**
   * Fetches all christenings for the filter dropdown
   * @returns {Promise<Array>} - List of all christenings
   */
  async fetchAllChristenings() {
    return this.fetchData('list-christenings');
  },
  
  /**
   * Fetches yearly data for a single parish
   * @param {string} parishName - Name of the parish
   * @returns {Promise<Array>} - Yearly data for the parish
   */
  async fetchParishYearly(parishName) {
    const params = {
      'type': 'parish-yearly',
      'parish': parishName
    };
    
    return this.fetchData('statistics', params);
  },
  
  /**
   * Fetches yearly data for multiple parishes
   * @param {Array} parishes - List of parish names
   * @returns {Promise<Object>} - Object mapping parish names to their yearly data
   */
  async fetchParishesYearly(parishes) {
    const results = {};
    
    for (const parish of parishes) {
      results[parish] = await this.fetchParishYearly(parish);
    }
    
    return results;
  }
};

// Export the service
window.DataService = DataService;

