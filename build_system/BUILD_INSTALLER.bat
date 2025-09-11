@echo off
echo ================================================================
echo YOLO MOB FINDER - COMPLETE BUILD AND INSTALLER CREATION
echo ================================================================
echo.

REM Set up environment - this script runs from build_system folder
cd /d "%~dp0"
set "BUILD_SYSTEM_DIR=%cd%"
cd ..
set "PROJECT_DIR=%cd%"

echo 📁 Project Directory: %PROJECT_DIR%
echo 🔧 Build System Directory: %BUILD_SYSTEM_DIR%
echo.

echo ================================================================
echo STEP 1: INSTALLING DEPENDENCIES
echo ================================================================
echo 📦 Ensuring all required packages are installed...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller pillow
echo ✅ Dependencies installation complete
echo.

echo ================================================================
echo STEP 2: CREATING APPLICATION ICON
echo ================================================================
echo 🎨 Creating application icon and installer images...
cd "%BUILD_SYSTEM_DIR%"
python create_icon.py
if errorlevel 1 (
    echo ❌ Icon creation failed, continuing without custom icons...
) else (
    echo ✅ Icons created successfully
)
echo.

echo ================================================================
echo STEP 3: BUILDING STANDALONE EXECUTABLE
echo ================================================================
echo 🔨 Building executable with PyInstaller...
python build_executable.py
if errorlevel 1 (
    echo ❌ Executable build failed!
    pause
    exit /b 1
)
echo ✅ Executable build complete
echo.

echo ================================================================
echo STEP 4: CREATING WINDOWS INSTALLER
echo ================================================================
echo 📦 Creating Windows installer with Inno Setup...

REM Check if Inno Setup is installed
set "INNO_SETUP="
if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" (
    set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
) else if exist "C:\Program Files\Inno Setup 6\iscc.exe" (
    set "INNO_SETUP=C:\Program Files\Inno Setup 6\iscc.exe"
) else (
    echo.
    echo ⚠️ INNO SETUP NOT FOUND!
    echo 📥 Please download and install Inno Setup 6 from:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo 🔧 After installation, run this script again to create the installer.
    echo 💡 Alternative: Use the portable distribution in the generated folder.
    echo.
    goto :skip_installer
)

echo 🔧 Found Inno Setup: %INNO_SETUP%
echo 🏗️ Compiling installer script...

REM Create installer output directory
if not exist "installer_output" mkdir installer_output

REM Compile the installer from build_system directory
"%INNO_SETUP%" "installer_script.iss"
if errorlevel 1 (
    echo ❌ Installer creation failed!
    echo 💡 Check installer_script.iss for errors
    goto :skip_installer
)

echo ✅ Windows installer created successfully!
echo 📦 Installer location: %BUILD_SYSTEM_DIR%\installer_output\

:skip_installer

echo.
echo ================================================================
echo BUILD COMPLETE! 🎉
echo ================================================================
echo.

if exist "%PROJECT_DIR%\dist\YOLO_Mob_Finder.exe" (
    echo ✅ EXECUTABLE: %PROJECT_DIR%\dist\YOLO_Mob_Finder.exe
) else (
    echo ❌ Executable not found in dist\ folder
)

if exist "%PROJECT_DIR%\YOLO_Mob_Finder_Portable" (
    echo ✅ PORTABLE VERSION: %PROJECT_DIR%\YOLO_Mob_Finder_Portable\ folder
) else (
    echo ❌ Portable distribution not found
)

if exist "%BUILD_SYSTEM_DIR%\installer_output\*.exe" (
    echo ✅ INSTALLER: %BUILD_SYSTEM_DIR%\installer_output\ folder
    for %%f in ("%BUILD_SYSTEM_DIR%\installer_output\*.exe") do echo    📦 %%f
) else (
    echo ⚠️ No installer created (Inno Setup needed)
)

echo.
echo 📋 NEXT STEPS:
echo ================
echo 1. Test the executable: %PROJECT_DIR%\dist\YOLO_Mob_Finder.exe
echo 2. Test portable version: %PROJECT_DIR%\YOLO_Mob_Finder_Portable\
if exist "%BUILD_SYSTEM_DIR%\installer_output\*.exe" (
    echo 3. Distribute installer: %BUILD_SYSTEM_DIR%\installer_output\YOLO_Mob_Finder_Installer_*.exe
) else (
    echo 3. Install Inno Setup and rerun to create installer
)
echo 4. Share with others - no Python required on target machines!
echo.
echo 🎮 USAGE REMINDER:
echo - Focus game window and press F1 to start/pause
echo - Read README.md for complete instructions
echo - Train custom YOLO model for best results
echo.

pause