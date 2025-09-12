@echo off
setlocal EnableDelayedExpansion

:: I-HNT Gaming Assistant - Offline Package Creator
:: Creates a fully offline installation package with all dependencies

echo.
echo 🎯========================================================🎯
echo ║                                                        ║
echo ║         I-HNT - Offline Package Creator               ║
echo ║                                                        ║
echo ║         Creates self-contained installation            ║
echo ║                                                        ║
echo 🎯========================================================🎯
echo.

:: Create directories
set OFFLINE_DIR=%~dp0I-HNT_Offline_Package
set WHEELS_DIR=%OFFLINE_DIR%\wheels
set PYTHON_DIR=%OFFLINE_DIR%\python_embedded

echo 📦 Creating offline package structure...
if exist "%OFFLINE_DIR%" rmdir /s /q "%OFFLINE_DIR%"
mkdir "%OFFLINE_DIR%"
mkdir "%WHEELS_DIR%"
mkdir "%PYTHON_DIR%"

:: Copy main files
echo 📋 Copying I-HNT files...
copy "i_hnt.py" "%OFFLINE_DIR%\" >nul
copy "requirements.txt" "%OFFLINE_DIR%\" >nul
copy "yolov8n.pt" "%OFFLINE_DIR%\" >nul
copy "README.md" "%OFFLINE_DIR%\" >nul
copy "README - Quick Start.txt" "%OFFLINE_DIR%\" >nul
copy "PROJECT_STATUS.md" "%OFFLINE_DIR%\" >nul

:: Download Python embedded distribution
echo 🐍 Downloading Python embedded distribution...
set PYTHON_VERSION=3.11.9
set PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip

powershell -Command "Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile 'python_embedded.zip' -UseBasicParsing"
powershell -Command "Expand-Archive -Path 'python_embedded.zip' -DestinationPath '%PYTHON_DIR%' -Force"
del "python_embedded.zip" >nul 2>&1

:: Download get-pip.py
echo 📦 Setting up pip for embedded Python...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing"

:: Configure embedded Python for pip
echo import sys; sys.path.append(r'%PYTHON_DIR%\Lib\site-packages') > "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp"
if exist "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" (
    type "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" >> "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp"
)
move "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth.temp" "%PYTHON_DIR%\python%PYTHON_VERSION:~0,4%._pth" >nul

:: Install pip
"%PYTHON_DIR%\python.exe" get-pip.py --no-warn-script-location
del "get-pip.py" >nul 2>&1

:: Download all wheels
echo 💾 Downloading dependency wheels for offline installation...
"%PYTHON_DIR%\Scripts\pip.exe" download -r requirements.txt -d "%WHEELS_DIR%" --no-warn-script-location

:: Create offline installer
echo 📝 Creating offline installer...
(
echo @echo off
echo setlocal EnableDelayedExpansion
echo.
echo :: I-HNT Gaming Assistant - Offline Installation
echo :: No internet connection required!
echo.
echo echo.
echo echo 🎯========================================================🎯
echo echo ║                                                        ║
echo echo ║         I-HNT Gaming Assistant - OFFLINE INSTALL     ║
echo echo ║                                                        ║
echo echo ║         "I Have No Time" - Work Hard, Game Smart!     ║
echo echo ║                                                        ║
echo echo ║              🤖 No Internet Required! 🤖              ║
echo echo ║                                                        ║
echo echo 🎯========================================================🎯
echo echo.
echo.
echo set PYTHON_DIR=%%~dp0python_embedded
echo set WHEELS_DIR=%%~dp0wheels
echo.
echo echo 📦 Installing I-HNT dependencies from offline wheels...
echo "%%PYTHON_DIR%%\Scripts\pip.exe" install --find-links "%%WHEELS_DIR%%" --no-index -r requirements.txt --no-warn-script-location
echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo.
echo     echo ✅ Offline installation completed successfully!
echo     echo.
echo     echo 🎮 TO START GAMING:
echo     echo    Double-click "I-HNT.bat"
echo     echo.
echo     echo 🎯 CONTROLS:
echo     echo    - Press CapsLock to start/pause hunting
echo     echo    - Focus your game window first
echo     echo.
echo     echo 🌟 Developed by HardyZ-2k2 - Black Angels Family
echo     echo.
echo ^) else ^(
echo     echo ❌ Installation failed! Please check error messages above.
echo     echo.
echo ^)
echo.
echo pause
) > "%OFFLINE_DIR%\INSTALL_OFFLINE.bat"

:: Create offline launcher
(
echo @echo off
echo title I-HNT Gaming Assistant ^(Offline^)
echo setlocal EnableDelayedExpansion
echo.
echo cd /d "%%~dp0"
echo.
echo set PYTHON_CMD=%%~dp0python_embedded\python.exe
echo.
echo echo 🎯 Starting I-HNT Gaming Assistant ^(Offline Mode^)...
echo echo.
echo "%%PYTHON_CMD%%" i_hnt.py
echo.
echo if %%ERRORLEVEL%% neq 0 ^(
echo     echo.
echo     echo ❌ Error occurred. Check messages above.
echo     pause
echo ^)
) > "%OFFLINE_DIR%\I-HNT.bat"

:: Copy README for offline package
(
echo 🎯 I-HNT Gaming Assistant - Offline Package
echo ===========================================
echo.
echo This is a completely self-contained I-HNT installation that works
echo without internet connection or Python installation!
echo.
echo INSTALLATION:
echo 1. Double-click "INSTALL_OFFLINE.bat"
echo 2. Wait for installation to complete
echo 3. Double-click "I-HNT.bat" to start gaming!
echo.
echo FEATURES:
echo • Complete Python environment included
echo • All dependencies pre-downloaded
echo • Works on any Windows 10/11 system
echo • No admin rights required
echo • No internet connection needed after setup
echo.
echo PACKAGE CONTENTS:
echo • python_embedded/    - Python 3.11.9 embedded
echo • wheels/            - All dependency wheel files
echo • i_hnt.py           - Main application
echo • yolov8n.pt         - YOLO AI model
echo • requirements.txt   - Dependency list
echo • README files       - Documentation
echo.
echo SIZE: ~200MB ^(Python + AI + Dependencies^)
echo.
echo 🌟 Developed by HardyZ-2k2 - Black Angels Family
echo "I Have No Time" - Work Hard, Game Smart!
) > "%OFFLINE_DIR%\README_OFFLINE.txt"

echo.
echo ✅ Offline package created successfully!
echo.
echo 📁 Package location: %OFFLINE_DIR%
echo 📦 Package size: ~200MB (complete installation)
echo.
echo 🎯 PACKAGE CONTENTS:
echo    • Python 3.11.9 embedded distribution
echo    • All I-HNT dependencies (offline wheels)
echo    • Complete I-HNT application files
echo    • Offline installer and launcher
echo.
echo 💡 TO DISTRIBUTE:
echo    1. Zip the entire "%OFFLINE_DIR%" folder
echo    2. Users extract and run "INSTALL_OFFLINE.bat"
echo    3. No Python or internet required!
echo.
echo 🌟 Perfect for sharing with friends or offline systems!
echo.
pause
