@echo off
setlocal
title Python Project Setup

echo ========================================
echo          PYTHON PROJECT SETUP
echo ========================================
echo.

:: Check Python
echo [1/4] Checking Python...

where python >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or is not in PATH.
    echo.
    echo Download Python from:
    echo https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

python --version

if %errorlevel% neq 0 (
    echo [ERROR] Python is not working correctly.
    pause
    exit /b 1
)

echo Python found!
echo.

:: Check pip
echo [2/4] Checking pip...

python -m pip --version >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] pip is not available.
    echo Attempting to install pip...

    python -m ensurepip --upgrade

    if %errorlevel% neq 0 (
        echo [ERROR] Unable to install pip.
        pause
        exit /b 1
    )
)

echo pip found!
echo.

:: Create virtual environment
echo [3/4] Creating virtual environment...

if not exist ".venv" (
    python -m venv .venv

    if %errorlevel% neq 0 (
        echo [ERROR] Unable to create the virtual environment.
        pause
        exit /b 1
    )

    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)

echo.

:: Activate virtual environment
call ".venv\Scripts\activate.bat"

if %errorlevel% neq 0 (
    echo [ERROR] Unable to activate the virtual environment.
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

:: Install dependencies
echo [4/4] Installing dependencies...

python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)

if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    python -m pip install requests
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo        INSTALLATION COMPLETED
echo ========================================
echo.

echo Python:
python --version

echo.
echo Requests:
python -m pip show requests | findstr "Name Version"

echo.
echo ========================================
echo          STARTING APPLICATION
echo ========================================
echo.

:: ipgrabber.py must be in the same folder as setup.bat
if not exist "ipgrabber.py" (
    echo [ERROR] ipgrabber.py was not found.
    echo.
    echo Make sure ipgrabber.py is located in the
    echo same folder as setup.bat.
    echo.
    pause
    exit /b 1
)

echo [OK] ipgrabber.py found.
echo [OK] Starting application...
echo.

python ipgrabber.py

echo.
echo ========================================
echo          APPLICATION CLOSED
echo ========================================
echo.

pause
