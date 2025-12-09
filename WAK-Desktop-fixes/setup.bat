@echo off
set "SCRIPT_PATH=%~dp0scripts\wallpaper_changer.py"
set "SCRIPT_PATH_TB=%~dp0scripts\fix_taskbar.ps1"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Use pythonw.exe for silent execution (no console window)
set "PYTHONW_EXE=pythonw.exe"

echo Richte Autostart fuer WAK-Desktop-fixes ein...

:: 1. Wallpaper (Silent, PythonW)
set VBS_SCRIPT=%TEMP%\CreateShortcut_WAK_Wall.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\WAK_Wallpaper.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%PYTHONW_EXE%" >> "%VBS_SCRIPT%"
echo oLink.Arguments = """%SCRIPT_PATH%""" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

:: 2. Taskbar (Silent-ish, PowerShell Hidden)
set VBS_SCRIPT=%TEMP%\CreateShortcut_WAK_TB.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\WAK_Taskbar.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "powershell.exe" >> "%VBS_SCRIPT%"
:: -WindowStyle Hidden to hide window, -ExecutionPolicy Bypass to allow script
echo oLink.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File ""%SCRIPT_PATH_TB%""" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo Fertig. Autostart eingerichtet.
echo Bitte druecken Sie Enter, um zu beenden.
pause
