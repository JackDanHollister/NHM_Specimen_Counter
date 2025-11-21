#!/bin/bash
# YOLO Web Service Startup Script

echo "🔬 Starting YOLO Specimen Counter Web Service..."
echo "================================================"

# Navigate to the yolo directory
cd /home/jack/Desktop/yolo

# Activate conda environment and start Flask
echo "📡 Starting Flask server on port 5000..."
echo "🌐 Local access: http://localhost:5000"
echo "📱 For phone access, start ngrok in another terminal:"
echo "   ngrok http 5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

# Start the Flask app
/home/jack/miniconda3/envs/yolo/bin/python app.py
