#!/usr/bin/env python3
"""
Generate a G13 background image that matches button overlay positions exactly.
"""

from PIL import Image, ImageDraw, ImageFilter
import os

# Import layout from the project
from src.g13_linux.gui.resources.g13_layout import (
    G13_BUTTON_POSITIONS,
    JOYSTICK_AREA,
    LCD_AREA,
    KEYBOARD_WIDTH,
    KEYBOARD_HEIGHT,
)

def create_g13_background():
    """Generate a stylized G13 device background image."""

    # Create base image with dark background
    img = Image.new('RGB', (KEYBOARD_WIDTH, KEYBOARD_HEIGHT), (20, 20, 22))
    draw = ImageDraw.Draw(img)

    # Device body outline (main chassis)
    body_margin = 40
    body_rect = [
        body_margin, 60,
        KEYBOARD_WIDTH - body_margin, KEYBOARD_HEIGHT - 100
    ]

    # Draw outer glow/edge
    for i in range(5):
        offset = 5 - i
        color = (45 + i*5, 45 + i*5, 48 + i*5)
        draw.rounded_rectangle(
            [body_rect[0]-offset, body_rect[1]-offset,
             body_rect[2]+offset, body_rect[3]+offset],
            radius=50, fill=color
        )

    # Main body
    draw.rounded_rectangle(body_rect, radius=45, fill=(32, 32, 36))

    # Inner panel (key area background)
    key_area = [120, 250, 680, 550]
    draw.rounded_rectangle(key_area, radius=20, fill=(25, 25, 28))

    # LCD display area
    lcd = LCD_AREA
    # LCD bezel
    draw.rounded_rectangle(
        [lcd["x"]-10, lcd["y"]-10,
         lcd["x"]+lcd["width"]+10, lcd["y"]+lcd["height"]+10],
        radius=8, fill=(15, 15, 18)
    )
    # LCD screen (dark green)
    draw.rectangle(
        [lcd["x"], lcd["y"], lcd["x"]+lcd["width"], lcd["y"]+lcd["height"]],
        fill=(8, 20, 8)
    )
    # LCD grid lines (subtle)
    for y in range(lcd["y"], lcd["y"]+lcd["height"], 4):
        draw.line([(lcd["x"], y), (lcd["x"]+lcd["width"], y)], fill=(12, 28, 12), width=1)

    # Draw button recesses (where physical keys sit)
    for button_id, pos in G13_BUTTON_POSITIONS.items():
        x, y, w, h = pos["x"], pos["y"], pos["width"], pos["height"]

        # Button recess (darker than surrounding)
        recess_color = (18, 18, 20)
        draw.rounded_rectangle([x-2, y-2, x+w+2, y+h+2], radius=6, fill=recess_color)

        # Key cap base (slightly lighter)
        key_color = (35, 35, 40)
        draw.rounded_rectangle([x, y, x+w, y+h], radius=5, fill=key_color)

        # Key cap highlight (top edge)
        highlight = (50, 50, 55)
        draw.line([(x+3, y+2), (x+w-3, y+2)], fill=highlight, width=1)

    # Joystick area
    js = JOYSTICK_AREA
    center_x = js["x"] + js["width"] // 2
    center_y = js["y"] + js["height"] // 2
    radius = js["width"] // 2

    # Joystick housing (recessed area)
    draw.ellipse(
        [center_x-radius-8, center_y-radius-8,
         center_x+radius+8, center_y+radius+8],
        fill=(22, 22, 25)
    )

    # Inner movement area
    draw.ellipse(
        [center_x-radius, center_y-radius,
         center_x+radius, center_y+radius],
        fill=(15, 15, 18)
    )

    # Joystick cap (center position)
    stick_radius = 22
    draw.ellipse(
        [center_x-stick_radius, center_y-stick_radius,
         center_x+stick_radius, center_y+stick_radius],
        fill=(40, 40, 45)
    )
    # Stick top highlight
    draw.ellipse(
        [center_x-stick_radius+4, center_y-stick_radius+4,
         center_x+stick_radius-4, center_y+stick_radius-4],
        fill=(50, 50, 55)
    )

    # Palm rest area (bottom curved section)
    palm_y = 620
    draw.rounded_rectangle(
        [100, palm_y, KEYBOARD_WIDTH-100, KEYBOARD_HEIGHT-120],
        radius=80, fill=(28, 28, 32)
    )

    # Logitech "G" logo area (bottom center)
    logo_x, logo_y = KEYBOARD_WIDTH // 2, KEYBOARD_HEIGHT - 180
    draw.ellipse([logo_x-30, logo_y-30, logo_x+30, logo_y+30], fill=(35, 35, 40))

    # Add subtle texture/noise
    # (skipped for performance, can add later)

    # Save the image
    output_path = "src/g13_linux/gui/resources/images/g13_device.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")
    print(f"Dimensions: {KEYBOARD_WIDTH}x{KEYBOARD_HEIGHT}")

    return img


if __name__ == "__main__":
    create_g13_background()
