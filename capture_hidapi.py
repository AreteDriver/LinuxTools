#!/usr/bin/env python3
"""Capture using hidapi with blocking reads"""
import hid
import time
import sys

print("=" * 70)
print("G13 BUTTON CAPTURE - Using hidapi")
print("=" * 70)

# Find G13
devices = hid.enumerate(0x046d, 0xc21c)
if not devices:
    print("ERROR: No G13 device found!")
    sys.exit(1)

print(f"\nFound {len(devices)} G13 interface(s):")
for i, dev in enumerate(devices):
    print(f"  {i+1}. Path: {dev['path']}")
    print(f"     Interface: {dev['interface_number']}")
    print(f"     Usage Page: {dev['usage_page']:#06x}")
    print(f"     Usage: {dev['usage']:#06x}")

# Try each interface
for i, dev in enumerate(devices):
    print(f"\n{'='*70}")
    print(f"Trying interface {i+1}: {dev['path']}")
    print("=" * 70)

    try:
        h = hid.device()
        h.open_path(dev["path"])

        print("✓ Device opened!")
        print(f"  Manufacturer: {h.get_manufacturer_string()}")
        print(f"  Product: {h.get_product_string()}")

        # Set NON-blocking mode
        h.set_nonblocking(0)  # Blocking reads

        print("\nWaiting for button presses (20 seconds)...")
        print("PRESS BUTTONS NOW!")
        print("-" * 70)

        start_time = time.time()
        event_count = 0

        while time.time() - start_time < 20:
            # Blocking read with 100ms timeout
            data = h.read(64, timeout_ms=100)

            if data:
                event_count += 1
                print(f"\n[Event #{event_count}] {time.strftime('%H:%M:%S')}")
                print(f"RAW ({len(data)} bytes): {' '.join(f'{b:02x}' for b in data)}")

                # Show non-zero bytes
                non_zero = [(idx, b) for idx, b in enumerate(data) if b != 0]
                if non_zero:
                    print("Non-zero bytes:")
                    for idx, val in non_zero:
                        binary = bin(val)[2:].zfill(8)
                        print(f"  Byte[{idx:2d}] = 0x{val:02x} ({val:3d}) = {binary}")

        h.close()

        print(f"\n{'='*70}")
        print(f"Interface {i+1} test complete. Events captured: {event_count}")
        print("=" * 70)

        if event_count > 0:
            print("\n✓✓✓ SUCCESS! This interface receives button data!")
            break

    except IOError as e:
        print(f"✗ Cannot open: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\nDone!")
