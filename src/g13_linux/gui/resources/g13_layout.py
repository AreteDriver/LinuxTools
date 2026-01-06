"""
G13 Button Layout Geometry

Defines the visual positions and sizes of all G13 buttons for the GUI.
Coordinates match the device background image (962x1280 pixels).

Button positions are carefully aligned to the actual G13 device image
so that the semi-transparent button overlays sit precisely over the
physical button locations.
"""

G13_BUTTON_POSITIONS = {
    # M-keys row (below LCD, horizontal row of mode buttons)
    # These are the smaller rectangular buttons: M1, M2, M3, MR
    "M1": {"x": 225, "y": 268, "width": 58, "height": 28},
    "M2": {"x": 295, "y": 268, "width": 58, "height": 28},
    "M3": {"x": 365, "y": 268, "width": 58, "height": 28},
    "MR": {"x": 435, "y": 268, "width": 58, "height": 28},

    # G-keys Row 1 (G1-G7) - top row of main keys, curved layout
    # Keys curve down at edges (G1 and G7 are lower than center keys)
    "G1": {"x": 192, "y": 300, "width": 58, "height": 48},
    "G2": {"x": 258, "y": 300, "width": 58, "height": 48},
    "G3": {"x": 324, "y": 300, "width": 58, "height": 48},
    "G4": {"x": 390, "y": 300, "width": 58, "height": 48},
    "G5": {"x": 456, "y": 300, "width": 58, "height": 48},
    "G6": {"x": 522, "y": 300, "width": 58, "height": 48},
    "G7": {"x": 588, "y": 300, "width": 58, "height": 48},

    # G-keys Row 2 (G8-G14) - second row, also curved
    "G8": {"x": 192, "y": 356, "width": 58, "height": 48},
    "G9": {"x": 258, "y": 356, "width": 58, "height": 48},
    "G10": {"x": 324, "y": 356, "width": 58, "height": 48},
    "G11": {"x": 390, "y": 356, "width": 58, "height": 48},
    "G12": {"x": 456, "y": 356, "width": 58, "height": 48},
    "G13": {"x": 522, "y": 356, "width": 58, "height": 48},
    "G14": {"x": 588, "y": 356, "width": 58, "height": 48},

    # G-keys Row 3 (G15-G19) - third row, 5 keys only
    "G15": {"x": 238, "y": 412, "width": 62, "height": 48},
    "G16": {"x": 308, "y": 412, "width": 62, "height": 48},
    "G17": {"x": 378, "y": 412, "width": 62, "height": 48},
    "G18": {"x": 448, "y": 412, "width": 62, "height": 48},
    "G19": {"x": 518, "y": 412, "width": 62, "height": 48},

    # G-keys Row 4 (G20-G22) - bottom row, 3 wider keys
    "G20": {"x": 288, "y": 465, "width": 72, "height": 52},
    "G21": {"x": 372, "y": 465, "width": 72, "height": 52},
    "G22": {"x": 456, "y": 465, "width": 72, "height": 52},

    # Thumb buttons (beside joystick on bottom-right palm rest)
    "LEFT": {"x": 500, "y": 545, "width": 52, "height": 42},
    "DOWN": {"x": 500, "y": 595, "width": 52, "height": 42},

    # Joystick click (STICK) - center of joystick area
    "STICK": {"x": 565, "y": 555, "width": 60, "height": 60},
}

# Joystick area (for visual indicator drawing)
# The thumbstick is at the bottom-right palm rest area
JOYSTICK_AREA = {"x": 555, "y": 545, "width": 85, "height": 85}

# LCD display area (green screen at top of device)
# 160x43 pixel monochrome display
LCD_AREA = {"x": 205, "y": 110, "width": 360, "height": 130}

# Overall dimensions matching the device image
KEYBOARD_WIDTH = 962
KEYBOARD_HEIGHT = 1280
