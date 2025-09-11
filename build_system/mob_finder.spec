# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for YOLO Mob Finder
Creates a standalone executable with all dependencies included
"""

import os
from pathlib import Path

# Get the directory containing this spec file and parent directory
spec_root = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(spec_root)

# Define paths (relative to project root)
main_script = os.path.join(project_root, 'mob_finder.py')
yolo_model = os.path.join(project_root, 'yolov8n.pt')

# Hidden imports for YOLO and deep learning libraries
hiddenimports = [
    'ultralytics',
    'torch',
    'torchvision', 
    'cv2',
    'numpy',
    'PIL',
    'yaml',
    'tqdm',
    'matplotlib',
    'mss',
    'pyautogui',
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'threading',
    'time',
    'pathlib',
    'platform',
    'socket',
    'urllib.request',
    'requests',
    'psutil',
    # YOLO specific modules
    'ultralytics.nn.modules',
    'ultralytics.utils',
    'ultralytics.engine',
    'ultralytics.models',
    'ultralytics.models.yolo',
    # PyTorch modules
    'torch.nn',
    'torch.nn.functional',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    'torchvision.transforms',
    'torchvision.models',
    # OpenCV modules
    'cv2.data',
    # Additional dependencies
    'pkg_resources.py2_warn',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements'
]

# Data files to include
datas = [
    (yolo_model, '.'),  # Include YOLO model in root of executable
    (os.path.join(project_root, 'README.md'), '.'),
    (os.path.join(project_root, 'PROJECT_STATUS.md'), '.'),
    (os.path.join(project_root, 'README_YOLO.md'), '.')
]

# Binaries (will be auto-detected, but we can specify additional ones)
binaries = []

# Analysis configuration
a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'unittest',
        'pdb',
        'doctest',
        'difflib',
        'inspect',
        'calendar',
        'pydoc',
        'pickle',
        'antigravity'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YOLO_Mob_Finder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debug output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'app_icon.ico') if os.path.exists(os.path.join(spec_root, 'app_icon.ico')) else None,
    version=None,
    uac_admin=False,  # Set to True if admin rights needed
    uac_uiaccess=False,
)

# Optional: Create a distribution folder (uncomment if needed)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='YOLO_Mob_Finder_Distribution'
# )