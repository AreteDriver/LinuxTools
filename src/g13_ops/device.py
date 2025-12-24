import hid

G13_VENDOR_ID = 0x046d
G13_PRODUCT_ID = 0xc21c

def open_g13():
    for dev in hid.enumerate():
        if dev["vendor_id"] == G13_VENDOR_ID and dev["product_id"] == G13_PRODUCT_ID:
            h = hid.device()
            h.open_path(dev["path"])
            h.set_nonblocking(True)
            return h
    raise RuntimeError("Logitech G13 not found")

def read_event(handle):
    data = handle.read(64)
    return data if data else None

