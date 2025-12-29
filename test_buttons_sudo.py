#!/usr/bin/env python3
"""
G13 Button Test - Requires sudo

This script uses libusb to read button/joystick input from the G13.
The kernel's hid-generic driver must be detached, which requires root.

Usage:
    sudo .venv/bin/python test_buttons_sudo.py
"""
import sys
import time

sys.path.insert(0, 'src')

from g13_ops.device import open_g13_libusb
from g13_ops.gui.models.event_decoder import EventDecoder

print("=" * 60)
print("G13 Button Test (using libusb - requires sudo)")
print("=" * 60)
print()

try:
    print("Opening G13 via libusb...")
    device = open_g13_libusb()
    print("Device opened successfully!")
    print()
    print("Press G13 buttons now! (30 second test)")
    print("-" * 60)
    print()

    decoder = EventDecoder()
    start_time = time.time()

    while time.time() - start_time < 30:
        data = device.read(timeout_ms=100)
        if data and len(data) >= 8:
            # Decode the report
            state = decoder.decode_report(bytes(data))
            pressed, released = decoder.get_button_changes(state)

            # Show press/release events
            for btn in pressed:
                print(f"  PRESSED:  {btn}")
            for btn in released:
                print(f"  RELEASED: {btn}")

            # Show joystick if moved
            if abs(state.joystick_x - 128) > 20 or abs(state.joystick_y - 128) > 20:
                print(f"  JOYSTICK: X={state.joystick_x:3d} Y={state.joystick_y:3d}")

    print()
    print("-" * 60)
    print("Test complete!")

except RuntimeError as e:
    print(f"Error: {e}")
    if "Access denied" in str(e) or "permission" in str(e).lower():
        print("\nTry running with sudo:")
        print("  sudo .venv/bin/python test_buttons_sudo.py")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nInterrupted")
finally:
    try:
        device.close()
        print("Device closed, kernel driver reattached")
    except:
        pass
