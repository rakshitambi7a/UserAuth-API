#!/bin/bash

# Quick start script for User Management API (Refactored)
# This script activates the virtual environment and starts the application

set -e

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

echo "🚀 Starting User Management API..."
source venv/bin/activate

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Make sure you're in the correct directory."
    exit 1
fi

# Start the application
echo "🌐 Starting server on http://localhost:5009"
python app.py
