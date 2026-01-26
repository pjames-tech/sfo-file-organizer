@echo off
:: Smart File Organizer - Build Script
:: Creates a standalone .exe using PyInstaller

title Smart File Organizer - Building Executable

cd /d "%~dp0"

echo.
echo ========================================================
echo      BUILDING STANDALONE EXECUTABLE
echo ========================================================
echo.

:: Check PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/2] Cleaning previous builds...
rmdir /s /q build dist 2>nul
del /f /q *.spec 2>nul

echo.
echo [2/2] Building 'Smart File Organizer.exe'...
echo       This may take a minute...
echo.

:: Build the EXE
:: --noconsole: Don't show terminal window
:: --onefile: Bundle everything into a single .exe
:: --name: Name of the output file
:: --add-data: Include necessary data files (custom_rules.json)
:: --icon: (Optional) We'll skip for now as we don't have an .ico file yet

pyinstaller --noconsole --onefile --name "Smart File Organizer" ^
    --add-data "custom_rules.json;." ^
    --collect-all rules_ui ^
    gui.py

if errorlevel 1 (
    echo.
    echo !! BUILD FAILED !!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo                   BUILD COMPLETE!
echo ========================================================
echo.
echo Your standalone executable is ready:
echo.
echo    dist\Smart File Organizer.exe
echo.
echo You can copy this file ANYWHERE and run it without Python!
echo.
pause
explorer dist
