#!/bin/bash
set -e

# Build React application
npm install
npm run build

# Verify build
if [ ! -d "build" ]; then
  echo "Build failed: build directory not found"
  exit 1
fi

echo "Frontend build completed successfully"
