"""
Settings Screen

General settings configuration.
"""

from ..items import MenuItem
from .base_menu import MenuScreen
from .toast import ToastScreen


class SettingsScreen(MenuScreen):
    """
    General settings menu.

    Provides access to device and application settings.
    """

    def __init__(self, manager):
        """
        Initialize settings screen.

        Args:
            manager: ScreenManager instance
        """
        items = [
            MenuItem(
                id="clock",
                label="Clock Display",
                submenu=lambda: ClockSettingsScreen(manager),
            ),
            MenuItem(
                id="idle_timeout",
                label="Idle Timeout",
                value_getter=lambda: "30s",
                submenu=lambda: TimeoutSettingsScreen(manager),
            ),
            MenuItem(
                id="stick_sensitivity",
                label="Stick Sensitivity",
                value_getter=lambda: "Normal",
                action=self._toggle_sensitivity,
            ),
            MenuItem(
                id="reset",
                label="Reset to Defaults",
                action=self._reset_defaults,
            ),
        ]
        super().__init__(manager, "SETTINGS", items)

    def _toggle_sensitivity(self):
        """Toggle stick sensitivity."""
        toast = ToastScreen(self.manager, "Sensitivity: Normal")
        self.manager.show_overlay(toast, duration=1.5)

    def _reset_defaults(self):
        """Reset all settings to defaults."""
        toast = ToastScreen(self.manager, "Settings reset")
        self.manager.show_overlay(toast, duration=2.0)


class ClockSettingsScreen(MenuScreen):
    """Clock display settings."""

    def __init__(self, manager):
        items = [
            MenuItem(
                id="format_24",
                label="24-hour",
                action=lambda: self._set_format("24h"),
            ),
            MenuItem(
                id="format_12",
                label="12-hour",
                action=lambda: self._set_format("12h"),
            ),
            MenuItem(
                id="show_seconds",
                label="Show Seconds",
                value_getter=lambda: "On",
                action=self._toggle_seconds,
            ),
            MenuItem(
                id="show_date",
                label="Show Date",
                value_getter=lambda: "On",
                action=self._toggle_date,
            ),
        ]
        super().__init__(manager, "CLOCK", items)

    def _set_format(self, fmt: str):
        toast = ToastScreen(self.manager, f"Format: {fmt}")
        self.manager.show_overlay(toast, duration=1.5)
        self.manager.pop()

    def _toggle_seconds(self):
        toast = ToastScreen(self.manager, "Seconds: On")
        self.manager.show_overlay(toast, duration=1.5)

    def _toggle_date(self):
        toast = ToastScreen(self.manager, "Date: On")
        self.manager.show_overlay(toast, duration=1.5)


class TimeoutSettingsScreen(MenuScreen):
    """Idle timeout settings."""

    def __init__(self, manager):
        items = [
            MenuItem(id="t_never", label="Never", action=lambda: self._set_timeout(0)),
            MenuItem(id="t_15", label="15 seconds", action=lambda: self._set_timeout(15)),
            MenuItem(id="t_30", label="30 seconds", action=lambda: self._set_timeout(30)),
            MenuItem(id="t_60", label="1 minute", action=lambda: self._set_timeout(60)),
            MenuItem(id="t_300", label="5 minutes", action=lambda: self._set_timeout(300)),
        ]
        super().__init__(manager, "TIMEOUT", items)

    def _set_timeout(self, seconds: int):
        if seconds == 0:
            msg = "Timeout: Never"
        elif seconds < 60:
            msg = f"Timeout: {seconds}s"
        else:
            msg = f"Timeout: {seconds // 60}m"

        toast = ToastScreen(self.manager, msg)
        self.manager.show_overlay(toast, duration=1.5)
        self.manager.pop()
