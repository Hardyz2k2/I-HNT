@echo off
setlocal EnableDelayedExpansion

:: I-HNT Gaming Assistant - Enhanced Installation Script
:: Automatically installs Python and all dependencies
:: No admin rights required - fully portable installation

echo.
echo 🎯========================================================🎯
echo ║                                                        ║
echo ║       I-HNT Gaming Assistant - Auto Installation      ║
echo ║                                                        ║
echo ║         "I Have No Time" - Work Hard, Game Smart!     ║
echo ║                                                        ║
echo ║              🤖 AI-Powered Gaming Automation          ║
echo ║                                                        ║
echo 🎯========================================================🎯
echo.
echo 📦 Checking system requirements...
echo.

:: Define variables
set PYTHON_VERSION=3.11.9
set PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_DIR=%~dp0python_embedded
set GETPIP_URL=https://bootstrap.pypa.io/get-pip.py
set REQUIREMENTS_FILE=%~dp0requirements.txt

:: Check if Python is already installed (system or embedded)
echo 🔍 Checking for existing Python installation...

:: First check system Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ System Python found!
    python --version
    set PYTHON_CMD=python
    goto :install_requirements
)

:: Check for our embedded Python
if exist "%PYTHON_DIR%\python.exe" (
    echo ✅ I-HNT Embedded Python found!
    "%PYTHON_DIR%\python.exe" --version
    set PYTHON_CMD="%PYTHON_DIR%\python.exe"
    goto :install_requirements
)

:: No Python found - install embedded Python
echo ❌ No Python installation found.
echo.
echo 🚀 Installing I-HNT Embedded Python (No admin rights needed)...
echo    📥 Downloading Python %PYTHON_VERSION% Embedded...
echo    📦 Version: Lightweight embedded distribution
echo    💾 Size: ~15MB download
echo    📁 Location: %PYTHON_DIR%
echo.

:: Create Python directory
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"

:: Download Python embedded zip using PowerShell
echo    ⬇️ Downloading Python embedded distribution...
powershell -Command "try { Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile 'python_embedded.zip' -UseBasicParsing; Write-Host '✅ Download completed successfully' } catch { Write-Host '❌ Download failed:' $_.Exception.Message; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to download Python embedded distribution.
    echo 💡 Please check your internet connection and try again.
    echo 🌐 Manual download: %PYTHON_EMBED_URL%
    pause
    exit /b 1
)

:: Extract Python embedded zip
echo    📂 Extracting Python embedded distribution...
powershell -Command "try { Expand-Archive -Path 'python_embedded.zip' -DestinationPath '%PYTHON_DIR%' -Force; Write-Host '✅ Extraction completed successfully' } catch { Write-Host '❌ Extraction failed:' $_.Exception.Message; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to extract Python embedded distribution.
    pause
    exit /b 1
)

:: Clean up zip file
del "python_embedded.zip" >nul 2>&1

:: Enable pip in embedded Python by modifying pth file
echo    🔧 Configuring embedded Python for pip support...
echo import sys; sys.path.append(r'%PYTHON_DIR%\Lib\site-packages') > "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp"
if exist "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" (
    type "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" >> "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp"
)
move "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp" "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" >nul

:: Download and install pip
echo    📦 Setting up pip for embedded Python...
powershell -Command "try { Invoke-WebRequest -Uri '%GETPIP_URL%' -OutFile 'get-pip.py' -UseBasicParsing; Write-Host '✅ get-pip.py downloaded' } catch { Write-Host '❌ get-pip.py download failed:' $_.Exception.Message; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to download get-pip.py
    pause
    exit /b 1
)

:: Install pip using embedded Python
echo    ⚙️ Installing pip...
"%PYTHON_DIR%\python.exe" get-pip.py --no-warn-script-location
if %errorlevel% neq 0 (
    echo ❌ Failed to install pip in embedded Python
    pause
    exit /b 1
)

:: Clean up get-pip.py
del "get-pip.py" >nul 2>&1

:: Set Python command for embedded installation
set PYTHON_CMD="%PYTHON_DIR%\python.exe"
set PIP_CMD="%PYTHON_DIR%\Scripts\pip.exe"

echo.
echo ✅ I-HNT Embedded Python installation completed!
echo    📍 Python Location: %PYTHON_DIR%
echo    🎯 Version: %PYTHON_VERSION% (embedded)
echo    📦 Pip: Ready for package installation
echo.

:install_requirements
:: Install I-HNT dependencies
echo ⚡ Installing I-HNT Gaming Assistant dependencies...
echo.
echo 📋 Required packages:
echo    • ultralytics    - YOLO AI for mob detection
echo    • opencv-python  - Computer vision processing  
echo    • pyautogui      - Mouse and keyboard automation
echo    • mss            - Ultra-fast screen capture
echo    • numpy          - Numerical operations
echo    • pynput         - Global hotkey controls
echo.

:: Set pip command based on Python installation type
if defined PIP_CMD (
    set PIP_INSTALL_CMD=%PIP_CMD%
) else (
    set PIP_INSTALL_CMD=%PYTHON_CMD% -m pip
)

:: Upgrade pip first
echo 🔄 Updating pip to latest version...
%PIP_INSTALL_CMD% install --upgrade pip --no-warn-script-location
echo.

:: Install requirements
echo 📦 Installing I-HNT dependencies...
if exist "%REQUIREMENTS_FILE%" (
    %PIP_INSTALL_CMD% install -r "%REQUIREMENTS_FILE%" --no-warn-script-location
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Failed to install some dependencies.
        echo 💡 This might be due to:
        echo    - Internet connection issues
        echo    - Missing system libraries
        echo    - Antivirus blocking downloads
        echo.
        echo 🔄 Try running this script again or install manually:
        echo    %PIP_INSTALL_CMD% install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo ❌ Requirements file not found: %REQUIREMENTS_FILE%
    echo 💡 Installing essential packages individually...
    
    :: Install essential packages one by one
    for %%P in (ultralytics opencv-python pyautogui mss numpy pynput) do (
        echo    Installing %%P...
        %PIP_INSTALL_CMD% install %%P --no-warn-script-location
    )
)

echo.
echo ✅ All dependencies installed successfully!
echo.

:: Final success message
echo 🎉========================================================🎉
echo ║                                                        ║
echo ║           🎯 I-HNT Installation Completed! 🎯          ║
echo ║                                                        ║
echo ║     Your AI-powered gaming assistant is ready!        ║
echo ║                                                        ║
echo 🎉========================================================🎉
echo.
echo 🚀 TO START GAMING:
echo ════════════════════
echo.
echo   Method 1: Double-click "I-HNT.bat"
echo   Method 2: Run: %PYTHON_CMD% i_hnt.py
echo.
echo 🎮 GAME CONTROLS:
echo ════════════════
echo   • Focus your game window
echo   • Press CapsLock to START hunting
echo   • Press CapsLock again to PAUSE/RESUME
echo   • Press Ctrl+C in terminal to EXIT
echo.
echo 💡 FEATURES READY:
echo ══════════════════
echo   ✅ YOLO AI mob detection (30+ FPS)
echo   ✅ Health bar monitoring
echo   ✅ Active hunting mode
echo   ✅ Character protection system
echo   ✅ Global hotkey controls
echo   ✅ Keyboard automation (123145)
echo.
echo 🛡️ SAFETY NOTES:
echo ═══════════════
echo   • Use responsibly and follow game terms
echo   • Built-in character protection active
echo   • Easy shutdown options available
echo.
echo 🌟 Developed by HardyZ-2k2 - Black Angels Family 🔥
echo.
echo Happy Gaming! Press any key to continue...
pause >nul
