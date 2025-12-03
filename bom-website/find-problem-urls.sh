#!/bin/bash

# Script to find old date-based URLs in content files
# Searches for patterns like /YYYY/MM/DD/ or deathbynumbers.org/YYYY/MM/DD/

echo "Searching for old date-based URLs in content files..."
echo "======================================================"
echo ""

# Search for date-based URL patterns in markdown files
grep -rn "deathbynumbers\.org/[0-9]\{4\}/[0-9]\{2\}/[0-9]\{2\}/" content/ --include="*.md" | while read line; do
    echo "$line"
done

echo ""
echo "======================================================"
echo "Search complete!"
