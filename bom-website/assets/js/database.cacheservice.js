/**
 * database.cacheservice.js
 * Provides caching functionality for the application
 */

const CacheService = {
  data: {},
  
  /**
   * Stores a value in the cache
   * @param {string} key - Cache key
   * @param {*} value - Value to store
   * @param {number} ttl - Time to live in milliseconds (0 = no expiry)
   */
  set(key, value, ttl = 0) {
    const item = {
      value,
      expires: ttl > 0 ? Date.now() + ttl : 0
    };
    
    this.data[key] = item;
    return value;
  },
  
  /**
   * Retrieves a value from the cache
   * @param {string} key - Cache key
   * @returns {*} - Cached value or null if not found or expired
   */
  get(key) {
    const item = this.data[key];
    
    if (!item) {
      return null;
    }
    
    // Check if expired
    if (item.expires > 0 && item.expires < Date.now()) {
      delete this.data[key];
      return null;
    }
    
    return item.value;
  },
  
  /**
   * Checks if a key exists in the cache and is not expired
   * @param {string} key - Cache key
   * @returns {boolean} - True if key exists and is not expired
   */
  has(key) {
    return this.get(key) !== null;
  },
  
  /**
   * Removes a specific key from the cache
   * @param {string} key - Cache key
   */
  remove(key) {
    delete this.data[key];
  },
  
  /**
   * Clears the entire cache or entries matching a prefix
   * @param {string} [prefix] - Optional prefix to selectively clear cache
   */
  clear(prefix) {
    if (prefix) {
      Object.keys(this.data).forEach(key => {
        if (key.startsWith(prefix)) {
          delete this.data[key];
        }
      });
    } else {
      this.data = {};
    }
  },
  
  /**
   * Returns a memoized version of a function
   * @param {Function} fn - Function to memoize
   * @param {Function} [keyFn] - Function to generate cache key from arguments
   * @param {number} ttl - Time to live in milliseconds
   * @returns {Function} - Memoized function
   */
  memoize(fn, keyFn, ttl = 0) {
    return (...args) => {
      const key = keyFn ? keyFn(...args) : JSON.stringify(args);
      
      if (this.has(key)) {
        return this.get(key);
      }
      
      const result = fn(...args);
      
      // Handle promises
      if (result instanceof Promise) {
        return result.then(value => this.set(key, value, ttl));
      }
      
      return this.set(key, result, ttl);
    };
  },
  
  /**
   * Gets cache statistics
   * @returns {Object} - Cache statistics
   */
  getStats() {
    const totalItems = Object.keys(this.data).length;
    let expired = 0;
    
    Object.values(this.data).forEach(item => {
      if (item.expires > 0 && item.expires < Date.now()) {
        expired++;
      }
    });
    
    return {
      totalItems,
      expired,
      active: totalItems - expired,
      memoryUsage: JSON.stringify(this.data).length
    };
  }
};

// Export the service
window.CacheService = CacheService;
