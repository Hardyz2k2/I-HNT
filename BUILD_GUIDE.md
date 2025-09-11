# 🚀 Building YOLO Mob Finder Executable

## Quick Start

To create a standalone executable and installer for your YOLO Mob Finder:

### 1. One-Click Build
Navigate to the `build_system` folder and run:
```batch
BUILD_INSTALLER.bat
```

### 2. What You'll Get
- **Standalone Executable** (`dist/YOLO_Mob_Finder.exe`) - Runs on any Windows PC without Python
- **Portable Version** (`YOLO_Mob_Finder_Portable/`) - Copy to USB drive, works anywhere  
- **Professional Installer** (`build_system/installer_output/`) - Creates Start Menu shortcuts

## Requirements
- Python 3.8+ (for building only)
- Inno Setup 6 (optional, for creating installer)

## Build System Files
All build-related files are organized in the `build_system/` folder:
- `BUILD_INSTALLER.bat` - Main build script (double-click to run)
- `mob_finder.spec` - PyInstaller configuration
- `installer_script.iss` - Inno Setup installer script
- `BUILD_INSTRUCTIONS.md` - Detailed build documentation

## Target System Requirements
- Windows 7 SP1 or newer
- 4GB+ RAM (8GB recommended)
- ~1GB disk space for installation

## Distribution
Once built, you can distribute:
- The single executable file
- The portable folder (no installation needed)
- The professional installer (recommended)

All methods work on target PCs without Python installed!

---
For detailed instructions, see `build_system/BUILD_INSTRUCTIONS.md`
