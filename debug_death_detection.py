#!/usr/bin/env python3
"""
Debug script for I-HNT Death Detection
This script helps debug why death detection might not be working
"""

import time
from i_hnt import IHNTMobFinder

def debug_death_detection():
    """Debug the death detection system with detailed output"""
    print("🔍 I-HNT Death Detection Debug Tool")
    print("=" * 50)
    
    # Create I-HNT instance
    i_hnt = IHNTMobFinder()
    
    # Enable death detection and debug mode
    i_hnt.death_detection_active = True
    i_hnt.death_debug_mode = True
    i_hnt.auto_handle_death = False  # Manual handling for debugging
    
    print("💀 Death Detection Debug Started")
    print("   - Debug mode enabled - will show detection values")
    print("   - Press Ctrl+C to stop debugging")
    print("   - Make sure your game is visible")
    print("   - Try to die in-game to see detection values")
    print("=" * 50)
    
    try:
        frame_count = 0
        while True:
            frame_count += 1
            
            # Test death detection with debug output
            if i_hnt.detect_player_death():
                if not i_hnt.player_dead:
                    i_hnt.player_dead = True
                    print(f"💀 DEATH DETECTED! (Frame {frame_count})")
                    print("   - Confirmation window found with debug values above")
                else:
                    print(f"💀 Death window still visible (Frame {frame_count})")
            else:
                if i_hnt.player_dead:
                    i_hnt.player_dead = False
                    print(f"✨ Death window disappeared (Frame {frame_count})")
                else:
                    # Show debug info every 30 frames (1 second at 30fps)
                    if frame_count % 30 == 0:
                        print(f"✅ No death detected (Frame {frame_count})")
            
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("\n⏹️ Death detection debug stopped")
        print("✅ Debug completed!")

if __name__ == "__main__":
    debug_death_detection()
