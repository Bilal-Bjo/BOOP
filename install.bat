@echo off
setlocal enabledelayedexpansion

echo.
echo   ✨ JUST BOOP IT ✨
echo.
echo   Installing Boop for Windows...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python is not installed or not in PATH.
    echo   Please install Python 3.10+ from https://python.org
    echo   Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Get the directory where this script is located
set "BOOP_DIR=%~dp0"
cd /d "%BOOP_DIR%"

:: Stop any running Boop instance
echo   Stopping existing Boop instance...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq *" 2>nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq *" 2>nul
timeout /t 1 /nobreak >nul

:: Remove old venv to ensure clean install
if exist ".venv" (
    echo   Removing old virtual environment...
    rmdir /s /q ".venv" 2>nul
)

:: Create virtual environment
echo   Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo   ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate and install dependencies
echo   Installing dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install watchdog pyyaml pystray Pillow --quiet
if errorlevel 1 (
    echo   ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: Determine which Python executable to use
set "PYTHON_PATH=%BOOP_DIR%.venv\Scripts\pythonw.exe"
if not exist "%PYTHON_PATH%" (
    set "PYTHON_PATH=%BOOP_DIR%.venv\Scripts\python.exe"
)

set "SCRIPT_PATH=%BOOP_DIR%app.py"

:: Create startup shortcut (overwrites existing)
echo   Creating startup shortcut...
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Create VBS script to run without console window
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%BOOP_DIR%"
echo WshShell.Run """%PYTHON_PATH%"" ""%SCRIPT_PATH%""", 0, False
) > "%STARTUP%\Boop.vbs"

:: Start Boop now
echo   Starting Boop...
start "" /d "%BOOP_DIR%" "%PYTHON_PATH%" "%SCRIPT_PATH%"

echo.
echo   ✨ Boop is ready!
echo   Look for the icon in your system tray.
echo.
echo   Boop will start automatically when Windows starts.
echo.
pause
