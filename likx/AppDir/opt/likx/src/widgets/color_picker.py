"""Inline hexagonal color picker widget for LikX editor."""

from __future__ import annotations

import math
from typing import Callable, List, Optional, Tuple

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from ..editor import Color  # noqa: E402
from ..i18n import _  # noqa: E402


class InlineColorPicker:
    """Hexagonal color palette with recent colors bar.

    A compact color picker widget designed for toolbar integration.
    Features:
    - 19 preset colors in honeycomb layout
    - Custom color picker (rainbow hex)
    - Recent colors bar (up to 8 colors)
    """

    # Default color palette - 19 colors
    DEFAULT_PALETTE: List[Tuple[float, float, float]] = [
        # Row 0 (10 hexes): grays + warm colors
        (0, 0, 0),
        (0.4, 0.4, 0.4),
        (0.75, 0.75, 0.75),
        (1, 1, 1),
        (0.5, 0, 0),
        (1, 0, 0),
        (1, 0.5, 0),
        (1, 1, 0),
        (0.5, 0.5, 0),
        (0, 0.5, 0),
        # Row 1 (9 hexes): cool colors
        (0, 0.8, 0),
        (0, 0.8, 0.8),
        (0, 0.5, 0.5),
        (0, 0, 0.5),
        (0, 0, 1),
        (0.3, 0, 0.5),
        (0.6, 0.3, 1),
        (1, 0.4, 0.7),
        (0.5, 0, 0.3),
    ]

    def __init__(
        self,
        on_color_selected: Callable[[float, float, float], None],
        get_recent_colors: Callable[[], List[Color]],
        parent_window: Optional[Gtk.Window] = None,
    ):
        """Initialize the color picker.

        Args:
            on_color_selected: Callback when a color is selected (r, g, b)
            get_recent_colors: Callback to get list of recent Color objects
            parent_window: Parent window for color chooser dialog
        """
        self._on_color_selected = on_color_selected
        self._get_recent_colors = get_recent_colors
        self._parent_window = parent_window

        self._hex_palette = list(self.DEFAULT_PALETTE)
        self._custom_color = (0.5, 0.5, 0.5)
        self._custom_hex_idx = 19  # Index for custom color picker hex
        self._hex_size = 9  # Small for toolbar
        self._hex_positions: List[Tuple[float, float, int]] = []
        self._selected_hex_idx = 5  # Default to red

        self._build_hex_positions()
        self._setup_widgets()

    def _build_hex_positions(self) -> None:
        """Calculate center positions for each hexagon in 2-row honeycomb layout."""
        size = self._hex_size
        hex_w = size * math.sqrt(3)  # Exact honeycomb horizontal spacing
        hex_h = size * 1.5  # Exact honeycomb vertical spacing

        # 2-row layout: 10 hexes on top, 10 hexes below (offset) - last is custom
        row_counts = [10, 10]
        color_idx = 0

        for row, count in enumerate(row_counts):
            # Offset odd rows for honeycomb effect
            x_offset = (hex_w / 2) if row % 2 == 1 else 0
            start_x = size + x_offset

            for col in range(count):
                cx = start_x + col * hex_w
                cy = size + row * hex_h
                self._hex_positions.append((cx, cy, color_idx))
                color_idx += 1

    def _setup_widgets(self) -> None:
        """Create the color picker widgets."""
        hex_w = self._hex_size * math.sqrt(3)
        hex_h = self._hex_size * 1.5
        canvas_w = int(hex_w * 10.5 + self._hex_size)
        canvas_h = int(hex_h * 2 + self._hex_size)

        # Create vertical container for hex picker + recent colors
        self._container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Hexagon drawing area
        self._hex_canvas = Gtk.DrawingArea()
        self._hex_canvas.set_size_request(canvas_w, canvas_h)
        self._hex_canvas.connect("draw", self._draw_hex_palette)
        self._hex_canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._hex_canvas.connect("button-press-event", self._on_hex_click)
        self._container.pack_start(self._hex_canvas, False, False, 0)

        # Recent colors bar
        self._recent_colors_bar = Gtk.DrawingArea()
        self._recent_colors_bar.set_size_request(canvas_w, 16)
        self._recent_colors_bar.connect("draw", self._draw_recent_colors)
        self._recent_colors_bar.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self._recent_colors_bar.connect("button-press-event", self._on_recent_color_click)
        self._container.pack_start(self._recent_colors_bar, False, False, 0)

    @property
    def widget(self) -> Gtk.Box:
        """Get the container widget to add to toolbar."""
        return self._container

    def get_selected_index(self) -> int:
        """Get the currently selected hex index."""
        return self._selected_hex_idx

    def set_selected_index(self, idx: int) -> None:
        """Set the selected hex index and redraw."""
        self._selected_hex_idx = idx
        self._hex_canvas.queue_draw()

    def refresh(self) -> None:
        """Refresh all color picker displays."""
        self._container.queue_draw()

    def refresh_recent_colors(self) -> None:
        """Refresh just the recent colors bar."""
        self._recent_colors_bar.queue_draw()

    def _draw_hex_palette(self, widget: Gtk.DrawingArea, cr) -> bool:
        """Draw hexagonal color palette with selection indicator."""
        import cairo

        size = self._hex_size

        for cx, cy, idx in self._hex_positions:
            is_custom = idx == self._custom_hex_idx
            is_selected = idx == self._selected_hex_idx

            cr.save()
            cr.translate(cx, cy)

            # Create hexagon path (pointy-top orientation)
            cr.move_to(0, -size)
            for i in range(1, 6):
                angle = math.pi / 3 * i - math.pi / 2
                cr.line_to(size * math.cos(angle), size * math.sin(angle))
            cr.close_path()

            if is_custom:
                # Draw rainbow gradient for custom color picker
                gradient = cairo.LinearGradient(-size, 0, size, 0)
                gradient.add_color_stop_rgb(0.0, 1, 0, 0)  # Red
                gradient.add_color_stop_rgb(0.17, 1, 0.5, 0)  # Orange
                gradient.add_color_stop_rgb(0.33, 1, 1, 0)  # Yellow
                gradient.add_color_stop_rgb(0.5, 0, 1, 0)  # Green
                gradient.add_color_stop_rgb(0.67, 0, 0.5, 1)  # Blue
                gradient.add_color_stop_rgb(0.83, 0.5, 0, 1)  # Indigo
                gradient.add_color_stop_rgb(1.0, 1, 0, 0.5)  # Violet
                cr.set_source(gradient)
            else:
                # Regular preset color
                if idx < len(self._hex_palette):
                    r, g, b = self._hex_palette[idx]
                else:
                    r, g, b = 0.5, 0.5, 0.5
                cr.set_source_rgb(r, g, b)

            cr.fill_preserve()

            # Draw border - highlight selected
            if is_selected:
                cr.set_source_rgba(1, 1, 1, 0.9)
                cr.set_line_width(2)
            else:
                cr.set_source_rgba(0.2, 0.2, 0.2, 0.6)
                cr.set_line_width(1)
            cr.stroke()

            cr.restore()

        return True

    def _on_hex_click(self, widget: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        """Handle click on hexagonal color palette."""
        x, y = event.x, event.y
        size = self._hex_size

        # Find which hexagon was clicked
        for cx, cy, idx in self._hex_positions:
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist < size * 0.9:
                if idx == self._custom_hex_idx:
                    # Open color chooser dialog
                    self._open_color_chooser()
                elif idx < len(self._hex_palette):
                    r, g, b = self._hex_palette[idx]
                    self._selected_hex_idx = idx
                    self._on_color_selected(r, g, b)
                    self._hex_canvas.queue_draw()
                return True

        return False

    def _open_color_chooser(self) -> None:
        """Open GTK color chooser dialog for custom color."""
        dialog = Gtk.ColorChooserDialog(title=_("Choose Color"))
        if self._parent_window:
            dialog.set_transient_for(self._parent_window)
        dialog.set_use_alpha(False)

        # Set current custom color as starting point
        r, g, b = self._custom_color
        rgba = Gdk.RGBA(red=r, green=g, blue=b, alpha=1.0)
        dialog.set_rgba(rgba)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            rgba = dialog.get_rgba()
            self._custom_color = (rgba.red, rgba.green, rgba.blue)
            self._selected_hex_idx = self._custom_hex_idx
            self._on_color_selected(rgba.red, rgba.green, rgba.blue)
            self._container.queue_draw()

        dialog.destroy()

    def _draw_recent_colors(self, widget: Gtk.DrawingArea, cr) -> bool:
        """Draw the recent colors bar below the hex picker."""
        recent = self._get_recent_colors()
        if not recent:
            # Draw placeholder text
            cr.set_source_rgba(0.5, 0.5, 0.6, 0.6)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(9)
            cr.move_to(4, 11)
            cr.show_text(_("Recent colors appear here"))
            return True

        # Draw recent color swatches
        swatch_size = 14
        spacing = 2
        x = 4

        for color in recent[:8]:  # Max 8 recent colors
            # Draw swatch background (for dark colors visibility)
            cr.set_source_rgba(0.3, 0.3, 0.4, 0.5)
            cr.rectangle(x - 1, 0, swatch_size + 2, swatch_size + 2)
            cr.fill()

            # Draw color swatch
            cr.set_source_rgb(color.r, color.g, color.b)
            cr.rectangle(x, 1, swatch_size, swatch_size)
            cr.fill()

            # Draw border
            cr.set_source_rgba(0.6, 0.6, 0.7, 0.8)
            cr.set_line_width(1)
            cr.rectangle(x, 1, swatch_size, swatch_size)
            cr.stroke()

            x += swatch_size + spacing

        return True

    def _on_recent_color_click(self, widget: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        """Handle click on recent colors bar."""
        recent = self._get_recent_colors()
        if not recent:
            return False

        swatch_size = 14
        spacing = 2
        x = 4

        for color in recent[:8]:
            if x <= event.x <= x + swatch_size and 1 <= event.y <= 1 + swatch_size:
                self._on_color_selected(color.r, color.g, color.b)
                self._selected_hex_idx = -1  # Deselect preset colors
                self._container.queue_draw()
                return True
            x += swatch_size + spacing

        return False


def draw_color_dot(cr, r: float, g: float, b: float) -> bool:
    """Draw a color dot (calls draw_neo_color)."""
    return draw_neo_color(cr, r, g, b)


def draw_neo_color(cr, r: float, g: float, b: float) -> bool:
    """Draw a futuristic color circle with glow effect."""
    # Outer glow
    cr.set_source_rgba(r, g, b, 0.3)
    cr.arc(9, 9, 9, 0, math.pi * 2)
    cr.fill()
    # Main color
    cr.set_source_rgb(r, g, b)
    cr.arc(9, 9, 7, 0, math.pi * 2)
    cr.fill()
    # Inner highlight
    cr.set_source_rgba(1, 1, 1, 0.3)
    cr.arc(7, 7, 3, 0, math.pi * 2)
    cr.fill()
    return True
