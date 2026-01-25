"""Enhanced Undo/Redo with History Preview for LikX.

Provides dropdown buttons showing the undo/redo stack with action names.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False

from .i18n import _

if TYPE_CHECKING:
    pass  # Types imported for documentation only

# Module-level flag to prevent CSS provider accumulation
_css_applied = False


def get_action_name(elements_before: List, elements_after: List) -> str:
    """Determine a descriptive name for the action based on element changes.

    Args:
        elements_before: Elements list before the action
        elements_after: Elements list after the action

    Returns:
        A descriptive action name
    """
    len_before = len(elements_before) if elements_before else 0
    len_after = len(elements_after) if elements_after else 0

    if len_after > len_before:
        # Element(s) added
        diff = len_after - len_before
        if diff == 1 and elements_after:
            # Get the type of the new element
            new_elem = elements_after[-1]
            tool_names = {
                "pen": _("Drew line"),
                "highlighter": _("Highlighted"),
                "line": _("Drew line"),
                "arrow": _("Added arrow"),
                "rectangle": _("Drew rectangle"),
                "ellipse": _("Drew ellipse"),
                "text": _("Added text"),
                "blur": _("Added blur"),
                "pixelate": _("Pixelated area"),
                "number": _("Added number"),
                "stamp": _("Added stamp"),
                "callout": _("Added callout"),
            }
            return tool_names.get(new_elem.tool.value, _("Added element"))
        return _("Added {} elements").format(diff)

    elif len_after < len_before:
        # Element(s) removed
        diff = len_before - len_after
        if diff == 1:
            return _("Deleted element")
        return _("Deleted {} elements").format(diff)

    else:
        # Same count - modification
        return _("Modified element")


class UndoHistoryEntry:
    """Represents an entry in the undo/redo history."""

    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index


class UndoRedoButtons:
    """Enhanced undo/redo buttons with history dropdown."""

    def __init__(
        self,
        on_undo: Callable[[], None],
        on_redo: Callable[[], None],
        on_undo_to: Callable[[int], None],
        on_redo_to: Callable[[int], None],
        get_undo_stack: Callable[[], List],
        get_redo_stack: Callable[[], List],
        get_elements: Callable[[], List],
    ):
        """Initialize the undo/redo buttons.

        Args:
            on_undo: Callback for single undo
            on_redo: Callback for single redo
            on_undo_to: Callback for undo to specific index
            on_redo_to: Callback for redo to specific index
            get_undo_stack: Function to get current undo stack
            get_redo_stack: Function to get current redo stack
            get_elements: Function to get current elements
        """
        if not GTK_AVAILABLE:
            raise RuntimeError("GTK is not available")

        self.on_undo = on_undo
        self.on_redo = on_redo
        self.on_undo_to = on_undo_to
        self.on_redo_to = on_redo_to
        self.get_undo_stack = get_undo_stack
        self.get_redo_stack = get_redo_stack
        self.get_elements = get_elements

        self._apply_styles()

        # Create container
        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)

        # Undo button with dropdown
        self.undo_box = Gtk.Box(spacing=0)
        self.undo_btn = Gtk.Button(label="\u21b6")  # ↶
        self.undo_btn.set_tooltip_text(_("Undo (Ctrl+Z)"))
        self.undo_btn.get_style_context().add_class("undo-btn")
        self.undo_btn.connect("clicked", lambda b: self.on_undo())
        self.undo_box.pack_start(self.undo_btn, False, False, 0)

        self.undo_dropdown = Gtk.MenuButton()
        self.undo_dropdown.set_label("\u25be")  # ▾
        self.undo_dropdown.get_style_context().add_class("undo-dropdown")
        self.undo_dropdown.connect("toggled", self._on_undo_dropdown_toggled)
        self.undo_box.pack_start(self.undo_dropdown, False, False, 0)

        self.container.pack_start(self.undo_box, False, False, 0)

        # Redo button with dropdown
        self.redo_box = Gtk.Box(spacing=0)
        self.redo_btn = Gtk.Button(label="\u21b7")  # ↷
        self.redo_btn.set_tooltip_text(_("Redo (Ctrl+Y)"))
        self.redo_btn.get_style_context().add_class("redo-btn")
        self.redo_btn.connect("clicked", lambda b: self.on_redo())
        self.redo_box.pack_start(self.redo_btn, False, False, 0)

        self.redo_dropdown = Gtk.MenuButton()
        self.redo_dropdown.set_label("\u25be")  # ▾
        self.redo_dropdown.get_style_context().add_class("redo-dropdown")
        self.redo_dropdown.connect("toggled", self._on_redo_dropdown_toggled)
        self.redo_box.pack_start(self.redo_dropdown, False, False, 0)

        self.container.pack_start(self.redo_box, False, False, 0)

        # Create popover menus
        self._create_undo_popover()
        self._create_redo_popover()

    def _apply_styles(self) -> None:
        """Apply CSS styles (only once per process)."""
        global _css_applied
        if _css_applied:
            return
        _css_applied = True

        css = b"""
        .undo-btn, .redo-btn {
            min-width: 28px;
            min-height: 28px;
            padding: 2px 6px;
            border: 1px solid transparent;
            border-radius: 4px 0 0 4px;
            background: transparent;
            color: #c0c0d0;
            font-size: 14px;
        }
        .undo-dropdown, .redo-dropdown {
            min-width: 16px;
            min-height: 28px;
            padding: 2px 4px;
            border: 1px solid transparent;
            border-left: none;
            border-radius: 0 4px 4px 0;
            background: transparent;
            color: #808090;
            font-size: 10px;
        }
        .undo-btn:hover, .redo-btn:hover,
        .undo-dropdown:hover, .redo-dropdown:hover {
            background: rgba(100, 100, 180, 0.2);
            border-color: rgba(130, 130, 200, 0.4);
        }
        .undo-btn:disabled, .redo-btn:disabled,
        .undo-dropdown:disabled, .redo-dropdown:disabled {
            color: #505060;
        }
        .history-popover {
            background: rgba(30, 30, 46, 0.98);
            border: 1px solid rgba(100, 100, 150, 0.5);
            border-radius: 8px;
            padding: 4px;
        }
        .history-item {
            min-height: 28px;
            padding: 4px 12px;
            border-radius: 4px;
            background: transparent;
            color: #c0c0d0;
            font-size: 12px;
        }
        .history-item:hover {
            background: rgba(100, 130, 220, 0.3);
            color: #ffffff;
        }
        .history-label {
            color: #8888aa;
            font-size: 11px;
            padding: 4px 8px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _create_undo_popover(self) -> None:
        """Create the undo history popover."""
        self.undo_popover = Gtk.Popover()
        self.undo_popover.set_relative_to(self.undo_dropdown)
        self.undo_popover.get_style_context().add_class("history-popover")

        self.undo_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.undo_list.set_margin_start(4)
        self.undo_list.set_margin_end(4)
        self.undo_list.set_margin_top(4)
        self.undo_list.set_margin_bottom(4)
        self.undo_popover.add(self.undo_list)

        self.undo_dropdown.set_popover(self.undo_popover)

    def _create_redo_popover(self) -> None:
        """Create the redo history popover."""
        self.redo_popover = Gtk.Popover()
        self.redo_popover.set_relative_to(self.redo_dropdown)
        self.redo_popover.get_style_context().add_class("history-popover")

        self.redo_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.redo_list.set_margin_start(4)
        self.redo_list.set_margin_end(4)
        self.redo_list.set_margin_top(4)
        self.redo_list.set_margin_bottom(4)
        self.redo_popover.add(self.redo_list)

        self.redo_dropdown.set_popover(self.redo_popover)

    def _on_undo_dropdown_toggled(self, button: Gtk.MenuButton) -> None:
        """Populate undo history when dropdown is opened."""
        if not button.get_active():
            return

        # Clear existing items
        for child in self.undo_list.get_children():
            self.undo_list.remove(child)

        undo_stack = self.get_undo_stack()
        current_elements = self.get_elements()

        if not undo_stack:
            label = Gtk.Label(label=_("No undo history"))
            label.get_style_context().add_class("history-label")
            self.undo_list.pack_start(label, False, False, 0)
        else:
            # Show most recent first (reverse order)
            prev_elements = current_elements
            for i, elements in enumerate(reversed(undo_stack)):
                idx = len(undo_stack) - 1 - i
                name = get_action_name(elements, prev_elements)
                prev_elements = elements

                btn = Gtk.Button(label=f"\u2022 {name}")  # • bullet
                btn.get_style_context().add_class("history-item")
                btn.set_relief(Gtk.ReliefStyle.NONE)
                btn.connect("clicked", self._on_undo_item_clicked, idx)
                self.undo_list.pack_start(btn, False, False, 0)

                # Limit to 10 items
                if i >= 9:
                    break

        self.undo_list.show_all()

    def _on_redo_dropdown_toggled(self, button: Gtk.MenuButton) -> None:
        """Populate redo history when dropdown is opened."""
        if not button.get_active():
            return

        # Clear existing items
        for child in self.redo_list.get_children():
            self.redo_list.remove(child)

        redo_stack = self.get_redo_stack()
        current_elements = self.get_elements()

        if not redo_stack:
            label = Gtk.Label(label=_("No redo history"))
            label.get_style_context().add_class("history-label")
            self.redo_list.pack_start(label, False, False, 0)
        else:
            # Show next redo first
            prev_elements = current_elements
            for i, elements in enumerate(reversed(redo_stack)):
                idx = len(redo_stack) - 1 - i
                name = get_action_name(prev_elements, elements)
                prev_elements = elements

                btn = Gtk.Button(label=f"\u2022 {name}")  # • bullet
                btn.get_style_context().add_class("history-item")
                btn.set_relief(Gtk.ReliefStyle.NONE)
                btn.connect("clicked", self._on_redo_item_clicked, idx)
                self.redo_list.pack_start(btn, False, False, 0)

                # Limit to 10 items
                if i >= 9:
                    break

        self.redo_list.show_all()

    def _on_undo_item_clicked(self, button: Gtk.Button, index: int) -> None:
        """Handle click on undo history item."""
        self.undo_popover.popdown()
        self.on_undo_to(index)

    def _on_redo_item_clicked(self, button: Gtk.Button, index: int) -> None:
        """Handle click on redo history item."""
        self.redo_popover.popdown()
        self.on_redo_to(index)

    def update_sensitivity(self, can_undo: bool, can_redo: bool) -> None:
        """Update button sensitivity based on stack state."""
        self.undo_btn.set_sensitive(can_undo)
        self.undo_dropdown.set_sensitive(can_undo)
        self.redo_btn.set_sensitive(can_redo)
        self.redo_dropdown.set_sensitive(can_redo)

    def get_widget(self) -> Gtk.Box:
        """Get the container widget."""
        return self.container
