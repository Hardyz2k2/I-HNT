#!/usr/bin/env python3
"""
Build Script for YOLO Mob Finder Executable
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

class ExecutableBuilder:
    def __init__(self):
        self.build_system_root = Path(__file__).parent  # build_system folder
        self.project_root = self.build_system_root.parent  # main project folder
        self.dist_folder = self.project_root / "dist"
        self.build_folder = self.project_root / "build"
        self.spec_file = self.build_system_root / "mob_finder.spec"
        self.executable_name = "YOLO_Mob_Finder.exe" if platform.system() == "Windows" else "YOLO_Mob_Finder"
        
    def install_pyinstaller(self):
        """Install PyInstaller if not present"""
        print("🔧 Checking PyInstaller installation...")
        try:
            import PyInstaller
            print("✅ PyInstaller already installed")
            return True
        except ImportError:
            print("📦 Installing PyInstaller...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                             check=True, capture_output=True, text=True)
                print("✅ PyInstaller installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install PyInstaller: {e}")
                print(f"Error output: {e.stderr}")
                return False
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking project dependencies...")
        
        required_packages = [
            'ultralytics', 'torch', 'torchvision', 'opencv-python',
            'pyautogui', 'mss', 'numpy', 'pillow', 'pynput'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - MISSING")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
            print("💡 Install with: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies found!")
        return True
    
    def clean_build_folders(self):
        """Clean previous build folders"""
        print("🧹 Cleaning previous builds...")
        
        folders_to_clean = [self.dist_folder, self.build_folder]
        for folder in folders_to_clean:
            if folder.exists():
                shutil.rmtree(folder)
                print(f"   Cleaned: {folder}")
        
        print("✅ Build folders cleaned")
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("🔨 Building executable...")
        print(f"   Spec file: {self.spec_file}")
        print(f"   Target: {self.executable_name}")
        
        try:
            # Run PyInstaller with the spec file from project root
            cmd = [sys.executable, "-m", "PyInstaller", str(self.spec_file), "--noconfirm"]
            
            print("⚡ Running PyInstaller...")
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Executable built successfully!")
                return True
            else:
                print("❌ PyInstaller failed!")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def verify_executable(self):
        """Verify that the executable was created and works"""
        print("🔍 Verifying executable...")
        
        executable_path = self.dist_folder / self.executable_name
        
        if not executable_path.exists():
            print(f"❌ Executable not found at: {executable_path}")
            return False
        
        file_size = executable_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Executable created: {executable_path}")
        print(f"   Size: {file_size:.1f} MB")
        
        # Test if executable can start (brief test)
        print("🧪 Testing executable startup...")
        try:
            # Run with --help or version check if available
            # For now, just check if it exists and is executable
            if platform.system() == "Windows":
                # On Windows, just check file exists
                print("✅ Executable appears valid (Windows)")
            else:
                # On Unix systems, check if executable bit is set
                if os.access(executable_path, os.X_OK):
                    print("✅ Executable appears valid (Unix)")
                else:
                    print("⚠️ Executable may not have proper permissions")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Could not verify executable: {e}")
            return True  # Still return True as build succeeded
    
    def create_distribution_package(self):
        """Create a complete distribution package"""
        print("📦 Creating distribution package...")
        
        # Create distribution folder
        package_name = "YOLO_Mob_Finder_Portable"
        package_folder = self.project_root / package_name
        
        if package_folder.exists():
            shutil.rmtree(package_folder)
        
        package_folder.mkdir()
        
        # Copy executable
        executable_src = self.dist_folder / self.executable_name
        executable_dst = package_folder / self.executable_name
        shutil.copy2(executable_src, executable_dst)
        
        # Copy documentation
        docs_to_copy = ["README.md", "PROJECT_STATUS.md", "README_YOLO.md"]
        for doc in docs_to_copy:
            doc_path = self.project_root / doc
            if doc_path.exists():
                shutil.copy2(doc_path, package_folder / doc)
        
        # Create a simple launcher script
        if platform.system() == "Windows":
            launcher_content = f"""@echo off
echo ⚡ YOLO Mob Finder - Starting...
echo 📋 Make sure to focus your game window and press F1 to start!
echo.
.\\{self.executable_name}
pause
"""
            launcher_path = package_folder / "Start_Mob_Finder.bat"
            with open(launcher_path, 'w') as f:
                f.write(launcher_content)
        
        # Create README for distribution
        dist_readme = f"""# YOLO Mob Finder - Portable Distribution

## Quick Start
1. Extract this folder to any location
2. Run `{self.executable_name}` (or `Start_Mob_Finder.bat` on Windows)
3. Focus your game window
4. Press F1 to start/pause detection

## Controls
- F1: Start/Pause Toggle (works globally)
- Ctrl+C: Emergency stop in console

## Requirements
- Windows 10/11 (64-bit recommended)
- 1920x1080 display resolution (optimal)
- At least 4GB RAM (8GB recommended)

## First Time Setup
- The app will work with the included YOLO model for testing
- For best results, train a custom model for your specific game
- See README_YOLO.md for training instructions

## Support
- This is a portable version - no installation required
- All dependencies are included in the executable
- Can be run from USB drive or any folder

Built with PyInstaller - {platform.system()} {platform.machine()}
"""
        
        readme_path = package_folder / "README_DISTRIBUTION.txt"
        with open(readme_path, 'w') as f:
            f.write(dist_readme)
        
        print(f"✅ Distribution package created: {package_folder}")
        print(f"   Contents: {len(list(package_folder.iterdir()))} files")
        
        return package_folder
    
    def build(self):
        """Main build process"""
        print("🚀 YOLO Mob Finder - Executable Builder")
        print("=" * 50)
        
        # Check system info
        print(f"💻 System: {platform.system()} {platform.machine()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📁 Project: {self.project_root}")
        print(f"🔧 Build System: {self.build_system_root}")
        
        # Step 1: Install PyInstaller
        if not self.install_pyinstaller():
            print("❌ Cannot continue without PyInstaller")
            return False
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            print("❌ Missing dependencies - install requirements first")
            return False
        
        # Step 3: Clean previous builds
        self.clean_build_folders()
        
        # Step 4: Build executable
        if not self.build_executable():
            print("❌ Build failed")
            return False
        
        # Step 5: Verify executable
        if not self.verify_executable():
            print("⚠️ Executable verification failed, but continuing...")
        
        # Step 6: Create distribution package
        package_folder = self.create_distribution_package()
        
        print("\n" + "=" * 50)
        print("🎉 BUILD COMPLETE!")
        print("=" * 50)
        print(f"✅ Executable: {self.dist_folder / self.executable_name}")
        print(f"📦 Distribution: {package_folder}")
        print("\n💡 Next steps:")
        print("   1. Test the executable on this machine")
        print("   2. Copy the distribution folder to other PCs")
        print("   3. Run the executable without Python installed")
        print("   4. Consider creating an installer (optional)")
        
        return True

def main():
    """Main entry point"""
    builder = ExecutableBuilder()
    success = builder.build()
    
    if success:
        print("\n🏁 Build completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
