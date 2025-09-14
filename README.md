# I-HNT Gaming Assistant 🎯

**"I Have No Time" - Work Hard, Game Smart!** 💪

An ultra-fast gaming assistant using **YOLO AI** for real-time mob detection and hunting. Perfect for busy gamers who want to maximize their limited gaming time!

## 🔥 PROJECT EVOLUTION

**From Manual Gaming → I-HNT Automation:**
- **Previous**: OCR text detection (~3 FPS, unreliable with moving mobs)
- **Current**: YOLO AI visual detection (30+ FPS, real-time tracking)
- **Result**: 10x faster processing, catches fast-moving mobs reliably

## ⚡ YOLO ADVANTAGES

- **🤖 AI VISION**: Deep learning recognizes mob shapes/appearance directly
- **⚡ 30+ FPS PROCESSING**: Real-time detection without OCR delays
- **🎯 MULTI-MOB DETECTION**: Sees ALL mobs simultaneously in crowded scenes
- **🧠 TARGET PERSISTENCE**: Intelligent tracking until mob dies
- **🔍 ACTIVE HUNTING**: Automatically searches when no mobs visible
- **🛡️ SMART PROTECTION**: Position-based character/pet protection
- **💀 DEATH DETECTION**: Automatically detects player death confirmation window
- **🎯 CONFIGURABLE DETECTION AREA**: Adjustable hunting zone for different weapon types
- **🎮 GLOBAL HOTKEYS**: CapsLock start/pause control without window switching
- **⌨️ KEYBOARD AUTOMATION**: Continuous skill sequence (1,2,3,1,4,5)

## 🚀 Quick Start

### 1. One-Click Installation
```bash
# Simply double-click install_ihnt.bat - that's it!
# Automatically installs Python 3.11 + all dependencies
# Creates virtual environment and launcher
```

### 2. Run the Application
```bash
# Double-click Start_IHNT.bat (recommended)
# Or run: python i_hnt.py
```

**NEW**: Complete automation! Our installer handles Python, dependencies, and virtual environment setup.

### 3. Global Hotkey Control
- **Focus your game window** (important!)
- Press **CapsLock** to start detection
- Use hotkeys anytime - no need to switch back to terminal!

### 4. Advanced Setup (Optional)
- Train custom YOLO model for better accuracy (see README_YOLO.md)
- Configure protection settings during startup
- Adjust detection parameters for your specific game

## 🛡️ Protection Features

### Position-Based Protection
- **Distance Protection**: 150-pixel safety radius around screen center
- **Real-Time Filtering**: Automatically excludes detections near character
- **Configurable Radius**: Adjustable protection zone for different games

### Death Detection System
- **Automatic Detection**: Monitors center screen for death confirmation window
- **Smart Recognition**: Detects dark confirmation window with text patterns
- **Auto-Handling**: Optional automatic resurrection or wait for help
- **Safety Mode**: Stops all hunting activities when player dies

### Interactive Setup
- **Character Names**: Enter during startup for reference
- **Pet Names**: Multiple pet protection support
- **Smart Recognition**: Position-based protection works regardless of names

### Example Protection
```
Character Position: Screen center (960, 540)
Protection Radius: 150 pixels
Death Detection: Center screen monitoring active
Status: All mobs within 150px of center are ignored

✅ Will target: Mobs outside protection radius
🛡️ Will avoid: Any detection within 150px of character
💀 Will detect: Player death confirmation window
```

## ⚙️ Configuration Options

### YOLO Model Configuration
- **Pretrained Model**: `yolov8n.pt` (included) - for testing only
- **Custom Model**: Train your own for game-specific detection
- **Performance**: Nano model (fastest) vs larger models (more accurate)

### Global Hotkey Controls
- **CapsLock**: Start/Pause Toggle - works from anywhere
- **Ctrl+C**: Emergency stop in terminal
- No need to switch windows - stay focused on your game!

### Protection Settings
- **Position-based**: Safe radius around character (configurable)
- **Death Detection**: Monitor center screen for death confirmation window
- **Interactive Setup**: Enter character/pet names during startup
- **Smart Filtering**: Excludes detections near protected areas

### Death Detection Configuration
- **Mode 1 - Respawn at Town**: Automatically clicks "Resurrect at the specified point" and pauses the app
- **Mode 2 - Wait for Other Players**: Clicks "Waiting for other player's help", presses F4, uses auto-res scroll, then continues hunting
- **Auto-Res Scroll Slot**: Configurable slot number (0-9) for auto-resurrection scroll
- **Safety First**: All hunting activities stop immediately when death is detected
- **Interactive Setup**: Choose your preferred death handling mode at startup

### Detection Area Configuration
- **Small Area (Sword)**: 150px radius - Close combat weapons
- **Medium Area (Spear)**: 300px radius - Mid-range weapons (default)
- **Large Area (Bow)**: 500px radius - Long-range weapons
- **Custom Area**: User-defined radius for specific needs
- **Weapon-Specific**: Optimized hunting zones for different playstyles

## ⚡ YOLO WORKFLOW

1. **📸 Ultra-Fast Capture**: 30+ FPS screen capture of optimized game area
2. **🤖 AI Detection**: YOLO neural network processes entire frame instantly
3. **🛡️ Smart Protection**: Real-time filtering of protected character areas
4. **🎯 Visual Recognition**: Direct mob detection without text processing
5. **🧠 Target Persistence**: Intelligent tracking until health bar disappears
6. **🔍 Active Hunting**: Automatic area exploration when no mobs visible
7. **⚡ Real-Time Loop**: Continuous 30+ FPS processing for moving targets

## ⏹️ Control Options

### Global Hotkeys (Work from Game Window)
- **CapsLock**: Start/Pause Toggle
- **No window switching needed** - hotkeys work globally

### Terminal Commands
- **Ctrl+C**: Emergency stop in terminal
- Focus stays on your game for seamless experience

## 💿 Installation Options

### Option 1: One-Click Installation (Recommended)
- **Double-click `install_ihnt.bat`** - Installs everything automatically
- **Auto-installs Python 3.11** - Downloads and configures Python if missing
- **Creates virtual environment** - Isolated dependency management
- **Generates launcher** - Creates `Start_IHNT.bat` for easy startup
- **Internet required** - Only for first-time setup

### Option 2: PowerShell Installation (Alternative)
- **Run `install_ihnt.ps1`** - Advanced PowerShell installer
- **Enables Windows Long Paths** - Prevents path length issues
- **Winget integration** - Uses Windows Package Manager when available
- **Administrator rights** - May require elevation for system changes

### Option 3: Manual Installation (Advanced)
```bash
# If you already have Python 3.11+
pip install -r requirements.txt
python i_hnt.py
```

### Option 4: Quick Start (After Installation)
- **Double-click `Start_IHNT.bat`** - Launches the application
- **Uses virtual environment** - Automatically activates `.venv`
- **No command line needed** - Simple double-click startup

## 🔧 System Requirements

- **Operating System**: Windows 10/11 (primary), Linux/macOS (compatible)
- **Python**: Auto-installed (or 3.8+ if manual)
- **RAM**: 4GB minimum, 8GB recommended for YOLO processing
- **Display**: 1920×1080 resolution (optimal performance)
- **Game**: Windowed or fullscreen mode
- **Internet**: Required for initial setup only

## 📦 Dependencies

All dependencies are automatically installed with:
```bash
pip install -r requirements.txt
```

**Essential Libraries:**
- `ultralytics` - YOLOv8 for real-time object detection (includes PyTorch)
- `opencv-python` - Image processing
- `pyautogui` - Mouse/keyboard automation
- `mss` - Ultra-fast screen capture
- `numpy` - Numerical operations
- `pynput` - Global hotkeys and input monitoring

## 🛠️ Troubleshooting

### YOLO Not Detecting Mobs
- **Issue**: Pretrained model won't detect game mobs accurately
- **Solution**: Train custom model with your game screenshots (see README_YOLO.md)
- **Temporary**: Test with pretrained model to verify setup works

### Performance Issues
- **GPU Recommended**: CUDA support included with ultralytics for 30+ FPS processing
- **CPU Mode**: Will work but slower (5-15 FPS)
- **Close Programs**: Free up system resources for better performance

### Hotkeys Not Working
- **Run as Administrator**: May be needed for global hotkeys
- **Game Window Focus**: Make sure game window is active when pressing CapsLock
- **Antivirus**: Temporarily disable if blocking input automation

### Protection Issues
- **Position-Based**: Uses screen center protection radius
- **Interactive Setup**: Configure during startup for best results
- **Distance Adjustment**: Modify protection radius in code if needed

## 🎯 Game Compatibility

Designed for games where:
- Mobs have distinct visual appearance that can be trained
- Screen resolution is 1920×1080 (adjustable in code)
- Visual elements are clear enough for YOLO detection
- Mouse clicking selects/attacks targets

**Best Results With:**
- Custom trained YOLO model specific to your game
- Good lighting and contrast in game scenes
- Consistent mob appearance across different areas

## 🔒 Safety & Ethics

- **Personal Use Only**: Use responsibly and in accordance with game terms
- **Built-in Safeguards**: Multiple protection layers prevent accidents
- **Easy Shutdown**: Multiple stop options for immediate control
- **No Game Modification**: Only uses screen reading and input simulation

## 📝 Console Output

The application provides detailed real-time feedback:
```
🎯 I-HNT - Real-Time Gaming Assistant
🔥 GPU Available: ✅ YES (CUDA enabled)
🎯 Target FPS: 30
🛡️ Character protection: 150 pixel radius
🔍 Found 3 potential mobs
✅ Mob detected at (1250, 400) (confidence: 0.87)
🎯 ZONE TARGET SELECTED: (1250, 400) - Conf: 0.87
🖱️ Clicking target at (1250, 410)
❤️ HEALTH DETECTED: Mob alive - PAUSING DETECTION
📊 FPS: 32.1 | Processed 960 frames
```

---

## 🎉 Ready to Use!

Your I-HNT Gaming Assistant is ready to go! Just run `python i_hnt.py` or double-click "Start_IHNT.bat" and press CapsLock to start hunting!

## 📚 Additional Resources

- **README_YOLO.md**: Detailed YOLO setup and custom model training
- **README - Quick Start.txt**: Simple user guide for non-technical users
- **INSTALLATION_INSTRUCTIONS.txt**: Comprehensive installation guide
- **requirements.txt**: All necessary dependencies
- **yolov8n.pt**: Pretrained YOLO model for testing

## 📁 Project Structure

```
Mouse Mover/
├── i_hnt.py                    # Main application (I-HNT Gaming Assistant)
├── install_ihnt.bat           # One-click installer (Windows)
├── install_ihnt.ps1           # PowerShell installer (Advanced)
├── Start_IHNT.bat             # Application launcher (generated)
├── requirements.txt            # Python dependencies
├── yolov8n.pt                 # Pretrained YOLO model
├── README.md                  # Main documentation
├── README_YOLO.md             # YOLO training guide
├── README - Quick Start.txt   # Simple user guide
├── PROJECT_STATUS.md          # Project status and architecture
├── INSTALLATION_INSTRUCTIONS.txt # Detailed installation guide
└── .venv/                     # Virtual environment (created by installer)
```

## 🚀 Project Status

**✅ PRODUCTION READY** - I-HNT Gaming Assistant
- **Main Application**: `i_hnt.py` - Ultra-fast AI-powered hunting assistant
- **Easy Launcher**: `Start_IHNT.bat` - Double-click to start instantly
- **Auto Installer**: `install_ihnt.bat` - One-click setup with Python 3.11
- **Technology**: YOLO AI for 30+ FPS real-time processing
- **Key Features**: Smart hunting, target persistence, active exploration
- **Control**: Global CapsLock hotkey for seamless gaming

**🌟 Developed by HardyZ-2k2 - Black Angels Family 🔥**

**"I Have No Time" but I love to game!** Focus your game window, press CapsLock, and let I-HNT handle the hunting while you focus on strategy! 🎯💪