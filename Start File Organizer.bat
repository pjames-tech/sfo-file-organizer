@echo off
:: Smart File Organizer - Desktop GUI Launcher
:: Double-click this file to open the application!

title Smart File Organizer

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

:: Launch the GUI
echo Starting Smart File Organizer...
pythonw gui.py

:: If pythonw fails, try python (will show console briefly)
if errorlevel 1 (
    python gui.py
)
