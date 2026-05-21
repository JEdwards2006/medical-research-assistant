@echo off
title Medical Research Assistant
echo.
echo ================================================
echo   Medical Research Assistant
echo ================================================
echo.
echo  Starting up... please wait a moment.
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python was not found on this computer.
    echo.
    echo  Please install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Click "Download Python" and run the installer.
    echo  Make sure to check the box that says
    echo  "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"
start "" "http://localhost:8000"
python server.py

pause
