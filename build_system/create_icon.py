#!/usr/bin/env python3
"""
Icon Creator for YOLO Mob Finder
Creates a simple application icon using PIL/Pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_app_icon():
    """Create a simple but professional-looking app icon"""
    
    # Icon size (ICO format supports multiple sizes)
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Create icons for different sizes
    icons = []
    
    for size in sizes:
        # Create a square image with transparency
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Color scheme - tech/gaming theme
        bg_color = (45, 55, 72, 255)      # Dark blue-gray background
        accent_color = (59, 130, 246, 255)  # Bright blue accent
        text_color = (255, 255, 255, 255)   # White text
        
        # Draw rounded rectangle background
        margin = max(2, size // 16)
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=max(4, size // 8),
            fill=bg_color,
            outline=accent_color,
            width=max(1, size // 32)
        )
        
        # Draw eye symbol (representing YOLO vision)
        center_x, center_y = size // 2, size // 2
        eye_size = max(6, size // 4)
        
        # Outer eye shape
        eye_bounds = [
            center_x - eye_size, center_y - eye_size // 2,
            center_x + eye_size, center_y + eye_size // 2
        ]
        draw.ellipse(eye_bounds, fill=text_color)
        
        # Inner pupil
        pupil_size = max(2, eye_size // 3)
        pupil_bounds = [
            center_x - pupil_size // 2, center_y - pupil_size // 2,
            center_x + pupil_size // 2, center_y + pupil_size // 2
        ]
        draw.ellipse(pupil_bounds, fill=bg_color)
        
        # Add crosshair for targeting
        line_length = max(3, size // 8)
        line_width = max(1, size // 64)
        
        # Vertical line
        draw.line([
            center_x, center_y - line_length,
            center_x, center_y + line_length
        ], fill=accent_color, width=line_width)
        
        # Horizontal line
        draw.line([
            center_x - line_length, center_y,
            center_x + line_length, center_y
        ], fill=accent_color, width=line_width)
        
        # Add small "AI" text if icon is large enough
        if size >= 64:
            try:
                # Try to use a built-in font
                font_size = max(8, size // 8)
                font = ImageFont.load_default()
                
                # Position text at bottom
                text = "AI"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_x = center_x - text_width // 2
                text_y = size - text_height - margin - 2
                
                draw.text((text_x, text_y), text, fill=accent_color, font=font)
                
            except Exception:
                # If font loading fails, skip text
                pass
        
        icons.append(icon)
        print(f"✅ Created {size}x{size} icon")
    
    # Save as ICO file
    icon_path = Path("app_icon.ico")
    icons[0].save(icon_path, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
    
    # Also save largest as PNG for reference
    png_path = Path("app_icon.png")
    icons[-1].save(png_path, format='PNG')
    
    print(f"✅ Icon saved: {icon_path}")
    print(f"✅ PNG reference: {png_path}")
    
    return icon_path, png_path

def create_installer_images():
    """Create images for the installer wizard"""
    
    # Installer banner image (164x314 pixels)
    banner_width, banner_height = 164, 314
    banner = Image.new('RGB', (banner_width, banner_height), (45, 55, 72))
    banner_draw = ImageDraw.Draw(banner)
    
    # Gradient effect (simple)
    for y in range(banner_height):
        color_factor = y / banner_height
        r = int(45 + (59 - 45) * color_factor)
        g = int(55 + (130 - 55) * color_factor)  
        b = int(72 + (246 - 72) * color_factor)
        banner_draw.line([(0, y), (banner_width, y)], fill=(r, g, b))
    
    # Add YOLO eye logo
    eye_center_x = banner_width // 2
    eye_center_y = banner_height // 3
    eye_size = 30
    
    # Draw eye
    eye_bounds = [
        eye_center_x - eye_size, eye_center_y - eye_size // 2,
        eye_center_x + eye_size, eye_center_y + eye_size // 2
    ]
    banner_draw.ellipse(eye_bounds, fill=(255, 255, 255))
    
    pupil_bounds = [
        eye_center_x - 10, eye_center_y - 10,
        eye_center_x + 10, eye_center_y + 10
    ]
    banner_draw.ellipse(pupil_bounds, fill=(45, 55, 72))
    
    # Crosshair
    banner_draw.line([
        eye_center_x, eye_center_y - 20,
        eye_center_x, eye_center_y + 20
    ], fill=(255, 255, 255), width=2)
    
    banner_draw.line([
        eye_center_x - 20, eye_center_y,
        eye_center_x + 20, eye_center_y
    ], fill=(255, 255, 255), width=2)
    
    banner.save("installer_image.bmp", "BMP")
    
    # Small installer image (55x58 pixels)
    small_width, small_height = 55, 58
    small = Image.new('RGB', (small_width, small_height), (45, 55, 72))
    small_draw = ImageDraw.Draw(small)
    
    # Mini eye logo
    small_eye_size = 15
    small_center_x = small_width // 2
    small_center_y = small_height // 2
    
    small_eye_bounds = [
        small_center_x - small_eye_size, small_center_y - small_eye_size // 2,
        small_center_x + small_eye_size, small_center_y + small_eye_size // 2
    ]
    small_draw.ellipse(small_eye_bounds, fill=(255, 255, 255))
    
    small_pupil_bounds = [
        small_center_x - 5, small_center_y - 5,
        small_center_x + 5, small_center_y + 5
    ]
    small_draw.ellipse(small_pupil_bounds, fill=(45, 55, 72))
    
    small.save("installer_small.bmp", "BMP")
    
    print("✅ Installer images created:")
    print("   - installer_image.bmp (164x314)")
    print("   - installer_small.bmp (55x58)")

def main():
    """Create all icon and image resources"""
    print("🎨 Creating application icons and installer images...")
    print("=" * 50)
    
    try:
        # Create app icons
        icon_path, png_path = create_app_icon()
        
        # Create installer images
        create_installer_images()
        
        print("\n✅ All graphics created successfully!")
        print("\nFiles created:")
        print(f"   📁 {icon_path} - Application icon")
        print(f"   📁 {png_path} - PNG reference")
        print("   📁 installer_image.bmp - Installer banner")
        print("   📁 installer_small.bmp - Installer small image")
        
    except ImportError:
        print("❌ PIL/Pillow not installed!")
        print("💡 Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error creating icons: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()