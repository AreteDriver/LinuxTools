"""
Event Decoder

Decodes G13 USB HID reports into button and joystick events.

CRITICAL: This module requires reverse engineering with physical G13 hardware.
The button mapping (BUTTON_MAP) is currently a stub and needs to be determined
through systematic testing by pressing each button and recording the raw USB data.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class G13ButtonState:
    """Represents decoded button and joystick states from a USB HID report"""
    g_buttons: int      # Bitmask for G1-G22 (bit 1-22)
    m_buttons: int      # Bitmask for M1-M3 (bit 1-3)
    joystick_x: int     # Analog X position (0-255)
    joystick_y: int     # Analog Y position (0-255)
    raw_data: bytes     # Original raw report for debugging


class EventDecoder:
    """
    Decodes G13 USB HID reports (64 bytes) into structured button/joystick data.

    IMPLEMENTATION STATUS: STUB - Requires hardware testing

    To complete this implementation:
    1. Run: python -m g13_ops.cli
    2. Press each button (G1-G22, M1-M3) individually
    3. Record the RAW output showing which bytes change
    4. Update BUTTON_MAP with correct (byte_index, bit_position) for each button
    5. Update JOYSTICK_X_BYTE and JOYSTICK_Y_BYTE with correct positions

    Reference implementation: https://github.com/ecraven/g13
    """

    # Button bit positions - TO BE DETERMINED via hardware testing
    # Format: 'button_id': (byte_index, bit_position)
    # Example: 'G1': (3, 0) means byte 3, bit 0
    BUTTON_MAP = {
        # G-keys (TO BE FILLED IN)
        # 'G1': (3, 0),
        # 'G2': (3, 1),
        # 'G3': (3, 2),
        # ... G4-G22

        # M-keys (TO BE FILLED IN)
        # 'M1': (2, 0),
        # 'M2': (2, 1),
        # 'M3': (2, 2),

        # MR key (if present)
        # 'MR': (2, 3),
    }

    # Joystick byte positions - TO BE VERIFIED
    JOYSTICK_X_BYTE = 4  # Placeholder - needs testing
    JOYSTICK_Y_BYTE = 5  # Placeholder - needs testing

    def __init__(self):
        self.last_state: G13ButtonState | None = None

    def decode_report(self, data: bytes | list) -> G13ButtonState:
        """
        Decode 64-byte HID report into structured data.

        Args:
            data: Raw 64-byte report from device

        Returns:
            Decoded button and joystick state

        Raises:
            ValueError: If data is not 64 bytes
        """
        # Convert list to bytes if needed
        if isinstance(data, list):
            data = bytes(data)

        if len(data) != 64:
            raise ValueError(f"Expected 64 bytes, got {len(data)}")

        # Decode button states
        g_buttons = self._decode_g_buttons(data)
        m_buttons = self._decode_m_buttons(data)

        # Decode joystick (if bytes are within range)
        joystick_x = data[self.JOYSTICK_X_BYTE] if len(data) > self.JOYSTICK_X_BYTE else 128
        joystick_y = data[self.JOYSTICK_Y_BYTE] if len(data) > self.JOYSTICK_Y_BYTE else 128

        state = G13ButtonState(
            g_buttons=g_buttons,
            m_buttons=m_buttons,
            joystick_x=joystick_x,
            joystick_y=joystick_y,
            raw_data=data
        )

        self.last_state = state
        return state

    def _decode_g_buttons(self, data: bytes) -> int:
        """
        Extract G1-G22 button states as bitmask.

        Returns:
            Integer bitmask where bit N represents button G{N}
        """
        result = 0

        # STUB IMPLEMENTATION - needs hardware testing
        # Iterate through BUTTON_MAP to extract bits
        for button_name, (byte_idx, bit_pos) in self.BUTTON_MAP.items():
            if button_name.startswith('G') and len(button_name) > 1:
                try:
                    button_num = int(button_name[1:])
                    if 1 <= button_num <= 22:
                        # Check if bit is set in the specified byte
                        if data[byte_idx] & (1 << bit_pos):
                            result |= (1 << button_num)
                except (ValueError, IndexError):
                    pass

        return result

    def _decode_m_buttons(self, data: bytes) -> int:
        """
        Extract M1-M3 button states as bitmask.

        Returns:
            Integer bitmask where bit N represents button M{N}
        """
        result = 0

        # STUB IMPLEMENTATION - needs hardware testing
        for button_name, (byte_idx, bit_pos) in self.BUTTON_MAP.items():
            if button_name.startswith('M') and len(button_name) > 1:
                try:
                    button_num = int(button_name[1:])
                    if 1 <= button_num <= 3:
                        if data[byte_idx] & (1 << bit_pos):
                            result |= (1 << button_num)
                except (ValueError, IndexError):
                    pass

        return result

    def get_pressed_buttons(self, state: G13ButtonState | None = None) -> List[str]:
        """
        Return list of currently pressed button names.

        Args:
            state: Button state to check (uses last_state if None)

        Returns:
            List of button IDs (e.g., ['G1', 'M2'])
        """
        if state is None:
            state = self.last_state

        if state is None:
            return []

        pressed = []

        # Check G buttons
        for i in range(1, 23):
            if state.g_buttons & (1 << i):
                pressed.append(f"G{i}")

        # Check M buttons
        for i in range(1, 4):
            if state.m_buttons & (1 << i):
                pressed.append(f"M{i}")

        return pressed

    def get_button_changes(self, new_state: G13ButtonState) -> Tuple[List[str], List[str]]:
        """
        Compare with previous state to detect button press/release events.

        Args:
            new_state: New button state

        Returns:
            Tuple of (pressed_buttons, released_buttons)
        """
        if self.last_state is None:
            # First state - consider all pressed buttons as new
            pressed = self.get_pressed_buttons(new_state)
            return (pressed, [])

        old_pressed = set(self.get_pressed_buttons(self.last_state))
        new_pressed = set(self.get_pressed_buttons(new_state))

        pressed = list(new_pressed - old_pressed)
        released = list(old_pressed - new_pressed)

        return (pressed, released)

    def analyze_raw_report(self, data: bytes) -> str:
        """
        Analyze raw report for reverse engineering.

        Returns human-readable hex dump for debugging.

        Args:
            data: 64-byte HID report

        Returns:
            Formatted hex string
        """
        if len(data) != 64:
            return f"Invalid length: {len(data)} bytes"

        lines = []
        lines.append("USB HID Report Analysis (64 bytes):")
        lines.append("=" * 60)

        # Show in groups of 16 bytes
        for i in range(0, 64, 16):
            chunk = data[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:04x}:  {hex_str}  {ascii_str}")

        lines.append("=" * 60)

        # Show non-zero bytes
        non_zero = [(i, b) for i, b in enumerate(data) if b != 0]
        if non_zero:
            lines.append("Non-zero bytes:")
            for idx, val in non_zero:
                lines.append(f"  Byte {idx:2d}: 0x{val:02x} ({val:3d}) = {bin(val)}")
        else:
            lines.append("All bytes are zero")

        return '\n'.join(lines)


# Helper function for testing/reverse engineering
def test_decoder_with_sample_data(sample_data: bytes):
    """
    Test function for analyzing sample HID reports.

    Usage:
        from g13_ops.gui.models.event_decoder import test_decoder_with_sample_data

        # Record output when pressing G1
        g1_data = bytes([...])
        test_decoder_with_sample_data(g1_data)
    """
    decoder = EventDecoder()

    print("Raw Data Analysis:")
    print(decoder.analyze_raw_report(sample_data))
    print()

    state = decoder.decode_report(sample_data)
    print("Decoded State:")
    print(f"  G-buttons bitmask: {state.g_buttons:022b}")
    print(f"  M-buttons bitmask: {state.m_buttons:03b}")
    print(f"  Joystick X: {state.joystick_x}")
    print(f"  Joystick Y: {state.joystick_y}")
    print(f"  Pressed buttons: {decoder.get_pressed_buttons(state)}")
