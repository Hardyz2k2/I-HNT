#!/usr/bin/env python3
"""
Mob Finder Direct - Direct Text Reading and Mouse Movement
This version reads text directly and moves the mouse to any mob with text above it
within the pre-defined red area margins. Automatically clicks without permission and avoids selecting the character.
"""

import time
import easyocr
import mss
import numpy as np
from PIL import Image
import warnings
import pyautogui
import cv2

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*pin_memory.*")
warnings.filterwarnings("ignore", message=".*CUDA.*")

class MobFinderDirect:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080
        self.mob_names = []
        self.reader = None
        self.sct = mss.mss()
        self.current_target = None
        self.monitoring_active = False
        
        # Pre-defined margins for the red area (based on your screenshot)
        # These margins define the game area where mobs are located
        self.margin_top = 150      # Below top UI panels
        self.margin_bottom = 150   # Above bottom UI panels
        self.margin_left = 200     # Left of game area
        self.margin_right = 200    # Right of game area
        
        # Load mob names
        self.load_mob_names()
        
        # Initialize OCR
        self.init_ocr()
        
        print(f"🎯 Mob Finder Direct initialized")
        print(f"📏 Game area: {self.screen_width-self.margin_left-self.margin_right}x{self.screen_height-self.margin_top-self.margin_bottom} pixels")
        print(f"🚫 Ignoring margins: Top={self.margin_top}, Bottom={self.margin_bottom}, Left={self.margin_left}, Right={self.margin_right}")
        print(f"🛡️ Character protection: 100 pixel radius around screen center")
    
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
            print(f"✅ Screenshot captured in {capture_time:.3f}s")
            print(f"📱 Full image size: {img_array.shape[1]}x{img_array.shape[0]}")
            print(f"🎮 Game area: ({game_x1}, {game_y1}) to ({game_x2}, {game_y2})")
            print(f"📏 Game area size: {game_x2 - game_x1}x{game_y2 - game_y1} pixels")
            
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
            
            # Use EasyOCR to detect text
            results = self.reader.readtext(
                cropped_image,
                paragraph=False,
                detail=1,
                height_ths=0.3,
                width_ths=0.3,
                text_threshold=0.3
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
            print(f"✅ Text detection completed in {detection_time:.3f}s")
            print(f"📝 Found {len(adjusted_results)} text elements in game area")
            
            return adjusted_results
            
        except Exception as e:
            print(f"❌ Text detection failed: {e}")
            return []
    
    def find_mobs_with_text(self, ocr_results):
        """Find mobs that have text above them in the game area"""
        start_time = time.time()
        print("🎯 Searching for mobs with text above them...")
        
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
            
            # Check if this text is in the game area and has reasonable confidence
            if confidence > 0.3:
                mob_entry = {
                    'text': text,
                    'confidence': confidence,
                    'position': (center_x, center_y),
                    'bbox': bbox,
                    'distance_from_character': distance_from_character
                }
                found_mobs.append(mob_entry)
                print(f"   ✅ Found potential mob: '{text}' at {mob_entry['position']} (confidence: {confidence:.2f}, distance from character: {distance_from_character:.1f})")
        
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
            # Calculate distance from character/center
            distance = mob['distance_from_character']
            
            # Check if mob is very close (attacking)
            if distance < 150:
                status = "⚔️ Close Combat"
            elif distance < 300:
                status = "🎯 Medium Range"
            else:
                status = "📏 Long Range"
                
            print(f"   {i}. '{mob['text']}' at {mob['position']} - {status}")
            print(f"      📏 Distance: {distance:.1f} pixels | Confidence: {mob['confidence']:.2f}")
        
        # Select mob closest to center
        best_mob = min(found_mobs, key=lambda mob: mob['distance_from_character'])
        
        print(f"\n🎯 Selection Results:")
        print(f"   Best target: '{best_mob['text']}' at {best_mob['position']}")
        print(f"   Distance from character: {best_mob['distance_from_character']:.1f} pixels")
        
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
        print("   5. Move mouse and AUTOMATICALLY click on target")
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
            # Move mouse to target
            if self.move_mouse_to_target(best_mob['position']):
                print("✅ Mouse movement successful!")
                
                # Automatically click on target (no permission needed)
                print("🖱️ Automatically clicking on target...")
                if self.click_on_target(best_mob['position']):
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
        print("   3. Automatically move mouse to best target")
        print("   4. AUTOMATICALLY click on target")
        print("   5. Continue monitoring indefinitely")
        print("=" * 50)
        print("💡 Press Ctrl+C to stop monitoring")
        print("=" * 50)
        
        self.monitoring_active = True
        round_count = 0
        
        try:
            while self.monitoring_active:
                round_count += 1
                print(f"\n🔄 ROUND {round_count} - Scanning for mobs with text...")
                print("-" * 40)
                
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
                
                found_mobs = self.find_mobs_with_text(ocr_results)
                if not found_mobs:
                    print("❌ No mobs with text found, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                print(f"🎉 Found {len(found_mobs)} mob(s) with text")
                
                # Select best target
                best_mob = self.select_best_mob(found_mobs)
                if best_mob:
                    print(f"🎯 Targeting: '{best_mob['text']}' at {best_mob['position']}")
                    
                    # Move mouse to target
                    if self.move_mouse_to_target(best_mob['position']):
                        print("✅ Mouse moved to target!")
                        
                        # Automatically click on target
                        print("🖱️ Automatically clicking on target...")
                        if self.click_on_target(best_mob['position']):
                            print("🎉 Target clicked!")
                        else:
                            print("❌ Click failed")
                    else:
                        print("❌ Failed to move mouse to target")
                
                # Wait before next scan
                print("   ⏱️ Waiting 3 seconds before next scan...")
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n⏹️ Continuous monitoring stopped by user")
            self.monitoring_active = False
        except Exception as e:
            print(f"\n❌ Error in continuous monitoring: {e}")
            self.monitoring_active = False
        
        print("🏁 Continuous monitoring mode ended")

def main():
    print("🎮 Mob Finder Direct - Direct Text Reading and Mouse Movement")
    print("Find mobs with text above them and move mouse directly to targets")
    print("🖱️ AUTOMATIC CLICKING - No permission needed!")
    print("🛡️ CHARACTER PROTECTION - Avoids selecting your character")
    print("=" * 70)
    
    # Create mob finder
    mob_finder = MobFinderDirect()
    
    try:
        # Ask user which mode they want
        print("\n🎯 Select Mode:")
        print("   1. Single Scan (find mobs once)")
        print("   2. Continuous Monitoring (continuously scan and target)")
        print("   3. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    print("\n🚀 Starting Single Scan Mode...")
                    mob_finder.run_single_scan()
                    break
                    
                elif choice == "2":
                    print("\n🚀 Starting Continuous Monitoring Mode...")
                    mob_finder.continuous_monitoring_mode()
                    break
                    
                elif choice == "3":
                    print("👋 Goodbye!")
                    return
                    
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n⏹️ Operation cancelled by user")
                break
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n🏁 Analysis complete!")

if __name__ == "__main__":
    main()
