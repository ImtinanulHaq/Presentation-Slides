const express = require('express');
const path = require('path');
const app = express();

const PORT = process.env.PORT || 3000;
const BUILD_DIR = path.join(__dirname, 'build');

// Serve static files with correct MIME types
app.use(express.static(BUILD_DIR, {
  setHeaders: (res, path) => {
    // Set correct MIME type for CSS
    if (path.endsWith('.css')) {
      res.setHeader('Content-Type', 'text/css');
    }
    // Set correct MIME type for JS
    if (path.endsWith('.js')) {
      res.setHeader('Content-Type', 'application/javascript');
    }
    // Cache headers for static assets
    if (path.includes('/static/')) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    }
  }
}));

// SPA: Send index.html for all non-file requests
app.get('*', (req, res) => {
  res.setHeader('Content-Type', 'text/html');
  res.sendFile(path.join(BUILD_DIR, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend server running on http://localhost:${PORT}`);
  console.log(`Serving from: ${BUILD_DIR}`);
});
