@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SoftUpdater - Build the Windows 7 / 32-bit Setup EXE

echo ==================================================
echo   SoftUpdater - build the Windows 7 / 32-bit Setup
echo   This one runs on: Windows 7 SP1 / 8 / 8.1 / 10 / 11
echo                     32-bit AND 64-bit Windows.
echo   It needs Python 3.8 32-bit installed ONCE (py -3.8-32).
echo   Output: dist\installer\SoftUpdater-Setup-1.0.0-win32.exe
echo           (1.0.0 = whatever the VERSION file says)
echo.
echo   To publish BOTH installers, first run
echo   build_installer.bat (Windows 10/11, 64-bit) and then
echo   this script - this one does NOT delete the other file.
echo ==================================================
echo.

rem ---- version: single source of truth = the VERSION file ----
set "VER="
if exist "VERSION" for /f "usebackq delims=" %%A in ("VERSION") do if not defined VER set "VER=%%A"
if not defined VER (
    echo [ERROR] The VERSION file is missing or empty.
    pause
    exit /b 1
)
echo App version: %VER%
echo.

rem ---- 0. Python 3.8 32-bit is REQUIRED for this build ----
rem Python 3.8 is the last Python that supports Windows 7, and the
rem 32-bit build is what makes the app run on 32-bit Windows too.
py -3.8-32 -c "import sys" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.8 32-bit was not found - this build needs it.
    echo Your normal Python is NOT used for this build, so nothing breaks.
    echo.
    echo One-time fix: download and run
    echo   https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe
    echo Keep the default options - it installs next to your current
    echo Python and registers itself as py -3.8-32.
    echo Then run this script again.
    pause
    exit /b 1
)
echo Found Python 3.8 32-bit:
py -3.8-32 -c "import sys; print('  ' + sys.executable)"
echo.

rem ---- 1. virtual environment + dependencies ----
if not exist ".venv32\Scripts\python.exe" (
    echo Creating the Windows 7 build environment...
    py -3.8-32 -m venv .venv32
    if errorlevel 1 (
        echo [ERROR] Could not create the .venv32 environment.
        pause
        exit /b 1
    )
)
call ".venv32\Scripts\activate.bat"
if not exist "build" mkdir "build"

echo [1/5] Installing the Windows 7 compatible dependencies...
echo       (full output: build\log-pip32.txt)
python -m pip install --upgrade pip -r requirements-win7.txt >"build\log-pip32.txt" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    echo Opening the log file...
    start notepad "build\log-pip32.txt"
    pause
    exit /b 1
)
echo       Dependencies OK - this build uses PyQt5 5.15, the last Qt
echo       that supports Windows 7 and 32-bit Windows.

rem ---- 2. clean ONLY this build's output - keep the 64-bit Setup ----
echo [2/5] Cleaning previous 32-bit build output...
if exist "build\app32" rmdir /s /q "build\app32"
if exist "build\pyi32" rmdir /s /q "build\pyi32"
if exist "build\SoftUpdater.spec" del /q "build\SoftUpdater.spec"
if exist "dist\installer\SoftUpdater-Setup-%VER%-win32.exe" del /q "dist\installer\SoftUpdater-Setup-%VER%-win32.exe"

rem ---- 3. version resource + PyInstaller build ----
echo [3/5] Building the application - this can take a few minutes...
echo       (full output: build\log-pyinstaller32.txt)
set "VINFO=%TEMP%\SoftUpdater_version_info.txt"
python "installer\make_version_info.py" "%VER%" "%VINFO%"
if errorlevel 1 (
    echo [ERROR] Could not create the version resource file.
    pause
    exit /b 1
)
rem ---- NOTE on paths: the icon and the script are given as ABSOLUTE
rem ---- paths ON PURPOSE. PyInstaller resolves a relative --icon path
rem ---- against the --specpath folder (build\) and NOT against the
rem ---- project folder - that is exactly what broke the previous build
rem ---- with "Icon input file ... build\app\assets\app.ico not found".
rem ---- Also: the Universal CRT (x86) is bundled into the exe so that it
rem ---- starts even on a Windows 7 SP1 machine that never received any
rem ---- Windows Updates. The 5.13 bootloader itself was verified to be
rem ---- statically linked, so with the UCRT inside the bundle the app
rem ---- boots on a clean Windows 7 as well.
set "UCRT_DIR=%SystemRoot%\SysWOW64"
if not exist "%UCRT_DIR%\ucrtbase.dll" set "UCRT_DIR=%SystemRoot%\System32"
set "UCRT_ARGS="
if exist "%UCRT_DIR%\ucrtbase.dll" if exist "%UCRT_DIR%\api-ms-win-crt-runtime-l1-1-0.dll" set "UCRT_ARGS=--add-binary "%UCRT_DIR%\api-ms-win-crt-*.dll;." --add-binary "%UCRT_DIR%\ucrtbase.dll;.""
if defined UCRT_ARGS (
    echo       Bundling the Universal CRT ^(x86^) from "%UCRT_DIR%"...
) else (
    echo       NOTE: Universal CRT DLLs not found - continuing without
    echo       them. Windows 8/10/11 targets are fine either way.
)
pyinstaller --noconfirm --clean --windowed --onefile --name SoftUpdater ^
    --distpath "build\app32" --workpath "build\pyi32" --specpath "build" ^
    --icon "%CD%\app\assets\app.ico" %UCRT_ARGS% --version-file "%VINFO%" "%CD%\run.py" ^
    >"build\log-pyinstaller32.txt" 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Opening the log file...
    start notepad "build\log-pyinstaller32.txt"
    pause
    exit /b 1
)
if not exist "build\app32\SoftUpdater.exe" (
    echo [ERROR] build\app32\SoftUpdater.exe was not produced. Opening the log file...
    start notepad "build\log-pyinstaller32.txt"
    pause
    exit /b 1
)
rem ---- safety gate: prove the exe is really the 32-bit build (the log
rem ---- line "Bootloader ... Windows-32bit-intel\runw.exe" only appears
rem ---- when a 32-bit Python environment produced it)
findstr /I /C:"Windows-32bit-intel" "build\log-pyinstaller32.txt" >nul
if errorlevel 1 (
    echo [ERROR] The exe was NOT built from the 32-bit Python environment.
    echo         It would not run on Windows 7 or on 32-bit Windows.
    echo         Fix: delete the .venv32 folder and run this script again
    echo         so it is recreated with py -3.8-32.
    echo Opening the log file...
    start notepad "build\log-pyinstaller32.txt"
    pause
    exit /b 1
)
echo       Application built: build\app32\SoftUpdater.exe - now packing it...

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

rem ---- 5. compile the Windows 7 / 32-bit Setup EXE ----
echo [5/5] Compiling the Windows 7 / 32-bit Setup EXE with Inno Setup...
"%ISCC%" /DAPP_VERSION=%VER% "installer\SoftUpdater-win32.iss" >"build\log-iscc32.txt" 2>&1
set "EC=%errorlevel%"
type "build\log-iscc32.txt"
if not "%EC%"=="0" (
    echo [ERROR] Inno Setup compilation failed. Opening the log file...
    start notepad "build\log-iscc32.txt"
    pause
    exit /b 1
)

set "SETUP=dist\installer\SoftUpdater-Setup-%VER%-win32.exe"
if not exist "%SETUP%" (
    echo [ERROR] The Setup EXE was not produced. Opening the log file...
    start notepad "build\log-iscc32.txt"
    pause
    exit /b 1
)

rem ---- checksum for the release page ----
echo.
echo ==================================================
echo   BUILD OK - the Windows 7 / 32-bit Setup is ready:
echo     %SETUP%
echo.
echo   This file installs on: Windows 7 SP1 / 8 / 8.1 /
echo   10 / 11 - BOTH 32-bit and 64-bit Windows.
echo.
echo   Publish BOTH files together:
echo     SoftUpdater-Setup-1.0.0.exe      - Windows 10/11, 64-bit
echo     SoftUpdater-Setup-1.0.0-win32.exe - everything above,
echo                                         plus Windows 7/8
echo   and tell people: if unsure, use the -win32 file.
echo.
echo   Its SHA-256 fingerprint:
echo.
certutil -hashfile "%SETUP%" SHA256
echo ==================================================
echo.
echo Opening the output folder...
if exist "dist\installer" start "" "dist\installer"
pause
endlocal
