::[Bat To Exe Converter]
::
::fBE1pAF6MU+EWGLUrRhkfUEFFUSyEVb6b5YO7env5uSA4mglcYI=
::fBE1pAF6MU+EWGLUrRhkfUEFFUSyEVb6b5MV5O317ueC+A0+Dt4Ka4rJyYiGIe0J63nAepU4239UjNgwPyl3PiK5YQUxqnp+m2uQJMLRngD3T1q1z3QYNVE6gnvV7A==
::fBE1pAF6MU+EWGLUrRhkfUEFFUSyEVb6b5MT+uX6+7DH8R9ddusrOJOb+buAM+8f7wWsQ58+33hWnYJs
::fBE1pAF6MU+EWGLUrRhkfUEGHUSyEVb6b5QY7OH16KqOoUITDqIcIrPuybGcM9wb60j+dKoJ2XlPlc4CGAhkTSCELj8mpmRHtXC5GsiJoAqsZ0ef41kMHWRijmDfgmtzMZomk8AMnW7wvGLU/w==
::fBE1pAF6MU+EWGLUrRhkfUEGHkSyEVb6b5QY7OH16KqVp14SQfA8fZyVlPrOD8tz
::fBE1pAF6MU+EWGLUrRhkfUEGH0SyEVb6b4UO5+v+/PnHpEQTXfE3fYu7
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFBNVQR6DAE+1BaAR7ebv/Na0kGJdZPAwcorYzoijL/UA7wjJeoAoxEZcmd0FDxRWMBuoYW8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFBNVQR6DAE+1BaAR7ebv/Na0kGJdZPAwcorYzoijL/UA7wjJeoAoxEZzltgYDRdUMBeza28=
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
REM I-HNT Gaming Assistant - One-Click Installer
REM "I Have No Time" - Work Hard, Game Smart!
REM 
REM This installer will:
REM - Auto-detect and install Python 3.11 if needed
REM - Create virtual environment (.venv)
REM - Install all required dependencies
REM - Generate Start_IHNT.bat launcher
REM 
REM Developed by HardyZ-2k2

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===============================================
echo  🎯 I-HNT Gaming Assistant - Auto Installer
echo ===============================================
echo  "I Have No Time" - Work Hard, Game Smart! 💪
echo.
echo  This will install Python 3.11 and all dependencies
echo  Virtual environment will be created automatically
echo  Internet connection required for first-time setup
echo.
echo ===============================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell available'" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell not found! This installer requires PowerShell.
    echo Please install PowerShell or use manual installation.
    pause
    exit /b 1
)

echo [INFO] Launching PowerShell installer...
echo.

REM Run the PowerShell installer with current directory
powershell -ExecutionPolicy Bypass -NoLogo -NoProfile -File "%~dp0install_ihnt.ps1" -ProjectDir "%~dp0"

REM Check if PowerShell installer succeeded
if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed! Check the output above for details.
    echo.
    echo Common fixes:
    echo - Run as Administrator (right-click bat file)
    echo - Check internet connection
    echo - Temporarily disable antivirus
    echo - Ensure Windows is up to date
    pause
    exit /b 1
)

echo.
echo ===============================================
echo  ✅ I-HNT Installation Complete!
echo ===============================================
echo.
echo  📁 Files created:
echo     - .venv (Python virtual environment)  
echo     - Start_IHNT.bat (Application launcher)
echo.
echo  🚀 To start I-HNT Gaming Assistant:
echo     - Double-click "Start_IHNT.bat"
echo     - Focus your game window
echo     - Press CapsLock to start hunting!
echo.
echo  🎯 Controls:
echo     - CapsLock = Start/Pause Toggle
echo     - F2 = Death Detection Test
echo     - F3 = Change Detection Area
echo     - F4 = Emergency Mouse Unlock
echo     - Ctrl+C = Exit
echo.
echo ===============================================
pause