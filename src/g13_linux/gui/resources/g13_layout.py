"""
G13 Button Layout Geometry

Defines the visual positions and sizes of all G13 buttons for the GUI.
Coordinates match the device background image (520x700 pixels).

Keys are arranged in curved arcs matching the real G13 ergonomic layout.
Outer keys on each row are positioned lower and angled outward.
"""

# Overall dimensions
KEYBOARD_WIDTH = 520
KEYBOARD_HEIGHT = 700

# Key sizing
KEY_W = 46  # Standard G-key width
KEY_H = 40  # Standard G-key height
M_KEY_W = 38  # M-key width
M_KEY_H = 18  # M-key height

# Convert center coords to top-left for Qt buttons
def _c(cx, cy, w, h):
    """Convert center (cx, cy) to top-left dict."""
    return {"x": int(cx - w/2), "y": int(cy - h/2), "width": w, "height": h}

# Row base Y positions
ROW1_Y = 185
ROW2_Y = 240
ROW3_Y = 295
ROW4_Y = 355

# Curved row offsets (outer keys lower)
CURVE_7 = [18, 8, 2, 0, 2, 8, 18]  # For 7-key rows
CURVE_5 = [12, 4, 0, 4, 12]        # For 5-key row

G13_BUTTON_POSITIONS = {
    # M-keys row (below LCD)
    "M1": _c(185, 130, M_KEY_W, M_KEY_H),
    "M2": _c(230, 130, M_KEY_W, M_KEY_H),
    "M3": _c(275, 130, M_KEY_W, M_KEY_H),
    "MR": _c(320, 130, M_KEY_W, M_KEY_H),

    # G-keys Row 1 (G1-G7) - curved arc
    "G1": _c(95,  ROW1_Y + 18, KEY_W, KEY_H),
    "G2": _c(148, ROW1_Y + 8,  KEY_W, KEY_H),
    "G3": _c(201, ROW1_Y + 2,  KEY_W, KEY_H),
    "G4": _c(254, ROW1_Y,      KEY_W, KEY_H),
    "G5": _c(307, ROW1_Y + 2,  KEY_W, KEY_H),
    "G6": _c(360, ROW1_Y + 8,  KEY_W, KEY_H),
    "G7": _c(413, ROW1_Y + 18, KEY_W, KEY_H),

    # G-keys Row 2 (G8-G14)
    "G8":  _c(95,  ROW2_Y + 18, KEY_W, KEY_H),
    "G9":  _c(148, ROW2_Y + 8,  KEY_W, KEY_H),
    "G10": _c(201, ROW2_Y + 2,  KEY_W, KEY_H),
    "G11": _c(254, ROW2_Y,      KEY_W, KEY_H),
    "G12": _c(307, ROW2_Y + 2,  KEY_W, KEY_H),
    "G13": _c(360, ROW2_Y + 8,  KEY_W, KEY_H),
    "G14": _c(413, ROW2_Y + 18, KEY_W, KEY_H),

    # G-keys Row 3 (G15-G19) - 5 keys
    "G15": _c(135, ROW3_Y + 12, KEY_W, KEY_H),
    "G16": _c(190, ROW3_Y + 4,  KEY_W, KEY_H),
    "G17": _c(245, ROW3_Y,      KEY_W, KEY_H),
    "G18": _c(300, ROW3_Y + 4,  KEY_W, KEY_H),
    "G19": _c(355, ROW3_Y + 12, KEY_W, KEY_H),

    # G-keys Row 4 (G20-G22) - 3 wider keys
    "G20": _c(175, ROW4_Y + 6, 60, 46),
    "G21": _c(245, ROW4_Y,     60, 46),
    "G22": _c(315, ROW4_Y + 6, 60, 46),

    # Thumb buttons
    "LEFT": _c(265, 480, 48, 36),
    "DOWN": _c(265, 530, 48, 36),

    # Joystick click
    "STICK": _c(385, 520, 44, 44),
}

# Joystick area (for visual indicator)
JOYSTICK_AREA = {"x": 337, "y": 472, "width": 96, "height": 96}

# LCD display area
LCD_AREA = {"x": 150, "y": 40, "width": 220, "height": 70}
