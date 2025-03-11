/**
 * database-initialize.js
 * Initializes the application and ensures services are loaded in the correct order
 */

(function() {
  // Define the service files in the order they should be loaded
  const serviceFiles = [
    '/js/database.cacheservice.js',
    '/js/database.urlservice.js', 
    '/js/database.dataservice.js',
    '/js/database.chartservice.js',
    '/js/database.alpine.js'  // Alpine component must come last
  ];
  
  // Counter to track loaded services
  let loadedCount = 0;
  
  // Function to check if all services are loaded
  function checkAllServicesLoaded() {
    loadedCount++;
    if (loadedCount === serviceFiles.length) {
      console.log('All services loaded successfully');
      // Signal that the application is ready
      document.dispatchEvent(new CustomEvent('app-initialized'));
    }
  }
  
  // Function to load a script
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      
      script.onload = () => {
        console.log(`Loaded: ${src}`);
        resolve();
      };
      
      script.onerror = () => {
        console.error(`Failed to load: ${src}`);
        reject(new Error(`Failed to load script: ${src}`));
      };
      
      document.head.appendChild(script);
    });
  }
  
  // Load services sequentially to maintain dependencies
  async function loadServices() {
    try {
      for (const serviceFile of serviceFiles) {
        await loadScript(serviceFile);
        checkAllServicesLoaded();
      }
    } catch (error) {
      console.error('Error loading services:', error);
    }
  }
  
  // Wait for DOM to be ready before loading services
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadServices);
  } else {
    loadServices();
  }
  
  // Add a timeout to detect if all services don't load
  setTimeout(() => {
    if (loadedCount < serviceFiles.length) {
      console.warn(`Not all services loaded. Loaded ${loadedCount}/${serviceFiles.length}`);
    }
  }, 10000); // 10 second timeout
})();
