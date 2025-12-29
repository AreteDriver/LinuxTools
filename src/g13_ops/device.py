import os
import glob
import fcntl

G13_VENDOR_ID = 0x046d
G13_PRODUCT_ID = 0xc21c


def _hidiocsfeature(length):
    """HIDIOCSFEATURE ioctl for setting feature reports."""
    return 0xC0004806 | (length << 16)


def _hidiocgfeature(length):
    """HIDIOCGFEATURE ioctl for getting feature reports."""
    return 0xC0004807 | (length << 16)


class HidrawDevice:
    """Wrapper for hidraw device file to provide consistent interface."""

    def __init__(self, path):
        self.path = path
        self._fd = None
        self._file = None

    def open(self):
        self._file = open(self.path, 'rb+', buffering=0)
        self._fd = self._file.fileno()
        os.set_blocking(self._fd, False)

    def read(self, size):
        try:
            data = self._file.read(size)
            return list(data) if data else None
        except BlockingIOError:
            return None

    def write(self, data):
        """Write an output report to the device."""
        return self._file.write(bytes(data))

    def send_feature_report(self, data):
        """
        Send a HID feature report to the device.

        Args:
            data: Report data (first byte should be report ID)

        Returns:
            Number of bytes written
        """
        if self._fd is None:
            raise RuntimeError("Device not open")

        buf = bytes(data)
        return fcntl.ioctl(self._fd, _hidiocsfeature(len(buf)), buf)

    def get_feature_report(self, report_id, size):
        """
        Get a HID feature report from the device.

        Args:
            report_id: Report ID to request
            size: Expected report size

        Returns:
            Report data as bytes
        """
        if self._fd is None:
            raise RuntimeError("Device not open")

        buf = bytearray(size)
        buf[0] = report_id
        fcntl.ioctl(self._fd, _hidiocgfeature(size), buf)
        return bytes(buf)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None
            self._fd = None


def find_g13_hidraw():
    """Find the hidraw device path for the G13."""
    for hidraw in glob.glob('/sys/class/hidraw/hidraw*'):
        uevent_path = os.path.join(hidraw, 'device', 'uevent')
        try:
            with open(uevent_path, 'r') as f:
                content = f.read()
                # Check for G13 HID_ID (format: 0003:0000046D:0000C21C)
                if '0000046D' in content.upper() and '0000C21C' in content.upper():
                    device_name = os.path.basename(hidraw)
                    return f'/dev/{device_name}'
        except (IOError, OSError):
            continue
    return None


def open_g13():
    """Open the G13 device and return a handle."""
    hidraw_path = find_g13_hidraw()
    if not hidraw_path:
        raise RuntimeError("Logitech G13 not found")

    device = HidrawDevice(hidraw_path)
    device.open()
    return device


def read_event(handle):
    """Read a HID report from the device."""
    data = handle.read(64)
    return data if data else None
