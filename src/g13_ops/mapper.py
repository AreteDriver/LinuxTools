from evdev import UInput, ecodes as e

# TODO: fill this with real mappings once you decode the G13 report format
# Example: logical_button_id -> Linux key code
BUTTON_TO_KEY = {
    # 1: e.KEY_1,
    # 2: e.KEY_2,
}

class G13Mapper:
    def __init__(self):
        self.ui = UInput()

    def close(self):
        self.ui.close()

    def send_key(self, keycode):
        """Emit a single key press + release."""
        self.ui.write(e.EV_KEY, keycode, 1)
        self.ui.write(e.EV_KEY, keycode, 0)
        self.ui.syn()

    def handle_raw_report(self, data: bytes | list[int]):
        """
        Given a raw G13 report (list of bytes), decode which logical button
        changed and emit the mapped key, if any.
        """
        # TODO: decode data -> logical_button_id
        # For now, just print for debugging
        print("RAW:", list(data))
        # Example once you know mapping:
        # button_id = decode_button(data)
        # keycode = BUTTON_TO_KEY.get(button_id)
        # if keycode:
        #     self.send_key(keycode)

