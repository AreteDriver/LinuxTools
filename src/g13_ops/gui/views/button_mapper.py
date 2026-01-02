"""
Button Mapper Widget

Visual G13 keyboard layout with clickable buttons.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from ..widgets.g13_button import G13Button
from ..resources.g13_layout import (
    G13_BUTTON_POSITIONS,
    LCD_AREA,
    JOYSTICK_AREA,
    KEYBOARD_WIDTH,
    KEYBOARD_HEIGHT,
)
import os


class ButtonMapperWidget(QWidget):
    """Visual G13 keyboard layout with clickable buttons"""

    button_clicked = pyqtSignal(str)  # Button ID clicked for configuration

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(KEYBOARD_WIDTH, KEYBOARD_HEIGHT)
        self.buttons = {}
        self.background_image = self._load_background_image()
        self._init_buttons()
        # Joystick position (0-255 for X and Y, 128 = center)
        self._joystick_x = 128
        self._joystick_y = 128

    def _load_background_image(self):
        """Load G13 layout background image if available"""
        # Try to find the image in the resources directory
        possible_paths = [
            os.path.join(
                os.path.dirname(__file__), "..", "resources", "images", "g13_layout.png"
            ),
            os.path.join(
                os.path.dirname(__file__), "..", "resources", "images", "g13_layout.jpg"
            ),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Scale to fit our widget dimensions while maintaining aspect ratio
                    return pixmap.scaled(
                        KEYBOARD_WIDTH,
                        KEYBOARD_HEIGHT,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
        return None

    def _init_buttons(self):
        """Create all G13 buttons based on layout"""
        for button_id, position in G13_BUTTON_POSITIONS.items():
            btn = G13Button(button_id, self)
            btn.setGeometry(
                position["x"], position["y"], position["width"], position["height"]
            )
            btn.clicked.connect(
                lambda checked=False, bid=button_id: self.button_clicked.emit(bid)
            )
            self.buttons[button_id] = btn

    def set_button_mapping(self, button_id: str, key_name: str):
        """Update button label with mapped key"""
        if button_id in self.buttons:
            self.buttons[button_id].set_mapping(key_name)

    def highlight_button(self, button_id: str, highlight: bool):
        """Highlight button when physically pressed"""
        if button_id in self.buttons:
            self.buttons[button_id].set_highlighted(highlight)

    def clear_all_highlights(self):
        """Clear all button highlights"""
        for btn in self.buttons.values():
            btn.set_highlighted(False)

    def update_joystick(self, x: int, y: int):
        """Update joystick position indicator (0-255 for each axis)"""
        self._joystick_x = x
        self._joystick_y = y
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Draw G13 keyboard layout - background image or simple outline"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.background_image:
            # Draw the background image
            painter.drawPixmap(0, 0, self.background_image)
        else:
            # Fallback: Draw simple keyboard outline and LCD area
            pen = QPen(QColor(100, 100, 100), 2)
            painter.setPen(pen)
            painter.drawRoundedRect(
                10, 10, KEYBOARD_WIDTH - 20, KEYBOARD_HEIGHT - 20, 10, 10
            )

            # Draw LCD area
            painter.setPen(QPen(QColor(50, 150, 50), 2))
            painter.drawRect(
                LCD_AREA["x"], LCD_AREA["y"], LCD_AREA["width"], LCD_AREA["height"]
            )

            # LCD label
            painter.setFont(QFont("Arial", 8))
            painter.drawText(LCD_AREA["x"] + 5, LCD_AREA["y"] + 15, "LCD (160x43)")

        # Draw joystick position indicator
        self._draw_joystick_indicator(painter)

    def _draw_joystick_indicator(self, painter: QPainter):
        """Draw a dot showing current joystick position"""
        # Joystick area center and radius
        center_x = JOYSTICK_AREA["x"] + JOYSTICK_AREA["width"] // 2
        center_y = JOYSTICK_AREA["y"] + JOYSTICK_AREA["height"] // 2
        radius = min(JOYSTICK_AREA["width"], JOYSTICK_AREA["height"]) // 2 - 10

        # Draw joystick boundary circle
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QColor(40, 40, 40, 100))
        painter.drawEllipse(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2
        )

        # Map joystick position (0-255) to pixel offset from center
        # 128 = center, 0 = full left/up, 255 = full right/down
        offset_x = int((self._joystick_x - 128) / 128 * (radius - 8))
        offset_y = int((self._joystick_y - 128) / 128 * (radius - 8))

        # Draw joystick position dot
        dot_x = center_x + offset_x
        dot_y = center_y + offset_y
        dot_radius = 12

        # Color based on distance from center (green = center, red = edge)
        distance = (offset_x**2 + offset_y**2) ** 0.5
        max_distance = radius - 8
        intensity = min(distance / max_distance, 1.0) if max_distance > 0 else 0
        color = QColor(
            int(100 + 155 * intensity),  # Red increases
            int(200 - 100 * intensity),  # Green decreases
            100
        )

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(color)
        painter.drawEllipse(
            dot_x - dot_radius, dot_y - dot_radius,
            dot_radius * 2, dot_radius * 2
        )
