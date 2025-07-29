#!/bin/bash

# Setup script for User Management API (Refactored)
# This script creates a virtual environment, installs dependencies, and initializes the database
# Usage: ./setup.sh [--dev|-d] for development dependencies

set -e  # Exit on any error

echo "🚀 Setting up User Management API..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python $required_version+ is required. Found Python $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📦 Installing dev dependencies..."
pip install -r requirements-dev.txt

# Check if .env exists, if not copy from example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please review and update .env file with your settings"
    else
        echo "ℹ️  No .env.example found, skipping .env creation"
    fi
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
python db/init_db.py

# Run password migration if needed
if [ -f "migrations/migrate_passwords.py" ]; then
    echo "🔐 Running password migration..."
    python migrations/migrate_passwords.py
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the application: python app.py"
echo "  3. Access the API at: http://localhost:5009"
echo ""
echo "To run tests:"
echo "  python -m pytest"
echo ""
echo "To install development dependencies:"
echo "  ./setup.sh --dev"
echo ""
echo "To deactivate the virtual environment later, run: deactivate"