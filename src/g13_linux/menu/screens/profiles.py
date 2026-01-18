"""
Profiles Screen

Profile selection and management.
"""

from ..items import MenuItem
from .base_menu import MenuScreen
from .toast import ToastScreen


class ProfilesScreen(MenuScreen):
    """
    Profile selection screen.

    Lists available profiles with current profile marked.
    """

    def __init__(self, manager):
        """
        Initialize profiles screen.

        Args:
            manager: ScreenManager instance
        """
        self.profile_manager = getattr(manager, "profile_manager", None)
        items = self._build_items()
        super().__init__(manager, "PROFILES", items)

    def _build_items(self) -> list[MenuItem]:
        """Build menu items from available profiles."""
        items = []

        if not self.profile_manager:
            items.append(MenuItem(
                id="no_pm",
                label="No profile manager",
                enabled=False,
            ))
            return items

        # Get current profile name
        current = None
        if hasattr(self.profile_manager, "current_name"):
            current = self.profile_manager.current_name
        elif hasattr(self.profile_manager, "current"):
            profile = self.profile_manager.current
            if profile:
                current = getattr(profile, "name", None)

        # Get profile list
        profile_names = []
        if hasattr(self.profile_manager, "list_profiles"):
            profile_names = self.profile_manager.list_profiles()
        elif hasattr(self.profile_manager, "profiles"):
            profile_names = list(self.profile_manager.profiles.keys())

        # Build items
        for name in profile_names:
            prefix = "* " if name == current else "  "
            items.append(MenuItem(
                id=f"profile_{name}",
                label=f"{prefix}{name}",
                action=lambda n=name: self._select_profile(n),
            ))

        # Add "New Profile" option
        items.append(MenuItem(
            id="new",
            label="+ New Profile",
            action=self._create_profile,
        ))

        return items

    def _select_profile(self, name: str):
        """
        Select and load a profile.

        Args:
            name: Profile name to load
        """
        if not self.profile_manager:
            return

        try:
            if hasattr(self.profile_manager, "load"):
                self.profile_manager.load(name)
            elif hasattr(self.profile_manager, "activate"):
                self.profile_manager.activate(name)

            # Return to previous screen
            self.manager.pop()

            # Show confirmation toast
            toast = ToastScreen(self.manager, f"Loaded: {name}")
            self.manager.show_overlay(toast, duration=2.0)

        except Exception as e:
            toast = ToastScreen(self.manager, f"Error: {e}")
            self.manager.show_overlay(toast, duration=3.0)

    def _create_profile(self):
        """Create new profile (placeholder)."""
        toast = ToastScreen(self.manager, "Use GUI for new profiles")
        self.manager.show_overlay(toast, duration=2.0)

    def on_enter(self):
        """Refresh profile list when entering."""
        self.items = self._build_items()
        self.selected_index = 0
        self.scroll_offset = 0
        self.mark_dirty()
