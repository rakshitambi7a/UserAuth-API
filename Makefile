# Makefile for User Management API

.PHONY: help setup install run clean test

# Default target
help:
	@echo "Available commands:"
	@echo "  setup    - Create virtual environment and install dependencies"
	@echo "  install  - Install dependencies in existing environment"
	@echo "  run      - Start the application"
	@echo "  clean    - Remove virtual environment and temporary files"
	@echo "  test     - Run tests (if available)"

# Setup virtual environment and install dependencies
setup:
	@echo "🚀 Setting up User Management API..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && python init_db.py
	@echo "✅ Setup complete! Run 'make run' to start the application."

# Install dependencies only
install:
	. venv/bin/activate && pip install -r requirements.txt

# Run the application
run:
	. venv/bin/activate && python app.py

# Clean up
clean:
	rm -rf venv/
	rm -f *.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Run tests (placeholder for future implementation)
test:
	@echo "Tests not implemented yet"
