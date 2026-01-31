@echo off
:: SFO File Organizer - Build Script
:: Creates a standalone .exe using PyInstaller

title SFO File Organizer - Building Executable

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
echo [1/2] Cleaning previous builds and caches...
rmdir /s /q build dist __pycache__ 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
:: Note: We do NOT delete the .spec file anymore as we want to use our customized one.

echo.
echo [2/2] Building 'SFO File Organizer.exe'...
echo       This may take a minute...
echo.

:: Build the EXE using the existing Spec file via python module
python -m PyInstaller --clean "SFO File Organizer.spec"

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
echo    dist\SFO File Organizer.exe
echo.
echo You can copy this file ANYWHERE and run it without Python!
echo.
pause
explorer dist
