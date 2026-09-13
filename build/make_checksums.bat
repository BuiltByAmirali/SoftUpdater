@echo off
setlocal EnableExtensions
rem ============================================================
rem  SoftUpdater - generate SHA256SUMS.txt for the built
rem  installers (64-bit and/or win32) before a GitHub Release.
rem
rem  Usage: double-click AFTER running build_installer.bat
rem         and/or build_installer32.bat. Writes
rem         dist\installer\SHA256SUMS.txt (standard
rem         "<hash>  <filename>" lines, verifiable with
rem         certutil / sha256sum -c).
rem ============================================================
cd /d "%~dp0.." || exit /b 1

echo SoftUpdater - SHA-256 checksum generator
echo.

if not exist "dist\installer" (
    echo [ERROR] dist\installer not found.
    echo         Run build_installer.bat and/or build_installer32.bat first.
    pause
    exit /b 1
)

set "OUTFILE=dist\installer\SHA256SUMS.txt"
if exist "%OUTFILE%" del "%OUTFILE%" >nul 2>&1

set /a COUNT=0
for %%F in ("dist\installer\SoftUpdater-Setup-*.exe") do (
    set /a COUNT+=1
    echo   hashing %%~nxF ...
    for /f "delims=" %%H in ('certutil -hashfile "%%~fF" SHA256 ^| find /v ":"') do (
        >>"%OUTFILE%" echo %%H  %%~nxF
    )
)

if %COUNT%==0 (
    echo [ERROR] No SoftUpdater-Setup-*.exe files found in dist\installer.
    pause
    exit /b 1
)

echo.
echo Wrote %OUTFILE% with %COUNT% hash^(es^):
echo.
type "%OUTFILE%"
echo.
echo Next steps:
echo   1. Create the GitHub Release for the version in the VERSION file.
echo   2. Upload EVERY Setup EXE above TOGETHER WITH SHA256SUMS.txt.
echo   3. Users verify with: certutil -hashfile ^<file^> SHA256
echo.
pause
exit /b 0
