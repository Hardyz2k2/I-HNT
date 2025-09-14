#!/usr/bin/env python3
"""
Death Detection with Screenshots
This script detects dark areas and saves screenshots for analysis
"""

import time
import cv2
import numpy as np
import mss
from datetime import datetime

def death_detection_with_screenshots():
    """Death detection that saves screenshots when dark areas are found"""
    print("📸 Death Detection with Screenshots")
    print("=" * 40)
    print("This will save screenshots when dark areas are detected")
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
        frame_count = 0
        while True:
            frame_count += 1
            
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
                timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
                filename = f"death_detected_{timestamp}_ratio_{dark_ratio:.3f}.png"
                cv2.imwrite(filename, img)
                print(f"💀 DARK AREA DETECTED! Ratio: {dark_ratio:.3f} - Saved: {filename}")
            else:
                if frame_count % 60 == 0:  # Every 30 seconds
                    print(f"✅ Normal screen. Dark ratio: {dark_ratio:.3f}")
            
            time.sleep(0.1)  # Check every 0.1 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Test stopped")
        print("Check the saved screenshots to see what was detected")

if __name__ == "__main__":
    death_detection_with_screenshots()
