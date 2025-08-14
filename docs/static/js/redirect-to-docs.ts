// Redirect from homepage to documentation
(() => {
  // Define types
  interface Window {
    location: Location;
  }

  // Check if we're on the homepage
  const isHomepage = (): boolean => {
    const path: string = window.location.pathname;
    return path === '/clickup-mcp-server/' || path === '/clickup-mcp-server';
  };

  // Perform the redirect if needed
  const redirectToDocs = (): void => {
    if (isHomepage()) {
      const targetUrl: string = `${window.location.origin}/clickup-mcp-server/document/introduction`;
      window.location.replace(targetUrl);
    }
  };

  // Execute the redirect function
  redirectToDocs();
})();
