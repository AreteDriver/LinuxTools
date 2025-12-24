"""
G13 Backlight Control

Controls the G13's RGB backlight.

STATUS: STUB IMPLEMENTATION
TODO: Implement USB HID commands for backlight control
Reference: libg13 project for backlight protocol
"""


class G13Backlight:
    """RGB backlight controller for G13"""

    def __init__(self, device_handle=None):
        """
        Initialize backlight controller.

        Args:
            device_handle: USB device handle from hidapi
        """
        self.device = device_handle
        self._current_color = (255, 255, 255)  # Default white
        self._current_brightness = 100

    def set_color(self, r: int, g: int, b: int):
        """
        Set RGB backlight color.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)

        TODO: Implement USB HID feature report for color
        """
        if not all(0 <= val <= 255 for val in (r, g, b)):
            raise ValueError("RGB values must be 0-255")

        self._current_color = (r, g, b)
        print(f"[Backlight STUB] Set color: RGB({r}, {g}, {b})")

    def set_color_hex(self, color_hex: str):
        """
        Set color from hex string.

        Args:
            color_hex: Color in #RRGGBB format
        """
        color_hex = color_hex.lstrip('#')
        if len(color_hex) != 6:
            raise ValueError("Hex color must be in #RRGGBB format")

        try:
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            self.set_color(r, g, b)
        except ValueError:
            raise ValueError("Invalid hex color format")

    def set_brightness(self, brightness: int):
        """
        Set brightness level.

        Args:
            brightness: Brightness (0-100)

        TODO: Implement brightness control
        - May need to scale RGB values
        - Or use separate brightness command if supported
        """
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be 0-100")

        self._current_brightness = brightness
        print(f"[Backlight STUB] Set brightness: {brightness}%")

    def get_color(self) -> tuple[int, int, int]:
        """Get current RGB color"""
        return self._current_color

    def get_brightness(self) -> int:
        """Get current brightness"""
        return self._current_brightness
