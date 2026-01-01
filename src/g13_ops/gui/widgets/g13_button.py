"""
G13 Button Widget

Custom QPushButton representing a single G13 button.
"""

try:
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtCore import Qt, pyqtSignal
except ImportError:
    # Stub for development without PyQt6
    class QPushButton:
        def __init__(self, *args, **kwargs):
            pass

    class Qt:
        pass

    def pyqtSignal(*args):
        return None


class G13Button(QPushButton):
    """Individual G13 button widget"""

    def __init__(self, button_id: str, parent=None):
        super().__init__(button_id, parent)
        self.button_id = button_id
        self.mapped_key = None
        self.is_highlighted = False
        self._update_style()

    def set_mapping(self, key_name: str | dict | None):
        """
        Set the mapped key and update display.

        Args:
            key_name: Key code name (e.g., 'KEY_1'), combo dict, or None to clear
                      Combo format: {'keys': ['KEY_LEFTCTRL', 'KEY_B'], 'label': '...'}
        """
        self.mapped_key = key_name

        if key_name is None or key_name == "KEY_RESERVED":
            display_text = self.button_id
        elif isinstance(key_name, dict):
            # Combo key format
            label = key_name.get("label", "")
            keys = key_name.get("keys", [])
            if label:
                display_text = f"{self.button_id}\n{label}"
            elif keys:
                # Show abbreviated key combo
                short_keys = [k.replace("KEY_", "") for k in keys]
                display_text = f"{self.button_id}\n{'+'.join(short_keys)}"
            else:
                display_text = self.button_id
        else:
            # Simple key format
            display_key = key_name.replace("KEY_", "")
            display_text = f"{self.button_id}\n{display_key}"

        self.setText(display_text)
        self._update_style()

    def set_highlighted(self, highlight: bool):
        """
        Highlight button when physically pressed.

        Args:
            highlight: True to highlight, False to unhighlight
        """
        self.is_highlighted = highlight
        self._update_style()

    def _has_mapping(self) -> bool:
        """Check if button has a valid mapping."""
        if not self.mapped_key:
            return False
        if self.mapped_key == "KEY_RESERVED":
            return False
        if isinstance(self.mapped_key, dict):
            return bool(self.mapped_key.get("keys"))
        return True

    def _update_style(self):
        """Update button appearance based on state"""
        if self.is_highlighted:
            # Green when physically pressed (more opaque)
            bg_color = "rgba(76, 175, 80, 0.85)"
            border_color = "#81C784"
        elif self._has_mapping():
            # Blue when mapped to a key (semi-transparent)
            bg_color = "rgba(33, 150, 243, 0.6)"
            border_color = "#64B5F6"
        else:
            # Gray when unmapped (very transparent)
            bg_color = "rgba(117, 117, 117, 0.4)"
            border_color = "#BDBDBD"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 2px solid {border_color};
                border-radius: 5px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 3px solid #FFC107;
                background-color: rgba(255, 193, 7, 0.5);
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.5);
            }}
        """)

    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color for hover effect"""
        # Simple lightening by blending with white
        color = hex_color.lstrip("#")
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for pressed effect"""
        color = hex_color.lstrip("#")
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        return f"#{r:02x}{g:02x}{b:02x}"
