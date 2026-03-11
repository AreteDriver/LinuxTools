"""Drawing mixin for LikX EditorWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk  # noqa: E402

from ..editor import ToolType, render_elements  # noqa: E402

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk


class DrawingMixin:
    """Mixin providing drawing/rendering methods for EditorWindow.

    This mixin expects the following attributes on the class:
    - editor_state: EditorState
    - result: CaptureResult (with pixbuf)
    - drawing_area: Gtk.DrawingArea
    - _callout_tail: Tuple[float, float] (optional, during callout creation)
    - _callout_box: Tuple[float, float] (optional, during callout creation)
    - _crop_start: Tuple[float, float] (optional, during crop)
    - _crop_end: Tuple[float, float] (optional, during crop)
    """

    def _on_draw(self, widget: Gtk.Widget, cr) -> bool:
        """Draw the screenshot and annotations with zoom support."""
        zoom = self.editor_state.zoom_level

        # Update drawing area size based on zoom
        base_width = self.result.pixbuf.get_width()
        base_height = self.result.pixbuf.get_height()
        new_width = int(base_width * zoom)
        new_height = int(base_height * zoom)
        self.drawing_area.set_size_request(new_width, new_height)

        # Apply zoom transform
        cr.scale(zoom, zoom)

        # Draw the image
        Gdk.cairo_set_source_pixbuf(cr, self.result.pixbuf, 0, 0)
        cr.paint()

        # Draw grid overlay if enabled (drawn before elements)
        self._draw_grid(cr)

        # Draw annotations (also scaled)
        elements = self.editor_state.get_elements()
        if elements:
            render_elements(cr, elements, self.result.pixbuf)

        # Draw callout preview during drag
        if (
            self.editor_state.is_drawing
            and self.editor_state.current_tool == ToolType.CALLOUT
            and hasattr(self, "_callout_tail")
            and hasattr(self, "_callout_box")
        ):
            self._draw_callout_preview(cr)

        # Draw crop selection preview
        if (
            self.editor_state.is_drawing
            and self.editor_state.current_tool == ToolType.CROP
            and hasattr(self, "_crop_start")
            and hasattr(self, "_crop_end")
        ):
            self._draw_crop_preview(cr)

        # Draw selection handles if an element is selected
        if self.editor_state.selected_index is not None:
            self._draw_selection_handles(cr)
            self._draw_snap_guides(cr)

        return True

    def _draw_callout_preview(self, cr) -> None:
        """Draw a preview of the callout being created."""
        tail_x, tail_y = self._callout_tail
        box_x, box_y = self._callout_box

        # Draw a simple preview box and line
        preview_text = "Click & drag to position"
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(14)
        extents = cr.text_extents(preview_text)

        padding = 10
        box_width = extents.width + padding * 2
        box_height = extents.height + padding * 2
        corner_radius = 8

        # Box position (centered on box position)
        bx = box_x - box_width / 2
        by = box_y - box_height / 2

        # Draw rounded rectangle
        cr.new_path()
        cr.move_to(bx + corner_radius, by)
        cr.line_to(bx + box_width - corner_radius, by)
        cr.arc(
            bx + box_width - corner_radius,
            by + corner_radius,
            corner_radius,
            -3.14159 / 2,
            0,
        )
        cr.line_to(bx + box_width, by + box_height - corner_radius)
        cr.arc(
            bx + box_width - corner_radius,
            by + box_height - corner_radius,
            corner_radius,
            0,
            3.14159 / 2,
        )
        cr.line_to(bx + corner_radius, by + box_height)
        cr.arc(
            bx + corner_radius,
            by + box_height - corner_radius,
            corner_radius,
            3.14159 / 2,
            3.14159,
        )
        cr.line_to(bx, by + corner_radius)
        cr.arc(
            bx + corner_radius,
            by + corner_radius,
            corner_radius,
            3.14159,
            3 * 3.14159 / 2,
        )
        cr.close_path()

        # Fill with light yellow (preview)
        cr.set_source_rgba(1.0, 1.0, 0.9, 0.8)
        cr.fill_preserve()

        # Border
        r, g, b, a = self.editor_state.current_color.to_tuple()
        cr.set_source_rgba(r, g, b, 0.8)
        cr.set_line_width(2)
        cr.stroke()

        # Draw tail line from box to point
        cr.move_to(box_x, box_y)
        cr.line_to(tail_x, tail_y)
        cr.stroke()

        # Draw a small circle at tail tip
        cr.arc(tail_x, tail_y, 4, 0, 2 * 3.14159)
        cr.fill()

        # Draw preview text
        cr.set_source_rgba(0.3, 0.3, 0.3, 0.8)
        cr.move_to(bx + padding, by + padding + extents.height)
        cr.show_text(preview_text)

    def _draw_crop_preview(self, cr) -> None:
        """Draw the crop selection rectangle with darkened outside area."""
        x1, y1 = self._crop_start
        x2, y2 = self._crop_end

        # Normalize coordinates
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top

        if width < 2 or height < 2:
            return

        # Get image dimensions
        img_w = self.result.pixbuf.get_width()
        img_h = self.result.pixbuf.get_height()

        # Darken areas outside selection
        cr.set_source_rgba(0, 0, 0, 0.5)
        # Top
        cr.rectangle(0, 0, img_w, top)
        cr.fill()
        # Bottom
        cr.rectangle(0, bottom, img_w, img_h - bottom)
        cr.fill()
        # Left
        cr.rectangle(0, top, left, height)
        cr.fill()
        # Right
        cr.rectangle(right, top, img_w - right, height)
        cr.fill()

        # Draw selection border
        cr.set_source_rgba(1, 1, 1, 0.9)
        cr.set_line_width(2)
        cr.rectangle(left, top, width, height)
        cr.stroke()

        # Draw corner handles
        handle_size = 8
        cr.set_source_rgba(1, 1, 1, 1)
        for hx, hy in [(left, top), (right, top), (left, bottom), (right, bottom)]:
            cr.rectangle(hx - handle_size / 2, hy - handle_size / 2, handle_size, handle_size)
            cr.fill()

        # Draw dimension text
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(12)
        dim_text = f"{int(width)} × {int(height)}"
        extents = cr.text_extents(dim_text)

        # Position below selection
        tx = left + (width - extents.width) / 2
        ty = bottom + 20

        # Background for text
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.rectangle(tx - 4, ty - extents.height - 2, extents.width + 8, extents.height + 6)
        cr.fill()

        # Text
        cr.set_source_rgba(1, 1, 1, 1)
        cr.move_to(tx, ty)
        cr.show_text(dim_text)

    def _draw_selection_handles(self, cr) -> None:
        """Draw selection bounding box and resize handles for selected elements."""
        if not self.editor_state.selected_indices:
            return

        # Draw selection box for each selected element
        for idx in self.editor_state.selected_indices:
            if 0 <= idx < len(self.editor_state.elements):
                elem = self.editor_state.elements[idx]
                bbox = self.editor_state._get_element_bbox(elem)
                if not bbox:
                    continue

                x1, y1, x2, y2 = bbox

                # Draw selection rectangle (dashed blue, or red if locked)
                if elem.locked:
                    cr.set_source_rgba(0.8, 0.2, 0.2, 0.8)  # Red for locked
                else:
                    cr.set_source_rgba(0.2, 0.5, 1.0, 0.8)  # Blue for unlocked
                cr.set_line_width(1.5)
                cr.set_dash([4, 4])
                cr.rectangle(x1, y1, x2 - x1, y2 - y1)
                cr.stroke()
                cr.set_dash([])  # Reset dash

                # Draw lock indicator for locked elements
                if elem.locked:
                    self._draw_lock_indicator(cr, x2 - 8, y1 + 8)

        # Draw resize handles only for single selection
        if len(self.editor_state.selected_indices) == 1:
            idx = next(iter(self.editor_state.selected_indices))
            elem = self.editor_state.elements[idx]
            bbox = self.editor_state._get_element_bbox(elem)
            if bbox:
                x1, y1, x2, y2 = bbox
                handle_size = 8
                handles = [
                    (x1, y1),  # nw
                    (x2, y1),  # ne
                    (x1, y2),  # sw
                    (x2, y2),  # se
                ]

                for hx, hy in handles:
                    # White fill with blue border
                    cr.set_source_rgba(1, 1, 1, 1)
                    cr.rectangle(
                        hx - handle_size / 2,
                        hy - handle_size / 2,
                        handle_size,
                        handle_size,
                    )
                    cr.fill_preserve()
                    cr.set_source_rgba(0.2, 0.5, 1.0, 1)
                    cr.set_line_width(1)
                    cr.stroke()

    def _draw_snap_guides(self, cr) -> None:
        """Draw visual snap guides when dragging an element."""
        if not self.editor_state.active_snap_guides:
            return

        # Get drawing area size for guide lines
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()

        # Draw snap guides in cyan dashed lines
        cr.set_source_rgba(0.0, 0.8, 0.8, 0.9)
        cr.set_line_width(1)
        cr.set_dash([6, 4])

        for guide_type, value in self.editor_state.active_snap_guides:
            if guide_type == "h":
                # Horizontal line at y=value
                cr.move_to(0, value)
                cr.line_to(width, value)
                cr.stroke()
            elif guide_type == "v":
                # Vertical line at x=value
                cr.move_to(value, 0)
                cr.line_to(value, height)
                cr.stroke()

        cr.set_dash([])  # Reset dash

    def _draw_grid(self, cr) -> None:
        """Draw grid overlay when grid snap is enabled."""
        if not self.editor_state.grid_snap_enabled:
            return

        grid_size = self.editor_state.grid_size
        width = self.result.pixbuf.get_width()
        height = self.result.pixbuf.get_height()

        # Light gray grid lines
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.3)
        cr.set_line_width(0.5)

        # Vertical lines
        x = grid_size
        while x < width:
            cr.move_to(x, 0)
            cr.line_to(x, height)
            x += grid_size
        cr.stroke()

        # Horizontal lines
        y = grid_size
        while y < height:
            cr.move_to(0, y)
            cr.line_to(width, y)
            y += grid_size
        cr.stroke()

    def _draw_lock_indicator(self, cr, x: float, y: float) -> None:
        """Draw a small lock icon at the given position."""
        # Lock icon: small padlock shape
        size = 12
        lx = x - size / 2
        ly = y - size / 2

        # Shackle (arc at top)
        cr.set_source_rgba(0.8, 0.2, 0.2, 0.9)
        cr.set_line_width(2)
        cr.arc(lx + size / 2, ly + 4, 4, 3.14159, 0)
        cr.stroke()

        # Body (rectangle)
        cr.rectangle(lx + 2, ly + 4, size - 4, size - 4)
        cr.fill()

        # Keyhole (small circle)
        cr.set_source_rgba(1, 1, 1, 1)
        cr.arc(lx + size / 2, ly + 8, 1.5, 0, 2 * 3.14159)
        cr.fill()
