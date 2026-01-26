@echo off
:: Smart File Organizer - Desktop Shortcut Creator
:: Run this ONCE to create shortcuts on your Desktop

title Creating Desktop Shortcuts

cd /d "%~dp0"

set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"

echo.
echo ====================================================
echo   Smart File Organizer - Shortcut Creator
echo ====================================================
echo.

:: Create VBScript to make shortcuts (only native way on Windows without extra tools)
echo Creating desktop shortcuts...

:: Create shortcut for GUI
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\File Organizer.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%Start File Organizer.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Smart File Organizer - Organize your files easily" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "shell32.dll,3" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

:: Create shortcut for Dashboard
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\File Organizer Dashboard.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%Open Dashboard.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Smart File Organizer - Web Dashboard" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "shell32.dll,14" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo.
echo ====================================================
echo   SUCCESS! Shortcuts created on your Desktop:
echo ====================================================
echo.
echo   [Folder Icon] File Organizer
echo       - Opens the desktop application
echo.
echo   [Globe Icon]  File Organizer Dashboard  
echo       - Opens the web dashboard in your browser
echo.
echo ====================================================
echo.
echo You can now close this window and use the shortcuts!
echo.
pause
