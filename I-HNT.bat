@echo off
title I-HNT Gaming Assistant

rem Change to the directory where this batch file is located
cd /d "%~dp0"

rem Check if Python is available
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

rem Check if i_hnt.py exists
if not exist "i_hnt.py" (
    echo ❌ i_hnt.py not found in current directory!
    echo.
    echo Make sure this file is in the same folder as i_hnt.py
    pause
    exit /b 1
)

rem Start I-HNT
python i_hnt.py

rem Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ I-HNT exited with an error. Check the messages above.
    pause
)
