#!/usr/bin/env python3
"""
Generate app icons for Family Household Manager
Creates icons in various sizes for Android and Play Store
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon(size=512):
    """Create the main app icon"""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    primary_color = (46, 125, 50)  # Green
    accent_color = (255, 193, 7)   # Amber
    background_color = (255, 255, 255, 220)  # White with slight transparency

    # Draw rounded rectangle background
    corner_radius = size // 8
    draw.rounded_rectangle([10, 10, size-10, size-10], fill=background_color, radius=corner_radius)

    # Draw house outline
    house_color = primary_color
    # House base
    house_width = size * 0.6
    house_height = size * 0.5
    house_x = (size - house_width) // 2
    house_y = size * 0.3

    # House walls
    draw.rectangle([house_x, house_y + house_height * 0.3, house_x + house_width, house_y + house_height],
                   fill=house_color)

    # House roof
    roof_points = [(house_x, house_y + house_height * 0.3),
                   (house_x + house_width//2, house_y),
                   (house_x + house_width, house_y + house_height * 0.3)]
    draw.polygon(roof_points, fill=(139, 69, 19))  # Brown roof

    # Door
    door_width = house_width * 0.15
    door_height = house_height * 0.4
    door_x = house_x + house_width * 0.4
    door_y = house_y + house_height * 0.6
    draw.rectangle([door_x, door_y, door_x + door_width, door_y + door_height], fill=(101, 67, 33))

    # Windows
    window_size = house_width * 0.12
    # Left window
    draw.rectangle([house_x + house_width * 0.15, house_y + house_height * 0.4,
                    house_x + house_width * 0.15 + window_size, house_y + house_height * 0.4 + window_size],
                   fill=(135, 206, 235))
    # Right window
    draw.rectangle([house_x + house_width * 0.7, house_y + house_height * 0.4,
                    house_x + house_width * 0.7 + window_size, house_y + house_height * 0.4 + window_size],
                   fill=(135, 206, 235))

    # Shopping cart symbol (simplified)
    cart_size = size * 0.25
    cart_x = size * 0.7
    cart_y = size * 0.65

    # Cart base
    draw.rectangle([cart_x, cart_y, cart_x + cart_size * 0.8, cart_y + cart_size * 0.6],
                   fill=(169, 169, 169))
    # Cart handle
    draw.rectangle([cart_x + cart_size * 0.8, cart_y - cart_size * 0.2,
                    cart_x + cart_size, cart_y + cart_size * 0.4], fill=(105, 105, 105))
    # Wheels
    wheel_size = cart_size * 0.15
    draw.ellipse([cart_x + cart_size * 0.1, cart_y + cart_size * 0.5,
                  cart_x + cart_size * 0.1 + wheel_size, cart_y + cart_size * 0.5 + wheel_size],
                 fill=(0, 0, 0))
    draw.ellipse([cart_x + cart_size * 0.6, cart_y + cart_size * 0.5,
                  cart_x + cart_size * 0.6 + wheel_size, cart_y + cart_size * 0.5 + wheel_size],
                 fill=(0, 0, 0))

    return img

def create_feature_graphic():
    """Create the Play Store feature graphic (1024x500)"""
    img = Image.new('RGB', (1024, 500), (46, 125, 50))  # Green background
    draw = ImageDraw.Draw(img)

    # Add some decorative elements
    # Title area
    title_bg = Image.new('RGBA', (800, 100), (255, 255, 255, 180))
    img.paste(title_bg, (100, 50), title_bg)

    # Add some geometric shapes
    draw.ellipse([50, 200, 150, 300], fill=(255, 193, 7, 128))
    draw.ellipse([850, 150, 950, 250], fill=(255, 87, 34, 128))
    draw.rectangle([200, 350, 400, 450], fill=(33, 150, 243, 128))
    draw.rectangle([600, 300, 800, 400], fill=(156, 39, 176, 128))

    return img

def create_screenshots():
    """Create placeholder screenshots"""
    # For demo purposes, create simple colored rectangles
    # In real implementation, you'd take actual screenshots
    screenshots = []

    for i in range(4):
        img = Image.new('RGB', (1080, 1920), (240, 248, 255))  # Light blue background
        draw = ImageDraw.Draw(img)

        # Add some mock UI elements
        draw.rectangle([100, 200, 980, 400], fill=(255, 255, 255), outline=(200, 200, 200))
        draw.rectangle([100, 500, 980, 1500], fill=(255, 255, 255), outline=(200, 200, 200))

        # Mock text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()

        draw.text((150, 250), f"Family Manager - Screen {i+1}", fill=(0, 0, 0), font=font)
        draw.text((150, 550), "Mock UI Elements", fill=(100, 100, 100), font=font)

        screenshots.append(img)

    return screenshots

def main():
    """Generate all required icons and assets"""
    assets_dir = "/home/server1/Desktop/meal-plan-inventory/assets"
    os.makedirs(assets_dir, exist_ok=True)

    # Generate main app icon (512x512)
    icon_512 = create_app_icon(512)
    icon_512.save(os.path.join(assets_dir, "icon.png"))

    # Generate additional icon sizes for Android
    sizes = [48, 72, 96, 144, 192]
    for size in sizes:
        icon = create_app_icon(size)
        icon.save(os.path.join(assets_dir, f"icon-{size}.png"))

    # Generate feature graphic
    feature_graphic = create_feature_graphic()
    feature_graphic.save(os.path.join(assets_dir, "feature_graphic.png"))

    # Generate presplash
    presplash = Image.new('RGB', (512, 512), (46, 125, 50))
    draw = ImageDraw.Draw(presplash)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    draw.text((100, 236), "Family Manager", fill=(255, 255, 255), font=font)
    presplash.save(os.path.join(assets_dir, "presplash.png"))

    # Generate mock screenshots
    screenshots = create_screenshots()
    for i, screenshot in enumerate(screenshots):
        screenshot.save(os.path.join(assets_dir, f"screenshot_{i+1}.png"))

    print("✅ All app assets generated successfully!")
    print(f"📁 Assets saved to: {assets_dir}")
    print("\nGenerated files:")
    for file in os.listdir(assets_dir):
        print(f"  - {file}")

if __name__ == "__main__":
    main()