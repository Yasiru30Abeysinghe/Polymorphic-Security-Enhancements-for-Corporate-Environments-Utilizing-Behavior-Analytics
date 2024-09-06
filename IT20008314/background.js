chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
      const url = new URL(details.url);
      const domain = url.hostname;
  
      // Communicate with the backend phishing detection system
      fetch('http://localhost:5000/check_domain', {  // Your Flask server URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ domain: domain })
      })
      .then(response => response.json())
      .then(data => {
        if (data.risk_status === 'Warning: Potential Phishing Site') {
          // Show an alert or take other action
          alert(`Warning! The site ${domain} may be a phishing site.`);
          
          // Optionally redirect the user to a warning page
          chrome.tabs.update(details.tabId, { url: chrome.runtime.getURL("warning.html") });
        }
      })
      .catch(error => console.error('Error:', error));
    },
    { urls: ["<all_urls>"] },  // Listen to all URLs
    ["blocking"]  // Block the request until a decision is made
  );
  