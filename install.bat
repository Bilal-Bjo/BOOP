@echo off
echo.
echo   ✨ JUST BOOP IT ✨
echo.
echo   Installing Boop for Windows...
echo.

:: Create virtual environment
python -m venv .venv
call .venv\Scripts\activate.bat

:: Install dependencies
pip install watchdog pyyaml pystray Pillow --quiet

:: Create startup shortcut
echo Creating startup shortcut...
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SCRIPT_PATH=%~dp0app.py
set PYTHON_PATH=%~dp0.venv\Scripts\pythonw.exe

:: Create VBS script to run without console window
echo Set WshShell = CreateObject("WScript.Shell") > "%STARTUP%\Boop.vbs"
echo WshShell.Run """%PYTHON_PATH%"" ""%SCRIPT_PATH%""", 0, False >> "%STARTUP%\Boop.vbs"

:: Start Boop now
start "" "%PYTHON_PATH%" "%SCRIPT_PATH%"

echo.
echo   ✨ Boop is ready!
echo   Look for ✨ in your system tray.
echo.
pause
