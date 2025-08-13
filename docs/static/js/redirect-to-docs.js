// Redirect from homepage to documentation
(function() {
  // Only redirect on the homepage
  if (window.location.pathname === '/clickup-mcp-server/' || 
      window.location.pathname === '/clickup-mcp-server') {
    window.location.replace(window.location.origin + '/clickup-mcp-server/document/introduction');
  }
})();
