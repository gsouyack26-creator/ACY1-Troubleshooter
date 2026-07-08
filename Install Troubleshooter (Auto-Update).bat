@echo off
title ACY1 Troubleshooter - Auto-Update Install
cls
echo.
echo  ============================================
echo   ACY1 Troubleshooter - Auto-Update Install
echo  ============================================
echo.
echo  Creates a Desktop shortcut that copies the
echo  latest version from the share every time you
echo  open it, then runs it locally (fast, and it
echo  still works if the share is briefly down).
echo.

set "localDir=%USERPROFILE%\Documents\ACY1 Troubleshooter"
set "launcherSrc=\\ant\dept-na\ACY1\Support\RME\Troubleshooter\Troubleshooter Launcher.vbs"
set "launcherDest=%localDir%\Troubleshooter Launcher.vbs"

if not exist "%launcherSrc%" (
    echo  ERROR: Cannot reach the share drive.
    echo  Make sure you are on the Amazon network and try again.
    echo.
    pause & exit /b 1
)

if not exist "%localDir%" mkdir "%localDir%"

REM Deploy launcher locally
copy /Y "%launcherSrc%" "%launcherDest%" >nul

REM Prime the local copy now so the first launch is instant
copy /Y "\\ant\dept-na\ACY1\Support\RME\Troubleshooter\ACY1_Troubleshooter.html" "%localDir%\ACY1_Troubleshooter.html" >nul 2>&1

REM Create Desktop shortcut pointing at the launcher (runs hidden via wscript)
set "PS1=%TEMP%\setup_troubleshooter.ps1"
(
  echo $sh = New-Object -ComObject WScript.Shell
  echo $desktop = [System.Environment]::GetFolderPath^('Desktop'^)
  echo $docs    = [System.Environment]::GetFolderPath^('MyDocuments'^)
  echo $sc = $sh.CreateShortcut^($desktop + '\ACY1 Troubleshooter.lnk'^)
  echo $sc.TargetPath       = 'wscript.exe'
  echo $sc.Arguments        = '"' + $docs + '\ACY1 Troubleshooter\Troubleshooter Launcher.vbs"'
  echo $sc.Description       = 'ACY1 Troubleshooter - Auto-Updating'
  echo $sc.WorkingDirectory  = $docs + '\ACY1 Troubleshooter'
  echo $sc.Save^(^)
  echo Write-Host 'Shortcut created.'
) > "%PS1%"

powershell -ExecutionPolicy Bypass -File "%PS1%"
del "%PS1%" >nul 2>&1

echo.
echo  ============================================
echo   Done!
echo  ============================================
echo.
echo  - Shortcut "ACY1 Troubleshooter" added to Desktop
echo  - Grabs the latest from the share on every open
echo  - Runs locally, so it is fast and works offline
echo.
pause
