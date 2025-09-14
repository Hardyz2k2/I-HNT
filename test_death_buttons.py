#!/usr/bin/env python3
"""
Test Death Button Positions
This script tests clicking on the death confirmation buttons
"""

import time
import pyautogui

def test_death_buttons():
    """Test clicking death confirmation buttons"""
    print("🧪 Testing Death Button Positions")
    print("=" * 40)
    print("This will test clicking on death confirmation buttons")
    print("Make sure the death window is visible!")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    screen_width, screen_height = 1920, 1080
    
    try:
        while True:
            print("\nChoose button to test:")
            print("1. Resurrect at town (left button)")
            print("2. Wait for help (right button)")
            print("3. Exit")
            
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                # Left button - Resurrect at town
                button_x = screen_width // 2 - 150
                button_y = screen_height // 2 + 200
                print(f"Clicking left button at ({button_x}, {button_y})")
                pyautogui.click(button_x, button_y)
                print("✅ Left button clicked")
                
            elif choice == "2":
                # Right button - Wait for help
                button_x = screen_width // 2 + 150
                button_y = screen_height // 2 + 200
                print(f"Clicking right button at ({button_x}, {button_y})")
                pyautogui.click(button_x, button_y)
                print("✅ Right button clicked")
                
            elif choice == "3":
                break
            else:
                print("❌ Invalid choice")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test stopped")

if __name__ == "__main__":
    test_death_buttons()
