#!/usr/bin/env python3
"""
YOLO Mob Finder - Real-Time Visual Object Detection
Uses YOLOv8 for ultra-fast real-time mob detection instead of slow OCR.
Designed specifically for catching fast-moving mobs with computer vision.
"""

import time
import cv2
import numpy as np
import mss
import pyautogui
import threading
from ultralytics import YOLO
import torch
from pathlib import Path
from pynput import keyboard
from pynput.keyboard import Key, Listener

class YOLOMobFinder:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080
        self.protected_names = []
        self.model = None
        self.monitoring_active = False
        self.keyboard_active = False
        self.stop_requested = False
        
        # Target persistence tracking
        self.current_target = None
        self.target_selected_time = None
        self.target_timeout = 6.0  # 6 seconds timeout
        
        # Active hunting mode
        self.hunting_mode = False
        self.last_mob_seen_time = None
        self.hunting_delay = 3.0  # Wait 3 seconds before hunting
        self.hunting_radius = 200  # Radius around character to hunt in
        self.hunting_click_delay = 0.5  # Delay between hunting clicks
        
        # Global hotkey controls
        self.paused = False
        self.hotkey_listener = None
        self.hotkeys_active = False
        
        # YOLO optimized settings for speed
        self.conf_threshold = 0.25      # Confidence threshold
        self.iou_threshold = 0.45       # IoU threshold for NMS
        self.max_detections = 300       # Maximum detections per image
        
        # Gaming area optimization (focus on center area where mobs typically are)
        self.margin_top = 100
        self.margin_bottom = 200    # Leave space for UI
        self.margin_left = 100
        self.margin_right = 100
        
        # Protection settings
        self.character_protection_radius = 150  # Pixels around center
        
        # Targeting settings
        self.target_offset_y = 10  # Small offset to click mob body
        
        # Performance settings
        self.use_gpu = torch.cuda.is_available()
        self.fps_target = 30  # Target FPS for real-time processing
        
        print("⚡ YOLO Mob Finder - Real-Time Visual Detection")
        print("=" * 60)
        print(f"🔥 GPU Available: {'✅ YES' if self.use_gpu else '❌ NO (CPU mode)'}")
        print(f"🎯 Target FPS: {self.fps_target}")
        print(f"📏 Detection area: {self.screen_width-self.margin_left-self.margin_right}x{self.screen_height-self.margin_top-self.margin_bottom}")
        print(f"🛡️ Character protection: {self.character_protection_radius} pixel radius")
        print(f"🎯 Target persistence: {self.target_timeout}s timeout (no health monitoring)")
        print(f"🎯 Active hunting: {self.hunting_radius}px radius when no mobs found")
        print(f"🎮 Global hotkeys: F1=Start/Pause Toggle")
        
    def load_yolo_model(self, model_path="yolov8n.pt"):
        """Load YOLO model for mob detection"""
        print(f"\n🤖 Loading YOLO model: {model_path}")
        start_time = time.time()
        
        try:
            # Check if custom trained model exists, otherwise use pretrained
            if not Path(model_path).exists():
                print("⚠️ Custom model not found, using YOLOv8 nano (pretrained)")
                print("💡 Note: You'll need to train a custom model for mob detection")
                model_path = "yolov8n.pt"  # Use nano model for speed
            
            # Load model
            self.model = YOLO(model_path)
            
            # Optimize for inference speed
            if self.use_gpu:
                self.model.to('cuda')
                print("🔥 Model loaded on GPU for maximum speed")
            else:
                print("💻 Model loaded on CPU")
                
            load_time = time.time() - start_time
            print(f"✅ YOLO model loaded in {load_time:.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            print("💡 Install requirements: pip install ultralytics torch")
            return False
    
    
    def should_switch_target(self):
        """Determine if we should switch to a new target based on timeout only"""
        if self.current_target is None or self.target_selected_time is None:
            return True  # No current target, can select new one
        
        # Check timeout (6 seconds)
        elapsed_time = time.time() - self.target_selected_time
        if elapsed_time >= self.target_timeout:
            print(f"   ⏰ Target timeout ({elapsed_time:.1f}s) - switching targets")
            return True
        
        # Target still within timeout
        print(f"   🎯 Staying on current target ({elapsed_time:.1f}s elapsed)")
        return False
    
    def set_current_target(self, target):
        """Set the current target and start tracking time"""
        self.current_target = target
        self.target_selected_time = time.time()
        print(f"   🎯 New target locked: {target['screen_position']} (conf: {target['confidence']:.2f})")
    
    def generate_hunting_position(self):
        """Generate random position around character for active hunting"""
        import random
        import math
        
        # Character position (screen center)
        char_x = self.screen_width // 2
        char_y = self.screen_height // 2
        
        # Generate random angle and distance
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(50, self.hunting_radius)  # Min 50px, max hunting_radius
        
        # Calculate hunting position
        hunt_x = int(char_x + distance * math.cos(angle))
        hunt_y = int(char_y + distance * math.sin(angle))
        
        # Keep within screen bounds with margins
        hunt_x = max(self.margin_left + 50, min(hunt_x, self.screen_width - self.margin_right - 50))
        hunt_y = max(self.margin_top + 50, min(hunt_y, self.screen_height - self.margin_bottom - 50))
        
        return (hunt_x, hunt_y)
    
    def active_hunting_mode(self):
        """Click random areas around character to find mobs when none are detected"""
        if self.last_mob_seen_time is None:
            self.last_mob_seen_time = time.time()
            return
        
        # Check if we should start hunting (3 second delay)
        time_since_last_mob = time.time() - self.last_mob_seen_time
        
        if time_since_last_mob >= self.hunting_delay:
            if not self.hunting_mode:
                print(f"\n🎯 ACTIVE HUNTING MODE: No mobs for {time_since_last_mob:.1f}s - searching area!")
                self.hunting_mode = True
            
            # Generate random hunting position
            hunt_pos = self.generate_hunting_position()
            
            print(f"   🎯 Hunting click at {hunt_pos} (radius: {self.hunting_radius}px)")
            
            try:
                # Click hunting position
                pyautogui.click(hunt_pos[0], hunt_pos[1], button='left')
                time.sleep(self.hunting_click_delay)
                
            except Exception as e:
                print(f"   ❌ Hunting click failed: {e}")
        
    def update_mob_detection_status(self, mobs_found):
        """Update mob detection status for hunting mode"""
        if mobs_found:
            if self.hunting_mode:
                print(f"   ✅ Mobs found! Exiting hunting mode")
                self.hunting_mode = False
            self.last_mob_seen_time = time.time()  # Reset timer
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys that work even when game window is focused"""
        def on_hotkey_press(key):
            try:
                if key == Key.f1:
                    self.handle_f1_toggle()
            except Exception as e:
                print(f"⚠️ Hotkey error: {e}")
        
        # Start global hotkey listener in background thread
        try:
            self.hotkey_listener = Listener(on_press=on_hotkey_press)
            self.hotkey_listener.daemon = True  # Dies with main thread
            self.hotkey_listener.start()
            self.hotkeys_active = True
            print("🎮 Global hotkeys activated!")
            print("   F1 = Start/Pause Toggle")
            return True
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")
            return False
    
    def handle_f1_toggle(self):
        """Handle F1 - Toggle Start/Pause"""
        if not self.monitoring_active:
            # Not running - start detection
            print("\n🚀 F1 PRESSED - Starting detection...")
            self.paused = False
            self.start_detection_thread()
        elif self.paused:
            # Currently paused - resume
            print("\n▶️ F1 PRESSED - Detection RESUMED!")
            self.paused = False
        else:
            # Currently running - pause
            print("\n⏸️ F1 PRESSED - Detection PAUSED!")
            self.paused = True
    
    
    def cleanup_hotkeys(self):
        """Cleanup hotkey listener"""
        if self.hotkey_listener and self.hotkeys_active:
            try:
                self.hotkey_listener.stop()
                self.hotkeys_active = False
                print("🎮 Hotkeys deactivated")
            except:
                pass
    
    def setup_protection(self):
        """Interactive setup for character and pet protection"""
        print("\n🛡️ VISUAL PROTECTION SETUP")
        print("=" * 40)
        print("For YOLO detection, we'll use position-based protection")
        print("(Character/pet name detection will be added in future versions)")
        
        # Get character name for reference (even though we use position-based protection)
        character_name = input("🧙 Enter your CHARACTER NAME (for reference): ").strip()
        if character_name:
            self.protected_names.append(character_name)
            print(f"✅ Character: {character_name} (protected by position)")
        
        # Pet names
        print("\n🐕 Enter PET NAMES (press Enter twice to finish):")
        pet_count = 1
        while True:
            pet_name = input(f"   Pet #{pet_count} (or press Enter to finish): ").strip()
            if not pet_name:
                break
            self.protected_names.append(pet_name)
            print(f"✅ Added pet: {pet_name} (protected by position)")
            pet_count += 1
        
        print(f"\n🛡️ Protection Summary:")
        print(f"   Names for reference: {len(self.protected_names)}")
        print(f"   Protection method: Position-based (around screen center)")
        print(f"   Protection radius: {self.character_protection_radius} pixels")
    
    def capture_game_area(self):
        """Capture optimized game area for YOLO processing"""
        # Create thread-safe MSS instance
        with mss.mss() as sct:
            try:
                # Define game area (excluding UI elements)
                game_area = {
                    'top': self.margin_top,
                    'left': self.margin_left,
                    'width': self.screen_width - self.margin_left - self.margin_right,
                    'height': self.screen_height - self.margin_top - self.margin_bottom
                }
                
                # Ultra-fast screen capture
                screenshot = sct.grab(game_area)
                
                # Convert to numpy array for YOLO
                frame = np.array(screenshot)
                
                # Convert BGRA to RGB (YOLO expects RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                
                return frame, game_area
                
            except Exception as e:
                print(f"❌ Screen capture failed: {e}")
                return None, None
    
    def detect_mobs_yolo(self, frame):
        """Use YOLO to detect mobs in the frame"""
        if self.model is None:
            return []
        
        try:
            # YOLO inference - optimized for speed
            results = self.model(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                max_det=self.max_detections,
                verbose=False  # Suppress output for speed
            )
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i in range(len(boxes)):
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                        confidence = boxes.conf[i].cpu().numpy()
                        class_id = int(boxes.cls[i].cpu().numpy())
                        
                        # Calculate center point for targeting
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        # Convert back to screen coordinates
                        screen_x = center_x + self.margin_left
                        screen_y = center_y + self.margin_top
                        
                        detection = {
                            'bbox': [x1, y1, x2, y2],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'center': (center_x, center_y),
                            'screen_position': (screen_x, screen_y),
                            'target_position': (screen_x, screen_y + self.target_offset_y)
                        }
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"❌ YOLO detection failed: {e}")
            return []
    
    def filter_protected_areas(self, detections):
        """Filter out detections in protected areas (character position)"""
        filtered_detections = []
        
        # Character position (screen center)
        char_x, char_y = self.screen_width // 2, self.screen_height // 2
        
        for detection in detections:
            screen_x, screen_y = detection['screen_position']
            
            # Calculate distance from character
            distance = ((screen_x - char_x) ** 2 + (screen_y - char_y) ** 2) ** 0.5
            
            if distance > self.character_protection_radius:
                filtered_detections.append(detection)
                print(f"✅ Mob detected at {detection['screen_position']} (confidence: {detection['confidence']:.2f})")
            else:
                print(f"🛡️ Skipping detection near character (distance: {distance:.1f}px)")
        
        return filtered_detections
    
    def select_target_with_persistence(self, detections):
        """Select target with persistence logic - stick to current target or find new one"""
        if not detections:
            return None
        
        # Check if we should stick with current target
        if not self.should_switch_target():
            # Try to find current target in new detections
            if self.current_target:
                current_pos = self.current_target['screen_position']
                
                # Look for target near current position (within 100px)
                for detection in detections:
                    det_pos = detection['screen_position']
                    distance = ((det_pos[0] - current_pos[0]) ** 2 + (det_pos[1] - current_pos[1]) ** 2) ** 0.5
                    
                    if distance < 100:  # Same target if within 100px
                        print(f"   🎯 Continuing with same target (moved {distance:.0f}px)")
                        # Update target position but keep same target
                        self.current_target['screen_position'] = det_pos
                        self.current_target['target_position'] = detection['target_position']
                        return self.current_target
        
        # Need to select new target
        best_target = self.select_best_target(detections)
        if best_target:
            self.set_current_target(best_target)
        
        return best_target
        
    def select_best_target(self, detections):
        """Select the best target from detections (closest to character)"""
        if not detections:
            return None
        
        # Character position
        char_x, char_y = self.screen_width // 2, self.screen_height // 2
        
        # Sort by distance to character (closest first)
        def distance_to_char(detection):
            x, y = detection['screen_position']
            return ((x - char_x) ** 2 + (y - char_y) ** 2) ** 0.5
        
        best_target = min(detections, key=distance_to_char)
        distance = distance_to_char(best_target)
        
        print(f"🎯 Best target: {best_target['screen_position']} (distance: {distance:.1f}px, conf: {best_target['confidence']:.2f})")
        
        return best_target
    
    def click_target(self, target):
        """Click on the selected target"""
        try:
            target_pos = target['target_position']
            
            print(f"🖱️ Clicking target at {target_pos}")
            
            # Direct click for maximum speed
            pyautogui.click(target_pos[0], target_pos[1], button='left')
            
            print("✅ Target clicked!")
            return True
            
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    def continuous_keyboard_automation(self):
        """Continuous keyboard pressing in background thread"""
        print("⌨️ Starting keyboard automation: 123145 sequence")
        self.keyboard_active = True
        sequence = "123145"
        
        try:
            while self.keyboard_active and self.monitoring_active and not self.stop_requested:
                for key in sequence:
                    if not self.keyboard_active or not self.monitoring_active or self.stop_requested:
                        break
                    
                    try:
                        pyautogui.press(key)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"❌ Key press failed: {e}")
                
                # Wait between sequences
                time.sleep(0.4)  # Total cycle = ~1 second
                
        except Exception as e:
            print(f"❌ Keyboard automation error: {e}")
        finally:
            self.keyboard_active = False
            print("⌨️ Keyboard automation stopped")
    
    def real_time_detection_loop(self):
        """Main real-time detection and targeting loop"""
        print("\n⚡ STARTING REAL-TIME YOLO DETECTION")
        print("=" * 50)
        print("🎮 Features:")
        print("   • Real-time visual mob detection")
        print("   • 30+ FPS processing speed")
        print("   • Instant targeting without OCR delays")
        print("   • Simultaneous multi-mob detection")
        print("   • Position-based character protection")
        print("=" * 50)
        
        self.monitoring_active = True
        frame_count = 0
        start_time = time.time()
        
        # Start keyboard automation thread
        keyboard_thread = threading.Thread(target=self.continuous_keyboard_automation, daemon=True)
        keyboard_thread.start()
        
        try:
            while self.monitoring_active and not self.stop_requested:
                loop_start = time.time()
                
                # Check if paused
                if self.paused:
                    print("⏸️ Detection paused - press F2 to resume or F3 to stop")
                    time.sleep(1)
                    continue
                
                # Capture game area
                frame, game_area = self.capture_game_area()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # YOLO detection
                detections = self.detect_mobs_yolo(frame)
                
                if detections:
                    print(f"🔍 Found {len(detections)} potential mobs")
                    
                    # Filter protected areas
                    safe_detections = self.filter_protected_areas(detections)
                    
                    if safe_detections:
                        # Update mob detection status
                        self.update_mob_detection_status(True)
                        
                        # Select target with persistence logic
                        best_target = self.select_target_with_persistence(safe_detections)
                        if best_target:
                            self.click_target(best_target)
                    else:
                        # No safe targets, update status and try hunting (if not disabled)
                        self.update_mob_detection_status(False)
                        self.active_hunting_mode()
                else:
                    # No detections at all, try hunting
                    print("🔍 No mobs detected")
                    self.update_mob_detection_status(False)
                    self.active_hunting_mode()
                
                # Calculate and maintain FPS
                frame_count += 1
                loop_time = time.time() - loop_start
                
                # FPS control
                target_frame_time = 1.0 / self.fps_target
                if loop_time < target_frame_time:
                    time.sleep(target_frame_time - loop_time)
                
                # FPS reporting every 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    current_fps = frame_count / elapsed
                    print(f"📊 FPS: {current_fps:.1f} | Processed {frame_count} frames")
                
        except KeyboardInterrupt:
            print("\n⏹️ Detection stopped by user")
        except Exception as e:
            print(f"\n❌ Detection error: {e}")
        finally:
            self.monitoring_active = False
            self.keyboard_active = False
            
            # Wait for keyboard thread
            if keyboard_thread.is_alive():
                keyboard_thread.join(timeout=2)
            
            print("🏁 Real-time detection ended")
    
    def start_detection_thread(self):
        """Start detection in a separate thread for hotkey control"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.keyboard_active = True
            detection_thread = threading.Thread(target=self.real_time_detection_loop, daemon=True)
            detection_thread.start()
            print("🚀 Detection thread started")

def main():
    print("⚡ YOLO Mob Finder - Real-Time Visual Detection")
    print("🔥 Ultra-fast object detection for moving mobs")
    print("=" * 60)
    
    # Create YOLO mob finder
    yolo_finder = YOLOMobFinder()
    
    # Skip protection setup for testing
    print("🛡️ SKIPPING PROTECTION SETUP FOR TESTING")
    yolo_finder.protected_names = []
    
    # Load YOLO model
    if not yolo_finder.load_yolo_model():
        print("❌ Cannot continue without YOLO model")
        return
    
    # Setup global hotkeys
    if not yolo_finder.setup_global_hotkeys():
        print("⚠️ Continuing without global hotkeys...")
    
    try:
        print("\n🎮 HOTKEY CONTROL MODE")
        print("=" * 40)
        print("🎯 CONTROLS:")
        print("   F1 = Start/Pause Toggle")
        print("   Ctrl+C = Emergency exit")
        print("=" * 40)
        print("💡 Focus your GAME WINDOW and press F1 to start!")
        print("💡 Press F1 again to pause/resume anytime!")
        print("💡 All hotkeys work globally (no need to focus terminal)")
        
        # Keep main thread alive for hotkeys
        while True:
            time.sleep(1)
            
            # Check if user requested stop
            if yolo_finder.stop_requested:
                break
                
        print("\n🏁 Detection stopped")
        
    except KeyboardInterrupt:
        print("\n⏹️ Emergency stop (Ctrl+C)")
        yolo_finder.stop_requested = True
        yolo_finder.monitoring_active = False
        yolo_finder.keyboard_active = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup
        yolo_finder.cleanup_hotkeys()
    
    print("\n🏁 YOLO Mob Finder complete!")

if __name__ == "__main__":
    main()
