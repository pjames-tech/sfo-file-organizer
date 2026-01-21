@echo off
REM Smart File Organizer - Scheduled Task Script
REM Run this script manually or via Windows Task Scheduler

cd /d "c:\Users\Victor\Documents\Coding\smart-file-organizer"

echo ============================================
echo Smart File Organizer - Scheduled Run
echo ============================================
echo Started at: %date% %time%
echo.

REM Run the organizer with default Downloads folder
"C:\Python314\python.exe" organizer.py --source "%USERPROFILE%\Downloads" --dest "%USERPROFILE%\Downloads\Organized" --log-level INFO

echo.
echo Finished at: %date% %time%
echo ============================================
