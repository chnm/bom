/**
 * database.dataservice.js
 * Handles all data fetching and processing operations for the Bills of Mortality application
 */

const DataService = {
  baseUrl: 'https://data.chnm.org/bom',
  cache: {},
  
  // Request management
  activeRequests: new Map(),
  requestQueue: [],
  
  /**
   * Cancel an active request by key
   * @param {string} requestKey - Unique key for the request
   */
  cancelActiveRequest(requestKey) {
    const controller = this.activeRequests.get(requestKey);
    if (controller) {
      controller.abort();
      this.activeRequests.delete(requestKey);
    }
  },

  /**
   * Generic method to fetch data from the API with request deduplication
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - Query parameters
   * @returns {Promise<Array|Object>} - Promise resolving to the fetched data or paginated response
   */
  async fetchData(endpoint, params = {}) {
    const url = new URL(`${this.baseUrl}/${endpoint}`);
    
    // Add query parameters
    Object.entries(params).forEach(([key, value]) => {
      if (Array.isArray(value) && value.length > 0) {
        url.searchParams.append(key, value.join(','));
      } else if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, value);
      }
    });
    
    const urlString = url.toString();
    const requestKey = `${endpoint}:${urlString}`;
    
    // Check cache first if caching is enabled for this request
    if (params.useCache !== false) {
      if (this.cache[urlString]) {
        console.log(`Using cached data for: ${urlString} (${this.cache[urlString].data?.length || 'unknown'} items)`);
        return this.cache[urlString];
      }
    }
    
    // Check if there's already an identical request in progress
    if (this.activeRequests.has(requestKey)) {
      console.log('Request already in progress, waiting for result:', urlString);
      try {
        return await this.activeRequests.get(requestKey).promise;
      } catch (error) {
        if (error.name === 'AbortError') {
          // Request was cancelled, proceed with new request
        } else {
          throw error;
        }
      }
    }
    
    // Create abort controller for this request
    const controller = new AbortController();
    const requestPromise = this._performFetch(urlString, endpoint, controller.signal, params.useCache !== false);
    
    // Store the controller and promise
    this.activeRequests.set(requestKey, { 
      abort: () => controller.abort(),
      promise: requestPromise 
    });
    
    try {
      const result = await requestPromise;
      return result;
    } finally {
      // Clean up the active request
      this.activeRequests.delete(requestKey);
    }
  },

  /**
   * Perform the actual fetch request
   * @private
   */
  async _performFetch(urlString, endpoint, signal, enableCache = true) {
    try {
      console.log('Fetching data from:', urlString);
      const response = await fetch(urlString, { signal });
      
      if (!response.ok) {
        console.error(`HTTP error ${response.status} for URL: ${urlString}`);
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const responseData = await response.json();
      
      if (responseData.error) {
        console.error(`API error for ${urlString}:`, responseData.error);
        throw new Error(responseData.error);
      }
      
      // Handle paginated response from new cursor-based API
      if (responseData.data && Array.isArray(responseData.data)) {
        console.log(`Received ${responseData.data.length} items from ${endpoint} (URL: ${urlString})`);
        
        // Safety check: prevent processing unexpectedly large datasets
        if (responseData.data.length > 1000) {
          console.error(`Dataset too large: ${responseData.data.length} items. This suggests a backend pagination issue.`);
          throw new Error(`Dataset too large: ${responseData.data.length} items received`);
        }
        
        // Add IDs to the data if not present
        responseData.data.forEach((item, index) => {
          if (!item.id) {
            item.id = index;
          }
        });
        
        // Cache the results if caching is enabled
        if (enableCache) {
          this.cache[urlString] = responseData;
        }
        
        return responseData; // Return full paginated response
      }
      
      // Handle legacy array response
      if (Array.isArray(responseData)) {
        console.log(`Received ${responseData.length} items from ${endpoint}`);
        
        // Add IDs to the data if not present
        responseData.forEach((item, index) => {
          if (!item.id) {
            item.id = index;
          }
        });
        
        // Cache the results if caching is enabled
        if (enableCache) {
          this.cache[urlString] = responseData;
        }
        
        return responseData;
      }
      
      // Return as-is for other response types
      if (enableCache) {
        this.cache[urlString] = responseData;
      }
      return responseData;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request cancelled:', urlString);
        throw error;
      }
      console.error(`Error fetching ${endpoint} data:`, error);
      return [];
    }
  },
  
  /**
   * Cancel all active requests
   */
  cancelAllRequests() {
    for (const [key, controller] of this.activeRequests) {
      try {
        controller.abort();
      } catch (e) {
        console.warn('Error cancelling request:', key, e);
      }
    }
    this.activeRequests.clear();
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
   * @param {Object} pagination - Pagination parameters (supports cursor or offset)
   * @returns {Promise<Object>} - Paginated response with data, next_cursor, and has_more
   */
  async fetchBills(billType, filters, pagination) {
    const params = {
      'bill-type': billType,
      'start-year': filters.selectedStartYear,
      'end-year': filters.selectedEndYear,
      'count-type': filters.selectedCountType,
      'parish': filters.selectedParishes
    };
    
    // Prioritize cursor-based pagination (default and preferred)
    if (pagination.cursor) {
      params.cursor = pagination.cursor;
      // Don't include page/limit/offset when using cursor
    } else if (pagination.page && pagination.page > 1) {
      // Only use page-based pagination for compatibility when explicitly requested
      params.page = pagination.page;
    } else if (pagination.limit) {
      // Direct limit/offset pagination as fallback
      params.limit = pagination.limit;
      if (pagination.offset) {
        params.offset = pagination.offset;
      }
    } else {
      // Default: always send a limit to ensure pagination works
      params.limit = 100;
    }
    
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

