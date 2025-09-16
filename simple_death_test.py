#!/usr/bin/env python3
"""
Simple Death Detection Test
This script uses a very basic approach to detect death
"""

import time
import cv2
import numpy as np
import mss

def simple_death_detection():
    """Very simple death detection test"""
    print("🔍 Simple Death Detection Test")
    print("=" * 40)
    print("This will detect ANY dark area in the center screen")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    # Capture area
    area = {
        'top': 200,
        'left': 400,
        'width': 1120,
        'height': 680
    }
    
    try:
        while True:
            with mss.mss() as sct:
                screenshot = sct.grab(area)
            img = np.array(screenshot)
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            
            # Count dark pixels
            dark_mask = gray < 100
            dark_pixels = np.sum(dark_mask)
            total_pixels = gray.shape[0] * gray.shape[1]
            dark_ratio = dark_pixels / total_pixels
            
            # Very simple detection
            if dark_ratio > 0.1:  # 10% dark pixels
                print(f"💀 DARK AREA DETECTED! Ratio: {dark_ratio:.3f}")
            else:
                print(f"✅ Normal screen. Dark ratio: {dark_ratio:.3f}")
            
            time.sleep(0.5)  # Check every 0.5 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Test stopped")

if __name__ == "__main__":
    simple_death_detection()
