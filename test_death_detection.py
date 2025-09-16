#!/usr/bin/env python3
"""
Test script for I-HNT Death Detection
This script tests the death detection functionality without running the full hunting system
"""

import time
from i_hnt import IHNTMobFinder

def test_death_detection():
    """Test the death detection system"""
    print("🧪 Testing I-HNT Death Detection System")
    print("=" * 50)
    
    # Create I-HNT instance
    i_hnt = IHNTMobFinder()
    
    # Enable death detection
    i_hnt.death_detection_active = True
    i_hnt.auto_handle_death = True  # Enable auto handling for testing
    i_hnt.death_handling_mode = "respawn_town"  # Default mode for testing
    
    print("💀 Death Detection Test Started")
    print("   - Looking for death confirmation window in center of screen")
    print("   - Press Ctrl+C to stop testing")
    print("   - Make sure your game is visible and try to die in-game")
    print("=" * 50)
    
    try:
        while True:
            # Test death detection
            if i_hnt.detect_player_death():
                if not i_hnt.player_dead:
                    i_hnt.player_dead = True
                    print("💀 DEATH DETECTED! Confirmation window found!")
                    print("   - Dark window with text patterns detected")
                    print("   - Death confirmation window is visible")
                    
                    # Test death handling options
                    print("\n🤖 Testing death handling options:")
                    print("   1. Testing 'Respawn at town' mode...")
                    i_hnt.death_handling_mode = "respawn_town"
                    i_hnt.handle_death_confirmation()
                    time.sleep(2)
                    
                    print("   2. Testing 'Wait for other players' mode...")
                    i_hnt.death_handling_mode = "wait_help"
                    i_hnt.auto_res_scroll_slot = "0"
                    i_hnt.handle_death_confirmation()
                    time.sleep(2)
                    
                else:
                    print("💀 Death window still visible...")
            else:
                if i_hnt.player_dead:
                    i_hnt.player_dead = False
                    print("✨ Death window disappeared - Player resurrected!")
                else:
                    print("✅ No death detected - Player is alive")
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n⏹️ Death detection test stopped")
        print("✅ Test completed successfully!")

if __name__ == "__main__":
    test_death_detection()
