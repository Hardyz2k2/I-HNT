#!/usr/bin/env python3
"""
Mob Finder Direct - Direct Text Reading and Mouse Movement
This version reads text directly and moves the mouse to any mob with text above it
within the pre-defined red area margins. Automatically clicks without permission, avoids selecting the character,
uses text-to-mob offset for accurate targeting, and continuously presses keyboard buttons (123145).
"""

import time
import easyocr
import mss
import numpy as np
from PIL import Image
import warnings
import pyautogui
import cv2
import threading

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*pin_memory.*")
warnings.filterwarnings("ignore", message=".*CUDA.*")

class MobFinderDirect:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080
        self.mob_names = []
        self.protected_names = []  # Character and pet names to avoid
        self.reader = None
        self.sct = mss.mss()
        self.current_target = None
        self.monitoring_active = False
        self.keyboard_active = False
        self.stop_requested = False
        
        # SPEED OPTIMIZED: Ultra-small margins for maximum speed
        # Reduced to 50/75 for minimal processing area - mobs should be near center anyway
        self.margin_top = 50       # Ultra-reduced for speed
        self.margin_bottom = 50    # Ultra-reduced for speed
        self.margin_left = 75      # Ultra-reduced for speed
        self.margin_right = 75     # Ultra-reduced for speed
        
        # Text-to-mob offset: move mouse downward from text to click on mob body
        self.text_to_mob_offset_y = 30  # Reduced for faster targeting
        
        # Speed optimization flags
        self.fast_mode = True
        self.quick_click = True
        
        # Exclusion zone: bottom-left chat area to avoid
        # Coordinates: (0, 800) to (400, 1080) - bottom-left chat/UI elements
        self.exclusion_zone = {'x1': 0, 'y1': 800, 'x2': 400, 'y2': 1080}  # pixels downward from text center to mob body
        
        # Load mob names
        self.load_mob_names()
        
        # Initialize protected names (will be set interactively)
        self.protected_names = []
        
        # Initialize OCR
        self.init_ocr()
        
        print(f"⚡ Mob Finder Direct initialized - SPEED OPTIMIZED MODE")
        print(f"📏 Game area: {self.screen_width-self.margin_left-self.margin_right}x{self.screen_height-self.margin_top-self.margin_bottom} pixels (ULTRA-SMALL FOR SPEED)")
        print(f"🚫 Margins: Top={self.margin_top}, Bottom={self.margin_bottom}, Left={self.margin_left}, Right={self.margin_right}")
        print(f"🛡️ Character protection: 100 pixel radius around screen center")
        print(f"⚡ SPEED MODE: Fast targeting with {self.text_to_mob_offset_y}px offset")
        print(f"⚡ QUICK CLICK: {'Enabled' if self.quick_click else 'Disabled'} - Direct clicks without mouse movement")
        print(f"⌨️ Continuous keyboard pressing: 123145 sequence")
        print(f"⏹️ Stop options: Press Ctrl+C or type 'stop' and press Enter")
    
    def load_mob_names(self):
        """Load mob names from mobs.txt file"""
        start_time = time.time()
        print("📚 Loading mob names...")
        
        try:
            with open('mobs.txt', 'r', encoding='utf-8') as file:
                content = file.read().strip()
                # Split by comma and clean up each name
                self.mob_names = [name.strip() for name in content.split(',') if name.strip()]
            
            load_time = time.time() - start_time
            print(f"✅ Loaded {len(self.mob_names)} mob names in {load_time:.3f}s")
            print(f"📋 Mob names: {', '.join(self.mob_names[:10])}{'...' if len(self.mob_names) > 10 else ''}")
            
        except Exception as e:
            print(f"❌ Error loading mob names: {e}")
            # Fallback to default mob names
            self.mob_names = ["Tiger", "Wolf", "Spider", "Ghost", "Demon", "Bandit"]
            print(f"🔄 Using fallback mob names: {', '.join(self.mob_names)}")
    
    def load_protected_names(self):
        """Load protected names (character and pets) from protected_names.txt file"""
        start_time = time.time()
        print("🛡️ Loading protected names...")
        
        try:
            with open('protected_names.txt', 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # Process each line, skip comments and empty lines
                self.protected_names = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.protected_names.append(line)
            
            load_time = time.time() - start_time
            print(f"✅ Loaded {len(self.protected_names)} protected names in {load_time:.3f}s")
            if self.protected_names:
                print(f"🛡️ Protected names: {', '.join(self.protected_names)}")
            else:
                print(f"ℹ️ No protected names configured (add names to protected_names.txt)")
            
        except FileNotFoundError:
            print(f"⚠️ protected_names.txt not found - no name protection active")
            self.protected_names = []
        except Exception as e:
            print(f"❌ Error loading protected names: {e}")
            self.protected_names = []
    
    def set_protected_names_interactively(self, character_name, pet_names):
        """Set protected names from interactive input"""
        self.protected_names = []
        
        # Add character name if provided
        if character_name and character_name.strip():
            self.protected_names.append(character_name.strip())
        
        # Add pet names if provided
        if pet_names:
            for pet_name in pet_names:
                if pet_name and pet_name.strip():
                    self.protected_names.append(pet_name.strip())
        
        print(f"🛡️ Protected names configured: {len(self.protected_names)} names")
        if self.protected_names:
            print(f"🛡️ Protected names: {', '.join(self.protected_names)}")
        else:
            print(f"ℹ️ No protected names configured - will not avoid any names")
    
    def init_ocr(self):
        """Initialize EasyOCR"""
        start_time = time.time()
        print("🔧 Initializing OCR...")
        
        try:
            # Force CPU mode to avoid GPU issues
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            init_time = time.time() - start_time
            print(f"✅ OCR initialized successfully in {init_time:.3f}s")
            
        except Exception as e:
            print(f"❌ OCR initialization failed: {e}")
            self.reader = None
    
    def is_protected_name(self, text):
        """Check if the detected text matches any protected names (character or pets)"""
        if not self.protected_names:
            return False
        
        text_lower = text.lower().strip()
        
        for protected_name in self.protected_names:
            protected_lower = protected_name.lower().strip()
            
            # Exact match
            if text_lower == protected_lower:
                return True
            
            # Partial match (protected name contained in text)
            if protected_lower in text_lower:
                return True
            
            # Reverse partial match (text contained in protected name)
            if text_lower in protected_lower:
                return True
            
            # Calculate similarity for fuzzy matching (handle OCR errors)
            similarity = self.calculate_similarity(text_lower, protected_lower)
            if similarity > 0.8:  # High similarity threshold for protected names
                return True
        
            return False
    
    def quick_target_verification(self, target_position):
        """Quickly verify target is still at position before clicking"""
        if not self.fast_mode:
            return True
            
        try:
            print(f"   🔍 Quick verification at {target_position}...")
            # Take a small screenshot around the target area
            x, y = target_position
            
            # Small area around target (100x100 pixels)
            verification_area = {
                'top': max(0, y - 50),
                'left': max(0, x - 50), 
                'width': 100,
                'height': 100
            }
            
            verification_shot = self.sct.grab(verification_area)
            verification_img = np.array(verification_shot)
            
            # Quick OCR check with very fast settings
            if self.reader:
                quick_results = self.reader.readtext(
                    verification_img,
                    paragraph=False,
                    detail=1,
                    height_ths=0.7,    # Very fast settings
                    width_ths=0.7,
                    text_threshold=0.7
                )
                
                # If we find any text, target is probably still there
                has_text = len(quick_results) > 0
                print(f"   {'✅' if has_text else '❌'} Quick verification: {'Target still there' if has_text else 'Target moved'}")
                return has_text
            
            return True  # If OCR fails, assume target is there
            
        except Exception as e:
            print(f"   ⚠️ Quick verification failed: {e}")
            return True  # If verification fails, proceed anyway
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
    def ensure_game_focused(self):
        """Try to ensure the game window is focused (without clicking)"""
        try:
            # Just bring the window to front without clicking
            # Note: This method no longer clicks to avoid unwanted center clicks
            return True
        except Exception as e:
            print(f"⚠️ Could not focus game window: {e}")
            return False

    def stop_monitoring(self):
        """Stop the monitoring and keyboard automation"""
        print("\n⏹️ Stop requested by user")
        self.stop_requested = True
        self.monitoring_active = False
        self.keyboard_active = False
        print("🛑 Stopping all operations...")

    def check_stop_input(self):
        """Check if user wants to stop (non-blocking)"""
        try:
            import msvcrt
            import sys
            
            # Windows-specific non-blocking input check
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':  # Enter key
                    # Read the line that was typed
                    try:
                        line = input().strip().lower()
                        if line in ['stop', 'quit', 'exit', 'q']:
                            return True
                    except:
                        pass
        except:
            # Fallback for non-Windows or if msvcrt not available
            try:
                import select
                import sys
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.readline()
                    if line.strip().lower() in ['stop', 'quit', 'exit', 'q']:
                        return True
            except:
                pass
        return False

    def continuous_keyboard_pressing(self):
        """Continuously press keyboard buttons 123145 in a loop"""
        print("⌨️ Starting continuous keyboard pressing: 123145 sequence")
        self.keyboard_active = True
        sequence = "123145"
        sequence_count = 0
        
        try:
            while self.keyboard_active and self.monitoring_active and not self.stop_requested:
                for key in sequence:
                    if not self.keyboard_active or not self.monitoring_active or self.stop_requested:
                        break
                    
                    try:
                        # Press key without focusing (to avoid center clicks)
                        pyautogui.press(key)
                        print(f"   ⌨️ Pressed key: {key}")
                        time.sleep(0.1)  # Small delay between key presses
                    except Exception as e:
                        print(f"   ❌ Key press failed for '{key}': {e}")
                
                sequence_count += 1
                if sequence_count % 10 == 0:  # Only print every 10 sequences to reduce spam
                    print(f"   🔄 Completed {sequence_count} sequences: {sequence}")
                
                # Check for stop during wait
                for i in range(5):  # 0.5 seconds = 5 * 0.1 second intervals
                    if self.stop_requested or not self.keyboard_active or not self.monitoring_active:
                        break
                    time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Keyboard pressing error: {e}")
        finally:
            self.keyboard_active = False
            print("⌨️ Continuous keyboard pressing stopped")
    
    def capture_screen(self):
        """Capture screenshot of the entire screen"""
        start_time = time.time()
        print("📸 Capturing screenshot...")
        
        try:
            # Capture entire screen
            monitor = self.sct.monitors[1]  # Primary monitor
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Calculate the game area dimensions
            game_x1 = self.margin_left
            game_y1 = self.margin_top
            game_x2 = img_array.shape[1] - self.margin_right
            game_y2 = img_array.shape[0] - self.margin_bottom
            
            capture_time = time.time() - start_time
            print(f"⚡ FAST screenshot: {capture_time:.3f}s")
            print(f"📏 Processing area: {game_x2 - game_x1}x{game_y2 - game_y1} pixels (SPEED OPTIMIZED)")
            
            return img_array
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def detect_text_in_game_area(self, image):
        """Detect text in the game area (red area) only"""
        if not self.reader:
            print("❌ OCR not available")
            return []
        
        start_time = time.time()
        print("🔍 Detecting text in game area...")
        
        try:
            # Crop the image to focus only on the game area (red area)
            cropped_image = image[self.margin_top : self.screen_height - self.margin_bottom,
                                  self.margin_left : self.screen_width - self.margin_right]
            
            print(f"   ✂️ Analyzing game area: {cropped_image.shape[1]}x{cropped_image.shape[0]} pixels")
            
            # SPEED OPTIMIZED: Use EasyOCR with faster settings
            results = self.reader.readtext(
                cropped_image,
                paragraph=False,
                detail=1,
                height_ths=0.5,     # Increased for speed (less sensitive)
                width_ths=0.5,      # Increased for speed (less sensitive) 
                text_threshold=0.5  # Increased for speed (higher confidence only)
            )
            
            # Adjust bounding box coordinates back to full screen coordinates
            adjusted_results = []
            for bbox, text, confidence in results:
                # Adjust each point in the bounding box
                adjusted_bbox = []
                for point in bbox:
                    adjusted_x = point[0] + self.margin_left
                    adjusted_y = point[1] + self.margin_top
                    adjusted_bbox.append([adjusted_x, adjusted_y])
                
                adjusted_results.append((adjusted_bbox, text, confidence))
            
            detection_time = time.time() - start_time
            print(f"⚡ FAST OCR completed in {detection_time:.3f}s")
            print(f"📝 Found {len(adjusted_results)} text elements (HIGH CONFIDENCE ONLY)")
            
            return adjusted_results
            
        except Exception as e:
            print(f"❌ Text detection failed: {e}")
            return []
    
    def filter_game_text(self, ocr_results):
        """Filter out text that looks like code/IDE text and keep only game text"""
        print("🔍 Filtering out IDE/code text...")
        
        # Common code/IDE text patterns to filter out
        code_patterns = [
            'def ', 'class ', 'import ', 'from ', 'if ', 'elif ', 'else:', 'for ', 'while ',
            'return ', 'print(', 'print ', 'self.', 'try:', 'except:', 'finally:',
            'Pressed', 'key:', 'confidence:', 'distance', 'status', 'Range', 'Combat',
            'f"', 'f\'', '{}', '[]', '()', '==', '!=', '<=', '>=', '+=', '-=',
            'True', 'False', 'None', 'and', 'or', 'not', 'in ', 'is ', 'with ',
            'time.', 'pyautogui.', 'cv2.', 'np.', 'threading.', 'mss.',
            'screen_width', 'screen_height', 'margin_', 'bbox', 'center_',
            'mob_', 'text_', 'position', 'confidence', 'distance', 'character',
            'round_count', 'monitoring_active', 'keyboard_active', 'reader',
            'sct', 'current_target', 'mob_names', 'exclusion_zone'
        ]
        
        # Common single characters that are likely code
        single_chars = ['{', '}', '[', ']', '(', ')', '=', '+', '-', '*', '/', '%', '&', '|', '^', '~', '<', '>', '!', '?', ':', ';', ',', '.', '\'', '"', '`']
        
        # Common numbers that are likely line numbers or code
        line_numbers = [str(i) for i in range(1, 1000)]  # Line numbers 1-999
        
        filtered_results = []
        
        for bbox, text, confidence in ocr_results:
            # Skip very short text (likely noise)
            if len(text.strip()) < 2:
                continue
            
            # Skip text that contains code patterns
            text_lower = text.lower().strip()
            is_code_text = False
            
            for pattern in code_patterns:
                if pattern.lower() in text_lower:
                    is_code_text = True
                    break
            
            # Skip single characters
            if len(text.strip()) == 1 and text.strip() in single_chars:
                is_code_text = True
            
            # Skip line numbers
            if text.strip() in line_numbers:
                is_code_text = True
            
            # Skip text that's mostly numbers and symbols
            if len(text.strip()) > 0:
                non_alpha_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
                if non_alpha_chars > len(text.strip()) * 0.7:  # More than 70% non-alphanumeric
                    is_code_text = True
            
            # Skip text that looks like variable names (starts with lowercase, contains underscores)
            if text.strip().replace('_', '').replace(' ', '').islower() and '_' in text:
                is_code_text = True
            
            # Additional check: Skip protected names (character/pets)
            if not is_code_text and self.is_protected_name(text):
                is_code_text = True
                print(f"   🛡️ Filtering out: '{text}' (confidence: {confidence:.2f}) - protected name (character/pet)")
            
            if not is_code_text:
                filtered_results.append((bbox, text, confidence))
                print(f"   ✅ Keeping: '{text}' (confidence: {confidence:.2f})")
            else:
                if not self.is_protected_name(text):
                    print(f"   ❌ Filtering out: '{text}' (confidence: {confidence:.2f}) - looks like code/IDE text")
        
        print(f"⚡ SPEED FILTERED: {len(ocr_results)} -> {len(filtered_results)} text elements")
        return filtered_results

    def find_mobs_with_text(self, ocr_results):
        """Find mobs that have text above them in the game area"""
        start_time = time.time()
        print("⚡ FAST SCAN: Searching for mobs with text above them...")
        
        found_mobs = []
        
        # Show all detected text for debugging
        print(f"\n🔍 All detected text in game area:")
        for i, (bbox, text, confidence) in enumerate(ocr_results):
            print(f"   {i+1:2d}. '{text}' (confidence: {confidence:.2f})")
        
        # Calculate screen center (where character typically is)
        screen_center_x = 1920 // 2  # 960
        screen_center_y = 1080 // 2  # 540
        
        # Look for any text that might be mob names or labels
        for bbox, text, confidence in ocr_results:
            # Calculate center of bounding box
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            center_x = int(sum(x_coords) / len(x_coords))
            center_y = int(sum(y_coords) / len(y_coords))
            
            # Calculate distance from character/center
            distance_from_character = ((center_x - screen_center_x) ** 2 + (center_y - screen_center_y) ** 2) ** 0.5
            
            # Avoid selecting the character (text too close to center)
            if distance_from_character < 100:  # 100 pixel radius around character
                print(f"   ⚠️ Skipping '{text}' - too close to character (distance: {distance_from_character:.1f} pixels)")
                continue
            
            # CRITICAL: Skip protected names (character/pets)
            if self.is_protected_name(text):
                print(f"   🛡️ Skipping protected name: '{text}' (character/pet protection)")
                continue
            
            # SPEED: Higher confidence threshold for faster processing
            if confidence > 0.6:  # Increased from 0.3 to 0.6 for speed
                # Calculate the actual mob position (text position + offset)
                mob_x = center_x
                mob_y = center_y + self.text_to_mob_offset_y  # Move downward to mob body
                
                mob_entry = {
                    'text': text,
                    'confidence': confidence,
                    'text_position': (center_x, center_y),  # Original text position
                    'mob_position': (mob_x, mob_y),         # Actual mob body position
                    'bbox': bbox,
                    'distance_from_character': distance_from_character
                }
                found_mobs.append(mob_entry)
                print(f"   ✅ Found potential mob: '{text}' at text {mob_entry['text_position']} -> mob {mob_entry['mob_position']} (confidence: {confidence:.2f}, distance from character: {distance_from_character:.1f})")
        
        search_time = time.time() - start_time
        print(f"✅ Mob search completed in {search_time:.3f}s")
        print(f"🎯 Found {len(found_mobs)} potential mobs with text (excluding character)")
        
        return found_mobs
    
    def select_best_mob(self, found_mobs):
        """Select the best mob to target (closest to center)"""
        if not found_mobs:
            return None
        
        # Calculate screen center (where character typically is)
        screen_center_x = 1920 // 2  # 960
        screen_center_y = 1080 // 2  # 540
        
        print(f"\n🔍 Analyzing {len(found_mobs)} potential mobs for best selection:")
        print(f"📍 Character position (screen center): ({screen_center_x}, {screen_center_y})")
        
        for i, mob in enumerate(found_mobs, 1):
            # Calculate distance from character/center using mob position (not text position)
            distance = ((mob['mob_position'][0] - screen_center_x) ** 2 + (mob['mob_position'][1] - screen_center_y) ** 2) ** 0.5
            
            # Check if mob is very close (attacking)
            if distance < 150:
                status = "⚔️ Close Combat"
            elif distance < 300:
                status = "🎯 Medium Range"
            else:
                status = "📏 Long Range"
                
            print(f"   {i}. '{mob['text']}' - Text at {mob['text_position']}, Mob at {mob['mob_position']} - {status}")
            print(f"      📏 Distance: {distance:.1f} pixels | Confidence: {mob['confidence']:.2f}")
        
        # Select mob closest to center using mob position
        best_mob = min(found_mobs, key=lambda mob: 
            ((mob['mob_position'][0] - screen_center_x) ** 2 + (mob['mob_position'][1] - screen_center_y) ** 2) ** 0.5)
        
        best_distance = ((best_mob['mob_position'][0] - screen_center_x) ** 2 + (best_mob['mob_position'][1] - screen_center_y) ** 2) ** 0.5
        
        print(f"\n🎯 Selection Results:")
        print(f"   Best target: '{best_mob['text']}'")
        print(f"   Text position: {best_mob['text_position']}")
        print(f"   Mob position: {best_mob['mob_position']}")
        print(f"   Distance from character: {best_distance:.1f} pixels")
        print(f"   Offset applied: {self.text_to_mob_offset_y} pixels downward")
        
        return best_mob
    
    def move_mouse_to_target(self, target_position):
        """Move mouse to the target position"""
        start_time = time.time()
        print(f"🖱️ Moving mouse to target at {target_position}...")
        
        try:
            # Get current mouse position
            current_pos = pyautogui.position()
            print(f"📍 Current mouse position: {current_pos}")
            
            # Move mouse to target with smooth animation
            pyautogui.moveTo(target_position[0], target_position[1], duration=0.5)
            
            # Verify movement
            new_pos = pyautogui.position()
            movement_time = time.time() - start_time
            
            print(f"✅ Mouse moved to {new_pos} in {movement_time:.3f}s")
            return True
            
        except Exception as e:
            print(f"❌ Mouse movement failed: {e}")
            return False
    
    def click_on_target(self, target_position):
        """Click on the target position"""
        start_time = time.time()
        print(f"🖱️ Clicking on target at {target_position}...")
        
        try:
            # Perform left click
            pyautogui.click(target_position[0], target_position[1], button='left')
            
            click_time = time.time() - start_time
            print(f"✅ Clicked successfully in {click_time:.3f}s")
            return True
            
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    def run_single_scan(self):
        """Run a single scan to find and target mobs"""
        print("🚀 Starting Single Scan Mode")
        print("=" * 50)
        print("📋 This mode will:")
        print("   1. Capture screenshot")
        print("   2. Detect text in the game area (red area)")
        print("   3. Find mobs with text above them (avoiding character)")
        print("   4. Select best target (closest to center)")
        print("   5. Move mouse to mob body (text position + offset)")
        print("   6. AUTOMATICALLY click on target")
        print("=" * 50)
        
        total_start_time = time.time()
        
        # Stage 1: Screenshot
        print("\n📸 STAGE 1: Screenshot Capture")
        print("-" * 30)
        image = self.capture_screen()
        if image is None:
            print("❌ Cannot continue without screenshot")
            return
        
        # Stage 2: Text Detection in Game Area
        print("\n🔍 STAGE 2: Text Detection in Game Area")
        print("-" * 30)
        ocr_results = self.detect_text_in_game_area(image)
        if not ocr_results:
            print("❌ No text detected in game area")
            return
        
        # Stage 3: Find Mobs with Text
        print("\n🎯 STAGE 3: Finding Mobs with Text")
        print("-" * 30)
        found_mobs = self.find_mobs_with_text(ocr_results)
        
        if not found_mobs:
            print("❌ No mobs with text found in game area")
            return
        
        # Stage 4: Select Best Target and Move Mouse
        print("\n🎯 STAGE 4: Target Selection and Mouse Movement")
        print("-" * 30)
        
        best_mob = self.select_best_mob(found_mobs)
        if best_mob:
            # Move mouse to mob body position (not text position)
            if self.move_mouse_to_target(best_mob['mob_position']):
                print("✅ Mouse movement successful!")
                print(f"🎯 Mouse positioned at mob body: {best_mob['mob_position']}")
                print(f"📝 Text was detected at: {best_mob['text_position']}")
                
                # Automatically click on target (no permission needed)
                print("🖱️ Automatically clicking on target...")
                if self.click_on_target(best_mob['mob_position']):
                    print("🎉 Target clicked successfully!")
                else:
                    print("❌ Click failed")
            else:
                print("❌ Mouse movement failed")
        
        # Time breakdown
        total_time = time.time() - total_start_time
        print(f"\n⏱️ Total execution time: {total_time:.3f}s")
    
    def continuous_monitoring_mode(self):
        """Run continuous monitoring mode - continuously scan and target mobs"""
        print("🚀 Starting Continuous Monitoring Mode")
        print("=" * 50)
        print("📋 This mode will:")
        print("   1. Continuously scan the game area")
        print("   2. Find mobs with text above them (avoiding character)")
        print("   3. Automatically move mouse to mob body (text + offset)")
        print("   4. AUTOMATICALLY click on target")
        print("   5. Continue monitoring indefinitely")
        print("   6. Continuously press keyboard buttons: 123145")
        print("=" * 50)
        print("💡 Press Ctrl+C to stop monitoring")
        print("=" * 50)
        
        self.monitoring_active = True
        round_count = 0
        
        # Start keyboard pressing in a separate thread
        keyboard_thread = threading.Thread(target=self.continuous_keyboard_pressing, daemon=True)
        keyboard_thread.start()
        print("⌨️ Keyboard pressing thread started")
        
        try:
            while self.monitoring_active and not self.stop_requested:
                round_count += 1
                print(f"\n🔄 ROUND {round_count} - Scanning for mobs with text...")
                print("-" * 40)
                print("💡 Type 'stop' and press Enter to stop, or press Ctrl+C")
                
                # Check for stop input
                if self.check_stop_input():
                    self.stop_monitoring()
                    break
                
                # Capture screenshot and find mobs
                image = self.capture_screen()
                if image is None:
                    print("❌ Screenshot failed, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                ocr_results = self.detect_text_in_game_area(image)
                if not ocr_results:
                    print("❌ No text detected in game area, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                # Filter out text that looks like code/IDE text
                filtered_results = self.filter_game_text(ocr_results)
                if not filtered_results:
                    print("❌ No game text found after filtering, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                found_mobs = self.find_mobs_with_text(filtered_results)
                if not found_mobs:
                    print("❌ No mobs with text found, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                print(f"🎉 Found {len(found_mobs)} mob(s) with text")
                
                # Select best target
                best_mob = self.select_best_mob(found_mobs)
                if best_mob:
                    print(f"🎯 Targeting: '{best_mob['text']}' - Text at {best_mob['text_position']}, Mob at {best_mob['mob_position']}")
                    
                    # SPEED MODE: Quick verification and immediate action
                    target_pos = best_mob['mob_position']
                    
                    if self.quick_click:
                        # ULTRA FAST: Skip mouse movement, click directly
                        print(f"⚡ FAST MODE: Direct click at {target_pos}")
                        
                        # Quick verification before clicking
                        if self.quick_target_verification(target_pos):
                            if self.click_on_target(target_pos):
                                print("🎉 Fast target clicked!")
                            else:
                                print("❌ Fast click failed")
                        else:
                            print("❌ Target moved, skipping click")
                    else:
                        # NORMAL MODE: Move mouse then click
                        if self.move_mouse_to_target(target_pos):
                            print("✅ Mouse moved to mob body!")
                            
                            if self.click_on_target(target_pos):
                                print("🎉 Target clicked!")
                            else:
                                print("❌ Click failed")
                        else:
                            print("❌ Failed to move mouse to target")
                
                # SPEED: Much faster scanning - wait only 1 second
                print("   ⚡ Waiting 1 second before next scan (FAST MODE)...")
                for i in range(10):  # 1 second = 10 * 0.1 second intervals
                    if self.stop_requested or not self.monitoring_active:
                        break
                    time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Continuous monitoring stopped by user")
            self.monitoring_active = False
            self.keyboard_active = False
        except Exception as e:
            print(f"\n❌ Error in continuous monitoring: {e}")
            self.monitoring_active = False
            self.keyboard_active = False
        
        # Wait for keyboard thread to finish
        if keyboard_thread.is_alive():
            print("⌨️ Waiting for keyboard thread to finish...")
            self.keyboard_active = False
            keyboard_thread.join(timeout=2)
        
        print("🏁 Continuous monitoring mode ended")

def get_user_input():
    """Get character name and pet names from user input"""
    print("🛡️ CHARACTER & PET PROTECTION SETUP")
    print("=" * 50)
    print("To avoid accidentally clicking on your character or pets,")
    print("please provide the following information:")
    print()
    
    # Get character name
    while True:
        character_name = input("🧙 Enter your CHARACTER NAME (or press Enter to skip): ").strip()
        if not character_name:
            print("   ⚠️ No character name provided - character protection disabled")
            break
        else:
            print(f"   ✅ Character name: '{character_name}'")
            break
    
    # Get pet names
    pet_names = []
    print("\n🐕 Enter your PET NAMES (one per line, press Enter twice to finish):")
    print("   Examples: DragonPet, PhoenixPet, TigerPet")
    
    pet_count = 1
    while True:
        pet_name = input(f"   Pet #{pet_count} (or press Enter to finish): ").strip()
        if not pet_name:
            break
        else:
            pet_names.append(pet_name)
            print(f"   ✅ Added pet: '{pet_name}'")
            pet_count += 1
    
    if not pet_names:
        print("   ⚠️ No pet names provided - pet protection disabled")
    
    # Summary
    print("\n📋 PROTECTION SUMMARY:")
    if character_name:
        print(f"   🧙 Character: {character_name}")
    if pet_names:
        print(f"   🐕 Pets: {', '.join(pet_names)}")
    
    total_protected = (1 if character_name else 0) + len(pet_names)
    print(f"   🛡️ Total protected names: {total_protected}")
    
    if total_protected == 0:
        print("   ⚠️ No protection configured - all detected text will be targetable")
        confirm = input("\n   Continue without name protection? (y/N): ").lower().strip()
        if confirm != 'y' and confirm != 'yes':
            print("   👋 Setup cancelled by user")
            return None, None
    
    print("   ✅ Protection setup complete!")
    return character_name, pet_names

def main():
    print("🎮 Mob Finder Direct - Direct Text Reading and Mouse Movement")
    print("Find mobs with text above them and move mouse directly to targets")
    print("🖱️ AUTOMATIC CLICKING - No permission needed!")
    print("🛡️ CHARACTER PROTECTION - Avoids selecting your character")
    print("🎯 SMART TARGETING - Text-to-mob offset for accurate clicks")
    print("⌨️ CONTINUOUS KEYBOARD - Automatically presses 123145 sequence")
    print("🔄 AUTO-START - Automatically starts continuous monitoring mode")
    print("=" * 70)
    
    # Get user input for protection
    try:
        character_name, pet_names = get_user_input()
        if character_name is None and pet_names is None:
            return  # User cancelled
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
        return
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        return
    
    print("\n" + "=" * 70)
    print("🚀 INITIALIZING MOB FINDER")
    print("=" * 70)
    
    # Create mob finder
    mob_finder = MobFinderDirect()
    
    # Set protected names from user input (override file-based loading)
    mob_finder.set_protected_names_interactively(character_name, pet_names)
    
    # Check if OCR initialized properly
    if mob_finder.reader is None:
        print("❌ OCR initialization failed! Cannot proceed.")
        print("💡 Please check your Python dependencies and try again.")
        return
    
    try:
        print("\n⚡ STARTING SPEED OPTIMIZED TARGETING MODE...")
        print("💡 SPEED FEATURES ENABLED:")
        print("   ⚡ Ultra-small processing area for maximum speed")
        print("   🔍 Quick verification before each click")
        print("   ⚡ Direct clicking without mouse movement")
        print("   🔄 1-second scan intervals (3x faster)")
        print("💡 STOP OPTIONS:")
        print("   - Press Ctrl+C to stop immediately")
        print("   - Type 'stop', 'quit', 'exit', or 'q' and press Enter")
        print("💡 Make sure your GAME WINDOW is open and focused!")
        print("=" * 50)
        
        # Give user time to focus the game window
        print("⏱️ Starting in 3 seconds... Make sure your game window is focused!")
        print("📝 IMPORTANT: Click on your game window to focus it during this countdown!")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        # Automatically start continuous monitoring mode
        mob_finder.continuous_monitoring_mode()
        
    except KeyboardInterrupt:
        print("\n⏹️ Application stopped by user")
        mob_finder.monitoring_active = False
        mob_finder.keyboard_active = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        mob_finder.monitoring_active = False
        mob_finder.keyboard_active = False
    
    print("\n🏁 Application complete!")

if __name__ == "__main__":
    main()
