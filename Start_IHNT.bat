@echo off
setlocal
pushd %~dp0
if not exist ".venv\Scripts\python.exe" (
  echo [ERR ] Python virtual environment not found. Run Install_IHNT.bat first.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python i_hnt.py
set exitcode=%errorlevel%
popd
echo.
echo Application exited with code %exitcode%
pause
