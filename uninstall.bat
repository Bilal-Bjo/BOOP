@echo off
echo.
echo   Uninstalling Boop...
echo.

:: Remove startup shortcut
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Boop.vbs" 2>nul

:: Try to stop Boop (best effort - may need manual close)
taskkill /f /im pythonw.exe 2>nul
taskkill /f /im python.exe 2>nul

echo.
echo   Done! Boop has been removed from startup.
echo   You can delete the boop folder to fully remove it.
echo.
pause
