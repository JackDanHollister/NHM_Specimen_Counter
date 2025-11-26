#!/bin/bash
# YOLO Web Service Startup Script

echo "🔬 Starting YOLO Specimen Counter Web Service..."
echo "================================================"

# Navigate to the yolo directory
cd /home/appuser/yolo

echo "📡 Starting Flask server on port 5000 (internal access)..."
echo "🌐 Local access: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

# Start the Flask app
/usr/local/bin/python app.py
