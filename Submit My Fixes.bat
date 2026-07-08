@echo off
title ACY1 Troubleshooter - Submit My Fixes
cls
echo.
echo  ============================================
echo   ACY1 Troubleshooter - Submit My Fixes
echo  ============================================
echo.
echo  Sends the fixes you exported (Downloads folder)
echo  to the RME review inbox. An admin reviews and
echo  publishes them so everyone sees the update.
echo.

set "INBOX=\\ant\dept-na\ACY1\Support\RME\Troubleshooter\Submissions"
set "DL=%USERPROFILE%\Downloads"

if not exist "%INBOX%" mkdir "%INBOX%" 2>nul
if not exist "%INBOX%" (
    echo  ERROR: Cannot reach the share drive.
    echo  Connect to the Amazon network and try again.
    echo.
    pause & exit /b 1
)

set "found="
for /f "delims=" %%f in ('dir /b /o-d "%DL%\troubleshooter_fixes_*.json" 2^>nul') do (
    if not defined found (
        set "found=%%f"
        copy /Y "%DL%\%%f" "%INBOX%\%USERNAME%__%%f" >nul
        echo  Submitted: %%f
        echo    as: %USERNAME%__%%f
    )
)

if not defined found (
    echo  No exported fixes found in your Downloads folder.
    echo.
    echo  In the Troubleshooter: click "Export Fixes" from the
    echo  Report Fix panel, then run this script again.
)

echo.
pause
