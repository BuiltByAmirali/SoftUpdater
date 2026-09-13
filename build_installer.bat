@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SoftUpdater - Build the official Setup EXE

echo ==================================================
echo   SoftUpdater - build the OFFICIAL installer
echo   Step 1: build the app with PyInstaller
echo   Step 2: pack it into a real Setup EXE with
echo           Inno Setup 6. If Inno Setup is not
echo           installed, it is downloaded and
echo           installed automatically.
echo   Output: dist\installer\SoftUpdater-Setup-1.0.0.exe
echo           (1.0.0 = whatever the VERSION file says)
echo ==================================================
echo.

rem ---- version: single source of truth = the VERSION file ----
rem for /f strips CRLF properly (set /p would keep a stray CR byte).
set "VER="
if exist "VERSION" for /f "usebackq delims=" %%A in ("VERSION") do if not defined VER set "VER=%%A"
if not defined VER (
    echo [ERROR] The VERSION file is missing or empty.
    pause
    exit /b 1
)
echo App version: %VER%
echo.

rem ---- 0. Python launcher ----
where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python launcher "py" was not found.
    echo Please install Python 3.10 or newer from https://www.python.org/downloads/
    echo and enable "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

rem ---- 1. virtual environment + dependencies ----
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
if not exist "build" mkdir "build"

echo [1/5] Installing dependencies - this can take a few minutes...
echo       (full output: build\log-pip.txt)
python -m pip install --upgrade pip -r requirements.txt pyinstaller >"build\log-pip.txt" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    echo Opening the log file...
    start notepad "build\log-pip.txt"
    pause
    exit /b 1
)
echo       Dependencies OK.

rem ---- 2. clean previous output ----
echo [2/5] Cleaning previous build output...
if exist "build\app" rmdir /s /q "build\app"
if exist "dist" rmdir /s /q "dist"
if exist "SoftUpdater.spec" del /q "SoftUpdater.spec"

rem ---- 3. version resource + PyInstaller build ----
echo [3/5] Building the application - this can take a few minutes...
echo       (full output: build\log-pyinstaller.txt)
set "VINFO=%TEMP%\SoftUpdater_version_info.txt"
python "installer\make_version_info.py" "%VER%" "%VINFO%"
if errorlevel 1 (
    echo [ERROR] Could not create the version resource file.
    pause
    exit /b 1
)
pyinstaller --noconfirm --clean --windowed --onefile --name SoftUpdater ^
    --distpath "build\app" --icon "app\assets\app.ico" --version-file "%VINFO%" run.py ^
    >"build\log-pyinstaller.txt" 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Opening the log file...
    start notepad "build\log-pyinstaller.txt"
    pause
    exit /b 1
)
if not exist "build\app\SoftUpdater.exe" (
    echo [ERROR] build\app\SoftUpdater.exe was not produced. Opening the log file...
    start notepad "build\log-pyinstaller.txt"
    pause
    exit /b 1
)
echo       Application built: build\app\SoftUpdater.exe - now packing it...

rem ---- 4. make sure Inno Setup 6 is available ----
echo [4/5] Looking for Inno Setup 6...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if defined ISCC goto have_iscc

echo       Inno Setup is not installed - installing it automatically.
set "INNOEXE=%CD%\build\innosetup-setup.exe"
if exist "%INNOEXE%" goto install_inno

echo       Downloading Inno Setup from the official GitHub releases...
echo       (full output: build\log-innosetup-download.txt)
powershell -NoProfile -ExecutionPolicy Bypass -Command "try{ $ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $vs='6.7.3','6.7.2','6.7.1','6.7.0','6.6.1','6.6.0','6.5.4','6.5.3','6.5.2','6.5.1','6.5.0','6.4.3'; foreach($v in $vs){ $t=$v.Replace('.','_'); $u='https://github.com/jrsoftware/issrc/releases/download/is-'+$t+'/innosetup-'+$v+'.exe'; Write-Output ('Trying '+$u); try{ Invoke-WebRequest -Uri $u -OutFile '%INNOEXE%' -UseBasicParsing -TimeoutSec 300 }catch{ Write-Output ('FAILED '+$v+': '+$_.Exception.Message); Remove-Item '%INNOEXE%' -ErrorAction SilentlyContinue; continue }; $f=Get-Item '%INNOEXE%'; $fs=[IO.File]::OpenRead('%INNOEXE%'); $b=New-Object byte[] 2; $null=$fs.Read($b,0,2); $fs.Close(); if(($b[0]-eq 77)-and($b[1]-eq 90)-and($f.Length -gt 3MB)){ Write-Output ('Downloaded and verified: '+$f.Length+' bytes'); exit 0 }; Write-Output ('Not a valid exe, trying next version: '+$v); Remove-Item '%INNOEXE%' -ErrorAction SilentlyContinue } }catch{ Write-Output ('ERROR: '+$_.Exception.Message) }; exit 1" >"build\log-innosetup-download.txt" 2>&1
if errorlevel 1 (
    echo [ERROR] Could not download Inno Setup. Check your internet connection.
    echo You can also install it manually from https://jrsoftware.org/isdl.php
    echo and then run this script again.
    start notepad "build\log-innosetup-download.txt"
    pause
    exit /b 1
)
echo       Download OK and verified.

:install_inno
echo       Installing Inno Setup silently...
echo       IF WINDOWS ASKS FOR PERMISSION, CLICK YES.
"%INNOEXE%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /LOG="%CD%\build\log-innosetup-install.txt"
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC (
    echo [ERROR] Inno Setup was downloaded but did not install.
    echo If you clicked NO on the Windows permission question, just run
    echo this script again and click YES. If the problem stays, delete
    echo the file build\innosetup-setup.exe and run this script again.
    echo Opening the installation log...
    start notepad "build\log-innosetup-install.txt"
    pause
    exit /b 1
)

:have_iscc
echo       Compiler found: "%ISCC%"

rem ---- 5. compile the Setup EXE ----
echo [5/5] Compiling the official Setup EXE with Inno Setup...
"%ISCC%" /DAPP_VERSION=%VER% "installer\SoftUpdater.iss" >"build\log-iscc.txt" 2>&1
set "EC=%errorlevel%"
type "build\log-iscc.txt"
if not "%EC%"=="0" (
    echo [ERROR] Inno Setup compilation failed. Opening the log file...
    start notepad "build\log-iscc.txt"
    pause
    exit /b 1
)

set "SETUP=dist\installer\SoftUpdater-Setup-%VER%.exe"
if not exist "%SETUP%" (
    echo [ERROR] The Setup EXE was not produced. Opening the log file...
    start notepad "build\log-iscc.txt"
    pause
    exit /b 1
)

rem ---- checksum for the release page ----
echo.
echo ==================================================
echo   BUILD OK - the OFFICIAL INSTALLER is ready:
echo     %SETUP%
echo.
echo   THIS file shows a real install wizard and is
echo   the ONLY file to publish or send to friends.
echo   Its wizard shows the license page, copies the
echo   app per-user - no admin needed - creates Start
echo   Menu and Desktop shortcuts and registers an
echo   uninstaller in Apps and features.
echo.
echo   Its SHA-256 fingerprint - put it next to the
echo   file on your download page:
echo.
certutil -hashfile "%SETUP%" SHA256
echo ==================================================
echo.
echo Opening the output folder...
if exist "dist\installer" start "" "dist\installer"
pause
endlocal
