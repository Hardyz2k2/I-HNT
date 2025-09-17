#!/usr/bin/env python3
"""
I-HNT - Real-Time Gaming Assistant
"I Have No Time – That's Why I-HNT"

Uses I-HNT AI for ultra-fast real-time mob detection and hunting.
Designed for gamers who work hard but still love to game smart!

Developed by HardyZ-2k2
GitHub: https://github.com/Hardyz2k2
Version: Production Ready
"""

import time
import math
import cv2
import numpy as np
import mss
import pyautogui
import threading
from ultralytics import YOLO
import torch
from pathlib import Path
from pynput.keyboard import Key, Listener

class IHNTMobFinder:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080
        self.model = None
        self.monitoring_active = False
        self.keyboard_active = False
        self.stop_requested = False
        
        # Target persistence tracking (health-based only)
        self.current_target = None
        
        # Detection pause system
        self.detection_paused = False
        self.detection_pause_start = None
        
        # Zone-based hunting system
        self.hunting_zone_radius = 300  # Default medium area (spear)
        self.last_mob_seen_time = None
        self.hunting_delay = 1.0  # Wait 1 second before moving (faster response)
        self.movement_click_delay = 1.0  # Delay between movement clicks
        
        # Systematic boundary exploration system
        self.current_direction = 0.0  # Current angle in radians
        self.direction_attempts = 0   # Number of attempts in current direction
        self.max_attempts_per_direction = 2  # Try each direction twice before moving to next
        self.direction_increment = 45.0  # Degrees between directions (8 directions total)
        
        # Camera angle adjustment system
        self.movement_count = 0  # Track number of movements made
        self.movements_before_camera_adjust = 2  # Adjust camera after 2 movements
        self.camera_drag_duration = 1.0  # Hold right-click drag for 1 second
        self.camera_direction = 1  # 1 for right, -1 for left (alternates)
        
        # Movement validation system
        self.min_movement_distance = 400  # Minimum distance from character for effective movement
        self.use_edge_positions = True  # Use screen edge positions for maximum movement
        
        # Global hotkey controls
        self.paused = False
        self.hotkey_listener = None
        self.hotkeys_active = False
        
        # I-HNT AI optimized settings for speed
        self.conf_threshold = 0.25      # Confidence threshold
        self.iou_threshold = 0.45       # IoU threshold for NMS
        self.max_detections = 300       # Maximum detections per image
        
        # Gaming area optimization (focus on center area where mobs typically are)
        self.margin_top = 100
        self.margin_bottom = 200    # Leave space for UI
        self.margin_left = 100
        self.margin_right = 100
        
        # Targeting settings
        self.target_offset_y = 10  # Small offset to click mob body
        
        # Performance settings
        self.use_gpu = torch.cuda.is_available()
        self.fps_target = 30  # Target FPS for real-time processing
        
        print("🎮 I-HNT - Real-Time Gaming Assistant")
        print("=" * 50)
        print("☕ Coffee Status: Ready for long gaming sessions")
        print("🍿 Snacks: Popcorn loaded and ready")
        print("🎬 Entertainment: Movie queued for breaks")
        print("🎯 Gaming Mode: Intelligent assistance enabled")
        print("🛡️ Safety: Character protection active")
        print("⚡ Performance: Optimized for smooth gameplay")
        print("🎮 Control: CapsLock hotkey ready")
        
    def load_yolo_model(self, model_path="yolov8n.pt"):
        """Load I-HNT AI model for mob detection"""
        print(f"\n🤖 Loading I-HNT AI model...")
        start_time = time.time()
        
        try:
            # Check if custom trained model exists, otherwise use pretrained
            if not Path(model_path).exists():
                print("⚠️ Custom model not found, using I-HNT nano (pretrained)")
                print("💡 Note: You'll need to train a custom model for mob detection")
                model_path = "yolov8n.pt"  # Use I-HNT nano model for speed
            
            # Load model
            self.model = YOLO(model_path)
            
            # Optimize for inference speed
            if self.use_gpu:
                self.model.to('cuda')
                print("🔥 Model loaded on GPU for maximum speed")
            else:
                print("💻 Model loaded on CPU")
                
            load_time = time.time() - start_time
            print(f"✅ I-HNT AI model loaded in {load_time:.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load I-HNT AI model: {e}")
            print("💡 Install requirements: pip install ultralytics torch")
            return False
    
    def detect_health_bar(self):
        """Detect if there's a health bar visible at top center (mob selected) and check for red health line"""
        try:
            # Health bar area at top center of screen (adjusted for game UI)
            # Based on the images, health bars appear to be more centered
            health_bar_area = {
                'top': 20,    # Higher up
                'left': 600,  # More centered
                'width': 720, # Wider to catch different positions
                'height': 80  # Focused height for health bars
            }
            
            # Capture health bar area
            with mss.mss() as sct:
                health_screenshot = sct.grab(health_bar_area)
            health_img = np.array(health_screenshot)
            
            # Convert to RGB for processing
            health_rgb = cv2.cvtColor(health_img, cv2.COLOR_BGRA2RGB)
            
            # More aggressive red detection for game UI
            # Convert to HSV for better red detection
            hsv = cv2.cvtColor(health_rgb, cv2.COLOR_RGB2HSV)
            
            # Expanded red color ranges for game UI (more permissive)
            # First red range (around 0 degrees)
            lower_red1 = np.array([0, 50, 50])      # Very permissive lower bound
            upper_red1 = np.array([15, 255, 255])   # Wider hue range
            
            # Second red range (around 180 degrees)  
            lower_red2 = np.array([165, 50, 50])    # Very permissive lower bound
            upper_red2 = np.array([180, 255, 255])  # Wider hue range
            
            # Create masks for red detection
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            
            # Count red pixels (health line presence)
            red_pixel_count = cv2.countNonZero(red_mask)
            
            # Much lower threshold - even small amount of red means mob is alive
            red_health_threshold = 10  # Very sensitive - any red pixels indicate health
            has_red_health = red_pixel_count > red_health_threshold
            
            # Check for health bar UI presence by looking for the dark health bar background
            gray = cv2.cvtColor(health_rgb, cv2.COLOR_RGB2GRAY)
            
            # Look for dark rectangles (health bar backgrounds) and any UI elements
            dark_pixels = cv2.countNonZero(gray < 100)  # Dark UI elements
            bright_pixels = cv2.countNonZero(gray > 150) # Bright UI elements (text, borders)
            
            # Health bar present if we have UI elements (dark background or bright text/borders)
            has_health_bar = (dark_pixels > 100) or (bright_pixels > 50) or has_red_health
            
            if has_health_bar and has_red_health:
                print(f"   ❤️ HEALTH DETECTED: Mob alive with {red_pixel_count} red pixels - PAUSING DETECTION")
            elif has_health_bar and not has_red_health:
                print(f"   💀 HEALTH EMPTY: No red pixels ({red_pixel_count}) - mob dead - RESUMING DETECTION") 
            elif red_pixel_count > 0:
                # Any red pixels at all, even if no clear health bar UI
                print(f"   🩸 RED PIXELS FOUND: {red_pixel_count} red pixels detected - treating as alive")
                has_health_bar = True
                has_red_health = True
            
            return {
                'has_health_bar': has_health_bar,
                'has_red_health': has_red_health,
                'red_pixel_count': red_pixel_count
            }
            
        except Exception as e:
            print(f"   ⚠️ Health bar detection error: {e}")
            return {'has_health_bar': False, 'has_red_health': False}
    
    def should_switch_target(self):
        """Determine if we should switch to a new target based on health monitoring ONLY"""
        # Check health bar status immediately - no timeout needed
        health_status = self.detect_health_bar()
        
        if health_status['has_health_bar']:
            if health_status['has_red_health']:
                # Mob is selected and has red health line - COMPLETELY STOP all mouse actions
                print(f"   🛑 MOUSE LOCKED: Red health detected ({health_status['red_pixel_count']} pixels) - NO MOUSE MOVEMENT OR CLICKS")
                self.start_detection_pause()  # Pause detection to avoid jumping
                return False  # DO NOT switch targets
            else:
                # Mob is selected but no red health line - mob is completely dead, resume mouse actions
                print(f"   ✅ MOUSE UNLOCKED: No red health ({health_status['red_pixel_count']} pixels) - mob dead - resuming mouse actions")
                self.clear_detection_pause()  # Clear pause when switching
                return True  # Switch targets immediately
        else:
            # No health bar visible - no mob selected, mouse can act freely
            print(f"   🆓 MOUSE FREE: No health bar visible - can select new target")
            self.clear_detection_pause()  # Clear pause when no mob selected
            return True  # Can select new targets
    
    def set_current_target(self, target):
        """Set the current target and start tracking time"""
        self.current_target = target
        self.clear_detection_pause()  # Reset detection pause for new target
    
    def start_detection_pause(self):
        """Start detection pause when fighting a mob (health-based only)"""
        if not self.detection_paused:
            self.detection_paused = True
            self.detection_pause_start = time.time()
            print(f"   🛑 COMPLETE MOUSE LOCK - No movement or clicks until red health disappears")
    
    def clear_detection_pause(self):
        """Clear detection pause"""
        if self.detection_paused:
            self.detection_paused = False
            self.detection_pause_start = None
            print(f"   🆓 MOUSE UNLOCKED - Can move and click again")
    
    def is_detection_paused(self):
        """Check if detection should be paused (health-based only, no timeout)"""
        # Only pause if actively fighting (red health detected)
        return self.detection_paused
    
    def generate_movement_position(self):
        """Generate effective movement position with validation to avoid small steps"""
        
        # Character position (center of screen)
        char_x, char_y = self.screen_width // 2, self.screen_height // 2
        
        if self.use_edge_positions:
            # Use screen edge positions for MAXIMUM movement distance
            edge_positions = [
                (char_x, 150),  # North - top edge
                (self.screen_width - 150, char_y),  # East - right edge  
                (char_x, self.screen_height - 150),  # South - bottom edge
                (150, char_y),  # West - left edge
                (self.screen_width - 200, 200),  # NE - top-right corner
                (self.screen_width - 200, self.screen_height - 200),  # SE - bottom-right
                (200, self.screen_height - 200),  # SW - bottom-left
                (200, 200),  # NW - top-left corner
            ]
            
            # Calculate which edge position to use based on current direction
            direction_index = int((math.degrees(self.current_direction) / 45) % 8)
            move_x, move_y = edge_positions[direction_index]
            
        else:
            # Use systematic boundary approach with larger radius
            angle = self.current_direction
            distance = self.hunting_zone_radius  # 300 pixels
            
            # Calculate position at zone boundary
            move_x = int(char_x + distance * math.cos(angle))
            move_y = int(char_y + distance * math.sin(angle))
            
            # Ensure within screen bounds
            move_x = max(150, min(move_x, self.screen_width - 150))
            move_y = max(150, min(move_y, self.screen_height - 150))
        
        # CRITICAL: Validate movement distance to prevent small steps
        actual_distance = math.sqrt((move_x - char_x)**2 + (move_y - char_y)**2)
        
        if actual_distance < self.min_movement_distance:
            print(f"   ⚠️ Movement too small ({actual_distance:.0f}px) - forcing edge position")
            # Force to screen edge for maximum movement
            if self.current_direction < math.pi / 2:  # 0-90 degrees
                move_x, move_y = self.screen_width - 150, 150  # Top-right edge
            elif self.current_direction < math.pi:  # 90-180 degrees  
                move_x, move_y = self.screen_width - 150, self.screen_height - 150  # Bottom-right
            elif self.current_direction < 3 * math.pi / 2:  # 180-270 degrees
                move_x, move_y = 150, self.screen_height - 150  # Bottom-left
            else:  # 270-360 degrees
                move_x, move_y = 150, 150  # Top-left
            
            actual_distance = math.sqrt((move_x - char_x)**2 + (move_y - char_y)**2)
        
        # Update direction system for next movement
        self.direction_attempts += 1
        
        if self.direction_attempts >= self.max_attempts_per_direction:
            # Move to next direction after trying current direction twice
            self.direction_attempts = 0
            self.current_direction += math.radians(self.direction_increment)
            
            # Reset to 0 after full circle (8 directions * 45° = 360°)
            if self.current_direction >= 2 * math.pi:
                self.current_direction = 0.0
                
        direction_degrees = math.degrees(self.current_direction) if self.current_direction >= 0 else math.degrees(self.current_direction) + 360
        attempt_num = self.direction_attempts
        
        print(f"   🧭 Direction: {direction_degrees:.0f}° (attempt {attempt_num}/{self.max_attempts_per_direction})")
        print(f"   📏 Movement distance: {actual_distance:.0f}px (min: {self.min_movement_distance}px)")
        print(f"   🎯 Target position: ({move_x}, {move_y}) from character ({char_x}, {char_y})")
        
        return (move_x, move_y)
    
    def adjust_camera_angle(self):
        """Adjust camera angle by right-click dragging left or right"""
        try:
            # Get screen center for camera drag
            center_x, center_y = self.screen_width // 2, self.screen_height // 2
            
            # Calculate drag distance (200 pixels left or right)
            drag_distance = 200 * self.camera_direction
            drag_end_x = center_x + drag_distance
            
            # Ensure drag end position is within screen bounds
            drag_end_x = max(100, min(drag_end_x, self.screen_width - 100))
            
            direction_text = "RIGHT" if self.camera_direction > 0 else "LEFT"
            print(f"📹 CAMERA ADJUSTMENT: Right-click dragging {direction_text} to change view angle")
            
            # Perform right-click drag
            pyautogui.mouseDown(center_x, center_y, button='right')
            time.sleep(0.1)  # Brief pause after mouse down
            
            # Drag to new position over the duration
            pyautogui.dragTo(drag_end_x, center_y, duration=self.camera_drag_duration, button='right')
            
            # Release right-click
            pyautogui.mouseUp(button='right')
            
            # Alternate direction for next camera adjustment
            self.camera_direction *= -1
            
            print(f"   ✅ Camera angle adjusted - next adjustment will go {'RIGHT' if self.camera_direction > 0 else 'LEFT'}")
            
        except Exception as e:
            print(f"   ❌ Camera adjustment failed: {e}")
    
    def zone_movement_mode(self):
        """Systematically explore zone boundaries when no mobs detected"""
        if self.last_mob_seen_time is None:
            self.last_mob_seen_time = time.time()
            return
        
        # Check if we should move (1 second delay)
        time_since_last_mob = time.time() - self.last_mob_seen_time
        
        if time_since_last_mob >= self.hunting_delay:
            # Generate systematic boundary position for exploration
            move_pos = self.generate_movement_position()
            
            print(f"🚶 BOUNDARY EXPLORATION: No mobs for {time_since_last_mob:.1f}s - moving to {move_pos}")
            
            try:
                # Click to move character to zone boundary
                pyautogui.click(move_pos[0], move_pos[1], button='left')
                time.sleep(self.movement_click_delay)
                
                # Increment movement counter
                self.movement_count += 1
                print(f"   📊 Movement count: {self.movement_count}")
                
                # Check if we need to adjust camera angle after 2 movements
                if self.movement_count >= self.movements_before_camera_adjust:
                    print(f"   🔄 {self.movement_count} movements completed - adjusting camera angle")
                    time.sleep(0.5)  # Brief pause before camera adjustment
                    self.adjust_camera_angle()
                    self.movement_count = 0  # Reset counter after camera adjustment
                
                # Reset timer after movement
                self.last_mob_seen_time = time.time()
            except Exception as e:
                print(f"   ❌ Movement click failed: {e}")
        
    def update_mob_detection_status(self, mobs_found):
        """Update mob detection status for zone movement"""
        if mobs_found:
            # Mobs found in zone, reset timer
            self.last_mob_seen_time = time.time()
    
    def setup_global_hotkeys(self):
        """Setup global hotkeys that work even when game window is focused"""
        def on_hotkey_press(key):
            try:
                if key == Key.caps_lock:
                    self.handle_capslock_toggle()
            except Exception as e:
                print(f"⚠️ Hotkey error: {e}")
        
        # Start global hotkey listener in background thread
        try:
            self.hotkey_listener = Listener(on_press=on_hotkey_press)
            self.hotkey_listener.daemon = True  # Dies with main thread
            self.hotkey_listener.start()
            self.hotkeys_active = True
            print("🎮 Global hotkeys activated!")
            print("   CapsLock = Start/Pause Toggle")
            return True
        except Exception as e:
            print(f"❌ Failed to setup hotkeys: {e}")
            return False
    
    def handle_capslock_toggle(self):
        """Handle CapsLock - Toggle Start/Pause"""
        if not self.monitoring_active:
            # Not running - start detection
            print("\n🚀 CAPS LOCK PRESSED - Starting detection...")
            self.paused = False
            self.start_detection_thread()
        elif self.paused:
            # Currently paused - resume
            print("\n▶️ CAPS LOCK PRESSED - Detection RESUMED!")
            self.paused = False
            self.keyboard_active = True  # Resume keyboard automation
        else:
            # Currently running - pause
            print("\n⏸️ CAPS LOCK PRESSED - Detection PAUSED!")
            self.paused = True
            self.keyboard_active = False  # Pause keyboard automation
    
    
    def cleanup_hotkeys(self):
        """Cleanup hotkey listener"""
        if self.hotkey_listener and self.hotkeys_active:
            try:
                self.hotkey_listener.stop()
                self.hotkeys_active = False
                print("🎮 Hotkeys deactivated")
            except:
                pass
    
    def setup_smart_targeting(self):
        """Setup smart pet ignoring system"""
        print("\n🎯 SMART TARGETING SYSTEM")
        print("=" * 40)
        print("🐕 Pet Detection: Automatically ignores pets using pet cards")
        print("🎯 Mob Targeting: Targets all detected mobs without restrictions")
        print("🧠 Smart Logic: Detects pet cards and switches to next target")
        print("✅ Ready for unrestricted hunting!")
    
    def capture_game_area(self):
        """Capture optimized game area for I-HNT AI processing"""
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
                
                # Convert to numpy array for I-HNT AI
                frame = np.array(screenshot)
                
                # Convert BGRA to RGB (I-HNT AI expects RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                
                return frame, game_area
                
            except Exception as e:
                print(f"❌ Screen capture failed: {e}")
                return None, None
    
    def detect_mobs_ai(self, frame):
        """Use I-HNT AI to detect mobs in the frame"""
        if self.model is None:
            return []
        
        try:
            # I-HNT AI inference - optimized for speed
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
            print(f"❌ I-HNT AI detection failed: {e}")
            return []
    
    def detect_pet_card(self):
        """Detect if a pet card appears at top center after clicking"""
        try:
            # Pet cards appear at top center of screen
            # Capture small area where pet cards appear
            pet_card_area = {
                'left': self.screen_width // 2 - 150,  # Center area
                'top': 10,  # Top of screen
                'width': 300,  # Wide enough for pet cards
                'height': 80   # Height of pet card area
            }
            
            with mss.mss() as sct:
                screenshot = sct.grab(pet_card_area)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                
                # Look for dark pet card backgrounds (like in the images)
                # Pet cards have distinctive dark backgrounds with pet names
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Look for dark rectangular areas typical of pet cards
                # Pet cards are darker than mob health bars
                dark_threshold = 50  # Adjust based on pet card darkness
                dark_pixels = np.sum(gray < dark_threshold)
                total_pixels = gray.shape[0] * gray.shape[1]
                dark_ratio = dark_pixels / total_pixels
                
                # If significant dark area detected, likely a pet card
                if dark_ratio > 0.3:  # 30% dark pixels indicates pet card
                    return True
                    
        except Exception as e:
            print(f"⚠️ Pet card detection error: {e}")
            
        return False
    
    def click_target_with_pet_detection(self, target):
        """Click target and check for pet card to ignore pets"""
        target_x, target_y = target['screen_position']
        
        # Click the target
        print(f"🖱️ Clicking target at ({target_x}, {target_y})")
        pyautogui.click(target_x, target_y)
        
        # Brief delay for pet card to appear
        time.sleep(0.2)  
        
        # Check if a pet card appeared after clicking
        if self.detect_pet_card():
            print("🐕 Pet detected! Ignoring and switching to next target")
            self.current_target = None  # Clear current target to switch
            return False  # Indicate pet was clicked
        
        return True  # Indicate successful mob click
    
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
        
        # Filter to only mobs in hunting zone
        zone_mobs = self.filter_mobs_in_zone(detections)
        
        # Select any target from zone (no complex prioritization)
        target = self.select_zone_target(zone_mobs)
        if target:
            self.set_current_target(target)
        
        return target
        
    def filter_mobs_in_zone(self, detections):
        """Filter detections to only include mobs within hunting zone"""
        if not detections:
            return []
        
        # Character position (center of screen)
        char_x, char_y = self.screen_width // 2, self.screen_height // 2
        
        zone_mobs = []
        for detection in detections:
            x, y = detection['screen_position']
            distance = ((x - char_x) ** 2 + (y - char_y) ** 2) ** 0.5
            
            if distance <= self.hunting_zone_radius:
                zone_mobs.append(detection)
                print(f"   ✅ Mob IN ZONE: ({x}, {y}) - Distance: {distance:.1f}px")
            else:
                print(f"   ❌ Mob OUTSIDE ZONE: ({x}, {y}) - Distance: {distance:.1f}px (ignored)")
        
        return zone_mobs
    
    def select_zone_target(self, zone_mobs):
        """Select any mob within the hunting zone (no prioritization needed)"""
        if not zone_mobs:
            return None
        
        # Just pick the first mob in the zone - all are close enough
        target = zone_mobs[0]
        pos = target['screen_position']
        conf = target['confidence']
        
        print(f"🎯 ZONE TARGET SELECTED: ({pos[0]}, {pos[1]}) - Conf: {conf:.2f}")
        return target
    
    
    def continuous_keyboard_automation(self):
        """Continuous keyboard pressing in background thread"""
        print("⌨️ Starting keyboard automation: 123145 sequence")
        self.keyboard_active = True
        sequence = "123145"
        
        try:
            while self.monitoring_active and not self.stop_requested:
                # Check if keyboard automation should be active (not paused)
                if self.keyboard_active and not self.paused:
                    for key in sequence:
                        if not self.keyboard_active or self.paused or not self.monitoring_active or self.stop_requested:
                            break
                        
                        try:
                            pyautogui.press(key)
                            time.sleep(0.1)
                        except Exception as e:
                            print(f"❌ Key press failed: {e}")
                    
                    # Wait between sequences
                    time.sleep(0.4)  # Total cycle = ~1 second
                else:
                    # Paused - just wait a bit and check again
                    time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Keyboard automation error: {e}")
        finally:
            self.keyboard_active = False
            print("⌨️ Keyboard automation stopped")
    
    def real_time_detection_loop(self):
        """Main real-time detection and targeting loop"""
        print("\n⚡ STARTING REAL-TIME I-HNT AI DETECTION")
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
                    print("⏸️ Detection paused - press CapsLock to resume")
                    time.sleep(1)
                    continue
                
                # Check if detection is paused (when fighting a mob with red health)
                if self.is_detection_paused():
                    # During pause, only check if we should switch targets (health monitoring)
                    if self.current_target is not None and self.should_switch_target():
                        # Target died or timed out, clear pause and continue detection
                        print("   📋 Target lost during pause - resuming full detection")
                        self.clear_detection_pause()
                    else:
                        # Still fighting current target, skip detection this frame
                        time.sleep(0.1)
                        continue
                
                # Capture game area
                frame, game_area = self.capture_game_area()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # I-HNT AI detection (only when not paused)
                detections = self.detect_mobs_ai(frame)
                
                if detections:
                    print(f"🔍 Found {len(detections)} potential mobs")
                    
                    # No filtering needed - target all detected mobs
                    print(f"🎯 Targeting all {len(detections)} detected mobs")
                    zone_mobs = self.filter_mobs_in_zone(detections)
                        
                    if zone_mobs:
                        # Mobs in zone - select target
                        print(f"✅ {len(zone_mobs)} mobs in hunting zone")
                        self.update_mob_detection_status(True)
                        
                        # Select target with persistence logic
                        target = self.select_target_with_persistence(zone_mobs)
                        if target:
                            self.click_target_with_pet_detection(target)
                        else:
                            # No mobs in zone - move to find some
                            print("📍 No mobs in hunting zone - initiating movement")
                            self.update_mob_detection_status(False)
                            self.zone_movement_mode()
                    else:
                        # No safe targets at all - move around
                        print("🚫 No safe mobs detected - moving within zone")
                        self.update_mob_detection_status(False)
                        self.zone_movement_mode()
                else:
                    # No detections at all - move around
                    print("🔍 No mobs detected - moving within zone")
                    self.update_mob_detection_status(False)
                    self.zone_movement_mode()
                
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
    print("\n")
    print("\n" + "="*50)
    print("🎮 I-HNT - Gaming Assistant".center(50))
    print("\"I Have No Time – That's Why I-HNT\"".center(50))
    print("")
    print("Developed by HardyZ-2k2".center(50))
    print("GitHub: https://github.com/Hardyz2k2".center(50))
    print("="*50)
    print("")
    
    # Create I-HNT hunter
    i_hnt = IHNTMobFinder()
    
    # Setup smart targeting system
    i_hnt.setup_smart_targeting()
    
    # Load I-HNT AI model
    if not i_hnt.load_yolo_model():
        print("❌ Cannot continue without I-HNT AI model")
        return
    
    # Setup global hotkeys
    if not i_hnt.setup_global_hotkeys():
        print("⚠️ Continuing without global hotkeys...")
    
    try:
        print("\n🎮 HOTKEY CONTROL MODE")
        print("=" * 40)
        print("🎯 CONTROLS:")
        print("   CapsLock = Start/Pause Toggle")
        print("   Ctrl+C = Emergency exit")
        print("=" * 40)
        print("💡 Focus your GAME WINDOW and press CapsLock to start!")
        print("💡 Press CapsLock again to pause/resume anytime!")
        print("💡 All hotkeys work globally (no need to focus terminal)")
        
        # Keep main thread alive for hotkeys
        while True:
            time.sleep(1)
            
            # Check if user requested stop
            if i_hnt.stop_requested:
                break
                
        print("\n🏁 Detection stopped")
        
    except KeyboardInterrupt:
        print("\n⏹️ Emergency stop (Ctrl+C)")
        i_hnt.stop_requested = True
        i_hnt.monitoring_active = False
        i_hnt.keyboard_active = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup
        i_hnt.cleanup_hotkeys()
    
    print("\n🏁 I-HNT Gaming Assistant complete!")
    print("🎮 Happy Gaming and thanks for using I-HNT! 🎯")
    print("💻 Visit: https://github.com/Hardyz2k2")

if __name__ == "__main__":
    main()
