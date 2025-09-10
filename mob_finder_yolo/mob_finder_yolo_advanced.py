#!/usr/bin/env python3
"""
Advanced YOLO Mob Finder - Configuration-based with Enhanced Features
Uses YAML configuration and advanced YOLO features for maximum performance.
"""

import time
import cv2
import numpy as np
import mss
import pyautogui
import threading
import yaml
from ultralytics import YOLO
import torch
from pathlib import Path

class AdvancedYOLOMobFinder:
    def __init__(self, config_path="config.yaml"):
        # Load configuration
        self.load_config(config_path)
        
        # Initialize components
        self.model = None
        self.sct = mss.mss()
        self.monitoring_active = False
        self.keyboard_active = False
        self.stop_requested = False
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_update = time.time()
        
        # Protection setup
        self.protected_names = []
        
        print("⚡ Advanced YOLO Mob Finder")
        print("=" * 50)
        print(f"🔥 GPU Available: {'✅ YES' if torch.cuda.is_available() else '❌ NO'}")
        print(f"🎯 Target FPS: {self.config['performance']['target_fps']}")
        print(f"📏 Detection area: {self.get_detection_area_size()}")
        print(f"🛡️ Protection radius: {self.config['protection']['character_radius']}px")
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Configuration loaded from {config_path}")
        except FileNotFoundError:
            print(f"⚠️ Config file {config_path} not found, using defaults")
            self.config = self.get_default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Default configuration if file not found"""
        return {
            'model': {
                'path': 'yolov8n.pt',
                'confidence_threshold': 0.25,
                'iou_threshold': 0.45,
                'max_detections': 300
            },
            'performance': {
                'target_fps': 30,
                'use_gpu': True,
                'use_half_precision': True
            },
            'screen': {
                'width': 1920,
                'height': 1080,
                'margins': {'top': 100, 'bottom': 200, 'left': 100, 'right': 100}
            },
            'protection': {
                'character_radius': 150,
                'enable_name_protection': False
            },
            'targeting': {
                'offset_y': 10,
                'prefer_closest': True,
                'click_delay': 0.1
            },
            'keyboard': {
                'enabled': True,
                'sequence': '123145',
                'sequence_delay': 1.0,
                'key_delay': 0.1
            },
            'logging': {
                'show_fps': True,
                'show_detections': True,
                'fps_update_interval': 30,
                'verbose': False
            }
        }
    
    def get_detection_area_size(self):
        """Calculate detection area size"""
        screen = self.config['screen']
        margins = screen['margins']
        width = screen['width'] - margins['left'] - margins['right']
        height = screen['height'] - margins['top'] - margins['bottom']
        return f"{width}x{height}"
    
    def setup_protection(self):
        """Interactive protection setup"""
        print("\n🛡️ PROTECTION SETUP")
        print("=" * 30)
        
        character_name = input("🧙 Character name (optional): ").strip()
        if character_name:
            self.protected_names.append(character_name)
            print(f"✅ Character: {character_name}")
        
        print("\n🐕 Pet names (press Enter twice to finish):")
        pet_count = 1
        while True:
            pet_name = input(f"   Pet #{pet_count}: ").strip()
            if not pet_name:
                break
            self.protected_names.append(pet_name)
            pet_count += 1
        
        print(f"\n🛡️ Protection: Position-based ({self.config['protection']['character_radius']}px radius)")
    
    def load_yolo_model(self):
        """Load and configure YOLO model"""
        model_path = self.config['model']['path']
        print(f"\n🤖 Loading YOLO model: {model_path}")
        
        try:
            self.model = YOLO(model_path)
            
            # GPU configuration
            if self.config['performance']['use_gpu'] and torch.cuda.is_available():
                self.model.to('cuda')
                print("🔥 Model loaded on GPU")
                
                # Half precision for speed
                if self.config['performance']['use_half_precision']:
                    print("⚡ Using half precision (FP16) for speed boost")
            else:
                print("💻 Model loaded on CPU")
            
            # Warm up model
            print("🔥 Warming up model...")
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            self.model(dummy_img, verbose=False)
            print("✅ Model ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
    
    def capture_optimized_frame(self):
        """Capture optimized game frame"""
        try:
            margins = self.config['screen']['margins']
            screen = self.config['screen']
            
            capture_area = {
                'top': margins['top'],
                'left': margins['left'],
                'width': screen['width'] - margins['left'] - margins['right'],
                'height': screen['height'] - margins['top'] - margins['bottom']
            }
            
            screenshot = self.sct.grab(capture_area)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            
            return frame, capture_area
            
        except Exception as e:
            if self.config['logging']['verbose']:
                print(f"❌ Capture failed: {e}")
            return None, None
    
    def detect_with_yolo(self, frame):
        """Advanced YOLO detection with configuration"""
        if self.model is None:
            return []
        
        try:
            model_config = self.config['model']
            
            # YOLO inference with advanced settings
            results = self.model(
                frame,
                conf=model_config['confidence_threshold'],
                iou=model_config['iou_threshold'],
                max_det=model_config['max_detections'],
                verbose=self.config['logging']['verbose'],
                half=self.config['performance']['use_half_precision'],
                agnostic_nms=self.config.get('yolo_advanced', {}).get('agnostic_nms', False),
                augment=self.config.get('yolo_advanced', {}).get('augment', False)
            )
            
            detections = []
            margins = self.config['screen']['margins']
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i in range(len(boxes)):
                        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                        confidence = float(boxes.conf[i].cpu().numpy())
                        class_id = int(boxes.cls[i].cpu().numpy())
                        
                        # Calculate centers
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        # Convert to screen coordinates
                        screen_x = center_x + margins['left']
                        screen_y = center_y + margins['top']
                        
                        # Apply targeting offset
                        target_x = screen_x
                        target_y = screen_y + self.config['targeting']['offset_y']
                        
                        detection = {
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence,
                            'class_id': class_id,
                            'center': (center_x, center_y),
                            'screen_position': (screen_x, screen_y),
                            'target_position': (target_x, target_y),
                            'size': (x2 - x1, y2 - y1)
                        }
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            if self.config['logging']['verbose']:
                print(f"❌ Detection failed: {e}")
            return []
    
    def filter_safe_targets(self, detections):
        """Filter detections based on protection settings"""
        safe_detections = []
        
        # Character position (screen center)
        screen = self.config['screen']
        char_x = screen['width'] // 2
        char_y = screen['height'] // 2
        protection_radius = self.config['protection']['character_radius']
        
        for detection in detections:
            screen_x, screen_y = detection['screen_position']
            distance = ((screen_x - char_x) ** 2 + (screen_y - char_y) ** 2) ** 0.5
            
            if distance > protection_radius:
                safe_detections.append(detection)
                
                if self.config['logging']['show_detections']:
                    print(f"✅ Target: {detection['screen_position']} (conf: {detection['confidence']:.2f}, dist: {distance:.0f}px)")
            else:
                if self.config['logging']['show_detections']:
                    print(f"🛡️ Protected: {detection['screen_position']} (too close: {distance:.0f}px)")
        
        return safe_detections
    
    def select_optimal_target(self, detections):
        """Select best target based on configuration"""
        if not detections:
            return None
        
        if self.config['targeting']['prefer_closest']:
            # Select closest to character
            screen = self.config['screen']
            char_x, char_y = screen['width'] // 2, screen['height'] // 2
            
            def distance_to_char(det):
                x, y = det['screen_position']
                return ((x - char_x) ** 2 + (y - char_y) ** 2) ** 0.5
            
            best_target = min(detections, key=distance_to_char)
        else:
            # Select highest confidence
            best_target = max(detections, key=lambda det: det['confidence'])
        
        return best_target
    
    def execute_target_click(self, target):
        """Execute optimized target click"""
        try:
            target_pos = target['target_position']
            
            if self.config['logging']['show_detections']:
                print(f"🎯 Clicking: {target_pos} (conf: {target['confidence']:.2f})")
            
            pyautogui.click(target_pos[0], target_pos[1], button='left')
            
            # Configurable click delay
            time.sleep(self.config['targeting']['click_delay'])
            return True
            
        except Exception as e:
            if self.config['logging']['verbose']:
                print(f"❌ Click failed: {e}")
            return False
    
    def keyboard_automation_loop(self):
        """Advanced keyboard automation with configuration"""
        if not self.config['keyboard']['enabled']:
            return
        
        print(f"⌨️ Keyboard automation: {self.config['keyboard']['sequence']}")
        self.keyboard_active = True
        
        sequence = self.config['keyboard']['sequence']
        key_delay = self.config['keyboard']['key_delay']
        sequence_delay = self.config['keyboard']['sequence_delay']
        
        try:
            while self.keyboard_active and self.monitoring_active and not self.stop_requested:
                for key in sequence:
                    if not self.keyboard_active or not self.monitoring_active or self.stop_requested:
                        break
                    
                    pyautogui.press(key)
                    time.sleep(key_delay)
                
                time.sleep(sequence_delay)
                
        except Exception as e:
            print(f"❌ Keyboard error: {e}")
        finally:
            self.keyboard_active = False
    
    def update_fps_counter(self):
        """Update FPS counter based on configuration"""
        if not self.config['logging']['show_fps']:
            return
        
        self.frame_count += 1
        current_time = time.time()
        
        if self.frame_count % self.config['logging']['fps_update_interval'] == 0:
            elapsed = current_time - self.start_time
            fps = self.frame_count / elapsed
            print(f"📊 FPS: {fps:.1f} | Frames: {self.frame_count}")
    
    def real_time_yolo_loop(self):
        """Main real-time YOLO detection loop"""
        print("\n⚡ STARTING ADVANCED YOLO DETECTION")
        print("=" * 50)
        
        self.monitoring_active = True
        target_fps = self.config['performance']['target_fps']
        target_frame_time = 1.0 / target_fps
        
        # Start keyboard thread
        keyboard_thread = threading.Thread(target=self.keyboard_automation_loop, daemon=True)
        keyboard_thread.start()
        
        try:
            while self.monitoring_active and not self.stop_requested:
                frame_start = time.time()
                
                # Capture frame
                frame, _ = self.capture_optimized_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # YOLO detection
                detections = self.detect_with_yolo(frame)
                
                if detections:
                    # Filter safe targets
                    safe_targets = self.filter_safe_targets(detections)
                    
                    if safe_targets:
                        # Select and click best target
                        best_target = self.select_optimal_target(safe_targets)
                        if best_target:
                            self.execute_target_click(best_target)
                
                # FPS control and monitoring
                self.update_fps_counter()
                
                # Maintain target FPS
                frame_time = time.time() - frame_start
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.monitoring_active = False
            self.keyboard_active = False
            
            if keyboard_thread.is_alive():
                keyboard_thread.join(timeout=2)
            
            print("🏁 Advanced YOLO detection ended")

def main():
    print("⚡ Advanced YOLO Mob Finder")
    print("🔧 Configuration-driven real-time detection")
    print("=" * 50)
    
    # Create finder
    finder = AdvancedYOLOMobFinder()
    
    # Setup protection
    finder.setup_protection()
    
    # Load model
    if not finder.load_yolo_model():
        print("❌ Cannot continue without model")
        return
    
    try:
        print("\n🚀 Starting in 3 seconds...")
        print("💡 Focus your game window!")
        
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        finder.real_time_yolo_loop()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n🏁 Complete!")

if __name__ == "__main__":
    main()
