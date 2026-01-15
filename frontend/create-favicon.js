const fs = require('fs');
const path = require('path');

// Create a proper favicon.ico (1x1 transparent PNG in ICO format)
// This is a minimal valid ICO file
const icoHex = '00000100010010100000010018000068040000';
const buffer = Buffer.from(icoHex, 'hex');

const faviconPath = path.join(__dirname, 'public', 'favicon.ico');
fs.writeFileSync(faviconPath, buffer);

console.log('✓ Favicon created at:', faviconPath);
