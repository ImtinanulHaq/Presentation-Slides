#!/bin/bash
set -e

echo "=== Building Presentation Tools Frontend ==="
echo "Node version:"
node --version
echo "NPM version:"
npm --version

echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Verifying react-scripts is available..."
if [ -f "./node_modules/.bin/react-scripts" ]; then
    echo "✓ react-scripts found at ./node_modules/.bin/react-scripts"
else
    echo "✗ react-scripts NOT found - checking node_modules"
    find node_modules -name "react-scripts" -type d 2>/dev/null || echo "react-scripts directory not found"
    exit 1
fi

echo ""
echo "Building application..."
CI=false NODE_ENV=production npm run build

echo ""
echo "✓ Build completed successfully!"
if [ -d "build" ]; then
    echo "✓ Build folder exists with size: $(du -sh build)"
fi
