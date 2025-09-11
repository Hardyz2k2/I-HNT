# YOLO Mob Finder - Build Instructions

## Creating Standalone Executable and Installer

This guide explains how to convert your YOLO Mob Finder Python project into a standalone executable that can run on any Windows PC without requiring Python installation.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (for building only)
- **Git** (if cloning from repository)
- **Inno Setup 6** (for creating Windows installer) - [Download here](https://jrsoftware.org/isdl.php)

### Python Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller pillow
```

## 🚀 Quick Build (Automated)

### Option 1: One-Click Build (Windows)
From the `build_system` folder:
```batch
BUILD_INSTALLER.bat
```
This script will:
1. Install all dependencies
2. Create application icons
3. Build standalone executable
4. Create portable distribution
5. Generate Windows installer (if Inno Setup installed)

### Option 2: Manual Steps

1. **Navigate to build_system folder**
   ```bash
   cd build_system
   ```

2. **Create Icons**
   ```bash
   python create_icon.py
   ```

3. **Build Executable**
   ```bash
   python build_executable.py
   ```

4. **Create Installer** (requires Inno Setup)
   ```bash
   iscc installer_script.iss
   ```

## 📁 Generated Files

After successful build, you'll have:

### Executable Files
- `../dist/YOLO_Mob_Finder.exe` - Standalone executable
- `../YOLO_Mob_Finder_Portable/` - Complete portable distribution
- `installer_output/YOLO_Mob_Finder_Installer_v1.0.exe` - Windows installer

### Build Artifacts
- `../build/` - PyInstaller build cache (can be deleted)
- `app_icon.ico` - Application icon file
- `installer_image.bmp` - Installer wizard images

## 🔧 Folder Structure

```
Mouse-Mover/
├── mob_finder.py           # Main application
├── requirements.txt        # Project dependencies
├── yolov8n.pt             # YOLO model
├── README.md              # Main documentation
├── PROJECT_STATUS.md      # Project status
├── README_YOLO.md         # YOLO training guide
├── dist/                  # Generated executable (after build)
├── build/                 # Build cache (after build)
└── build_system/          # Build system files
    ├── BUILD_INSTALLER.bat       # Main build script
    ├── mob_finder.spec           # PyInstaller config
    ├── build_executable.py       # Build automation
    ├── create_icon.py           # Icon creator
    ├── installer_script.iss     # Inno Setup script
    ├── LICENSE.txt              # Software license
    ├── INSTALLATION_INFO.txt    # Pre-install info
    ├── USAGE_INSTRUCTIONS.txt   # Post-install guide
    ├── BUILD_INSTRUCTIONS.md    # This file
    └── installer_output/        # Generated installer
```

## 🔧 Customization Options

### PyInstaller Configuration (`mob_finder.spec`)

**Performance Options:**
```python
# Reduce executable size
excludes=['tkinter', 'unittest', 'pdb']

# Enable UPX compression
upx=True

# Bundle everything in one file
onefile=True  # Add to EXE() parameters
```

**Adding Files:**
```python
datas = [
    ('custom_model.pt', '.'),     # Custom YOLO model
    ('config.yaml', 'config/'),   # Configuration files  
    ('assets/*', 'assets/'),      # Asset folder
]
```

### Installer Configuration (`installer_script.iss`)

**Version Information:**
```inno
#define MyAppVersion "1.1"
#define MyAppPublisher "Your Company"
```

**Installation Options:**
```inno
PrivilegesRequired=admin        ; Require admin rights
DefaultDirName={autopf}\YourApp ; Installation directory
```

## 🧪 Testing

### Testing Executable
1. Copy `../dist/YOLO_Mob_Finder.exe` to clean PC (no Python)
2. Run and verify all features work
3. Check console output for missing dependencies
4. Test on different Windows versions (7, 10, 11)

### Testing Portable Distribution
1. Copy `../YOLO_Mob_Finder_Portable/` folder to USB drive
2. Run on different computers
3. Verify no installation required

### Testing Installer
1. Run installer on clean system
2. Verify shortcuts created
3. Test uninstaller
4. Check Start Menu entries

## 🚨 Troubleshooting

### Common Build Issues

**"Module not found" errors:**
```bash
# Add missing modules to hiddenimports in .spec file
hiddenimports = ['missing_module_name']
```

**Large executable size:**
```bash
# Exclude unnecessary modules
excludes = ['matplotlib', 'scipy', 'pandas']
```

**Missing files at runtime:**
```python
# Add data files to spec
datas = [('missing_file.txt', '.')]
```

### Runtime Issues

**"Failed to execute script" error:**
- Run from command prompt to see full error
- Check for missing DLL files
- Ensure all paths in code use relative paths

**Performance issues:**
- YOLO models may be slower without GPU
- Consider model optimization for CPU-only systems
- Test on target hardware specs

### Installer Issues

**Inno Setup compilation errors:**
- Check file paths in `installer_script.iss`
- Ensure all referenced files exist
- Use absolute paths for source files

## 📦 Distribution

### File Sizes (Approximate)
- Standalone executable: 800MB - 1.2GB
- Portable zip: 400MB - 600MB  
- Installer: 450MB - 650MB

### Distribution Methods

**Direct Distribution:**
- Share `YOLO_Mob_Finder_Portable.zip`
- No installation required
- Works from any folder

**Professional Distribution:**
- Use Windows installer (.exe)
- Creates Start Menu shortcuts
- Proper uninstall support
- Digital signing recommended

## 🔒 Security Considerations

### Windows Defender
- Large executables may trigger false positives
- Consider code signing certificate for distribution
- Test on multiple antivirus solutions

### Digital Signing (Optional)
```batch
# Sign executable (requires certificate)
signtool sign /f certificate.pfx /p password /t http://timestamp.verisign.com/scripts/timstamp.dll YOLO_Mob_Finder.exe
```

## 🎯 Advanced Configuration

### Custom YOLO Models
Add custom trained models to distribution:
```python
# In .spec file
datas = [
    ('custom_mob_model.pt', '.'),
    ('game_specific_model.pt', 'models/'),
]
```

### Configuration Files
Include default configuration:
```python
datas = [
    ('default_config.yaml', 'config/'),
    ('protection_settings.json', 'config/'),
]
```

### Multiple Executables
Create different versions for different games:
```inno
; In installer script
#define GameType "RPG"
Name: "{group}\{#MyAppName} ({#GameType})"; 
```

## 📊 Build Performance

### Build Times (Approximate)
- Icon creation: 5-10 seconds
- Executable build: 3-8 minutes (depending on system)
- Installer creation: 30-60 seconds

### System Requirements for Building
- 8GB+ RAM recommended
- 5GB+ free disk space
- SSD recommended for faster builds

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Build Executable
on: [push, release]
jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Build
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
        cd build_system
        python build_executable.py
```

## 💡 Tips and Best Practices

1. **Test Early and Often**
   - Build executables frequently during development
   - Test on clean systems without Python

2. **Minimize Dependencies**
   - Only include necessary packages
   - Use virtual environments for clean builds

3. **Optimize for Size**
   - Enable UPX compression
   - Exclude debugging modules
   - Use smaller YOLO models if acceptable

4. **User Experience**
   - Include comprehensive documentation
   - Create clear error messages
   - Provide troubleshooting guides

5. **Version Control**
   - Tag releases appropriately
   - Keep build scripts in version control
   - Document changes between versions

## 📞 Support

If you encounter issues during the build process:

1. Check console output for detailed error messages
2. Verify all dependencies are installed correctly
3. Test individual build steps manually
4. Check GitHub Issues for similar problems
5. Create detailed bug reports with:
   - Python version
   - Operating system
   - Full error messages
   - Steps to reproduce

---

**Happy Building! 🚀**

Your YOLO Mob Finder is now ready for distribution to any Windows PC!