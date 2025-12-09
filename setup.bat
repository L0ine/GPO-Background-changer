@echo off
set "SCRIPT_PATH=%~dp0scripts\wallpaper_changer.py"
set "SCRIPT_PATH_TB=%~dp0scripts\fix_taskbar.py"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "PYTHON_EXE=python.exe"

echo Richte Autostart fuer WAK-Desktop-fixes ein...

:: 1. Wallpaper (Silent, No Restart)
set VBS_SCRIPT=%TEMP%\CreateShortcut_WAK_Wall.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\WAK_Wallpaper.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHON_EXE%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = """%SCRIPT_PATH%""" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

:: 2. Taskbar (Silent, No Restart)
set VBS_SCRIPT=%TEMP%\CreateShortcut_WAK_TB.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\WAK_Taskbar.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHON_EXE%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = """%SCRIPT_PATH_TB%""" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo Fertig.
pause
