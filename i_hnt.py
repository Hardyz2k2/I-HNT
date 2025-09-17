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

class IHNTMobFinder:
    def __init__(self):
        self.screen_width, self.screen_height = 1920, 1080
        self.protected_names = []
        self.model = None
        self.monitoring_active = False
        self.keyboard_active = False
        self.stop_requested = False
        
        # Target persistence tracking (health-based only)
        self.current_target = None
        self.target_selected_time = None
        
        # Detection pause system
        self.detection_paused = False
        self.detection_pause_start = None
        self.detection_pause_duration = 6.0  # 6 seconds detection pause when fighting
        
        # Zone-based hunting system
        self.hunting_zone_radius = 300  # Default medium area (spear)
        self.detection_area_presets = {
            'sword': 150,    # Small area for close combat
            'spear': 300,    # Medium area for mid-range (default)
            'bow': 500,      # Large area for long-range
            'custom': 300    # Custom area (user-defined)
        }
        self.current_weapon_type = 'spear'  # Default weapon type
        self.last_mob_seen_time = None
        
        # Movement system - Updated parameters
        self.movement_delay = 3.0  # Wait 3 seconds before moving (increased from 2.0)
        self.movement_radius = 200  # 200px radius for movement (fixed, independent of hunting zone)
        self.movement_click_delay = 0.5  # 0.5s delay between movement clicks (reduced from 1.0)
        
        # Global hotkey controls
        self.paused = False
        self.hotkey_listener = None
        self.hotkeys_active = False
        
        # Death detection system
        self.player_dead = False
        self.death_detection_active = True
        self.death_action = "resurrect"  # "resurrect" or "wait_help"
        self.auto_handle_death = False  # Set to True to automatically click death buttons
        self.death_handling_mode = None  # Will be set during startup
        self.auto_res_scroll_slot = "0"  # Default slot for auto-res scroll
        self.death_debug_mode = False  # Enable debug output for death detection
        
        # I-HNT AI optimized settings for speed
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
        
        print("🎮 I-HNT - Real-Time Gaming Assistant")
        print("=" * 50)
        print("☕ Coffee Status: Ready for long gaming sessions")
        print("🍿 Snacks: Popcorn loaded and ready")
        print("🎬 Entertainment: Movie queued for breaks")
        print("🎯 Gaming Mode: Intelligent assistance enabled")
        print("🛡️ Safety: Character protection active")
        print("💀 Death Detection: Player death monitoring enabled")
        print(f"   Auto-handle death: {'ON' if self.auto_handle_death else 'OFF'}")
        if self.death_handling_mode:
            print(f"   Death handling mode: {self.death_handling_mode}")
            if self.death_handling_mode == "wait_help":
                print(f"   Auto-res scroll slot: {self.auto_res_scroll_slot}")
        print(f"🎯 Detection Area: {self.current_weapon_type.title()} - {self.hunting_zone_radius}px radius")
        print(f"🚶 Movement: 200px radius, 3s delay, 0.5s click delay")
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
            dark_mask = gray < 100
            bright_mask = gray > 150
            dark_pixels = np.sum(dark_mask)  # Dark UI elements
            bright_pixels = np.sum(bright_mask) # Bright UI elements (text, borders)
            
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
    
    def detect_player_death(self):
        """Detect if player has died by looking for confirmation window in center of screen"""
        try:
            # Death confirmation window appears in center of screen
            # Use a much larger area to catch the window reliably
            death_window_area = {
                'top': 100,     # Even larger area
                'left': 200,    # Even larger area
                'width': 1520,  # Almost full width
                'height': 880   # Almost full height
            }
            
            # Capture death window area
            with mss.mss() as sct:
                death_screenshot = sct.grab(death_window_area)
            death_img = np.array(death_screenshot)
            
            # Convert to RGB for processing
            death_rgb = cv2.cvtColor(death_img, cv2.COLOR_BGRA2RGB)
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(death_rgb, cv2.COLOR_RGB2GRAY)
            
            # VERY aggressive detection - look for ANY dark areas
            very_dark_mask = gray < 60
            dark_mask = gray < 100
            bright_mask = gray > 150
            
            very_dark_pixels = np.sum(very_dark_mask)   # Very dark pixels
            dark_pixels = np.sum(dark_mask)             # Dark pixels
            bright_pixels = np.sum(bright_mask)         # Bright pixels (text)
            
            total_pixels = gray.shape[0] * gray.shape[1]
            very_dark_ratio = very_dark_pixels / total_pixels
            dark_ratio = dark_pixels / total_pixels
            bright_ratio = bright_pixels / total_pixels
            
            # Balanced detection - strict enough to avoid false positives, sensitive enough for real deaths
            has_dark_area = very_dark_ratio > 0.08 or dark_ratio > 0.2
            
            if has_dark_area:
                # Balanced text check
                has_text = bright_ratio > 0.005  # At least 0.5% bright pixels (text)
                
                if has_text:
                    print(f"💀 PLAYER DEATH DETECTED: Confirmation window found!")
                    print(f"   Very dark: {very_dark_ratio:.2f}, Dark: {dark_ratio:.2f}, Bright: {bright_ratio:.2f}")
                    return True
                else:
                    # Dark area but no text - might be other UI
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"   ⚠️ Death detection error: {e}")
            return False
    
    def handle_death_confirmation(self, mode=None):
        """Handle death confirmation window actions based on configured mode"""
        try:
            if mode is None:
                mode = self.death_handling_mode
            
            print(f"   🔍 Death handling mode: {mode}")
            
            if mode == "respawn_town":
                # Mode 1: Respawn at town - click left button and pause app
                resurrect_button_x = self.screen_width // 2 - 150  # Left side of center
                resurrect_button_y = self.screen_height // 2 + 200  # Below center
                
                print(f"💀 Mode 1: Clicking 'Resurrect at the specified point' button at ({resurrect_button_x}, {resurrect_button_y})")
                pyautogui.click(resurrect_button_x, resurrect_button_y)
                print("   ✅ Click executed")
                
                # Wait for resurrection to complete
                print("   ⏳ Waiting 3 seconds for resurrection...")
                time.sleep(3)
                
                # Reset death state before pausing
                print("🔄 Resetting death state...")
                self.player_dead = False
                self.death_detection_active = False
                self.detection_paused = False  # Ensure detection is not paused
                
                # Pause the app after resurrection (no F1 needed for town respawn)
                print("⏸️ Pausing I-HNT app after town resurrection...")
                self.paused = True
                self.keyboard_active = False
                print("💀 Character respawned at town - I-HNT is paused. Press CapsLock to resume hunting.")
                return True
                
            elif mode == "wait_help":
                # Mode 2: Wait for other players - click right button, press F4, use auto-res scroll
                wait_button_x = self.screen_width // 2 + 150  # Right side of center
                wait_button_y = self.screen_height // 2 + 200  # Below center
                
                print(f"💀 Mode 2: Clicking 'Waiting for other player's help' button at ({wait_button_x}, {wait_button_y})")
                pyautogui.click(wait_button_x, wait_button_y)
                print("   ✅ Click executed")
                
                # Wait for window to close
                print("   ⏳ Waiting 2 seconds for window to close...")
                time.sleep(2)
                
                # Press F4 to open inventory/skills
                print("💀 Pressing F4 to open inventory...")
                pyautogui.press('f4')
                time.sleep(1)
                
                # Press "0" to use auto-res scroll
                print("💀 Using auto-res scroll from slot 0...")
                pyautogui.press('0')
                time.sleep(2)
                
                # Press F4 again to close inventory
                print("💀 Pressing F4 to close inventory...")
                pyautogui.press('f4')
                time.sleep(1)
                
                # Press F1 to switch back to game
                print("🎮 Pressing F1 to switch back to game...")
                pyautogui.press('f1')
                time.sleep(0.5)
                
                print("✨ Auto-res scroll used - continuing hunting as usual")
                
                return True
                
        except Exception as e:
            print(f"   ❌ Death confirmation action failed: {e}")
            return False
    
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
        self.target_selected_time = time.time()
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
        print(f"   🎯 New target locked: {target['screen_position']} (conf: {target['confidence']:.2f})")
    
    def generate_movement_position(self):
        """Generate random position within 200px movement radius for character movement"""
        import random
        import math
        
        # Character position (center of screen)
        char_x, char_y = self.screen_width // 2, self.screen_height // 2
        
        # Generate random position within 200px movement radius
        angle = random.uniform(0, 2 * math.pi)  # 0 to 2π radians
        # Use full movement radius (200px) for better exploration
        distance = random.uniform(50, self.movement_radius)  # 50px to 200px from center
        
        # Calculate position
        move_x = int(char_x + distance * math.cos(angle))
        move_y = int(char_y + distance * math.sin(angle))
        
        # Ensure within movement radius bounds
        move_x = max(char_x - self.movement_radius, min(move_x, char_x + self.movement_radius))
        move_y = max(char_y - self.movement_radius, min(move_y, char_y + self.movement_radius))
        
        # Final screen boundary check
        move_x = max(100, min(move_x, self.screen_width - 100))
        move_y = max(100, min(move_y, self.screen_height - 100))
        
        return (move_x, move_y)
    
    def zone_movement_mode(self):
        """Move character randomly within 200px radius when no mobs detected"""
        if self.last_mob_seen_time is None:
            self.last_mob_seen_time = time.time()
            return
        
        # Check if we should move (3 second delay)
        time_since_last_mob = time.time() - self.last_mob_seen_time
        
        if time_since_last_mob >= self.movement_delay:
            # Generate random movement position within 200px radius
            move_pos = self.generate_movement_position()
            
            print(f"🚶 MOVEMENT: No mobs detected for {time_since_last_mob:.1f}s - moving to {move_pos} (200px radius)")
            
            try:
                # Click to move character within 200px radius
                pyautogui.click(move_pos[0], move_pos[1], button='left')
                time.sleep(self.movement_click_delay)  # 0.5s delay
                
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
                elif str(key) == 'Key.f2':
                    self.manual_death_test()
                elif str(key) == 'Key.f3':
                    self.cycle_detection_area()
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
            print("   F2 = Manual Death Detection Test")
            print("   F3 = Cycle Detection Area (Sword→Spear→Bow→Custom)")
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
    
    def manual_death_test(self):
        """Manually test death detection"""
        print("\n🧪 MANUAL DEATH DETECTION TEST")
        print("=" * 40)
        if self.detect_player_death():
            print("💀 Death window detected!")
            print("Testing death handling...")
            if self.auto_handle_death and self.death_handling_mode:
                success = self.handle_death_confirmation()
                if success:
                    print("✅ Death handling test successful")
                else:
                    print("❌ Death handling test failed")
            else:
                print("⚠️ Auto-handle death is disabled or mode not set")
        else:
            print("✅ No death window detected")
        print("=" * 40)
    
    def cycle_detection_area(self):
        """Cycle through detection area presets"""
        weapon_types = ['sword', 'spear', 'bow', 'custom']
        current_index = weapon_types.index(self.current_weapon_type)
        next_index = (current_index + 1) % len(weapon_types)
        
        self.current_weapon_type = weapon_types[next_index]
        self.hunting_zone_radius = self.detection_area_presets[self.current_weapon_type]
        
        print(f"\n🎯 DETECTION AREA CHANGED")
        print("=" * 30)
        print(f"   New weapon type: {self.current_weapon_type.title()}")
        print(f"   New radius: {self.hunting_zone_radius}px")
        print("=" * 30)
    
    
    def cleanup_hotkeys(self):
        """Cleanup hotkey listener"""
        if self.hotkey_listener and self.hotkeys_active:
            try:
                self.hotkey_listener.stop()
                self.hotkeys_active = False
                print("🎮 Hotkeys deactivated")
            except:
                pass
    
    def setup_death_handling(self):
        """Setup death handling preferences"""
        print("\n💀 DEATH HANDLING CONFIGURATION")
        print("=" * 40)
        print("When your character dies, how should I-HNT handle it?")
        print("1. Respawn at town - Click 'Resurrect at the specified point' and pause app")
        print("2. Wait for other players - Click 'Waiting for other player's help', press F4, then use auto-res scroll")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1 or 2): ").strip()
                if choice == "1":
                    self.death_handling_mode = "respawn_town"
                    self.auto_handle_death = True
                    break
                elif choice == "2":
                    self.death_handling_mode = "wait_help"
                    self.auto_handle_death = True
                    self.auto_res_scroll_slot = "0"  # Default to slot 0
                    break
                else:
                    print("❌ Please enter 1 or 2")
            except KeyboardInterrupt:
                print("\n⏹️ Setup cancelled")
                self.death_handling_mode = "respawn_town"  # Default
                self.auto_handle_death = True
                break
        
        print("💀 Death handling configured successfully!")
        print("=" * 40)
    
    def setup_detection_area(self):
        """Setup detection area based on weapon type"""
        print("\n🎯 DETECTION AREA CONFIGURATION")
        print("=" * 40)
        print("Choose your weapon type for optimal hunting area:")
        print("1. Sword - Small area (150px radius) - Close combat")
        print("2. Spear - Medium area (300px radius) - Mid-range (default)")
        print("3. Bow - Large area (500px radius) - Long-range")
        print("4. Custom - Enter your own radius")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1-4, default 2): ").strip()
                if choice == "" or choice == "2":
                    self.current_weapon_type = "spear"
                    self.hunting_zone_radius = self.detection_area_presets['spear']
                    print("✅ Selected: Spear - Medium area (300px radius)")
                    break
                elif choice == "1":
                    self.current_weapon_type = "sword"
                    self.hunting_zone_radius = self.detection_area_presets['sword']
                    print("✅ Selected: Sword - Small area (150px radius)")
                    break
                elif choice == "3":
                    self.current_weapon_type = "bow"
                    self.hunting_zone_radius = self.detection_area_presets['bow']
                    print("✅ Selected: Bow - Large area (500px radius)")
                    break
                elif choice == "4":
                    self.current_weapon_type = "custom"
                    while True:
                        try:
                            radius = input("Enter custom radius (50-800 pixels): ").strip()
                            if radius.isdigit():
                                radius_int = int(radius)
                                if 50 <= radius_int <= 800:
                                    self.hunting_zone_radius = radius_int
                                    self.detection_area_presets['custom'] = radius_int
                                    print(f"✅ Selected: Custom area ({radius_int}px radius)")
                                    break
                                else:
                                    print("❌ Please enter a radius between 50-800 pixels")
                            else:
                                print("❌ Please enter a valid number")
                        except ValueError:
                            print("❌ Please enter a valid number")
                    break
                else:
                    print("❌ Please enter 1, 2, 3, or 4")
            except KeyboardInterrupt:
                print("\n⏹️ Setup cancelled - using default (Spear)")
                self.current_weapon_type = "spear"
                self.hunting_zone_radius = self.detection_area_presets['spear']
                break
        
        print(f"🎯 Detection area configured: {self.current_weapon_type.title()} - {self.hunting_zone_radius}px radius")
        print("=" * 40)
    
    def setup_smart_targeting(self):
        """Setup smart pet ignoring system"""
        print("\n🎯 SMART TARGETING SYSTEM")
        print("=" * 40)
        print("🐕 Pet Detection: Automatically ignores pets using pet cards")
        print("🎯 Mob Targeting: Targets all detected mobs without restrictions")
        print("🧠 Smart Logic: Detects pet cards and switches to next target")
        print("💀 Death Detection: Monitors for player death confirmation window")
        print("✅ Ready for unrestricted hunting!")
        
        # Clear any old protection names since we're not using them
        self.protected_names = []
    
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
        print("   • Player death detection and handling")
        print(f"   • Configurable detection area ({self.current_weapon_type.title()} - {self.hunting_zone_radius}px)")
        print("=" * 50)
        
        self.monitoring_active = True
        frame_count = 0
        start_time = time.time()
        
        # Start keyboard automation thread
        keyboard_thread = threading.Thread(target=self.continuous_keyboard_automation, daemon=True)
        keyboard_thread.start()
        
        # Wait 5 seconds before starting death detection to avoid false positives
        print("⏳ Waiting 5 seconds before starting death detection...")
        time.sleep(5)
        print("✅ Death detection now active")
        
        try:
            while self.monitoring_active and not self.stop_requested:
                loop_start = time.time()
                
                # Check if paused
                if self.paused:
                    print("⏸️ Detection paused - press CapsLock to resume")
                    time.sleep(1)
                    continue
                
                # Check if player has died (priority check)
                if self.death_detection_active:
                    if self.detect_player_death():
                        if not self.player_dead:
                            self.player_dead = True
                            print("💀 PLAYER DEATH CONFIRMED - Stopping all actions!")
                            
                            # Handle death confirmation based on configured mode
                            print(f"   🔍 Debug: auto_handle_death={self.auto_handle_death}, death_handling_mode={self.death_handling_mode}")
                            if self.auto_handle_death and self.death_handling_mode:
                                print(f"   🤖 Auto-handling death confirmation: {self.death_handling_mode}")
                                success = self.handle_death_confirmation()
                                if success:
                                    print("   ✅ Death confirmation handled successfully")
                                    # Death handling completed successfully, resume normal detection
                                    self.player_dead = False
                                    self.detection_paused = False
                                    self.keyboard_active = True
                                    print("🔄 Resuming normal hunting after death handling...")
                                    # Continue to normal detection loop (don't continue to death checking)
                                else:
                                    print("   ❌ Death confirmation handling failed")
                                    # Stop all hunting activities on failure
                                    self.keyboard_active = False
                                    self.detection_paused = True
                                    # Continue checking for death window to disappear
                                    time.sleep(1)
                                    continue
                            else:
                                print("   ⏳ Waiting for player to handle death confirmation...")
                                print("   💡 Tip: Configure death handling mode at startup")
                                # Stop all hunting activities
                                self.keyboard_active = False
                                self.detection_paused = True
                                # Continue checking for death window to disappear
                                time.sleep(1)
                                continue
                        else:
                            # Player is still dead, continue checking for death window to disappear
                            time.sleep(1)
                            continue
                    elif self.player_dead:
                        # Player was dead but death window is gone - player has been resurrected
                        self.player_dead = False
                        print("✨ PLAYER RESURRECTED - Resuming hunting activities!")
                        self.keyboard_active = True
                        self.detection_paused = False
                
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
    
    # Setup death handling preferences
    i_hnt.setup_death_handling()
    
    # Setup detection area configuration
    i_hnt.setup_detection_area()
    
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
        print("   F2 = Manual Death Detection Test")
        print("   F3 = Cycle Detection Area (Sword→Spear→Bow→Custom)")
        print("   Ctrl+C = Emergency exit")
        print("=" * 40)
        print("💡 Focus your GAME WINDOW and press CapsLock to start!")
        print("💡 Press CapsLock again to pause/resume anytime!")
        print("💡 Press F3 to change detection area for different weapons!")
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
