#!/usr/bin/env python3
"""
Screen Capture Test for Death Detection
This script captures the center screen area and saves it to see what we're actually detecting
"""

import time
import cv2
import numpy as np
import mss
from datetime import datetime

def capture_center_screen():
    """Capture center screen area and save for analysis"""
    print("📸 Screen Capture Test for Death Detection")
    print("=" * 50)
    
    # Define center screen area (same as death detection)
    death_window_area = {
        'top': 200,     # Center vertically
        'left': 300,    # Center horizontally
        'width': 1320,  # Wide enough to catch the window
        'height': 680   # Tall enough to catch the window
    }
    
    print("🎯 Capturing center screen area...")
    print(f"   Area: {death_window_area}")
    print("   Make sure your game is visible and try to die!")
    print("   Press Ctrl+C to stop capturing")
    print("=" * 50)
    
    try:
        frame_count = 0
        while True:
            frame_count += 1
            
            # Capture center screen area
            with mss.mss() as sct:
                screenshot = sct.grab(death_window_area)
            img = np.array(screenshot)
            
            # Convert to RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
            
            # Analyze pixel values
            very_dark_mask = gray < 50
            dark_mask = gray < 80
            bright_mask = gray > 200
            
            very_dark_pixels = np.sum(very_dark_mask)
            dark_pixels = np.sum(dark_mask)
            bright_pixels = np.sum(bright_mask)
            total_pixels = gray.shape[0] * gray.shape[1]
            
            very_dark_ratio = very_dark_pixels / total_pixels
            dark_ratio = dark_pixels / total_pixels
            bright_ratio = bright_pixels / total_pixels
            
            # Show values every second
            if frame_count % 30 == 0:
                print(f"Frame {frame_count}: Very dark: {very_dark_ratio:.3f}, Dark: {dark_ratio:.3f}, Bright: {bright_ratio:.3f}")
                
                # Save image every 5 seconds for analysis
                if frame_count % 150 == 0:
                    timestamp = datetime.now().strftime("%H%M%S")
                    filename = f"screen_capture_{timestamp}.png"
                    cv2.imwrite(filename, rgb_img)
                    print(f"   💾 Saved screenshot: {filename}")
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("\n⏹️ Screen capture stopped")
        print("✅ Check the saved screenshots to see what the detection area looks like")

if __name__ == "__main__":
    capture_center_screen()
