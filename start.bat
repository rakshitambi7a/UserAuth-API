@echo off
REM Quick start script for User Management API (Windows - Refactored)
REM This script activates the virtual environment and starts the application

if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "app.py" (
    echo ❌ app.py not found. Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo 🚀 Starting User Management API...
call venv\Scripts\activate.bat

echo 🌐 Starting server on http://localhost:5009
python app.py

pause
