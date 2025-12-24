from evdev import UInput, ecodes as e

# TODO: fill this with real mappings once you decode the G13 report format
# Example: logical_button_id -> Linux key code
BUTTON_TO_KEY = {
    # 1: e.KEY_1,
    # 2: e.KEY_2,
}


class G13Mapper:
    """
    G13 event mapper - converts button presses to keyboard events.

    Enhanced to support profile loading from GUI.
    """

    def __init__(self):
        self.ui = UInput()
        self.button_map = {}  # button_id (str) -> evdev keycode (int)

    def close(self):
        self.ui.close()

    def load_profile(self, profile_data: dict):
        """
        Load button mappings from profile.

        Args:
            profile_data: Profile dict with 'mappings' key
                         Format: {'G1': 'KEY_1', 'G2': 'KEY_ESCAPE', ...}
        """
        self.button_map = {}
        mappings = profile_data.get('mappings', {})

        for button_id, key_name in mappings.items():
            # Convert KEY_* string to evdev keycode
            if hasattr(e, key_name):
                keycode = getattr(e, key_name)
                self.button_map[button_id] = keycode

    def handle_button_event(self, button_id: str, is_pressed: bool):
        """
        Handle decoded button event from GUI.

        Args:
            button_id: Button identifier (e.g., 'G1', 'M1')
            is_pressed: True if pressed, False if released
        """
        if button_id in self.button_map:
            keycode = self.button_map[button_id]
            state = 1 if is_pressed else 0
            self.ui.write(e.EV_KEY, keycode, state)
            self.ui.syn()

    def send_key(self, keycode):
        """Emit a single key press + release."""
        self.ui.write(e.EV_KEY, keycode, 1)
        self.ui.write(e.EV_KEY, keycode, 0)
        self.ui.syn()

    def handle_raw_report(self, data: bytes | list[int]):
        """
        Given a raw G13 report (list of bytes), decode which logical button
        changed and emit the mapped key, if any.

        NOTE: This is the legacy CLI interface. The GUI uses handle_button_event instead.
        """
        # TODO: decode data -> logical_button_id
        # For now, just print for debugging
        print("RAW:", list(data))
        # Example once you know mapping:
        # button_id = decode_button(data)
        # keycode = BUTTON_TO_KEY.get(button_id)
        # if keycode:
        #     self.send_key(keycode)

