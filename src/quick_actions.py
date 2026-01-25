"""Quick Actions Floating Panel for LikX.

A floating panel that appears near selected elements with contextual quick actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False

from .i18n import _

if TYPE_CHECKING:
    pass  # Types imported for documentation only

# Module-level flag to prevent CSS provider accumulation
_css_applied = False


class QuickAction:
    """Represents a quick action button."""

    def __init__(
        self,
        icon: str,
        tooltip: str,
        callback: Callable[[], None],
        enabled_check: Optional[Callable[[], bool]] = None,
    ):
        self.icon = icon
        self.tooltip = tooltip
        self.callback = callback
        self.enabled_check = enabled_check or (lambda: True)


class QuickActionsPanel:
    """Floating panel with contextual quick actions for selected elements."""

    def __init__(self, parent_window: Gtk.Window):
        if not GTK_AVAILABLE:
            raise RuntimeError("GTK is not available")

        self.parent_window = parent_window
        self.visible = False
        self._hide_timer_id = None
        self._actions: List[QuickAction] = []

        # Create popup window
        self.popup = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.popup.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.popup.set_decorated(False)
        self.popup.set_skip_taskbar_hint(True)
        self.popup.set_skip_pager_hint(True)
        self.popup.set_transient_for(parent_window)

        # Apply styling
        self._apply_styles()

        # Create container
        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.container.get_style_context().add_class("quick-actions-panel")
        self.popup.add(self.container)

        # Track mouse to auto-hide
        self.popup.connect("leave-notify-event", self._on_leave)
        self.popup.connect("enter-notify-event", self._on_enter)

    def _apply_styles(self) -> None:
        """Apply CSS styles to the panel (only once per process)."""
        global _css_applied
        if _css_applied:
            return
        _css_applied = True

        css = b"""
        .quick-actions-panel {
            background: rgba(30, 30, 46, 0.95);
            border: 1px solid rgba(100, 100, 150, 0.5);
            border-radius: 8px;
            padding: 4px 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }
        .quick-action-btn {
            min-width: 28px;
            min-height: 28px;
            padding: 4px;
            border: none;
            border-radius: 6px;
            background: transparent;
            color: #c0c0d0;
            font-size: 14px;
        }
        .quick-action-btn:hover {
            background: rgba(100, 130, 220, 0.3);
            color: #ffffff;
        }
        .quick-action-btn:active {
            background: rgba(100, 130, 220, 0.5);
        }
        .quick-action-btn:disabled {
            color: #606070;
        }
        .quick-action-sep {
            background: rgba(100, 100, 140, 0.4);
            min-width: 1px;
            margin: 4px 2px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def set_actions(self, actions: List[QuickAction]) -> None:
        """Set the actions to display in the panel."""
        self._actions = actions
        self._rebuild_buttons()

    def _rebuild_buttons(self) -> None:
        """Rebuild the action buttons."""
        # Clear existing children
        for child in self.container.get_children():
            self.container.remove(child)

        for i, action in enumerate(self._actions):
            # Add separator between groups (after delete, after clipboard ops)
            if i in [1, 3]:
                sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                sep.get_style_context().add_class("quick-action-sep")
                self.container.pack_start(sep, False, False, 0)

            btn = Gtk.Button(label=action.icon)
            btn.set_tooltip_text(action.tooltip)
            btn.get_style_context().add_class("quick-action-btn")
            btn.set_sensitive(action.enabled_check())
            btn.connect("clicked", lambda b, a=action: self._on_action_clicked(a))
            self.container.pack_start(btn, False, False, 0)

        self.container.show_all()

    def _on_action_clicked(self, action: QuickAction) -> None:
        """Handle action button click."""
        self.hide()
        action.callback()

    def show_at(
        self,
        x: int,
        y: int,
        element_bbox: Optional[Tuple[float, float, float, float]] = None,
    ) -> None:
        """Show the panel near the given position.

        Args:
            x, y: Screen coordinates to show near
            element_bbox: Optional (x1, y1, x2, y2) bounding box of selected element
        """
        if not self._actions:
            return

        self._rebuild_buttons()

        # Get panel size
        self.popup.show_all()
        width = self.popup.get_allocated_width()
        height = self.popup.get_allocated_height()

        # Position above and centered on the selection
        if element_bbox:
            x1, y1, x2, y2 = element_bbox
            panel_x = int((x1 + x2) / 2 - width / 2)
            panel_y = int(y1 - height - 8)
        else:
            panel_x = x - width // 2
            panel_y = y - height - 8

        # Keep on screen
        screen = Gdk.Screen.get_default()
        screen_width = screen.get_width()

        panel_x = max(10, min(panel_x, screen_width - width - 10))
        if panel_y < 10:
            # Show below if not enough space above
            panel_y = int(y2 + 8) if element_bbox else y + 20

        self.popup.move(panel_x, panel_y)
        self.popup.show_all()
        self.visible = True

        # Cancel any pending hide timer
        if self._hide_timer_id:
            GLib.source_remove(self._hide_timer_id)
            self._hide_timer_id = None

    def hide(self) -> None:
        """Hide the panel."""
        if self._hide_timer_id:
            GLib.source_remove(self._hide_timer_id)
            self._hide_timer_id = None
        self.popup.hide()
        self.visible = False

    def _on_leave(self, widget: Gtk.Widget, event: Gdk.EventCrossing) -> bool:
        """Handle mouse leaving the panel - start hide timer."""
        if event.detail == Gdk.NotifyType.INFERIOR:
            return False
        # Delay hide to allow moving back
        self._hide_timer_id = GLib.timeout_add(800, self._delayed_hide)
        return False

    def _on_enter(self, widget: Gtk.Widget, event: Gdk.EventCrossing) -> bool:
        """Handle mouse entering the panel - cancel hide timer."""
        if self._hide_timer_id:
            GLib.source_remove(self._hide_timer_id)
            self._hide_timer_id = None
        return False

    def _delayed_hide(self) -> bool:
        """Hide after delay."""
        self.hide()
        return False  # Don't repeat

    def update_position(
        self, bbox: Tuple[float, float, float, float], drawing_area: Gtk.Widget
    ) -> None:
        """Update panel position based on element bounding box.

        Args:
            bbox: (x1, y1, x2, y2) in image coordinates
            drawing_area: The drawing area widget for coordinate conversion
        """
        if not self.visible:
            return

        # Convert image coords to screen coords
        window = drawing_area.get_window()
        if not window:
            return

        origin = window.get_origin()
        if origin[0]:  # Success
            win_x, win_y = origin[1], origin[2]
        else:
            return

        x1, y1, x2, y2 = bbox
        screen_x = win_x + (x1 + x2) / 2
        screen_y = win_y + y1

        self.show_at(int(screen_x), int(screen_y), bbox)


def create_selection_actions(editor_window) -> List[QuickAction]:
    """Create the standard set of quick actions for selected elements.

    Args:
        editor_window: The EditorWindow instance

    Returns:
        List of QuickAction objects
    """

    def has_selection() -> bool:
        return bool(
            editor_window.editor_state and editor_window.editor_state.selected_indices
        )

    def is_unlocked() -> bool:
        if not editor_window.editor_state:
            return False
        return not editor_window.editor_state.is_selection_locked()

    def has_multiple() -> bool:
        return has_selection() and len(editor_window.editor_state.selected_indices) > 1

    actions = [
        # Delete
        QuickAction(
            icon="\u2715",  #
            tooltip=_("Delete (Del)"),
            callback=lambda: editor_window._delete_selected(),
            enabled_check=lambda: has_selection() and is_unlocked(),
        ),
        # Duplicate
        QuickAction(
            icon="\u2750",  # ❐
            tooltip=_("Duplicate (Ctrl+D)"),
            callback=lambda: editor_window._duplicate_selected(),
            enabled_check=lambda: has_selection() and is_unlocked(),
        ),
        # Copy
        QuickAction(
            icon="\u2398",  # ⎘
            tooltip=_("Copy (Ctrl+C)"),
            callback=lambda: editor_window._copy_annotations(),
            enabled_check=has_selection,
        ),
        # Bring to front
        QuickAction(
            icon="\u2191",  # ↑
            tooltip=_("Bring to Front (Ctrl+])"),
            callback=lambda: editor_window._bring_to_front(),
            enabled_check=has_selection,
        ),
        # Send to back
        QuickAction(
            icon="\u2193",  # ↓
            tooltip=_("Send to Back (Ctrl+[)"),
            callback=lambda: editor_window._send_to_back(),
            enabled_check=has_selection,
        ),
        # Lock/Unlock
        QuickAction(
            icon="\U0001f512",  # 🔒
            tooltip=_("Lock/Unlock (Ctrl+L)"),
            callback=lambda: editor_window._toggle_lock(),
            enabled_check=has_selection,
        ),
        # Group (only for multiple selection)
        QuickAction(
            icon="\u25a3",  # ▣
            tooltip=_("Group (Ctrl+G)"),
            callback=lambda: editor_window._group_selected(),
            enabled_check=has_multiple,
        ),
    ]

    return actions
