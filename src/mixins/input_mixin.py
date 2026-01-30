"""Input handling mixin for LikX EditorWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib  # noqa: E402

from ..editor import ToolType  # noqa: E402

if TYPE_CHECKING:
    from gi.repository import Gtk


class InputMixin:
    """Mixin providing mouse/input handling for EditorWindow.

    This mixin expects the following attributes on the class:
    - editor_state: EditorState
    - result: CaptureResult (with pixbuf)
    - drawing_area: Gtk.DrawingArea
    - window: Gtk.Window
    - _callout_tail: Tuple[float, float] (set during callout creation)
    - _callout_box: Tuple[float, float] (set during callout creation)
    - _crop_start: Tuple[float, float] (set during crop)
    - _crop_end: Tuple[float, float] (set during crop)

    And the following methods:
    - _show_text_dialog(x: float, y: float)
    - _show_callout_dialog()
    - _show_radial_menu(x_root: float, y_root: float)
    - _show_quick_actions()
    - _hide_quick_actions()
    - _pick_color(x: float, y: float)
    - _apply_crop()
    - _update_zoom_label()
    """

    def _screen_to_image(self, x: float, y: float) -> tuple:
        """Convert screen coordinates to image coordinates (accounting for zoom)."""
        zoom = self.editor_state.zoom_level
        return x / zoom, y / zoom

    def _update_resize_cursor(self, img_x: float, img_y: float) -> None:
        """Update cursor based on hover position over resize handles."""
        # Map handle names to cursor types
        handle_cursors = {
            "nw": Gdk.CursorType.TOP_LEFT_CORNER,
            "ne": Gdk.CursorType.TOP_RIGHT_CORNER,
            "sw": Gdk.CursorType.BOTTOM_LEFT_CORNER,
            "se": Gdk.CursorType.BOTTOM_RIGHT_CORNER,
        }

        handle = self.editor_state._hit_test_handles(img_x, img_y)
        if handle and handle in handle_cursors:
            cursor = Gdk.Cursor.new_for_display(
                self.window.get_display(), handle_cursors[handle]
            )
            self.drawing_area.get_window().set_cursor(cursor)
        elif self.editor_state.get_selected():
            # Hovering over selected element - show move cursor
            elem = self.editor_state.get_selected()
            if self.editor_state._hit_test_element(elem, img_x, img_y):
                cursor = Gdk.Cursor.new_for_display(
                    self.window.get_display(), Gdk.CursorType.FLEUR
                )
                self.drawing_area.get_window().set_cursor(cursor)
            else:
                self.drawing_area.get_window().set_cursor(None)
        else:
            self.drawing_area.get_window().set_cursor(None)

    def _on_button_press(self, widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        """Handle mouse button press."""
        # Convert screen coords to image coords
        img_x, img_y = self._screen_to_image(event.x, event.y)

        if event.button == 1:
            if self.editor_state.current_tool == ToolType.SELECT:
                # Try to select an element at this position
                # Shift+click adds to selection (multi-select)
                shift_held = event.state & Gdk.ModifierType.SHIFT_MASK
                self.editor_state.select_at(
                    img_x, img_y, add_to_selection=bool(shift_held)
                )
                self.drawing_area.queue_draw()
                # Show quick actions panel if something was selected
                if self.editor_state.selected_indices:
                    GLib.timeout_add(150, self._show_quick_actions)
                else:
                    self._hide_quick_actions()
            elif self.editor_state.current_tool == ToolType.TEXT:
                # Show text input dialog
                self._show_text_dialog(img_x, img_y)
            elif self.editor_state.current_tool == ToolType.NUMBER:
                # Place number marker on click
                self.editor_state.add_number(img_x, img_y)
                self.drawing_area.queue_draw()
            elif self.editor_state.current_tool == ToolType.COLORPICKER:
                # Pick color from image
                self._pick_color(img_x, img_y)
            elif self.editor_state.current_tool == ToolType.STAMP:
                # Place stamp on click
                self.editor_state.add_stamp(img_x, img_y)
                self.drawing_area.queue_draw()
            elif self.editor_state.current_tool == ToolType.CALLOUT:
                # Start callout: first point is tail tip
                self._callout_tail = (img_x, img_y)
                self._callout_box = (img_x + 50, img_y - 50)  # Initial offset
                self.editor_state.is_drawing = True
            elif self.editor_state.current_tool == ToolType.CROP:
                # Start crop selection
                self._crop_start = (img_x, img_y)
                self._crop_end = (img_x, img_y)
                self._crop_shift = event.state & Gdk.ModifierType.SHIFT_MASK
                self.editor_state.is_drawing = True
            else:
                self.editor_state.start_drawing(img_x, img_y)
        elif event.button == 3:
            # Right-click: show radial menu
            self._show_radial_menu(event.x_root, event.y_root)
        return True

    def _on_button_release(
        self, widget: Gtk.Widget, event: Gdk.EventButton
    ) -> bool:
        """Handle mouse button release."""
        img_x, img_y = self._screen_to_image(event.x, event.y)
        if event.button == 1:
            if self.editor_state.current_tool == ToolType.SELECT:
                # Finish moving/resizing
                self.editor_state.finish_move()
                self.drawing_area.queue_draw()
            elif self.editor_state.current_tool == ToolType.CALLOUT:
                # Finish callout: show text dialog
                if hasattr(self, "_callout_tail"):
                    self._callout_box = (img_x, img_y)
                    self.editor_state.is_drawing = False
                    self._show_callout_dialog()
            elif self.editor_state.current_tool == ToolType.CROP:
                # Apply crop
                if hasattr(self, "_crop_start") and hasattr(self, "_crop_end"):
                    self.editor_state.is_drawing = False
                    self._apply_crop()
            elif self.editor_state.current_tool != ToolType.TEXT:
                self.editor_state.finish_drawing(img_x, img_y)
                self.drawing_area.queue_draw()
        return True

    def _handle_select_motion(self, img_x: float, img_y: float, shift: bool) -> None:
        """Handle motion for SELECT tool."""
        if self.editor_state._drag_start is not None:
            if self.editor_state.move_selected(img_x, img_y, aspect_locked=shift):
                self.drawing_area.queue_draw()
        else:
            self._update_resize_cursor(img_x, img_y)

    def _handle_crop_motion(self, img_x: float, img_y: float, shift: bool) -> None:
        """Handle motion for CROP tool."""
        if not hasattr(self, "_crop_start"):
            return
        if shift:
            dx, dy = img_x - self._crop_start[0], img_y - self._crop_start[1]
            size = max(abs(dx), abs(dy))
            self._crop_end = (
                self._crop_start[0] + (size if dx >= 0 else -size),
                self._crop_start[1] + (size if dy >= 0 else -size),
            )
        else:
            self._crop_end = (img_x, img_y)
        self.drawing_area.queue_draw()

    def _on_motion(self, widget: Gtk.Widget, event: Gdk.EventMotion) -> bool:
        """Handle mouse motion."""
        img_x, img_y = self._screen_to_image(event.x, event.y)
        shift = bool(event.state & Gdk.ModifierType.SHIFT_MASK)

        if self.editor_state.current_tool == ToolType.SELECT:
            self._handle_select_motion(img_x, img_y, shift)
            return True

        if self.editor_state.is_drawing:
            tool = self.editor_state.current_tool
            if tool == ToolType.CALLOUT and hasattr(self, "_callout_tail"):
                self._callout_box = (img_x, img_y)
                self.drawing_area.queue_draw()
            elif tool == ToolType.CROP:
                self._handle_crop_motion(img_x, img_y, shift)
            elif tool != ToolType.TEXT:
                self.editor_state.continue_drawing(img_x, img_y)
                self.drawing_area.queue_draw()
        return True

    def _on_scroll(self, widget: Gtk.Widget, event: Gdk.EventScroll) -> bool:
        """Handle scroll events for zooming."""
        # Only zoom when Ctrl is held or when Zoom tool is active
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        is_zoom_tool = self.editor_state.current_tool == ToolType.ZOOM

        if ctrl or is_zoom_tool:
            if event.direction == Gdk.ScrollDirection.UP:
                self.editor_state.zoom_in()
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.editor_state.zoom_out()
            elif event.direction == Gdk.ScrollDirection.SMOOTH:
                # Handle smooth scrolling (trackpads)
                _, dx, dy = event.get_scroll_deltas()
                if dy < 0:
                    self.editor_state.zoom_in(1.1)
                elif dy > 0:
                    self.editor_state.zoom_out(1.1)

            self._update_zoom_label()
            self.drawing_area.queue_draw()
            return True
        return False
