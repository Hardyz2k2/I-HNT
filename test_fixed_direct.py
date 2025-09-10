#!/usr/bin/env python3
"""
Test script to verify the fixed Mob Finder Direct functionality
"""

import time
from mob_finder_direct import MobFinderDirect

def test_fixed_functionality():
    print("🧪 Testing Fixed Mob Finder Direct Functionality")
    print("=" * 60)
    
    # Create mob finder instance
    mob_finder = MobFinderDirect()
    
    # Test 1: Check OCR initialization
    print("\n1️⃣ Testing OCR Initialization:")
    if mob_finder.reader is not None:
        print("   ✅ OCR initialized successfully")
    else:
        print("   ❌ OCR initialization failed")
        return False
    
    # Test 2: Check text filtering
    print("\n2️⃣ Testing Text Filtering:")
    test_ocr_results = [
        ([[100, 100], [200, 100], [200, 120], [100, 120]], "def test_function", 0.9),
        ([[100, 150], [200, 150], [200, 170], [100, 170]], "Tiger", 0.8),
        ([[100, 200], [200, 200], [200, 220], [100, 220]], "Pressed key: 1", 0.7),
        ([[100, 250], [200, 250], [200, 270], [100, 270]], "Wolf", 0.9),
        ([[100, 300], [200, 300], [200, 320], [100, 320]], "confidence: 0.8", 0.6),
    ]
    
    filtered = mob_finder.filter_game_text(test_ocr_results)
    print(f"   📊 Filtered {len(test_ocr_results)} -> {len(filtered)} text elements")
    
    # Should keep "Tiger" and "Wolf", filter out code text
    expected_kept = ["Tiger", "Wolf"]
    actual_kept = [text for _, text, _ in filtered]
    
    if all(name in actual_kept for name in expected_kept):
        print("   ✅ Text filtering working correctly")
    else:
        print("   ❌ Text filtering not working properly")
        print(f"   Expected: {expected_kept}, Got: {actual_kept}")
    
    # Test 3: Check game focus method
    print("\n3️⃣ Testing Game Focus Method:")
    try:
        result = mob_finder.ensure_game_focused()
        print(f"   ✅ Game focus method executed: {result}")
    except Exception as e:
        print(f"   ❌ Game focus method failed: {e}")
    
    # Test 4: Check single scan mode
    print("\n4️⃣ Testing Single Scan Mode:")
    print("   ⚠️ This will capture a screenshot and analyze it")
    print("   💡 Make sure your game window is open and focused!")
    
    try:
        # Run a single scan
        mob_finder.run_single_scan()
        print("   ✅ Single scan completed")
    except Exception as e:
        print(f"   ❌ Single scan failed: {e}")
    
    print("\n✅ All tests completed!")
    print("💡 The fixed version should now:")
    print("   - Filter out IDE/code text properly")
    print("   - Focus on game window")
    print("   - Work with game window open")
    print("   - Stop properly with Ctrl+C")
    print("   - Press keyboard keys correctly")

if __name__ == "__main__":
    test_fixed_functionality()


