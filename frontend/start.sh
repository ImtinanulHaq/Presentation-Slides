#!/bin/bash

# Start serve with proper configuration
npx serve -s build -l 3000 \
  --no-clipboard \
  --single \
  --spa \
  --cors \
  --etag
