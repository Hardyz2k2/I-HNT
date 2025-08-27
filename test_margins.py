#!/usr/bin/env python3
"""
Test script to demonstrate the new margin functionality in MobFinder
This script shows how the app now ignores screen edges for faster text extraction
"""

from mob_finder_simple import MobFinder

def test_margins():
    print("🧪 Testing Margin Functionality")
    print("=" * 50)
    
    # Create mob finder instance
    mob_finder = MobFinder()
    
    # Show current settings
    print("\n📊 Initial Settings:")
    print(f"Screen resolution: {mob_finder.screen_width}x{mob_finder.screen_height}")
    print(f"Current margins: Top={mob_finder.margin_top}, Bottom={mob_finder.margin_bottom}, Left={mob_finder.margin_left}, Right={mob_finder.margin_right}")
    print(f"Text extraction area: {mob_finder.screen_width-mob_finder.margin_left-mob_finder.margin_right}x{mob_finder.screen_height-mob_finder.margin_top-mob_finder.margin_bottom} pixels")
    
    # Test different margin configurations
    print("\n🔧 Testing Different Margin Configurations:")
    
    # Test 1: Default margins (100px all around)
    print("\n1️⃣ Default margins (100px all around):")
    mob_finder.configure_margins(100, 100, 100, 100)
    
    # Test 2: Larger margins (200px all around)
    print("\n2️⃣ Larger margins (200px all around):")
    mob_finder.configure_margins(200, 200, 200, 200)
    
    # Test 3: Asymmetric margins
    print("\n3️⃣ Asymmetric margins (top=50, bottom=150, left=75, right=125):")
    mob_finder.configure_margins(50, 150, 75, 125)
    
    # Test 4: Minimal margins (10px all around)
    print("\n4️⃣ Minimal margins (10px all around):")
    mob_finder.configure_margins(10, 10, 10, 10)
    
    # Test 5: Reset to default
    print("\n5️⃣ Reset to default margins (100px all around):")
    mob_finder.configure_margins(100, 100, 100, 100)
    
    print("\n✅ Margin testing completed!")
    print("💡 You can now run the main app with optimized margins for faster text extraction")

if __name__ == "__main__":
    test_margins()

