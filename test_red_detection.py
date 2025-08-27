#!/usr/bin/env python3
"""
Test script to demonstrate the new red area detection functionality in MobFinder
This script shows how the app now automatically detects the red game region and focuses text extraction on it
"""

from mob_finder_simple import MobFinder
import cv2
import numpy as np

def test_red_detection():
    print("🔴 Testing Red Area Detection Functionality")
    print("=" * 60)
    
    # Create mob finder instance
    mob_finder = MobFinder()
    
    # Show initial settings
    print("\n📊 Initial Settings:")
    print(f"Screen resolution: {mob_finder.screen_width}x{mob_finder.screen_height}")
    print(f"Default margins: Top={mob_finder.margin_top}, Bottom={mob_finder.margin_bottom}, Left={mob_finder.margin_left}, Right={mob_finder.margin_right}")
    
    # Test the red detection method
    print("\n🔍 Testing Red Area Detection:")
    print("This will attempt to detect the red game region in your screenshot")
    print("Make sure you have a screenshot with a red rectangle visible!")
    
    # Create a test image with a red rectangle (simulating your game interface)
    print("\n🎨 Creating test image with red rectangle...")
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    # Add a red rectangle in the center (simulating your game area)
    red_rect_x1, red_rect_y1 = 200, 150
    red_rect_x2, red_rect_y2 = 1720, 930
    # Note: OpenCV uses BGR format, but our detection expects RGB
    # So we'll create a red rectangle that will be detected
    test_image[red_rect_y1:red_rect_y2, red_rect_x1:red_rect_x2] = [255, 0, 0]  # Red in RGB
    
    print(f"✅ Test image created with red rectangle at ({red_rect_x1}, {red_rect_y1}) to ({red_rect_x2}, {red_rect_y2})")
    print(f"📏 Red rectangle size: {red_rect_x2 - red_rect_x1}x{red_rect_y2 - red_rect_y1} pixels")
    
    # Test red area detection
    print("\n🔍 Testing automatic red area detection...")
    success = mob_finder.detect_game_region(test_image)
    
    if success:
        print("\n🎯 Red area detection successful!")
        print(f"📍 Detected margins: Top={mob_finder.margin_top}, Bottom={mob_finder.margin_bottom}, Left={mob_finder.margin_left}, Right={mob_finder.margin_right}")
        print(f"📏 Game region size: {1920-mob_finder.margin_left-mob_finder.margin_right}x{1080-mob_finder.margin_top-mob_finder.margin_bottom} pixels")
        
        # Test auto-configure margins
        print("\n⚙️ Testing auto-configure margins...")
        mob_finder.auto_configure_margins(test_image)
        
    else:
        print("\n⚠️ Red area detection failed, using default margins")
        mob_finder.configure_margins(100, 100, 100, 100)
    
    print("\n✅ Red area detection testing completed!")
    print("💡 The app will now automatically focus text extraction on the detected game region")
    print("💡 This should significantly improve performance by ignoring UI elements at screen edges")

if __name__ == "__main__":
    test_red_detection()
