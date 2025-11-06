#!/bin/bash
# Vercel Ignored Build Step for web/
# Exit 0 = Build
# Exit 1 = Skip build

echo "Checking for web/ changes..."

# Check if web/ directory or its dependencies changed
if git diff HEAD^ HEAD --quiet -- \
  web/ \
  shared/ \
  package.json \
  package-lock.json \
  pnpm-lock.yaml \
  turbo.json
then
  echo "✓ No web changes - SKIPPING build"
  exit 1  # Skip
else
  echo "✓ Web changes detected - BUILDING"
  exit 0  # Build
fi
