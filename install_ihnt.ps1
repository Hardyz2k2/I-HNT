<# 
I-HNT Gaming Assistant – One-click Installer (PowerShell)
- Enables Windows Long Paths
- Installs Python 3.11 (x64) if missing (winget preferred)
- Creates venv (.venv) and installs dependencies
- Generates Start_IHNT.bat launcher
- Works with paths containing spaces
#>

param(
  [string]$ProjectDir = (Split-Path -Parent $PSCommandPath)
)

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-OK($msg){ Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Elevate if needed
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
  Write-Warn "Not running as Administrator. Re-launching elevated..."
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = "powershell.exe"
  $psi.Arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -ProjectDir `"$ProjectDir`""
  $psi.Verb = "runas"
  try { [Diagnostics.Process]::Start($psi) | Out-Null } catch { Write-Err "Elevation cancelled by user."; exit 1 }
  exit 0
}

# Normalize project path
$ProjectDir = ($ProjectDir -replace '"','').TrimEnd('\','/')
if (-not (Test-Path -LiteralPath $ProjectDir)) {
  Write-Err "ProjectDir not found: $ProjectDir"
  exit 1
}
Set-Location -LiteralPath $ProjectDir
Write-OK "Project directory: $ProjectDir"

# Enable Long Paths
Write-Info "Enabling Windows Long Paths..."
try {
  New-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Force | Out-Null
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWord -Force | Out-Null
  Write-OK "Long Paths enabled."
} catch { Write-Warn "Could not enable Long Paths. Some packages with very long paths may fail." }

# Python detection/installation helpers
function Refresh-EnvPath {
  $machine = [Environment]::GetEnvironmentVariable("Path","Machine")
  $user    = [Environment]::GetEnvironmentVariable("Path","User")
  $env:Path = "$machine;$user"
}
function Detect-Python {
  $v = $null
  try { $v = & python --version 2>$null } catch {}
  if (-not $v) { try { $v = & py -V 2>$null } catch {} }
  return $v
}
function Get-PythonExe {
  try {
    $p = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($p) { return $p }
  } catch {}
  try {
    $pyCmd = (Get-Command py -ErrorAction SilentlyContinue).Source
    if ($pyCmd) {
      $candidate = & py -3.11 -c "import sys;print(sys.executable)" 2>$null
      if ($LASTEXITCODE -eq 0 -and $candidate) { return $candidate.Trim() }
    }
  } catch {}
  return $null
}

$requiredMajor = 3; $requiredMinor = 11
Write-Info "Checking for Python $requiredMajor.$requiredMinor+ ..."
$detected = Detect-Python
$needInstall = $true
if ($detected -and ($detected -match "([0-9]+)\.([0-9]+)\.([0-9]+)")) {
  $maj = [int]$Matches[1]; $min = [int]$Matches[2]
  if ($maj -gt $requiredMajor -or ($maj -eq $requiredMajor -and $min -ge $requiredMinor)) { $needInstall = $false }
}

if ($needInstall) {
  Write-Warn "Python $requiredMajor.$requiredMinor+ not found. Installing Python 3.11 (x64)..."
  $installed = $false
  try {
    winget --version *> $null
    if ($LASTEXITCODE -eq 0) {
      Write-Info "Using winget to install Python 3.11..."
      winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements -h
      $installed = $true
    }
  } catch {}
  if (-not $installed) {
    $temp = Join-Path $env:TEMP "python311_installer.exe"
    $url  = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    Write-Info "Downloading Python from official source..."
    try {
      Invoke-WebRequest -Uri $url -OutFile $temp -UseBasicParsing
      Write-Info "Running silent Python installer..."
      & $temp /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
      Start-Sleep -Seconds 6
      Remove-Item $temp -Force -ErrorAction SilentlyContinue
      $installed = $true
    } catch { Write-Err "Python download/install failed: $($_.Exception.Message)" }
  }
  Refresh-EnvPath
}

$pythonExe = Get-PythonExe
if (-not $pythonExe) { Write-Err "Python was not detected after installation. Please install Python 3.11 (x64) manually and re-run."; exit 1 }
Write-OK "Python detected: $pythonExe"

# Ensure pip tools
Write-Info "Ensuring pip/setuptools/wheel are up to date..."
try {
  & $pythonExe -m ensurepip -U
  & $pythonExe -m pip install --upgrade pip setuptools wheel
  Write-OK "pip/setuptools/wheel ready."
} catch { Write-Err "pip bootstrap failed: $($_.Exception.Message)"; exit 1 }

# Create venv
$venvPath   = Join-Path $ProjectDir ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
  Write-Info "Creating virtual environment in .venv ..."
  & $pythonExe -m venv ".venv"
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $venvPython)) { Write-Err "Failed to create virtual environment."; exit 1 }
  Write-OK "Virtual environment created."
} else { Write-Info "Virtual environment already exists." }

# Upgrade pip inside venv
Write-Info "Upgrading pip inside venv..."
& $venvPython -m pip install --upgrade pip setuptools wheel

# ---------- FIXED FUNCTION: no collision with $args ---------- #
function Install-WithArgs {
  param([string[]]$pkgArgs)
  # Use splatting with a NON-reserved name
  & $venvPython -m pip install @pkgArgs
  return ($LASTEXITCODE -eq 0)
}

# Install dependencies
$requirements = Join-Path $ProjectDir "requirements.txt"
$installedOK = $false

if (Test-Path -LiteralPath $requirements) {
  Write-Info "Installing from requirements.txt ..."
  if (Install-WithArgs @("-r","requirements.txt","--upgrade")) {
    $installedOK = $true
  } else {
    Write-Warn "Retrying with --prefer-binary and --no-cache-dir ..."
    if (Install-WithArgs @("-r","requirements.txt","--upgrade","--prefer-binary","--no-cache-dir")) {
      $installedOK = $true
    }
  }
} else {
  Write-Warn "requirements.txt not found. Falling back to individual packages."
}

if (-not $installedOK) {
  $pkgs = @(
    "ultralytics>=8.0.0",
    "opencv-python>=4.8.0",
    "pyautogui>=0.9.54",
    "mss>=9.0.1",
    "numpy>=1.24.0",
    "pynput>=1.7.6"
  )
  foreach ($p in $pkgs) {
    Write-Info "Installing $p ..."
    if (-not (Install-WithArgs @($p,"--prefer-binary","--no-cache-dir"))) {
      Write-Err "Failed to install $p (continuing)."
    }
  }
}

Write-OK "Dependency installation step complete."

# Create Start_IHNT.bat
$batPath = Join-Path $ProjectDir "Start_IHNT.bat"
$batContent = @"
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
"@
Set-Content -LiteralPath $batPath -Value $batContent -Encoding ASCII
Write-OK "Launcher created: $batPath"

# Optional smoke test
Write-Info "Quick import test (cv2, numpy, mss, pynput, ultralytics)..."
$importTest = @"
try:
    import cv2, numpy, mss, pynput, ultralytics
    print('IMPORTS_OK')
except Exception as e:
    print('IMPORTS_FAIL:', e)
"@
$tempPy = Join-Path $env:TEMP "ihnt_import_test.py"
Set-Content -LiteralPath $tempPy -Value $importTest -Encoding ASCII
& $venvPython $tempPy
Remove-Item -LiteralPath $tempPy -Force -ErrorAction SilentlyContinue

Write-OK "Setup completed. Use Start_IHNT.bat to run I-HNT."
Read-Host "Press Enter to exit"

