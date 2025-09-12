@echo off
echo.
echo 🎯================================================🎯
echo ║                                                ║
echo ║    I-HNT Gaming Assistant - Installation      ║
echo ║                                                ║
echo ║      "I Have No Time" - Work Hard, Game Smart!║
echo ║                                                ║
echo 🎯================================================🎯
echo.
echo 📦 Installing required packages...
echo.

python -m pip install --upgrade pip
echo.

echo ⚡ Installing I-HNT dependencies...
pip install -r requirements.txt

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ Installation completed successfully!
    echo.
    echo 🎮 To start I-HNT Gaming Assistant:
    echo    1. Double-click "I-HNT.bat"
    echo    2. Or run: python i_hnt.py
    echo.
    echo 🎯 Controls:
    echo    - Press CapsLock to start/pause hunting
    echo    - Focus your game window first
    echo    - Press Ctrl+C in terminal to exit
    echo.
    echo 🌟 Developed by HardyZ-2k2
    echo 🔥 Black Angels Family
    echo.
) else (
    echo ❌ Installation failed! Please check your Python installation.
    echo.
    echo 💡 Make sure you have:
    echo    - Python 3.8+ installed
    echo    - Internet connection for downloading packages
    echo.
)

pause
