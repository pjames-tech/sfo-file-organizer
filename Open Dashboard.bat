@echo off
:: Smart File Organizer - Web Dashboard Launcher
:: Double-click this file to open the dashboard in your browser!

title Smart File Organizer Dashboard

:: Change to the script directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================
    echo   Python is not installed on this computer
    echo ============================================
    echo.
    echo Please install Python from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

:: Launch the dashboard
echo.
echo ====================================================
echo   Smart File Organizer - Web Dashboard
echo ====================================================
echo.
echo Starting server... Your browser will open shortly.
echo.
echo Keep this window open while using the dashboard.
echo Close this window when you're done.
echo.

python dashboard.py
