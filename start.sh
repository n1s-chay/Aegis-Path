#!/bin/bash

# Aegis-Path Startup Script

echo "=========================================="
echo "  Starting Aegis-Path Women Safety App"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q flask flask-cors opencv-python-headless numpy requests

echo "✓ Dependencies installed"

# Start the server
echo ""
echo "=========================================="
echo "  Starting API Server"
echo "=========================================="
echo ""
echo "Server will be available at:"
echo "  - http://localhost:5000"
echo ""
echo "Open index.html in your browser to use the app"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
