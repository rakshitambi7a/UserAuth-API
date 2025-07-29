@echo off
REM Setup script for User Management API (Windows - Refactored)
REM This script creates a virtual environment, installs dependencies, and initializes the database
REM Usage: setup.bat [dev] for development dependencies

echo 🚀 Setting up User Management API...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip



REM Install development dependencies (optional)
echo 📦 Installing dev dependencies...
pip install -r requirements-dev.txt

REM Check if .env exists, if not copy from example
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Creating .env file from template...
        copy ".env.example" ".env" >nul
        echo ⚠️  Please review and update .env file with your settings
    ) else (
        echo ℹ️  No .env.example found, skipping .env creation
    )
) else (
    echo ✅ .env file already exists
)

REM Initialize database
echo 🗄️  Initializing database...
python db\init_db.py

REM Run password migration if needed
if exist "migrations\migrate_passwords.py" (
    echo 🔐 Running password migration...
    python migrations\migrate_passwords.py
)

echo.
echo 🎉 Setup complete!
echo.
echo To start the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the application: python app.py
echo   3. Access the API at: http://localhost:5009
echo.
echo To run tests:
echo   python -m pytest
echo.
echo To install development dependencies:
echo   setup.bat dev
echo.
echo To deactivate the virtual environment later, run: deactivate

pause
