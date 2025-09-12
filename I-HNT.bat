@echo off
title I-HNT Gaming Assistant
setlocal EnableDelayedExpansion

rem Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo 🎯========================================================🎯
echo ║                                                        ║
echo ║            I-HNT Gaming Assistant Launcher            ║
echo ║                                                        ║
echo ║         "I Have No Time" - Work Hard, Game Smart!     ║
echo ║                                                        ║
echo 🎯========================================================🎯
echo.

rem Define Python paths
set EMBEDDED_PYTHON=%~dp0python_embedded\python.exe
set PYTHON_CMD=

rem First, check for I-HNT embedded Python
if exist "%EMBEDDED_PYTHON%" (
    echo ✅ Using I-HNT Embedded Python
    "%EMBEDDED_PYTHON%" --version
    set PYTHON_CMD=%EMBEDDED_PYTHON%
    goto :run_ihnt
)

rem Fall back to system Python
python --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Using System Python
    python --version
    set PYTHON_CMD=python
    goto :run_ihnt
)

rem No Python found
echo ❌ No Python installation found!
echo.
echo 💡 SOLUTIONS:
echo    1. Run "INSTALL.bat" first (recommended - installs everything automatically)
echo    2. Install Python manually from: https://www.python.org/downloads/
echo.
echo 🎯 The INSTALL.bat will automatically download and set up:
echo    • Python (embedded, no admin rights needed)
echo    • All I-HNT dependencies
echo    • Ready-to-use gaming assistant
echo.
pause
exit /b 1

:run_ihnt
rem Check if i_hnt.py exists
if not exist "i_hnt.py" (
    echo ❌ i_hnt.py not found in current directory!
    echo.
    echo 💡 Make sure this file is in the same folder as i_hnt.py
    echo    Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo 🚀 Starting I-HNT Gaming Assistant...
echo.
echo 💡 REMEMBER:
echo    • Focus your game window
echo    • Press CapsLock to start/pause hunting
echo    • Press Ctrl+C here to exit completely
echo.
echo ⚡ Starting in 3 seconds... (Press Ctrl+C to cancel)
timeout /t 3 /nobreak >nul

rem Start I-HNT with appropriate Python
"%PYTHON_CMD%" i_hnt.py

rem Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ I-HNT exited with an error. Check the messages above.
    echo.
    echo 💡 TROUBLESHOOTING:
    echo    • Run "INSTALL.bat" to ensure all dependencies are installed
    echo    • Check if your antivirus is blocking the application
    echo    • Ensure you have a stable internet connection for YOLO model downloads
    echo.
    pause
)

echo.
echo 🎯 Thank you for using I-HNT Gaming Assistant!
echo 🌟 Developed by HardyZ-2k2 - Black Angels Family
