"""Keyboard handling mixin for LikX EditorWindow."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from ..capture import CaptureResult  # noqa: E402
from ..editor import ToolType  # noqa: E402

if TYPE_CHECKING:
    pass


class KeyboardMixin:
    """Mixin providing keyboard handling for EditorWindow.

    This mixin expects the following attributes on the class:
    - editor_state: EditorState
    - drawing_area: Gtk.DrawingArea
    - statusbar: Gtk.Statusbar
    - statusbar_context: int
    - notebook: Gtk.Notebook
    - tabs: List[TabContent]
    - current_tab_index: int
    - tool_buttons: Dict[ToolType, Gtk.ToggleButton]
    - save_handler: SaveHandler

    And the following methods:
    - _show_toast(message: str)
    - _set_tool(tool: ToolType)
    - _show_command_palette()
    - _update_zoom_label()
    - close_tab(index: int)
    """

    def _init_key_bindings(self) -> None:
        """Initialize keyboard shortcut dispatch tables."""
        # Tool shortcuts (no modifiers)
        self._tool_shortcuts = {
            Gdk.KEY_p: ToolType.PEN,
            Gdk.KEY_h: ToolType.HIGHLIGHTER,
            Gdk.KEY_l: ToolType.LINE,
            Gdk.KEY_a: ToolType.ARROW,
            Gdk.KEY_r: ToolType.RECTANGLE,
            Gdk.KEY_e: ToolType.ELLIPSE,
            Gdk.KEY_t: ToolType.TEXT,
            Gdk.KEY_b: ToolType.BLUR,
            Gdk.KEY_x: ToolType.PIXELATE,
            Gdk.KEY_m: ToolType.MEASURE,
            Gdk.KEY_n: ToolType.NUMBER,
            Gdk.KEY_i: ToolType.COLORPICKER,
            Gdk.KEY_s: ToolType.STAMP,
            Gdk.KEY_z: ToolType.ZOOM,
            Gdk.KEY_k: ToolType.CALLOUT,
            Gdk.KEY_c: ToolType.CROP,
            Gdk.KEY_v: ToolType.SELECT,
        }

        # Ctrl+Alt alignment shortcuts: (key, method, success_msg)
        self._align_shortcuts = {
            Gdk.KEY_l: ("align_left", "Aligned left"),
            Gdk.KEY_L: ("align_left", "Aligned left"),
            Gdk.KEY_r: ("align_right", "Aligned right"),
            Gdk.KEY_R: ("align_right", "Aligned right"),
            Gdk.KEY_t: ("align_top", "Aligned top"),
            Gdk.KEY_T: ("align_top", "Aligned top"),
            Gdk.KEY_b: ("align_bottom", "Aligned bottom"),
            Gdk.KEY_B: ("align_bottom", "Aligned bottom"),
            Gdk.KEY_c: ("align_center_horizontal", "Aligned center (horizontal)"),
            Gdk.KEY_C: ("align_center_horizontal", "Aligned center (horizontal)"),
            Gdk.KEY_m: ("align_center_vertical", "Aligned center (vertical)"),
            Gdk.KEY_M: ("align_center_vertical", "Aligned center (vertical)"),
            Gdk.KEY_w: ("match_width", "Matched width"),
            Gdk.KEY_W: ("match_width", "Matched width"),
            Gdk.KEY_e: ("match_height", "Matched height"),
            Gdk.KEY_E: ("match_height", "Matched height"),
            Gdk.KEY_s: ("match_size", "Matched size"),
            Gdk.KEY_S: ("match_size", "Matched size"),
            Gdk.KEY_f: ("flip_vertical", "Flipped vertically"),
            Gdk.KEY_F: ("flip_vertical", "Flipped vertically"),
        }

    def _handle_alignment_shortcut(self, key: int) -> bool:
        """Handle Ctrl+Alt alignment shortcuts."""
        if key not in self._align_shortcuts:
            return False
        method_name, success_msg = self._align_shortcuts[key]
        method = getattr(self.editor_state, method_name)
        if method():
            self._show_toast(success_msg)
            self.drawing_area.queue_draw()
        else:
            self._show_toast("Select 2+ elements")
        return True

    def _ctrl_copy(self) -> None:
        """Handle Ctrl+C (copy)."""
        if self.editor_state.selected_indices:
            if self.editor_state.copy_selected():
                self._show_toast(f"Copied {len(self.editor_state.selected_indices)} annotation(s)")
        else:
            self.save_handler.copy_to_clipboard()

    def _ctrl_paste(self) -> None:
        """Handle Ctrl+V (paste annotations, or image from system clipboard as new tab)."""
        if self.editor_state.has_clipboard() and self.editor_state.paste_annotations():
            self._show_toast(f"Pasted {len(self.editor_state.selected_indices)} annotation(s)")
            self.drawing_area.queue_draw()
            return

        # No annotation clipboard — try pasting image from system clipboard
        self._paste_image_from_clipboard()

    def _ctrl_lock_toggle(self) -> None:
        """Handle Ctrl+L (lock toggle)."""
        if self.editor_state.toggle_lock_selected():
            state = "Locked" if self.editor_state.is_selection_locked() else "Unlocked"
            self._show_toast(state)
            self.drawing_area.queue_draw()
        else:
            self._show_toast("Select element(s) to lock")

    def _ctrl_grid_toggle(self) -> None:
        """Handle Ctrl+' (grid snap toggle)."""
        new_state = not self.editor_state.grid_snap_enabled
        self.editor_state.set_grid_snap(new_state)
        self._show_toast("Grid snap ON" if new_state else "Grid snap OFF")
        self.drawing_area.queue_draw()

    def _handle_ctrl_shortcuts(self, key: int, shift: bool) -> bool:
        """Handle Ctrl+key shortcuts. Returns True if handled."""
        # Simple shortcuts with immediate actions
        simple_shortcuts = {
            Gdk.KEY_s: self.save_handler.save,
            Gdk.KEY_z: self._undo,
            Gdk.KEY_y: self._redo,
            Gdk.KEY_c: self._ctrl_copy,
            Gdk.KEY_v: self._ctrl_paste,
            Gdk.KEY_l: self._ctrl_lock_toggle,
            Gdk.KEY_apostrophe: self._ctrl_grid_toggle,
        }

        if key in simple_shortcuts:
            simple_shortcuts[key]()
            return True

        # Shortcuts that need success check and toast
        action_shortcuts = {
            Gdk.KEY_bracketright: (self.editor_state.bring_to_front, "Brought to front"),
            Gdk.KEY_bracketleft: (self.editor_state.send_to_back, "Sent to back"),
            Gdk.KEY_d: (
                self.editor_state.duplicate_selected,
                lambda: f"Duplicated {len(self.editor_state.selected_indices)} annotation(s)",
            ),
        }

        if key in action_shortcuts:
            action, msg = action_shortcuts[key]
            if action():
                self._show_toast(msg() if callable(msg) else msg)
                self.drawing_area.queue_draw()
            return True

        return False

    def _handle_ctrl_shift_shortcuts(self, key: int) -> bool:
        """Handle Ctrl+Shift+key shortcuts. Returns True if handled."""
        if key in (Gdk.KEY_p, Gdk.KEY_P):
            self._show_command_palette()
            return True

        # Shortcuts with action/success/fail pattern
        shortcuts = {
            (Gdk.KEY_h, Gdk.KEY_H): (
                self.editor_state.distribute_horizontal,
                "Distributed horizontally",
                "Select 3+ elements to distribute",
            ),
            (Gdk.KEY_j, Gdk.KEY_J): (
                self.editor_state.distribute_vertical,
                "Distributed vertically",
                "Select 3+ elements to distribute",
            ),
            (Gdk.KEY_g, Gdk.KEY_G): (
                self.editor_state.ungroup_selected,
                "Ungrouped",
                "No groups to ungroup",
            ),
            (Gdk.KEY_f, Gdk.KEY_F): (
                self.editor_state.flip_horizontal,
                "Flipped horizontally",
                "Select element(s) to flip",
            ),
            (Gdk.KEY_r, Gdk.KEY_R): (
                lambda: self.editor_state.rotate_selected(-90),
                "Rotated -90°",
                "Select element(s) to rotate",
            ),
        }

        for keys, (action, success_msg, fail_msg) in shortcuts.items():
            if key in keys:
                if action():
                    self._show_toast(success_msg)
                    self.drawing_area.queue_draw()
                else:
                    self._show_toast(fail_msg)
                return True

        return False

    def _handle_tab_switch(self, key: int, shift: bool) -> bool:
        """Handle Ctrl+Tab / Ctrl+Shift+Tab for tab switching."""
        if key != Gdk.KEY_Tab or len(self.tabs) <= 1:
            return key == Gdk.KEY_Tab
        offset = -1 if shift else 1
        self.notebook.set_current_page((self.current_tab_index + offset) % len(self.tabs))
        return True

    def _handle_opacity_adjust(self, key: int) -> bool:
        """Handle Shift+[ / Shift+] for opacity adjustment."""
        adjustments = {Gdk.KEY_bracketleft: -0.1, Gdk.KEY_bracketright: 0.1}
        if key not in adjustments:
            return False
        if self.editor_state.adjust_selected_opacity(adjustments[key]):
            opacity = self.editor_state.get_selected_opacity() or 1.0
            self._show_toast(f"Opacity: {int(opacity * 100)}%")
            self.drawing_area.queue_draw()
        else:
            self._show_toast("Select element(s) to adjust opacity")
        return True

    def _handle_zoom_shortcuts(self, key: int) -> bool:
        """Handle zoom shortcuts (+/-/0)."""
        if key in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
            self.editor_state.zoom_in()
        elif key in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
            self.editor_state.zoom_out()
        elif key == Gdk.KEY_0:
            self.editor_state.reset_zoom()
        else:
            return False
        self._update_zoom_label()
        self.drawing_area.queue_draw()
        return True

    def _handle_arrow_nudge(self, key: int, shift: bool) -> bool:
        """Handle arrow key nudging."""
        nudge = 10 if shift else 1
        offsets = {
            Gdk.KEY_Up: (0, -nudge),
            Gdk.KEY_Down: (0, nudge),
            Gdk.KEY_Left: (-nudge, 0),
            Gdk.KEY_Right: (nudge, 0),
        }
        if key not in offsets:
            return False
        if self.editor_state.nudge_selected(*offsets[key]):
            self.drawing_area.queue_draw()
        return True

    def _handle_ctrl_key(self, key: int, shift: bool, alt: bool) -> bool:
        """Handle Ctrl+key combinations."""
        if self._handle_tab_switch(key, shift):
            return True
        if not shift and key in (Gdk.KEY_w, Gdk.KEY_W):
            self.close_tab(self.current_tab_index)
            return True
        if not shift and key in (Gdk.KEY_g, Gdk.KEY_G):
            if self.editor_state.group_selected():
                self._show_toast(f"Grouped {len(self.editor_state.selected_indices)} elements")
                self.drawing_area.queue_draw()
            else:
                self._show_toast("Select 2+ elements to group")
            return True
        if not shift and not alt and key in (Gdk.KEY_r, Gdk.KEY_R):
            if self.editor_state.rotate_selected(90):
                self._show_toast("Rotated 90°")
                self.drawing_area.queue_draw()
            else:
                self._show_toast("Select element(s) to rotate")
            return True
        if shift and self._handle_ctrl_shift_shortcuts(key):
            return True
        if alt and self._handle_alignment_shortcut(key):
            return True
        if not shift and not alt and self._handle_ctrl_shortcuts(key, shift):
            return True
        return False

    def _handle_tool_shortcut(self, key: int) -> bool:
        """Handle tool selection shortcuts."""
        if key not in self._tool_shortcuts:
            return False
        tool = self._tool_shortcuts[key]
        self._set_tool(tool)
        if hasattr(self, "tool_buttons") and tool in self.tool_buttons:
            self.tool_buttons[tool].set_active(True)
        return True

    def _handle_escape(self) -> bool:
        """Handle Escape key."""
        if self.editor_state.selected_index is not None:
            self.editor_state.deselect()
        else:
            self.editor_state.cancel_drawing()
        self.drawing_area.queue_draw()
        return True

    def _on_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle keyboard shortcuts using dispatch tables."""
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        shift = event.state & Gdk.ModifierType.SHIFT_MASK
        alt = event.state & Gdk.ModifierType.MOD1_MASK
        key = event.keyval

        if ctrl and self._handle_ctrl_key(key, shift, alt):
            return True

        if shift and not ctrl and not alt and self._handle_opacity_adjust(key):
            return True

        if self._handle_tool_shortcut(key):
            return True

        if self._handle_zoom_shortcuts(key):
            return True

        if key in (Gdk.KEY_Delete, Gdk.KEY_BackSpace):
            if self.editor_state.delete_selected():
                self.statusbar.push(self.statusbar_context, "Element deleted")
                self.drawing_area.queue_draw()
            return True

        if self._handle_arrow_nudge(key, shift):
            return True

        if key == Gdk.KEY_Escape:
            return self._handle_escape()

        return False

    def _paste_image_from_clipboard(self) -> None:
        """Paste an image from the system clipboard as a new tab."""
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        pixbuf = clipboard.wait_for_image()

        if pixbuf is None:
            self._show_toast("No image on clipboard")
            return

        result = CaptureResult(success=True, pixbuf=pixbuf)

        if hasattr(self, "add_tab"):
            self.add_tab(result, switch_to=True)
            # Show tab bar now that we have multiple tabs
            if hasattr(self, "notebook"):
                self.notebook.set_show_tabs(True)
            self._show_toast("Pasted image from clipboard")
        else:
            logging.warning("Cannot paste image: add_tab not available")
