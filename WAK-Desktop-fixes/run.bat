@echo off
echo Starting Wallpaper Fix...
python "%~dp0scripts\wallpaper_changer.py"

echo Starting Taskbar Fix...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\fix_taskbar.ps1"

echo Done.
pause
