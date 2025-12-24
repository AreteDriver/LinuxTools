"""
G13 LCD Control

Controls the G13's 160x43 monochrome LCD display.

STATUS: STUB IMPLEMENTATION
TODO: Implement USB HID control transfers for LCD
Reference: libg13 project for LCD protocol
"""


class G13LCD:
    """LCD display controller for G13 (160x43 monochrome)"""

    WIDTH = 160
    HEIGHT = 43

    def __init__(self, device_handle=None):
        """
        Initialize LCD controller.

        Args:
            device_handle: USB device handle from hidapi
        """
        self.device = device_handle

    def clear(self):
        """
        Clear LCD display.

        TODO: Implement USB control transfer to clear LCD
        """
        print("[LCD STUB] Clear display")

    def write_text(self, text: str, x: int = 0, y: int = 0):
        """
        Write text to LCD.

        Args:
            text: Text to display
            x: X position (0-159)
            y: Y position (0-42)

        TODO: Implement text rendering and USB transfer
        - Need bitmap font
        - Convert text to pixels
        - Send to device via USB
        """
        print(f"[LCD STUB] Display text: '{text}' at ({x}, {y})")

    def write_bitmap(self, bitmap: bytes):
        """
        Write raw bitmap to LCD.

        Args:
            bitmap: 160x43 monochrome bitmap

        TODO: Implement USB transfer protocol
        - Bitmap should be WIDTH * HEIGHT // 8 bytes
        - Send via USB HID feature report
        """
        expected_size = (self.WIDTH * self.HEIGHT) // 8
        if len(bitmap) != expected_size:
            raise ValueError(f"Invalid bitmap size: expected {expected_size} bytes, got {len(bitmap)}")

        print(f"[LCD STUB] Display bitmap: {len(bitmap)} bytes")

    def set_brightness(self, level: int):
        """
        Set LCD brightness.

        Args:
            level: Brightness level (0-100)

        TODO: Implement brightness control if supported
        """
        if not 0 <= level <= 100:
            raise ValueError("Brightness must be 0-100")

        print(f"[LCD STUB] Set brightness: {level}%")
