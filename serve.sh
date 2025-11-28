#!/bin/bash
# Simple script to serve the generated site

cd docs
echo "Starting web server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
echo "RSS Feed: http://localhost:8000/feed.xml"
echo ""
python3 -m http.server 8000
