"""Minimap Navigator for LikX.

A small semi-transparent minimap showing the full image with viewport indicator.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable, Optional, Tuple

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GdkPixbuf, Gtk

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False

if TYPE_CHECKING:
    pass  # Types imported for documentation only

# Module-level flag to prevent CSS provider accumulation
_css_applied = False


class MinimapNavigator:
    """A small minimap overlay showing the full image with viewport and annotations."""

    # Minimap sizing
    MAX_WIDTH = 180
    MAX_HEIGHT = 120
    MARGIN = 12
    OPACITY = 0.85

    def __init__(
        self,
        parent_widget: Gtk.Widget,
        on_navigate: Callable[[float, float], None],
    ):
        """Initialize the minimap.

        Args:
            parent_widget: The parent drawing area widget
            on_navigate: Callback when user clicks minimap (receives center x, y in image coords)
        """
        if not GTK_AVAILABLE:
            raise RuntimeError("GTK is not available")

        self.parent_widget = parent_widget
        self.on_navigate = on_navigate
        self.visible = True
        self._dragging = False

        # Image data
        self._pixbuf: Optional[GdkPixbuf.Pixbuf] = None
        self._scaled_pixbuf: Optional[GdkPixbuf.Pixbuf] = None
        self._scale = 1.0
        self._minimap_width = 0
        self._minimap_height = 0

        # Viewport rectangle (in image coordinates)
        self._viewport_x = 0.0
        self._viewport_y = 0.0
        self._viewport_w = 0.0
        self._viewport_h = 0.0

        # Annotation markers
        self._annotation_positions: list[Tuple[float, float]] = []

        # Create overlay drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(self.MAX_WIDTH, self.MAX_HEIGHT)
        self.drawing_area.connect("draw", self._on_draw)
        self.drawing_area.connect("button-press-event", self._on_button_press)
        self.drawing_area.connect("button-release-event", self._on_button_release)
        self.drawing_area.connect("motion-notify-event", self._on_motion)

        self.drawing_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        self._apply_styles()

    def _apply_styles(self) -> None:
        """Apply CSS styles (only once per process)."""
        global _css_applied
        if _css_applied:
            return
        _css_applied = True

        css = b"""
        .minimap-container {
            background: rgba(20, 20, 30, 0.85);
            border: 1px solid rgba(100, 100, 150, 0.5);
            border-radius: 8px;
            padding: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def set_image(self, pixbuf: GdkPixbuf.Pixbuf) -> None:
        """Set the source image for the minimap.

        Args:
            pixbuf: The full-size image pixbuf
        """
        self._pixbuf = pixbuf

        # Calculate scale to fit in max dimensions
        img_w = pixbuf.get_width()
        img_h = pixbuf.get_height()

        # Guard against zero-dimension images to prevent division by zero
        if img_w <= 0 or img_h <= 0:
            return

        scale_w = self.MAX_WIDTH / img_w
        scale_h = self.MAX_HEIGHT / img_h
        self._scale = min(scale_w, scale_h)

        self._minimap_width = int(img_w * self._scale)
        self._minimap_height = int(img_h * self._scale)

        # Create scaled thumbnail
        self._scaled_pixbuf = pixbuf.scale_simple(
            self._minimap_width,
            self._minimap_height,
            GdkPixbuf.InterpType.BILINEAR,
        )

        self.drawing_area.set_size_request(
            self._minimap_width + 8,
            self._minimap_height + 8,
        )
        self.drawing_area.queue_draw()

    def set_viewport(self, x: float, y: float, width: float, height: float) -> None:
        """Set the current viewport rectangle (in image coordinates).

        Args:
            x, y: Top-left corner of viewport
            width, height: Size of viewport
        """
        self._viewport_x = x
        self._viewport_y = y
        self._viewport_w = width
        self._viewport_h = height
        self.drawing_area.queue_draw()

    def set_annotations(self, elements: list) -> None:
        """Set annotation marker positions.

        Args:
            elements: List of DrawingElement objects
        """
        self._annotation_positions = []
        for elem in elements:
            if elem.points:
                # Use center of element
                xs = [p.x for p in elem.points]
                ys = [p.y for p in elem.points]
                cx = (min(xs) + max(xs)) / 2
                cy = (min(ys) + max(ys)) / 2
                self._annotation_positions.append((cx, cy))
        self.drawing_area.queue_draw()

    def set_visible(self, visible: bool) -> None:
        """Show or hide the minimap."""
        self.visible = visible
        if visible:
            self.drawing_area.show()
        else:
            self.drawing_area.hide()

    def toggle_visible(self) -> bool:
        """Toggle visibility and return new state."""
        self.visible = not self.visible
        self.set_visible(self.visible)
        return self.visible

    def _on_draw(self, widget: Gtk.Widget, cr) -> bool:
        """Draw the minimap."""
        if not self._scaled_pixbuf:
            return True

        try:
            import cairo  # noqa: F401 - needed for Gdk cairo functions
        except ImportError:
            return True

        # Background
        cr.set_source_rgba(0.08, 0.08, 0.12, self.OPACITY)
        cr.paint()

        # Draw scaled image
        Gdk.cairo_set_source_pixbuf(cr, self._scaled_pixbuf, 4, 4)
        cr.paint()

        # Draw annotation markers
        if self._annotation_positions:
            cr.set_source_rgba(1.0, 0.5, 0.2, 0.9)  # Orange markers
            for ax, ay in self._annotation_positions:
                # Convert to minimap coordinates
                mx = 4 + ax * self._scale
                my = 4 + ay * self._scale
                cr.arc(mx, my, 3, 0, 2 * math.pi)
                cr.fill()

        # Draw viewport rectangle
        if self._viewport_w > 0 and self._viewport_h > 0:
            vx = 4 + self._viewport_x * self._scale
            vy = 4 + self._viewport_y * self._scale
            vw = self._viewport_w * self._scale
            vh = self._viewport_h * self._scale

            # Clamp to minimap bounds
            vx = max(4, min(vx, 4 + self._minimap_width - 2))
            vy = max(4, min(vy, 4 + self._minimap_height - 2))
            vw = min(vw, self._minimap_width - (vx - 4))
            vh = min(vh, self._minimap_height - (vy - 4))

            # Semi-transparent fill
            cr.set_source_rgba(0.4, 0.6, 1.0, 0.2)
            cr.rectangle(vx, vy, vw, vh)
            cr.fill()

            # Border
            cr.set_source_rgba(0.4, 0.6, 1.0, 0.9)
            cr.set_line_width(1.5)
            cr.rectangle(vx, vy, vw, vh)
            cr.stroke()

        # Border around minimap
        cr.set_source_rgba(0.4, 0.4, 0.5, 0.6)
        cr.set_line_width(1)
        cr.rectangle(3, 3, self._minimap_width + 2, self._minimap_height + 2)
        cr.stroke()

        return True

    def _on_button_press(self, widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        """Handle mouse press on minimap."""
        if event.button == 1:
            self._dragging = True
            self._navigate_to(event.x, event.y)
        return True

    def _on_button_release(self, widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        """Handle mouse release."""
        if event.button == 1:
            self._dragging = False
        return True

    def _on_motion(self, widget: Gtk.Widget, event: Gdk.EventMotion) -> bool:
        """Handle mouse motion for dragging."""
        if self._dragging:
            self._navigate_to(event.x, event.y)
        return True

    def _navigate_to(self, mx: float, my: float) -> None:
        """Navigate to the clicked position.

        Args:
            mx, my: Minimap coordinates
        """
        if not self._pixbuf:
            return

        # Convert minimap coords to image coords
        img_x = (mx - 4) / self._scale
        img_y = (my - 4) / self._scale

        # Clamp to image bounds
        img_w = self._pixbuf.get_width()
        img_h = self._pixbuf.get_height()
        img_x = max(0, min(img_x, img_w))
        img_y = max(0, min(img_y, img_h))

        self.on_navigate(img_x, img_y)


def create_minimap_overlay(
    parent_container: Gtk.Widget,
    drawing_area: Gtk.Widget,
    on_navigate: Callable[[float, float], None],
) -> MinimapNavigator:
    """Create a minimap overlay positioned in the corner of the drawing area.

    Args:
        parent_container: Container widget to add minimap to
        drawing_area: The main drawing area
        on_navigate: Callback for navigation

    Returns:
        MinimapNavigator instance
    """
    minimap = MinimapNavigator(drawing_area, on_navigate)

    # Create an overlay to position minimap
    if isinstance(parent_container, Gtk.Overlay):
        # Add minimap to overlay
        minimap.drawing_area.set_halign(Gtk.Align.END)
        minimap.drawing_area.set_valign(Gtk.Align.END)
        minimap.drawing_area.set_margin_end(MinimapNavigator.MARGIN)
        minimap.drawing_area.set_margin_bottom(MinimapNavigator.MARGIN)
        parent_container.add_overlay(minimap.drawing_area)
    else:
        # Fallback: just return the minimap for manual positioning
        pass

    return minimap
