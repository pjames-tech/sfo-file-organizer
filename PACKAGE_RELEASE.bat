@echo off
:: SFO File Organizer - Release Packager
:: Prepares a clean folder ready to be zipped and sent to users

title SFO File Organizer - Packaging Release

cd /d "%~dp0"

echo.
echo ========================================================
echo      PACKAGING FOR DISTRIBUTION
echo ========================================================
echo.

:: 1. Check if EXE exists
if not exist "dist\SFO File Organizer.exe" (
    echo Error: Executable not found!
    echo Please run BUILD_EXE.bat first.
    echo.
    pause
    exit /b 1
)

:: 2. Build Installer (Optional)
echo.
echo Checking for Inno Setup Compiler...
set "ISCC="

:: Check if ISCC is in PATH first
where ISCC.exe >nul 2>&1
if not errorlevel 1 (
    set "ISCC=ISCC.exe"
    goto :found_iscc
)

:: Check common installation paths
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)
if exist "C:\Users\Victor\AppData\Local\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Users\Victor\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)
if exist "%USERPROFILE%\AppData\Local\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%USERPROFILE%\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)

:: Not found
echo Inno Setup not found. Skipping installer creation.
echo (Install Inno Setup 6 to generate 'SFOFileOrganizer_Setup.exe')
echo.
echo If you have Inno Setup installed elsewhere, add it to your PATH or
echo edit this script to include the correct location.
goto :after_iscc

:found_iscc
echo Found Inno Setup! Compiling installer...
"%ISCC%" "setup.iss"
if errorlevel 1 (
    echo Warning: Installer compilation failed.
) else (
    echo Installer created successfully!
)

:after_iscc

:: 3. Create Release folder
echo.
echo Preparing Release folder...
if exist "Release" rmdir /s /q "Release"
mkdir "Release"

:: 4. Copy Files
echo Copying files to Release...

:: Copy Standalone EXE
if exist "dist\SFO File Organizer.exe" (
    copy "dist\SFO File Organizer.exe" "Release\" >nul
    echo [OK] Standalone EXE copied.
)

:: Copy Installer (if it was built)
if exist "Installer\SFOFileOrganizer_Setup.exe" (
    copy "Installer\SFOFileOrganizer_Setup.exe" "Release\" >nul
    echo [OK] Installer copied.
)

:: Copy Readme
copy "QUICK START.md" "Release\READ ME FIRST.txt" >nul

echo.
echo ========================================================
echo                   PACKAGE READY!
echo ========================================================
echo.
echo The "Release" folder now contains:
if exist "Release\SFO File Organizer.exe" echo  - Standalone Application
if exist "Release\SFOFileOrganizer_Setup.exe" echo  - Installer (Setup)
echo.
echo You can zip this folder and share it!
echo.
pause
explorer Release
