@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SoftUpdater - Build EXE

echo ============================================
echo   SoftUpdater - PORTABLE build (ONE single exe)
echo   NOTE: this creates a portable folder,
echo   NOT an installer. For the real Setup
echo   EXE to publish, run build_installer.bat
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
echo Installing dependencies (this can take a few minutes)...
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo Cleaning previous build output...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "SoftUpdater.spec" del /q "SoftUpdater.spec"

rem ---- version resource for formal EXE metadata (best effort) ----
set "VER="
if exist "VERSION" set /p VER=<VERSION
if "%VER%"=="" set "VER=1.0.0"
set "VINFO=%TEMP%\SoftUpdater_version_info.txt"
python "installer\make_version_info.py" "%VER%" "%VINFO%" >nul
set "VARG="
if exist "%VINFO%" set "VARG=--version-file %VINFO%"

echo.
echo Building the executable...
pyinstaller --noconfirm --clean --windowed --onefile --name SoftUpdater --icon "app\assets\app.ico" %VARG% run.py
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Read the messages above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   BUILD OK
echo   Your program is ONE single file:
echo     dist\SoftUpdater.exe
echo.
echo   Copy this ONE file to any Windows PC and
echo   run it - no folders needed next to it.
echo.
echo   This is the PORTABLE version (no installer).
echo   To create the official Setup EXE for
echo   publishing, run build_installer.bat
echo ============================================
echo.
echo Opening the output folder...
if exist "dist" start "" "dist"
pause
endlocal
