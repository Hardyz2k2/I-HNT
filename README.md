# Mob Finder Direct - SPEED OPTIMIZED Gaming Tool ⚡

An ultra-fast Python automation application optimized for targeting **MOVING MOBS** with lightning-quick processing and real-time verification.

## ⚡ SPEED FEATURES

- **⚡ ULTRA-FAST PROCESSING**: 50% smaller OCR area for lightning speed
- **🔍 REAL-TIME VERIFICATION**: Quick check before each click to catch moving mobs  
- **⚡ INSTANT CLICKING**: Direct clicks without mouse movement delays12
- **🔄 3x FASTER SCANNING**: 1-second intervals instead of 3 seconds
- **🎯 MOVING MOB OPTIMIZED**: Specifically designed to catch fast-moving targets
- **🛡️ SMART PROTECTION**: Advanced character and pet protection system
- **🎮 INTERACTIVE SETUP**: Enter your character and pet names at startup
- **⌨️ KEYBOARD AUTOMATION**: Continuously presses skill sequence (1,2,3,1,4,5)

3145## 🚀 Quick Start

23### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python mob_finder_direct.py
```

### 3. Setup Protection
When prompted, enter:
- Your character name
- Your pet names (one per line, press Enter twice to finish)

### 4. Start Gaming
- Focus your game window during the 3-second countdown
- The app will automatically start targeting mobs
- Your character and pets will be protected from clicks

## 🛡️ Protection Features

### Character Protection
- **Distance Protection**: 100-pixel safety radius around screen center
- **Name Protection**: Your character name is automatically avoided

### Pet Protection
- **Smart Matching**: Handles various name formats and OCR errors
- **Multiple Pets**: Support for unlimited pet names
- **Fuzzy Matching**: Works even with slight OCR misreads

### Example Protection
```
Character: "MyWarrior"
Pets: ["DragonPet", "PhoenixCompanion", "TigerMount"]

✅ Will target: "Black Tiger", "Baroi Wolf", "Spider"
🛡️ Will avoid: "MyWarrior", "DragonPet", "mywarrior", "dragonpet123"
```

## ⚙️ Configuration Files

### `mobs.txt`
List of mob names to target (comma-separated):
```
Mangyang, Black Tiger, Baroi Wolf, Earth Ghost, Spider
```

### `protected_names.txt` (Optional)
Pre-configure protected names:
```
# Character name
MyCharacter

# Pet names  
DragonPet
PhoenixPet
```
*Note: Interactive setup at startup overrides this file*

## ⚡ SPEED-OPTIMIZED WORKFLOW

1. **⚡ Ultra-Fast Capture**: Lightning-quick screenshots of optimized game area
2. **🔍 Speed OCR**: High-confidence text detection with 50% smaller processing area  
3. **🛡️ Instant Protection**: Real-time filtering of character/pet names
4. **🎯 Quick Detection**: Rapid mob identification from filtered text
5. **⚡ Direct Targeting**: Instant clicks without mouse movement delays
6. **🔍 Real-Time Verification**: Quick check that target hasn't moved
7. **🔄 Rapid Loop**: 1-second intervals for maximum responsiveness

## ⏹️ Stop Options

- **Ctrl+C**: Immediate stop
- **Text Commands**: Type any of these and press Enter:
  - `stop`
  - `quit` 
  - `exit`
  - `q`

## 🔧 System Requirements

- **Operating System**: Windows 10/11 (recommended), Linux, macOS
- **Python**: 3.7+ (Python 3.8+ recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Display**: 1920×1080 resolution (optimal performance)
- **Game**: Windowed or fullscreen mode

## 📦 Dependencies

All dependencies are automatically installed with:
```bash
pip install -r requirements.txt
```

**Core Libraries:**
- `easyocr` - Text recognition
- `opencv-python` - Image processing  
- `pyautogui` - Mouse/keyboard automation
- `mss` - Fast screen capture
- `numpy` - Numerical operations
- `pillow` - Image handling

## 🛠️ Troubleshooting

### OCR Not Working
- Ensure all dependencies are installed
- Try running: `pip install --upgrade easyocr`
- Make sure your game text is visible and not too small

### Protection Not Working  
- Verify you entered character/pet names correctly during setup
- Check console messages for protection confirmations
- Names are matched with fuzzy logic, so slight variations should work

### Mouse/Keyboard Not Working
- Make sure game window is focused
- Run application as administrator if needed
- Disable antivirus real-time protection temporarily

### Performance Issues
- Lower game resolution if needed
- Close unnecessary programs
- The app automatically optimizes processing areas

## 🎯 Game Compatibility

Designed for games where:
- Mob names appear as text above characters
- Screen resolution is 1920×1080 (adjustable)
- Text is readable by OCR
- Mouse clicking selects targets

## 🔒 Safety & Ethics

- **Personal Use Only**: Use responsibly and in accordance with game terms
- **Built-in Safeguards**: Multiple protection layers prevent accidents
- **Easy Shutdown**: Multiple stop options for immediate control
- **No Game Modification**: Only uses screen reading and input simulation

## 📝 Console Output

The application provides detailed feedback:
```
🛡️ Protected names configured: 3 names
🛡️ Protected names: MyCharacter, DragonPet, PhoenixPet
🔍 All detected text in game area:
   🛡️ Skipping protected name: 'MyCharacter' (character/pet protection)
   ✅ Found potential mob: 'Black Tiger' 
🎯 Targeting: 'Black Tiger' - Mouse moved and clicked!
```

---

## 🎉 Ready to Use!

Your streamlined mob finder is ready to go. Just run `python mob_finder_direct.py` and follow the prompts!

**Remember**: This SPEED OPTIMIZED version is specifically designed to catch MOVING MOBS! Focus your game window during the countdown, and experience lightning-fast targeting. ⚡🎯