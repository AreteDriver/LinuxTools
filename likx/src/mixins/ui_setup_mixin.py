"""UI setup mixin for LikX EditorWindow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from ..editor import ArrowStyle, ToolType  # noqa: E402
from ..i18n import _  # noqa: E402
from ..minimap import MinimapNavigator  # noqa: E402
from ..onboarding import OnboardingManager  # noqa: E402
from ..quick_actions import QuickActionsPanel, create_selection_actions  # noqa: E402
from ..undo_history import UndoRedoButtons  # noqa: E402
from ..widgets.color_picker import InlineColorPicker  # noqa: E402

if TYPE_CHECKING:
    pass


class UISetupMixin:
    """Mixin providing UI widget creation for EditorWindow.

    This mixin expects the following attributes on the class:
    - window: Gtk.Window
    - editor_state: EditorState
    - result: CaptureResult (with pixbuf)
    - drawing_area: Gtk.DrawingArea
    - save_handler: SaveHandler

    And the following methods:
    - _on_tool_toggled(button, tool)
    - _on_arrow_style_toggled(button, style)
    - _on_font_family_changed(combo)
    - _on_bold_toggled(button)
    - _on_italic_toggled(button)
    - _on_size_changed(spin)
    - _set_color_rgb(r, g, b)
    - _undo(), _redo(), _undo_to(index), _redo_to(index)
    - _on_minimap_navigate(img_x, img_y)
    """

    def _init_cursors(self) -> None:
        """Initialize cursors for drawing tools."""
        display = Gdk.Display.get_default()
        self._arrow_cursor = Gdk.Cursor.new_from_name(display, "default")

        # Create crosshair cursor with centered hotspot
        try:
            import cairo

            size = 24
            center = size // 2

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
            cr = cairo.Context(surface)

            # Black outline
            cr.set_source_rgba(0, 0, 0, 1)
            cr.set_line_width(3)
            cr.move_to(center, 2)
            cr.line_to(center, size - 2)
            cr.stroke()
            cr.move_to(2, center)
            cr.line_to(size - 2, center)
            cr.stroke()

            # White center
            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_line_width(1)
            cr.move_to(center, 2)
            cr.line_to(center, size - 2)
            cr.stroke()
            cr.move_to(2, center)
            cr.line_to(size - 2, center)
            cr.stroke()

            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, size, size)
            self._crosshair_cursor = Gdk.Cursor.new_from_pixbuf(
                display, pixbuf, center, center
            )
        except ImportError:
            self._crosshair_cursor = Gdk.Cursor.new_from_name(display, "crosshair")

    def _update_cursor(self) -> None:
        """Update cursor based on current tool."""
        if not self.editor_state:
            return
        if not hasattr(self, "drawing_area") or not self.drawing_area.get_window():
            return

        drawing_tools = {
            ToolType.PEN,
            ToolType.HIGHLIGHTER,
            ToolType.LINE,
            ToolType.ARROW,
            ToolType.RECTANGLE,
            ToolType.ELLIPSE,
            ToolType.BLUR,
            ToolType.PIXELATE,
            ToolType.ERASER,
            ToolType.CALLOUT,
            ToolType.CROP,
        }

        if self.editor_state.current_tool in drawing_tools:
            self.drawing_area.get_window().set_cursor(self._crosshair_cursor)
        else:
            self.drawing_area.get_window().set_cursor(self._arrow_cursor)

    def _init_quick_actions_panel(self) -> None:
        """Initialize the quick actions floating panel."""
        self._quick_actions = QuickActionsPanel(self.window)
        self._quick_actions.set_actions(create_selection_actions(self))

    def _init_minimap(self) -> None:
        """Initialize the minimap navigator."""
        self._minimap = MinimapNavigator(
            self.drawing_area,
            on_navigate=self._on_minimap_navigate,
        )
        # Set initial image
        if self.result and self.result.pixbuf:
            self._minimap.set_image(self.result.pixbuf)
        # Initially hidden, shown when zoomed
        self._minimap.set_visible(False)
        self._minimap_visible = False

    def _init_onboarding(self) -> None:
        """Initialize and start onboarding if first run."""
        self._onboarding = OnboardingManager(self)
        if self._onboarding.should_show():
            self._onboarding.start()

    def _create_sidebar(self) -> Gtk.Box:
        """Create vertical tool sidebar."""
        css = b"""
        .sidebar {
            background: linear-gradient(180deg, #252536 0%, #1e1e2e 100%);
            border-right: 1px solid #3d3d5c;
            padding: 4px;
        }
        .sidebar-btn {
            min-width: 36px;
            min-height: 36px;
            padding: 4px;
            border: 1px solid transparent;
            border-radius: 6px;
            background: transparent;
            color: #c0c0d0;
            font-size: 14px;
        }
        .sidebar-btn:hover {
            background: rgba(100, 100, 180, 0.2);
            border-color: rgba(130, 130, 200, 0.4);
            color: #ffffff;
        }
        .sidebar-btn:checked {
            background: rgba(100, 130, 220, 0.35);
            border-color: #6688dd;
            color: #ffffff;
        }
        .sidebar-sep {
            background: rgba(100, 100, 140, 0.3);
            min-height: 1px;
            margin: 4px 2px;
        }
        """
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self._load_css(css),
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        sidebar.get_style_context().add_class("sidebar")

        self.tool_buttons = {}

        # Drawing tools group
        drawing_tools = [
            ("⊹", ToolType.SELECT, "Select (V)"),
            ("✎", ToolType.PEN, "Pen (P)"),
            ("▓", ToolType.HIGHLIGHTER, "Highlighter (H)"),
            ("—", ToolType.LINE, "Line (L)"),
            ("→", ToolType.ARROW, "Arrow (A)"),
            ("▭", ToolType.RECTANGLE, "Rectangle (R)"),
            ("○", ToolType.ELLIPSE, "Ellipse (E)"),
            ("A", ToolType.TEXT, "Text (T)"),
            ("💬", ToolType.CALLOUT, "Callout (K)"),
        ]
        for icon, tool, tip in drawing_tools:
            btn = Gtk.ToggleButton(label=icon)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("sidebar-btn")
            btn.connect("toggled", self._on_tool_toggled, tool)
            self.tool_buttons[tool] = btn
            sidebar.pack_start(btn, False, False, 0)

        # Separator
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep1.get_style_context().add_class("sidebar-sep")
        sidebar.pack_start(sep1, False, False, 2)

        # Privacy tools
        privacy_tools = [
            ("▦", ToolType.BLUR, "Blur (B)"),
            ("▤", ToolType.PIXELATE, "Pixelate (X)"),
        ]
        for icon, tool, tip in privacy_tools:
            btn = Gtk.ToggleButton(label=icon)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("sidebar-btn")
            btn.connect("toggled", self._on_tool_toggled, tool)
            self.tool_buttons[tool] = btn
            sidebar.pack_start(btn, False, False, 0)

        # Separator
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep2.get_style_context().add_class("sidebar-sep")
        sidebar.pack_start(sep2, False, False, 2)

        # Utility tools
        utility_tools = [
            ("✓", ToolType.STAMP, "Stamp (S)"),
            ("📏", ToolType.MEASURE, "Measure (M)"),
            ("①", ToolType.NUMBER, "Number (N)"),
            ("💧", ToolType.COLORPICKER, "Color Picker (I)"),
        ]
        for icon, tool, tip in utility_tools:
            btn = Gtk.ToggleButton(label=icon)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("sidebar-btn")
            btn.connect("toggled", self._on_tool_toggled, tool)
            self.tool_buttons[tool] = btn
            sidebar.pack_start(btn, False, False, 0)

        # Separator
        sep3 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep3.get_style_context().add_class("sidebar-sep")
        sidebar.pack_start(sep3, False, False, 2)

        # View/edit tools
        view_tools = [
            ("✂", ToolType.CROP, "Crop (C)"),
            ("🔍", ToolType.ZOOM, "Zoom (Z)"),
            ("✕", ToolType.ERASER, "Eraser"),
        ]
        for icon, tool, tip in view_tools:
            btn = Gtk.ToggleButton(label=icon)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("sidebar-btn")
            btn.connect("toggled", self._on_tool_toggled, tool)
            self.tool_buttons[tool] = btn
            sidebar.pack_start(btn, False, False, 0)

        # Default to pen tool
        self.tool_buttons[ToolType.PEN].set_active(True)

        return sidebar

    def _create_context_bar(self) -> Gtk.Box:
        """Create context-sensitive toolbar that adapts to active tool."""
        css = b"""
        .context-bar {
            background: linear-gradient(180deg, #252536 0%, #1e1e2e 100%);
            border-bottom: 1px solid #3d3d5c;
            padding: 4px 8px;
            min-height: 36px;
        }
        .context-group {
            padding: 0 4px;
        }
        .ctx-btn {
            min-width: 28px;
            min-height: 28px;
            padding: 2px 6px;
            border: 1px solid transparent;
            border-radius: 4px;
            background: transparent;
            color: #c0c0d0;
            font-size: 12px;
        }
        .ctx-btn:hover {
            background: rgba(100, 100, 180, 0.2);
            border-color: rgba(130, 130, 200, 0.4);
        }
        .ctx-btn:checked {
            background: rgba(100, 130, 220, 0.35);
            border-color: #6688dd;
        }
        .ctx-spin {
            background: rgba(35, 35, 50, 0.9);
            border: 1px solid rgba(80, 80, 120, 0.5);
            border-radius: 4px;
            color: #d0d0e0;
            padding: 2px 4px;
            min-width: 50px;
        }
        .ctx-label {
            color: #8888aa;
            font-size: 11px;
            margin-right: 4px;
        }
        .action-btn {
            min-width: 28px;
            min-height: 28px;
            padding: 2px 6px;
            border: 1px solid rgba(100, 180, 100, 0.4);
            border-radius: 4px;
            background: rgba(80, 160, 80, 0.15);
            color: #90d090;
            font-size: 13px;
        }
        .action-btn:hover {
            background: rgba(80, 180, 80, 0.3);
            border-color: rgba(100, 200, 100, 0.6);
            color: #ffffff;
        }
        .stamp-popover-btn {
            min-width: 32px;
            min-height: 32px;
            padding: 2px;
            font-size: 16px;
        }
        """
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self._load_css(css),
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.get_style_context().add_class("context-bar")

        # === SIZE GROUP (most tools use this) ===
        self.ctx_size_box = Gtk.Box(spacing=4)
        self.ctx_size_box.get_style_context().add_class("context-group")
        size_label = Gtk.Label(label=_("Size:"))
        size_label.get_style_context().add_class("ctx-label")
        self.ctx_size_box.pack_start(size_label, False, False, 0)
        self.size_spin = Gtk.SpinButton()
        self.size_spin.set_range(1, 50)
        self.size_spin.set_value(3)
        self.size_spin.set_increments(1, 5)
        self.size_spin.get_style_context().add_class("ctx-spin")
        self.size_spin.connect("value-changed", self._on_size_changed)
        self.ctx_size_box.pack_start(self.size_spin, False, False, 0)
        bar.pack_start(self.ctx_size_box, False, False, 0)

        # === INLINE HEX COLOR PICKER ===
        self.ctx_color_box = Gtk.Box(spacing=0)
        self.ctx_color_box.get_style_context().add_class("context-group")
        self.color_picker = InlineColorPicker(
            on_color_selected=self._set_color_rgb,
            get_recent_colors=lambda: (
                self.editor_state.get_recent_colors() if self.editor_state else []
            ),
            parent_window=self.window,
        )
        self.ctx_color_box.pack_start(self.color_picker.widget, False, False, 0)
        bar.pack_start(self.ctx_color_box, False, False, 0)

        # === ARROW STYLE GROUP ===
        self.ctx_arrow_box = Gtk.Box(spacing=2)
        self.ctx_arrow_box.get_style_context().add_class("context-group")
        self.arrow_style_buttons = {}
        for label, style, tip in [
            ("→", ArrowStyle.OPEN, "Open"),
            ("▶", ArrowStyle.FILLED, "Filled"),
            ("⟷", ArrowStyle.DOUBLE, "Double"),
        ]:
            btn = Gtk.ToggleButton(label=label)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("ctx-btn")
            btn.connect("toggled", self._on_arrow_style_toggled, style)
            self.arrow_style_buttons[style] = btn
            self.ctx_arrow_box.pack_start(btn, False, False, 0)
        self.arrow_style_buttons[ArrowStyle.OPEN].set_active(True)
        bar.pack_start(self.ctx_arrow_box, False, False, 0)

        # === TEXT STYLE GROUP ===
        self.ctx_text_box = Gtk.Box(spacing=4)
        self.ctx_text_box.get_style_context().add_class("context-group")
        self.font_combo = Gtk.ComboBoxText()
        for font in ["Sans", "Serif", "Monospace", "Ubuntu", "DejaVu Sans"]:
            self.font_combo.append_text(font)
        self.font_combo.set_active(0)
        self.font_combo.connect("changed", self._on_font_family_changed)
        self.ctx_text_box.pack_start(self.font_combo, False, False, 0)
        self.bold_btn = Gtk.ToggleButton(label="B")
        self.bold_btn.set_tooltip_text(_("Bold"))
        self.bold_btn.get_style_context().add_class("ctx-btn")
        self.bold_btn.connect("toggled", self._on_bold_toggled)
        self.ctx_text_box.pack_start(self.bold_btn, False, False, 0)
        self.italic_btn = Gtk.ToggleButton(label="I")
        self.italic_btn.set_tooltip_text(_("Italic"))
        self.italic_btn.get_style_context().add_class("ctx-btn")
        self.italic_btn.connect("toggled", self._on_italic_toggled)
        self.ctx_text_box.pack_start(self.italic_btn, False, False, 0)
        bar.pack_start(self.ctx_text_box, False, False, 0)

        # === STAMP SELECTOR GROUP ===
        self.ctx_stamp_box = Gtk.Box(spacing=2)
        self.ctx_stamp_box.get_style_context().add_class("context-group")
        self.stamp_buttons = {}
        self._create_stamp_popover()
        self.stamp_selector_btn = Gtk.Button(label="✓ ▾")
        self.stamp_selector_btn.set_tooltip_text(_("Select stamp"))
        self.stamp_selector_btn.get_style_context().add_class("ctx-btn")
        self.stamp_selector_btn.connect(
            "clicked", lambda b: self.stamp_popover.show_all()
        )
        self.ctx_stamp_box.pack_start(self.stamp_selector_btn, False, False, 0)
        bar.pack_start(self.ctx_stamp_box, False, False, 0)

        # Spacer
        bar.pack_start(Gtk.Box(), True, True, 0)

        # === EDIT GROUP (always visible) - Enhanced Undo/Redo ===
        self._undo_redo_buttons = UndoRedoButtons(
            on_undo=self._undo,
            on_redo=self._redo,
            on_undo_to=self._undo_to,
            on_redo_to=self._redo_to,
            get_undo_stack=lambda: (
                self.editor_state.undo_stack if self.editor_state else []
            ),
            get_redo_stack=lambda: (
                self.editor_state.redo_stack if self.editor_state else []
            ),
            get_elements=lambda: (
                self.editor_state.elements if self.editor_state else []
            ),
        )
        bar.pack_start(self._undo_redo_buttons.get_widget(), False, False, 0)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_start(4)
        sep.set_margin_end(4)
        bar.pack_start(sep, False, False, 0)

        # === OUTPUT GROUP (always visible) ===
        out_box = Gtk.Box(spacing=4)
        for icon, cb, tip in [
            ("💾", lambda w: self.save_handler.save(), "Save"),
            ("📋", lambda w: self.save_handler.copy_to_clipboard(), "Copy"),
            ("☁", lambda w: self.save_handler.upload(), "Upload"),
        ]:
            btn = Gtk.Button(label=icon)
            btn.set_tooltip_text(tip)
            btn.get_style_context().add_class("action-btn")
            btn.connect("clicked", lambda b, c=cb: c())
            out_box.pack_start(btn, False, False, 0)
        bar.pack_start(out_box, False, False, 0)

        return bar

    def _refresh_recent_colors(self) -> None:
        """Refresh the recent colors display."""
        if hasattr(self, "color_picker"):
            self.color_picker.refresh_recent_colors()

    def _create_stamp_popover(self) -> None:
        """Create stamp selector popover."""
        self.stamp_popover = Gtk.Popover()
        self.stamp_popover.set_relative_to(self.ctx_stamp_box)

        pop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        pop_box.set_margin_start(8)
        pop_box.set_margin_end(8)
        pop_box.set_margin_top(8)
        pop_box.set_margin_bottom(8)

        stamp_rows = [
            ["✓", "✗", "⚠", "❓", "⭐", "❤", "👍", "👎"],
            ["➡", "⬆", "⬇", "⬅", "●", "■", "▲", "ℹ"],
        ]
        for row_stamps in stamp_rows:
            row_box = Gtk.Box(spacing=2)
            for stamp in row_stamps:
                btn = Gtk.Button(label=stamp)
                btn.set_tooltip_text(f"Stamp: {stamp}")
                btn.get_style_context().add_class("stamp-popover-btn")
                btn.connect("clicked", self._on_stamp_selected, stamp)
                self.stamp_buttons[stamp] = btn
                row_box.pack_start(btn, False, False, 0)
            pop_box.pack_start(row_box, False, False, 0)

        self.stamp_popover.add(pop_box)
        self.current_stamp = "✓"
        if self.editor_state:
            self.editor_state.set_stamp(self.current_stamp)

    def _on_stamp_selected(self, button: Gtk.Button, stamp: str) -> None:
        """Handle stamp selection from popover."""
        self.current_stamp = stamp
        self.editor_state.set_stamp(stamp)
        self.stamp_selector_btn.set_label(f"{stamp} ▾")
        self.stamp_popover.popdown()

    def _update_context_bar(self) -> None:
        """Update context bar visibility based on current tool."""
        if not self.editor_state:
            return
        tool = self.editor_state.current_tool

        # Tools that use size
        size_tools = {
            ToolType.PEN,
            ToolType.HIGHLIGHTER,
            ToolType.LINE,
            ToolType.ARROW,
            ToolType.RECTANGLE,
            ToolType.ELLIPSE,
            ToolType.BLUR,
            ToolType.PIXELATE,
            ToolType.ERASER,
        }
        # Tools that use color
        color_tools = {
            ToolType.PEN,
            ToolType.HIGHLIGHTER,
            ToolType.LINE,
            ToolType.ARROW,
            ToolType.RECTANGLE,
            ToolType.ELLIPSE,
            ToolType.TEXT,
            ToolType.CALLOUT,
            ToolType.NUMBER,
        }

        self.ctx_size_box.set_visible(tool in size_tools)
        self.ctx_color_box.set_visible(tool in color_tools)
        self.ctx_arrow_box.set_visible(tool == ToolType.ARROW)
        self.ctx_text_box.set_visible(tool in {ToolType.TEXT, ToolType.CALLOUT})
        self.ctx_stamp_box.set_visible(tool == ToolType.STAMP)

    def _load_css(self, css: bytes) -> Gtk.CssProvider:
        """Load CSS into a provider."""
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        return provider

    def _create_separator(self) -> Gtk.Separator:
        """Create a vertical separator."""
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.get_style_context().add_class("toolbar-separator")
        return sep
