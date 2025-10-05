@echo off
REM =================================================================
REM Samplify Virtual Environment Setup Script (Windows)
REM =================================================================
REM This script creates a Python virtual environment for Samplify
REM development and installs all required dependencies.
REM
REM Requirements:
REM   - Python 3.10+ installed and in PATH
REM   - Git installed (for cloning repository)
REM
REM Usage:
REM   setup_env.bat
REM =================================================================

echo.
echo ================================================================
echo Samplify Virtual Environment Setup (Windows)
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

REM Display Python version
echo [INFO] Detected Python version:
python --version
echo.

REM Check Python version is 3.10+
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo [ERROR] Python 3.10+ required, found Python %PYVER%
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 10 (
    echo [ERROR] Python 3.10+ required, found Python %PYVER%
    exit /b 1
)

echo [INFO] Python version check passed
echo.

REM Create virtual environment
echo [INFO] Creating virtual environment in 'venv' directory...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [SUCCESS] Virtual environment created
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

REM Install dependencies
if exist requirements.txt (
    echo [INFO] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
    echo.
) else (
    echo [WARNING] requirements.txt not found, skipping dependency installation
    echo.
)

REM Install development dependencies
if exist requirements-dev.txt (
    echo [INFO] Installing development dependencies from requirements-dev.txt...
    pip install -r requirements-dev.txt
    if errorlevel 1 (
        echo [WARNING] Failed to install development dependencies
    ) else (
        echo [SUCCESS] Development dependencies installed
    )
    echo.
) else (
    echo [INFO] requirements-dev.txt not found, skipping development dependencies
    echo.
)

echo ================================================================
echo Setup Complete!
echo ================================================================
echo.
echo Virtual environment created and activated.
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate the environment, run:
echo   deactivate
echo.
echo Next steps:
echo   1. Run Django migrations: python manage.py migrate
echo   2. Create superuser: python manage.py createsuperuser
echo   3. Run development server: python manage.py runserver
echo.
echo ================================================================
