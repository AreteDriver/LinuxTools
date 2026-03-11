"""Global keyboard shortcuts for LikX."""

import logging
import os
import subprocess
from typing import Callable, Dict, List, Tuple


class HotkeyManager:
    """Manages global keyboard shortcuts."""

    # Base path for LikX custom keybindings
    GNOME_SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"
    GNOME_BASE_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"

    def __init__(self):
        # key_id -> (callback, command)
        self.hotkeys: Dict[str, Tuple[Callable, str]] = {}
        self.desktop_env = self._detect_desktop_environment()
        self._registered_paths: List[str] = []

    def _detect_desktop_environment(self) -> str:
        """Detect the current desktop environment."""
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

        if "gnome" in desktop:
            return "gnome"
        elif "kde" in desktop or "plasma" in desktop:
            return "kde"
        elif "xfce" in desktop:
            return "xfce"
        elif "mate" in desktop:
            return "mate"
        else:
            return "unknown"

    def register_hotkey(
        self, key_combo: str, callback: Callable, command: str, hotkey_id: str = ""
    ) -> bool:
        """Register a global hotkey.

        Args:
            key_combo: Key combination (e.g., '<Control><Shift>F')
            callback: Function to call when hotkey is pressed
            command: Command to execute
            hotkey_id: Unique identifier for this hotkey (e.g., 'fullscreen', 'region')

        Returns:
            True if registration successful
        """
        # Generate ID from command if not provided
        if not hotkey_id:
            if "--" in command:
                hotkey_id = command.split("--")[-1].split()[0]
            else:
                hotkey_id = "default"

        self.hotkeys[hotkey_id] = (callback, command)

        if self.desktop_env == "gnome":
            return self._register_gnome_hotkey(key_combo, command, hotkey_id)
        elif self.desktop_env == "kde":
            return self._register_kde_hotkey(key_combo, command, hotkey_id)

        return False

    def _register_gnome_hotkey(self, key_combo: str, command: str, hotkey_id: str) -> bool:
        """Register hotkey in GNOME with unique path per hotkey."""
        try:
            # Create unique path for this hotkey
            custom_path = f"{self.GNOME_BASE_PATH}/likx-{hotkey_id}/"

            # Get current custom keybindings
            result = subprocess.run(
                ["gsettings", "get", self.GNOME_SCHEMA, "custom-keybindings"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                current = result.stdout.strip()
                if custom_path not in current:
                    # Add our custom path
                    if current == "@as []":
                        new_value = f"['{custom_path}']"
                    else:
                        # Parse existing and add
                        new_value = current.rstrip("]") + f", '{custom_path}']"

                    subprocess.run(
                        [
                            "gsettings",
                            "set",
                            self.GNOME_SCHEMA,
                            "custom-keybindings",
                            new_value,
                        ],
                        timeout=5,
                    )

                # Set the binding properties
                binding_schema = f"{self.GNOME_SCHEMA}.custom-keybinding:{custom_path}"
                name = f"LikX {hotkey_id.replace('-', ' ').title()}"

                subprocess.run(["gsettings", "set", binding_schema, "name", name], timeout=5)
                subprocess.run(["gsettings", "set", binding_schema, "command", command], timeout=5)
                subprocess.run(
                    ["gsettings", "set", binding_schema, "binding", key_combo], timeout=5
                )

                if custom_path not in self._registered_paths:
                    self._registered_paths.append(custom_path)

                return True
        except Exception as e:
            logging.warning("Failed to register GNOME hotkey '%s': %s", hotkey_id, e)

        return False

    def _register_kde_hotkey(self, key_combo: str, command: str, hotkey_id: str) -> bool:
        """Register hotkey in KDE Plasma via custom .desktop shortcut files.

        Creates a .desktop file in ~/.local/share/kglobalaccel/ and registers
        the shortcut via kwriteconfig5/kwriteconfig6.
        """
        try:
            from pathlib import Path

            # Convert GTK accelerator to KDE format
            kde_combo = self._gtk_to_kde_shortcut(key_combo)
            if not kde_combo:
                return False

            # Write a .desktop service file for the action
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            desktop_file = desktop_dir / f"likx-{hotkey_id}.desktop"
            desktop_file.write_text(
                f"[Desktop Entry]\n"
                f"Type=Application\n"
                f"Name=LikX {hotkey_id.replace('-', ' ').title()}\n"
                f"Exec={command}\n"
                f"NoDisplay=true\n"
                f"X-KDE-GlobalAccel={kde_combo}\n",
                encoding="utf-8",
            )

            # Try kwriteconfig6 first (Plasma 6), fallback to kwriteconfig5
            config_tool = self._find_kde_config_tool()
            if not config_tool:
                return False

            # Register in kglobalshortcutsrc
            service_name = f"likx-{hotkey_id}.desktop"
            result = subprocess.run(
                [
                    config_tool,
                    "--file",
                    "kglobalshortcutsrc",
                    "--group",
                    service_name,
                    "--key",
                    "_launch",
                    f"{kde_combo},none,LikX {hotkey_id.replace('-', ' ').title()}",
                ],
                capture_output=True,
                timeout=5,
            )

            if result.returncode == 0:
                if hotkey_id not in self._registered_paths:
                    self._registered_paths.append(hotkey_id)
                return True
        except Exception as e:
            logging.warning("Failed to register KDE hotkey '%s': %s", hotkey_id, e)

        return False

    @staticmethod
    def _gtk_to_kde_shortcut(gtk_combo: str) -> str:
        """Convert GTK accelerator format to KDE shortcut format.

        Example: '<Super><Shift>S' -> 'Meta+Shift+S'
        """
        mapping = {
            "<Control>": "Ctrl+",
            "<Ctrl>": "Ctrl+",
            "<Shift>": "Shift+",
            "<Alt>": "Alt+",
            "<Super>": "Meta+",
            "<Meta>": "Meta+",
        }

        result = gtk_combo
        for gtk_mod, kde_mod in mapping.items():
            result = result.replace(gtk_mod, kde_mod)

        # Clean up: remove angle brackets from key name if any remain
        result = result.replace("<", "").replace(">", "")
        return result if result else ""

    @staticmethod
    def _find_kde_config_tool() -> str:
        """Find available KDE config tool (kwriteconfig6 or kwriteconfig5)."""
        for tool in ["kwriteconfig6", "kwriteconfig5"]:
            try:
                subprocess.run([tool, "--help"], capture_output=True, timeout=2)
                return tool
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return ""

    def update_hotkey(self, hotkey_id: str, key_combo: str) -> bool:
        """Update an existing hotkey binding without re-registering command.

        Args:
            hotkey_id: The hotkey identifier (e.g., 'fullscreen', 'region')
            key_combo: New key combination

        Returns:
            True if update successful
        """
        if self.desktop_env == "gnome":
            try:
                custom_path = f"{self.GNOME_BASE_PATH}/likx-{hotkey_id}/"
                binding_schema = f"{self.GNOME_SCHEMA}.custom-keybinding:{custom_path}"

                result = subprocess.run(
                    ["gsettings", "set", binding_schema, "binding", key_combo],
                    capture_output=True,
                )
                return result.returncode == 0
            except Exception as e:
                logging.warning("Failed to update hotkey '%s': %s", hotkey_id, e)
                return False
        return False

    def unregister_all(self) -> None:
        """Unregister all LikX hotkeys."""
        if self.desktop_env == "gnome":
            try:
                result = subprocess.run(
                    ["gsettings", "get", self.GNOME_SCHEMA, "custom-keybindings"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    current = result.stdout.strip()

                    for path in self._registered_paths:
                        current = current.replace(f"'{path}', ", "")
                        current = current.replace(f", '{path}'", "")
                        current = current.replace(f"'{path}'", "")

                    if current in ("[]", "[@as ]", ""):
                        current = "@as []"

                    subprocess.run(
                        [
                            "gsettings",
                            "set",
                            self.GNOME_SCHEMA,
                            "custom-keybindings",
                            current,
                        ],
                        timeout=5,
                    )

            except Exception as e:
                logging.warning("Failed to unregister GNOME hotkeys: %s", e)

        elif self.desktop_env == "kde":
            try:
                from pathlib import Path

                desktop_dir = Path.home() / ".local" / "share" / "applications"
                config_tool = self._find_kde_config_tool()

                for hotkey_id in self._registered_paths:
                    # Remove .desktop file
                    desktop_file = desktop_dir / f"likx-{hotkey_id}.desktop"
                    if desktop_file.exists():
                        desktop_file.unlink()

                    # Remove from kglobalshortcutsrc
                    if config_tool:
                        subprocess.run(
                            [
                                config_tool,
                                "--file",
                                "kglobalshortcutsrc",
                                "--group",
                                f"likx-{hotkey_id}.desktop",
                                "--delete",
                                "_launch",
                            ],
                            capture_output=True,
                            timeout=5,
                        )
            except Exception as e:
                logging.warning("Failed to unregister KDE hotkeys: %s", e)

        self._registered_paths.clear()
        self.hotkeys.clear()
