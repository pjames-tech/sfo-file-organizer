@echo off
:: Smart File Organizer - Release Packager
:: Prepares a clean folder ready to be zipped and sent to users

title Smart File Organizer - Packaging Release

cd /d "%~dp0"

echo.
echo ========================================================
echo      PACKAGING FOR DISTRIBUTION
echo ========================================================
echo.

:: 1. Check if EXE exists
if not exist "dist\Smart File Organizer.exe" (
    echo Error: Executable not found!
    echo Please run BUILD_EXE.bat first.
    echo.
    pause
    exit /b 1
)

:: 2. Create Release folder
echo Cleaning Release folder...
if exist "Release" rmdir /s /q "Release"
mkdir "Release"

:: 3. Copy Key Files
echo Copying files...
copy "dist\Smart File Organizer.exe" "Release\" >nul
copy "QUICK START.md" "Release\READ ME FIRST.txt" >nul

echo.
echo ========================================================
echo                   PACKAGE READY!
echo ========================================================
echo.
echo A "Release" folder has been created with everything needed.
echo.
echo Instructions for you:
echo 1. Open the "Release" folder
echo 2. Right-click the files -> Send to -> Compressed (zipped) folder
echo 3. Send that ZIP file to your users!
echo.
pause
explorer Release
