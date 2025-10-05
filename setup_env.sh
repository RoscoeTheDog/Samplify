#!/usr/bin/env bash
# =================================================================
# Samplify Virtual Environment Setup Script (macOS/Linux)
# =================================================================
# This script creates a Python virtual environment for Samplify
# development and installs all required dependencies.
#
# Requirements:
#   - Python 3.10+ installed
#   - Git installed (for cloning repository)
#
# Usage:
#   chmod +x setup_env.sh
#   ./setup_env.sh
# =================================================================

set -e  # Exit on error

echo ""
echo "================================================================"
echo "Samplify Virtual Environment Setup (macOS/Linux)"
echo "================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10+ using your package manager:"
    echo "  - macOS: brew install python@3.11"
    echo "  - Ubuntu/Debian: sudo apt-get install python3.11"
    echo "  - Fedora: sudo dnf install python3.11"
    exit 1
fi

# Display Python version
echo "[INFO] Detected Python version:"
python3 --version
echo ""

# Check Python version is 3.10+
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "[ERROR] Python 3.10+ required, found Python $PYTHON_VERSION"
    exit 1
fi

echo "[INFO] Python version check passed"
echo ""

# Create virtual environment
echo "[INFO] Creating virtual environment in 'venv' directory..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi
echo "[SUCCESS] Virtual environment created"
echo ""

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi
echo "[SUCCESS] Virtual environment activated"
echo ""

# Upgrade pip
echo "[INFO] Upgrading pip to latest version..."
python -m pip install --upgrade pip || echo "[WARNING] Failed to upgrade pip, continuing anyway..."
echo ""

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
    echo "[SUCCESS] Dependencies installed"
    echo ""
else
    echo "[WARNING] requirements.txt not found, skipping dependency installation"
    echo ""
fi

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    echo "[INFO] Installing development dependencies from requirements-dev.txt..."
    if pip install -r requirements-dev.txt; then
        echo "[SUCCESS] Development dependencies installed"
    else
        echo "[WARNING] Failed to install development dependencies"
    fi
    echo ""
else
    echo "[INFO] requirements-dev.txt not found, skipping development dependencies"
    echo ""
fi

echo "================================================================"
echo "Setup Complete!"
echo "================================================================"
echo ""
echo "Virtual environment created and activated."
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate the environment, run:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "  1. Run Django migrations: python manage.py migrate"
echo "  2. Create superuser: python manage.py createsuperuser"
echo "  3. Run development server: python manage.py runserver"
echo ""
echo "================================================================"
