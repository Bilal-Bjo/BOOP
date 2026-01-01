@echo off
echo Uninstalling Boop...

:: Remove startup shortcut
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Boop.vbs" 2>nul

:: Kill running Boop process
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq Boop*" 2>nul

echo Done! Boop has been removed.
pause
