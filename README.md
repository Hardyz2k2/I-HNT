# Mouse Mover & Mob Finder Suite

A Python application suite that automatically finds text on the screen, moves the mouse cursor to it, and performs automated actions. Includes a simple mouse mover and advanced mob finders with configurable screen margins.

## Applications

### 1. Mouse Mover (Simple)
A Python application that automatically finds the text "Light" on the screen, moves the mouse cursor to it, performs a left click, and then stops.

### 2. Mob Finder (Advanced)
An advanced application that finds mob names from a configurable list, moves the mouse to targets, and monitors health bars with configurable screen margins for improved performance.

### 3. Mob Finder Direct (Fast & Direct)
A streamlined version that directly reads text in the game area and moves the mouse to any mob with text above it, without text comparison or complex matching.

## Features

### Mouse Mover
- **Real-time monitoring** - Continuously scans your screen for "Light" text
- **Automatic detection** - Uses EasyOCR for accurate text recognition
- **Smart movement** - Moves mouse cursor to detected text with smooth animation
- **Auto-click** - Automatically left-clicks on the target once found
- **Auto-stop** - Application automatically exits after completing the mission
- **Performance optimized** - Fast screen capture and processing for real-time operation

### Mob Finder (Advanced)
- **Configurable Margins** - Ignore screen edges for faster text extraction
- **Mob Name Detection** - Find multiple mob types from a configurable list
- **Health Bar Monitoring** - Track target health and auto-switch when needed
- **Smart Target Selection** - Prioritize mobs by distance and combat status
- **Continuous Operation** - Run indefinitely with automatic target switching
- **Performance Optimization** - Cropped screen analysis reduces processing time

### Mob Finder Direct
- **Direct Text Reading** - No text comparison or complex matching
- **Pre-defined Margins** - Focuses on red game area automatically
- **Fast Processing** - Immediate mouse movement to text locations
- **Simple Targeting** - Finds any mob with text above it
- **Performance Focused** - Optimized for speed over accuracy

## Requirements

- Python 3.6 or higher
- Windows, macOS, or Linux

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Standard Real-Time Version
```bash
python mouse_mover.py
```

### Ultra-Fast Version (Maximum Performance)
```bash
python mouse_mover_ultra_fast.py
```

### Mob Finder (Advanced)
```bash
python mob_finder_simple.py
```

### Mob Finder Direct (Fast & Direct)
```bash
python mob_finder_direct.py
```

### Test Scripts
```bash
# Test margin functionality
python test_margins.py

# Test red area detection
python test_red_detection.py

# Test direct mob finder
python test_direct_finder.py
```

## How It Works

The application operates in a **one-shot mission** mode:

1. **🔍 Continuous Scanning** - Monitors your screen in real-time (10 FPS standard, 20 FPS ultra-fast)
2. **🎯 Target Detection** - Uses EasyOCR to find text containing "Light"
3. **🖱️ Smart Movement** - Moves mouse cursor to the highest-confidence text location
4. **🖱️ Auto-Click** - Performs left-click on the target
5. **✅ Mission Complete** - Automatically stops and exits

## Performance Features

- **Fast Screen Capture** - Uses `mss` library for optimized screen capture
- **Real-time Processing** - Processes frames continuously without delays
- **Smart Movement Logic** - Only moves mouse when target position changes significantly
- **Background OCR** - EasyOCR initialization runs in background thread
- **Optimized Settings** - Configured for speed vs. accuracy balance

## Configuration Options

### Standard Version (`mouse_mover.py`)
- **Capture Interval**: 100ms (10 FPS)
- **Movement Threshold**: 50 pixels
- **Mouse Movement Duration**: 0.2 seconds

### Ultra-Fast Version (`mouse_mover_ultra_fast.py`)
- **Capture Interval**: 50ms (20 FPS)
- **Movement Threshold**: 30 pixels
- **Mouse Movement Duration**: 0.05 seconds
- **Aggressive OCR Settings** - Faster but slightly less accurate

## Safety Features

- **Failsafe Disabled** - Allows real-time operation without corner-triggered stops
- **Manual Override** - Press Ctrl+C to stop at any time
- **Error Handling** - Graceful handling of OCR and mouse movement errors
- **Position Validation** - Ensures mouse movements are within screen bounds

## Use Cases

- **Automated Testing** - Click on specific UI elements
- **Accessibility** - Assist users with motor difficulties
- **Workflow Automation** - Automate repetitive clicking tasks
- **Gaming** - Auto-click on specific game elements
- **Data Entry** - Automate form interactions

## Troubleshooting

### No Text Detected
- Ensure "Light" text is clearly visible on screen
- Check that text has good contrast with background
- Verify EasyOCR models are properly downloaded

### Performance Issues
- Use the ultra-fast version for maximum speed
- Close unnecessary applications to free up CPU
- Ensure sufficient RAM for OCR processing

### Mouse Movement Issues
- Check that pyautogui has proper permissions
- Verify screen resolution detection is correct
- Ensure no other applications are controlling the mouse

## Technical Details

- **OCR Engine**: EasyOCR (CPU-optimized)
- **Screen Capture**: mss library for fast capture
- **Mouse Control**: pyautogui for cross-platform compatibility
- **Threading**: Background OCR initialization and real-time processing
- **Memory Management**: Efficient buffer management with deque

## Notes

- The application will **automatically stop** after clicking the target
- **Real-time operation** means continuous monitoring until target is found
- **Performance varies** based on system capabilities and screen content
- **First run** may be slower due to EasyOCR model download
- **CPU usage** will be higher during real-time operation
