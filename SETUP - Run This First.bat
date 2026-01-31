@echo off
:: SFO File Organizer - First Time Setup
:: Run this ONCE after downloading the application

title SFO File Organizer - First Time Setup

cd /d "%~dp0"

echo.
echo ========================================================
echo      SFO FILE ORGANIZER - FIRST TIME SETUP
echo ========================================================
echo.
echo This will set up everything you need to get started.
echo.
pause

:: Step 1: Check Python
echo.
echo [Step 1/3] Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo !! Python is NOT installed !!
    echo.
    echo Please follow these steps:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Click the big yellow "Download Python" button
    echo   3. Run the installer
    echo   4. IMPORTANT: Check the box "Add Python to PATH"
    echo   5. Click "Install Now"
    echo   6. After installation, run this setup again
    echo.
    echo Opening Python download page in your browser...
    start https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo OK - Python is installed!

:: Step 2: Install dependencies
echo.
echo [Step 2/3] Installing required packages...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not install some packages, but the app should still work.
) else (
    echo OK - Packages installed!
)

:: Step 3: Create desktop shortcuts
echo.
echo [Step 3/3] Creating desktop shortcuts...
call "Create Desktop Shortcuts.bat" >nul 2>&1
echo OK - Shortcuts created!

echo.
echo ========================================================
echo                   SETUP COMPLETE!
echo ========================================================
echo.
echo You now have two shortcuts on your Desktop:
echo.
echo   [1] FILE ORGANIZER (Desktop App)
echo       Click this for the main application.
echo       Use this to organize files in any folder.
echo.
echo   [2] FILE ORGANIZER DASHBOARD (Web Browser)
echo       Click this to open the advanced dashboard.
echo       Manage rules, view history, and more.
echo.
echo ========================================================
echo.
echo Would you like to start the File Organizer now? (Y/N)
set /p ANSWER="> "
if /i "%ANSWER%"=="Y" (
    start "" "Start File Organizer.bat"
)

echo.
echo Setup complete! You can close this window.
echo.
pause
