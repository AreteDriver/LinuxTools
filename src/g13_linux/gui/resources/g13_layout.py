"""
G13 Button Layout Geometry

Defines the visual positions and sizes of all G13 buttons for the GUI.
Coordinates based on 1024x1024 background image with auto-detected boxes.
"""

# Overall dimensions
KEYBOARD_WIDTH = 1024
KEYBOARD_HEIGHT = 1024

# Key sizing based on detected boxes
KEY_W = 32
KEY_H = 24
M_KEY_W = 31
M_KEY_H = 21
WIDE_KEY_W = 49


def _box(x, y, w, h):
    """Create position dict from x, y, width, height."""
    return {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}


# Button positions based on debug image analysis
# Standard G13 layout: G1-G14 top section, G15-G19 row 3, G20-G22 row 4
# Reference: g13_button_map_autodetect.json coordinates
G13_BUTTON_POSITIONS = {
    # M-keys row (small keys just below LCD)
    "M1": _box(419, 382, M_KEY_W, M_KEY_H),
    "M2": _box(456, 382, 32, 22),
    "M3": _box(495, 383, M_KEY_W, 23),
    "MR": _box(530, 383, M_KEY_W, 23),

    # G13 (left edge key) - moved left
    "G13": _box(350, 372, 51, 27),

    # G14 (right edge key) - moved right
    "G14": _box(590, 383, 33, 22),

    # Row 1: G1-G7 - G7 moved right
    "G1": _box(373, 422, 37, 27),
    "G2": _box(416, 427, 33, 25),
    "G3": _box(455, 428, 33, 26),
    "G4": _box(495, 431, 32, 24),
    "G5": _box(533, 430, 33, 24),
    "G6": _box(572, 428, 34, 25),
    "G7": _box(625, 424, 38, 27),

    # Row 2: G8-G12 - G12 moved right
    "G8": _box(397, 463, 50, 26),
    "G9": _box(452, 466, 34, 25),
    "G10": _box(493, 467, 33, 26),
    "G11": _box(534, 467, 33, 26),
    "G12": _box(590, 464, 49, 28),

    # Row 3: G15-G19
    "G15": _box(415, 491, 32, 24),
    "G16": _box(453, 493, 32, 24),
    "G17": _box(491, 495, 32, 24),
    "G18": _box(529, 493, 32, 24),
    "G19": _box(567, 491, 32, 24),

    # Row 4: G20-G22
    "G20": _box(438, 521, 40, 24),
    "G21": _box(484, 523, 40, 24),
    "G22": _box(530, 521, 40, 24),

    # Thumb buttons - adjusted positions
    "LEFT": _box(625, 530, 30, 28),
    "DOWN": _box(628, 575, 50, 30),

    # Joystick/STICK - on the thumbstick
    "STICK": _box(640, 525, 38, 38),
}

# Joystick area (for visual indicator)
JOYSTICK_AREA = {"x": 638, "y": 523, "width": 42, "height": 42}

# LCD display area
LCD_AREA = {"x": 410, "y": 340, "width": 200, "height": 60}
