"""
G13 Button Layout Geometry

Defines the visual positions and sizes of all G13 buttons for the GUI.
Coordinates are approximate based on G13 physical layout.
"""

# Button positions for visual layout
# Format: 'button_id': {'x': int, 'y': int, 'width': int, 'height': int}

G13_BUTTON_POSITIONS = {
    # Top row (G1-G5)
    'G1': {'x': 50, 'y': 50, 'width': 50, 'height': 40},
    'G2': {'x': 110, 'y': 50, 'width': 50, 'height': 40},
    'G3': {'x': 170, 'y': 50, 'width': 50, 'height': 40},
    'G4': {'x': 230, 'y': 50, 'width': 50, 'height': 40},
    'G5': {'x': 290, 'y': 50, 'width': 50, 'height': 40},

    # Second row (G6-G10)
    'G6': {'x': 50, 'y': 100, 'width': 50, 'height': 40},
    'G7': {'x': 110, 'y': 100, 'width': 50, 'height': 40},
    'G8': {'x': 170, 'y': 100, 'width': 50, 'height': 40},
    'G9': {'x': 230, 'y': 100, 'width': 50, 'height': 40},
    'G10': {'x': 290, 'y': 100, 'width': 50, 'height': 40},

    # Third row (G11-G14)
    'G11': {'x': 50, 'y': 150, 'width': 50, 'height': 40},
    'G12': {'x': 110, 'y': 150, 'width': 50, 'height': 40},
    'G13': {'x': 170, 'y': 150, 'width': 50, 'height': 40},
    'G14': {'x': 230, 'y': 150, 'width': 50, 'height': 40},

    # Fourth row (G15-G18)
    'G15': {'x': 50, 'y': 200, 'width': 50, 'height': 40},
    'G16': {'x': 110, 'y': 200, 'width': 50, 'height': 40},
    'G17': {'x': 170, 'y': 200, 'width': 50, 'height': 40},
    'G18': {'x': 230, 'y': 200, 'width': 50, 'height': 40},

    # Bottom row (G19-G22)
    'G19': {'x': 50, 'y': 250, 'width': 50, 'height': 40},
    'G20': {'x': 110, 'y': 250, 'width': 50, 'height': 40},
    'G21': {'x': 170, 'y': 250, 'width': 50, 'height': 40},
    'G22': {'x': 230, 'y': 250, 'width': 50, 'height': 40},

    # M-keys (mode keys) - right side
    'M1': {'x': 380, 'y': 50, 'width': 45, 'height': 35},
    'M2': {'x': 380, 'y': 95, 'width': 45, 'height': 35},
    'M3': {'x': 380, 'y': 140, 'width': 45, 'height': 35},

    # MR key (record macro)
    'MR': {'x': 380, 'y': 185, 'width': 45, 'height': 35},
}

# Joystick area (drawn separately, not a button)
JOYSTICK_AREA = {'x': 450, 'y': 200, 'width': 100, 'height': 100}

# LCD display area
LCD_AREA = {'x': 500, 'y': 30, 'width': 160, 'height': 43}

# Overall keyboard dimensions
KEYBOARD_WIDTH = 700
KEYBOARD_HEIGHT = 350
