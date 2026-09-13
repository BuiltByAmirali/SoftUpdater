@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SoftUpdater - Run

echo ============================================
echo   SoftUpdater - starting application
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python launcher "py" was not found.
    echo Please install Python 3.10 or newer from https://www.python.org/downloads/
    echo and enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo Starting SoftUpdater...
python run.py
if errorlevel 1 (
    echo.
    echo [ERROR] The application exited with an error.
    pause
)
endlocal
