#!/bin/bash

# Covered Call App - Run Script
# This script starts the Flask development server

echo "Starting Covered Call App..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Start the Flask application
echo "Starting Flask server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "================================"

python3 app.py