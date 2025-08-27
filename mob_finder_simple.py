import time
import easyocr
import mss
import numpy as np
from PIL import Image
import warnings
import pyautogui
from difflib import SequenceMatcher
import cv2

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*pin_memory.*")
warnings.filterwarnings("ignore", message=".*CUDA.*")

class MobFinder:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080  # Default, will be updated
        self.mob_names = []
        self.reader = None
        self.sct = mss.mss()
        self.current_target = None
        self.monitoring_active = False
        
        # Load mob names
        self.load_mob_names()
        
        # Initialize OCR
        self.init_ocr()
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two strings using SequenceMatcher"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def is_similar_mob_name(self, detected_text, mob_name, similarity_threshold=0.7):
        """Check if detected text is similar to a mob name"""
        # Exact match
        if detected_text.lower() == mob_name.lower():
            return True
        
        # Calculate similarity
        similarity = self.calculate_similarity(detected_text, mob_name)
        
        # Check if similarity is above threshold
        if similarity >= similarity_threshold:
            print(f"   🔍 Similarity match: '{detected_text}' ≈ '{mob_name}' (similarity: {similarity:.2f})")
            return True
        
        # Handle common OCR errors for specific mob names
        if mob_name.lower() == "baroi wolf":
            # Common OCR misreadings of "Baroi Wolf"
            common_errors = [
                "baroi vvwolf", "baroi wwolf", "baroi wvolf", "baroi vvolf",
                "baroi wvlf", "baroi vvlf", "baroi wvol", "baroi vvol",
                "baroi wv", "baroi vv", "baroi wolf", "baroi wol"
            ]
            if detected_text.lower() in common_errors:
                print(f"   🔍 OCR error match: '{detected_text}' → '{mob_name}' (common misreading)")
                return True
        
        return False
    
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
            
            capture_time = time.time() - start_time
            print(f"✅ Screenshot captured in {capture_time:.3f}s")
            print(f"📱 Image size: {img_array.shape[1]}x{img_array.shape[0]}")
            
            return img_array
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def detect_text(self, image):
        """Detect text in the image using OCR"""
        if not self.reader:
            print("❌ OCR not available")
            return []
        
        start_time = time.time()
        print("🔍 Detecting text...")
        
        try:
            # Use EasyOCR to detect text with lower threshold for testing
            results = self.reader.readtext(
                image,
                paragraph=False,
                detail=1,
                height_ths=0.3,
                width_ths=0.3,
                text_threshold=0.3  # Lowered from 0.6 to catch more text
            )
            
            detection_time = time.time() - start_time
            print(f"✅ Text detection completed in {detection_time:.3f}s")
            print(f"📝 Found {len(results)} text elements")
            
            return results
            
        except Exception as e:
            print(f"❌ Text detection failed: {e}")
            return []

    def find_mob_names(self, ocr_results):
        """Find mob names in the detected text"""
        start_time = time.time()
        print("🎯 Searching for mob names...")
        
        found_mobs = []
        
        # Show all detected text for debugging
        print(f"\n🔍 All detected text (showing first 20):")
        for i, (bbox, text, confidence) in enumerate(ocr_results[:20]):
            print(f"   {i+1:2d}. '{text}' (confidence: {confidence:.2f})")
        
        if len(ocr_results) > 20:
            print(f"   ... and {len(ocr_results) - 20} more text elements")
        
        print(f"\n🔍 Searching for mob names with similarity matching...")
        for bbox, text, confidence in ocr_results:
            # Check if any mob name is found in the detected text
            for mob_name in self.mob_names:
                # Use similarity matching to handle OCR errors
                if self.is_similar_mob_name(text, mob_name) and confidence > 0.3:
                    found_mobs.append(self._create_mob_entry(mob_name, text, confidence, bbox))
                    print(f"   ✅ Found mob: '{text}' → '{mob_name}' (confidence: {confidence:.2f})")
                    break  # Found a mob in this text, move to next
        
        search_time = time.time() - start_time
        print(f"✅ Mob search completed in {search_time:.3f}s")
        
        return found_mobs
    
    def _create_mob_entry(self, mob_name, text, confidence, bbox):
        """Helper method to create a mob entry dictionary"""
        # Calculate center of bounding box
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        center_x = int(sum(x_coords) / len(x_coords))
        center_y = int(sum(y_coords) / len(y_coords))
        
        return {
            'name': mob_name,
            'text': text,
            'confidence': confidence,
            'position': (center_x, center_y),
            'bbox': bbox
        }
    
    def select_best_mob_instance(self, found_mobs):
        """Select the best mob instance (prioritize mobs closer to character/center of screen)"""
        if not found_mobs:
            return None
        
        # Calculate screen center (where character typically is)
        screen_center_x = 1920 // 2  # 960
        screen_center_y = 1080 // 2  # 540
        
        print(f"\n🔍 Analyzing {len(found_mobs)} mob instances for best selection:")
        print(f"📍 Character position (screen center): ({screen_center_x}, {screen_center_y})")
        
        for i, mob in enumerate(found_mobs, 1):
            # Calculate distance from character/center
            distance = ((mob['position'][0] - screen_center_x) ** 2 + (mob['position'][1] - screen_center_y) ** 2) ** 0.5
            screen_half = "UPPER" if mob['position'][1] < 540 else "LOWER"
            
            # Check if mob is very close (attacking)
            if distance < 50:
                status = "🔥 ATTACKING (Very Close!)"
            elif distance < 100:
                status = "⚔️ Close Combat"
            elif distance < 200:
                status = "🎯 Medium Range"
            else:
                status = "📏 Long Range"
                
            print(f"   {i}. {mob['name']} at {mob['position']} (Y: {mob['position'][1]}) - {screen_half} half")
            print(f"      📏 Distance: {distance:.1f} pixels | {status} | Confidence: {mob['confidence']:.2f}")
        
        # Prioritize mobs closer to character/center of screen
        def calculate_priority(mob):
            # Calculate distance from character/center
            distance = ((mob['position'][0] - screen_center_x) ** 2 + (mob['position'][1] - screen_center_y) ** 2) ** 0.5
            
            # EXTREME PRIORITY for attacking mobs (very close to character)
            if distance < 50:  # Mob is very close/overlapping with character
                # Give massive priority boost for attacking mobs
                attack_bonus = 100.0  # Extremely high priority
                print(f"   🔥 ATTACKING MOB DETECTED: '{mob['name']}' at distance {distance:.1f} - Extreme priority!")
                return attack_bonus
            
            # HIGH PRIORITY for close combat mobs
            elif distance < 100:
                close_combat_bonus = 50.0 + (1 - (distance / 100)) * 20
                return close_combat_bonus
            
            # Normal distance priority for medium/long range
            else:
                # Distance priority: Closer mobs get higher priority (inverse of distance)
                # Max screen diagonal is ~2200 pixels, so normalize distance to 0-1 range
                distance_score = max(0, 1 - (distance / 2200))
                
                # Confidence score (0-1)
                confidence_score = mob['confidence']
                
                # Combine scores: Distance is more important than confidence
                # Distance gets 80% weight, confidence gets 20% weight
                total_priority = (distance_score * 0.8) + (confidence_score * 0.2)
                
                return total_priority
        
        # Sort by calculated priority (highest first)
        sorted_mobs = sorted(found_mobs, key=calculate_priority, reverse=True)
        
        best_mob = sorted_mobs[0]
        best_priority = calculate_priority(best_mob)
        best_distance = ((best_mob['position'][0] - screen_center_x) ** 2 + (best_mob['position'][1] - screen_center_y) ** 2) ** 0.5
        
        print(f"\n🎯 Selection Results:")
        print(f"   Best instance: {best_mob['name']} at {best_mob['position']}")
        print(f"   Priority score: {best_priority:.3f}")
        print(f"   Distance from character: {best_distance:.1f} pixels")
        
        # Show priority reason
        if best_distance < 50:
            print(f"   🎯 Priority: EXTREME - Attacking mob (very close to character)")
        elif best_distance < 100:
            print(f"   🎯 Priority: HIGH - Close combat range")
        else:
            print(f"   🎯 Priority: NORMAL - Distance-based selection")
            
        print(f"   Screen half: {'UPPER' if best_mob['position'][1] < 540 else 'LOWER'}")
        
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
    
    def detect_health_bar(self, image):
        """Detect the red health bar in the target panel (top center)"""
        try:
            # Define the target panel area (top center of screen)
            # Target panel is typically around (800, 50) to (1120, 150)
            panel_x1, panel_y1 = 800, 50
            panel_x2, panel_y2 = 1120, 150
            
            # Extract the target panel region
            panel_region = image[panel_y1:panel_y2, panel_x1:panel_x2]
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(panel_region, cv2.COLOR_RGB2HSV)
            
            # Define red color range for health bar
            # Red wraps around in HSV, so we need two ranges
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            # Create masks for red detection
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            
            # Find contours in the red mask
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check if we found a red health bar
            health_bar_found = False
            if contours:
                # Look for horizontal red bars (health bars are typically horizontal)
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Health bars are typically wider than tall and in the middle of the panel
                    if w > h * 2 and w > 50 and y > 20 and y < 80:
                        health_bar_found = True
                        break
            
            return health_bar_found
            
        except Exception as e:
            print(f"   ⚠️ Health bar detection error: {e}")
            return False
    
    def monitor_current_target(self, found_mobs):
        """Continuously monitor the current target's health bar"""
        if not self.current_target or not found_mobs:
            return False
        
        print(f"\n🔍 Monitoring target: {self.current_target['name']} at {self.current_target['position']}")
        print("   📊 Checking health bar status...")
        
        # Capture current screen
        image = self.capture_screen()
        if image is None:
            return False
        
        # Check if health bar is still visible
        health_bar_visible = self.detect_health_bar(image)
        
        if health_bar_visible:
            print("   ✅ Health bar visible - target still alive")
            return True
        else:
            print("   ❌ Health bar disappeared - target died!")
            return False
    
    def select_next_best_mob(self, found_mobs, exclude_current=True):
        """Select the next best mob, excluding the current target if requested"""
        if not found_mobs:
            return None
        
        # Filter out the current target if requested
        available_mobs = found_mobs
        if exclude_current and self.current_target:
            available_mobs = [mob for mob in found_mobs if mob['position'] != self.current_target['position']]
            if not available_mobs:
                print("   ⚠️ No other mobs available")
                return None
        
        # Use the existing selection logic
        return self.select_best_mob_instance(available_mobs)
    
    def switch_target(self, new_target, found_mobs):
        """Switch to a new target and update monitoring"""
        if self.current_target:
            print(f"   🔄 Switching target: {self.current_target['name']} → {new_target['name']}")
        else:
            print(f"   🎯 Setting initial target: {new_target['name']}")
        
        self.current_target = new_target
        
        # Move mouse to new target
        if self.move_mouse_to_target(new_target['position']):
            print(f"   ✅ Mouse moved to new target: {new_target['name']}")
            return True
        else:
            print(f"   ❌ Failed to move mouse to new target")
            return False
    
    def continuous_monitoring_mode(self):
        """Run continuous monitoring mode - find mobs, select target, monitor health, switch when needed"""
        print("🚀 Starting Continuous Monitoring Mode")
        print("=" * 50)
        print("📋 This mode will:")
        print("   1. Find all available mobs")
        print("   2. Select the best target (closest/attacking)")
        print("   3. Monitor the target's health bar")
        print("   4. Automatically switch to next target when current dies")
        print("   5. Continue monitoring indefinitely")
        print("=" * 50)
        
        self.monitoring_active = True
        round_count = 0
        
        try:
            while self.monitoring_active:
                round_count += 1
                print(f"\n🔄 ROUND {round_count} - Scanning for mobs...")
                print("-" * 40)
                
                # Stage 1: Screenshot and find mobs
                image = self.capture_screen()
                if image is None:
                    print("❌ Screenshot failed, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                ocr_results = self.detect_text(image)
                if not ocr_results:
                    print("❌ No text detected, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                found_mobs = self.find_mob_names(ocr_results)
                if not found_mobs:
                    print("❌ No mobs found, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                
                print(f"🎉 Found {len(found_mobs)} mob(s) available")
                
                # Stage 2: Select target (current or new)
                if not self.current_target:
                    # First time - select best mob
                    best_mob = self.select_best_mob_instance(found_mobs)
                    if best_mob:
                        self.switch_target(best_mob, found_mobs)
                    else:
                        print("❌ Failed to select initial target, retrying...")
                        time.sleep(2)
                        continue
                else:
                    # Check if current target is still alive
                    target_alive = self.monitor_current_target(found_mobs)
                    
                    if not target_alive:
                        # Current target died, select new one
                        print("   💀 Current target died, selecting new target...")
                        new_target = self.select_next_best_mob(found_mobs, exclude_current=True)
                        if new_target:
                            self.switch_target(new_target, found_mobs)
                        else:
                            print("   ⚠️ No new targets available, waiting...")
                            time.sleep(3)
                            continue
                    else:
                        # Current target still alive, continue monitoring
                        print(f"   ✅ Target {self.current_target['name']} is still alive, continuing...")
                
                # Stage 3: Wait before next check
                print("   ⏱️ Waiting 3 seconds before next health check...")
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n⏹️ Continuous monitoring stopped by user")
            self.monitoring_active = False
        except Exception as e:
            print(f"\n❌ Error in continuous monitoring: {e}")
            self.monitoring_active = False
        
        print("🏁 Continuous monitoring mode ended")
    
    def run_analysis(self):
        """Run the complete mob finding analysis"""
        print("🚀 Starting Mob Finder Analysis")
        print("=" * 50)
        
        total_start_time = time.time()
        
        # Stage 1: Screenshot
        print("\n📸 STAGE 1: Screenshot Capture")
        print("-" * 30)
        image = self.capture_screen()
        if image is None:
            print("❌ Cannot continue without screenshot")
            return
        
        # Stage 2: Text Detection
        print("\n🔍 STAGE 2: Text Detection")
        print("-" * 30)
        ocr_results = self.detect_text(image)
        if not ocr_results:
            print("❌ No text detected in screenshot")
            return
        
        # Stage 3: Mob Name Search
        print("\n🎯 STAGE 3: Mob Name Search")
        print("-" * 30)
        found_mobs = self.find_mob_names(ocr_results)
        
        # Results
        print("\n📊 RESULTS")
        print("=" * 50)
        
        if found_mobs:
            print(f"🎉 Found {len(found_mobs)} mob instance(s)!")
            for i, mob in enumerate(found_mobs, 1):
                print(f"\n{i}. Mob: {mob['name']}")
                print(f"   📝 Full text: '{mob['text']}'")
                print(f"   🎯 Position: {mob['position']}")
                print(f"   📊 Confidence: {mob['confidence']:.2f}")
            
            # Stage 4: Select Best Instance and Move Mouse
            print("\n🎯 STAGE 4: Target Selection and Mouse Movement")
            print("-" * 30)
            
            best_mob = self.select_best_mob_instance(found_mobs)
            if best_mob:
                # Move mouse to target
                if self.move_mouse_to_target(best_mob['position']):
                    print("✅ Mouse movement successful!")
                    
                    # Ask user if they want to click
                    print("\n🖱️ Would you like to click on the target? (y/n): ", end="")
                    try:
                        user_input = input().lower().strip()
                        if user_input in ['y', 'yes']:
                            if self.click_on_target(best_mob['position']):
                                print("🎉 Target clicked successfully!")
                            else:
                                print("❌ Click failed")
                        else:
                            print("ℹ️ Click skipped by user")
                    except KeyboardInterrupt:
                        print("\n⏹️ Click cancelled by user")
                else:
                    print("❌ Mouse movement failed")
        else:
            print("❌ No mob names found in the screenshot")
            print("💡 Try adjusting the mob names in mobs.txt or check the screenshot content")
        
        # Time breakdown
        total_time = time.time() - total_start_time
        print(f"\n⏱️ Total execution time: {total_time:.3f}s")
        
        # Show sample of detected text for debugging
        if ocr_results:
            print(f"\n🔍 Sample detected text (first 5):")
            for i, (bbox, text, conf) in enumerate(ocr_results[:5]):
                print(f"   {i+1}. '{text}' (confidence: {conf:.2f})")

def main():
    print("🎮 Mob Finder - Advanced Version")
    print("Find mob names, move mouse, click on targets, and monitor health bars")
    print("=" * 70)
    
    # Create mob finder
    mob_finder = MobFinder()
    
    try:
        # Ask user which mode they want
        print("\n🎯 Select Mode:")
        print("   1. Single Analysis (find mobs once)")
        print("   2. Continuous Monitoring (find mobs, monitor health, auto-switch)")
        print("   3. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    print("\n🚀 Starting Single Analysis Mode...")
                    mob_finder.run_analysis()
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
