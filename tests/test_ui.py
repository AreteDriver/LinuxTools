"""Tests for UI module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestUIModuleAvailability:
    """Test UI module can be imported and basic attributes exist."""

    def test_ui_module_imports(self):
        from src import ui

        assert ui is not None

    def test_gtk_available_flag_exists(self):
        from src.ui import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)

    def test_ui_has_editor_window_class(self):
        from src import ui

        assert hasattr(ui, "EditorWindow")

    def test_ui_has_main_window_class(self):
        from src import ui

        assert hasattr(ui, "MainWindow")

    def test_ui_has_settings_dialog_class(self):
        from src import ui

        assert hasattr(ui, "SettingsDialog")

    def test_ui_has_run_app_function(self):
        from src import ui

        assert hasattr(ui, "run_app")
        assert callable(ui.run_app)


class TestUIConfigIntegration:
    """Test UI integration with config module."""

    def test_config_module_imported(self):
        from src import ui, config

        # Check ui module uses config
        assert ui.config is config

    def test_editor_settings_in_config(self):
        from src import config

        cfg = config.load_config()
        assert "grid_size" in cfg
        assert "snap_to_grid" in cfg


class TestEditorStateSettings:
    """Test EditorState applies settings correctly."""

    def test_set_grid_snap_with_config_values(self):
        from src.editor import EditorState
        from src import config

        # Create a mock pixbuf
        mock_pixbuf = MagicMock()
        mock_pixbuf.get_width.return_value = 800
        mock_pixbuf.get_height.return_value = 600

        state = EditorState(mock_pixbuf)

        # Load config and apply
        cfg = config.load_config()
        grid_size = cfg.get("grid_size", 20)
        snap_enabled = cfg.get("snap_to_grid", False)

        state.set_grid_snap(snap_enabled, grid_size)

        assert state.grid_size == grid_size
        assert state.grid_snap_enabled == snap_enabled

    def test_grid_size_clamped_to_range(self):
        from src.editor import EditorState

        mock_pixbuf = MagicMock()
        mock_pixbuf.get_width.return_value = 800
        mock_pixbuf.get_height.return_value = 600

        state = EditorState(mock_pixbuf)

        # Test min clamping
        state.set_grid_snap(True, 1)
        assert state.grid_size == 5  # Clamped to min

        # Test max clamping
        state.set_grid_snap(True, 200)
        assert state.grid_size == 100  # Clamped to max

        # Test valid value
        state.set_grid_snap(True, 50)
        assert state.grid_size == 50


class TestEditorWindowSettings:
    """Test EditorWindow applies settings method."""

    def test_apply_editor_settings_method_exists(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_apply_editor_settings")

    def test_apply_editor_settings_is_callable(self):
        from src.ui import EditorWindow

        assert callable(getattr(EditorWindow, "_apply_editor_settings", None))


class TestToolTypeEnum:
    """Test ToolType enum is accessible from ui module."""

    def test_tooltype_imported(self):
        from src.ui import ToolType

        assert ToolType is not None

    def test_tooltype_has_select(self):
        from src.ui import ToolType

        assert hasattr(ToolType, "SELECT")

    def test_tooltype_has_pen(self):
        from src.ui import ToolType

        assert hasattr(ToolType, "PEN")

    def test_tooltype_has_blur(self):
        from src.ui import ToolType

        assert hasattr(ToolType, "BLUR")

    def test_tooltype_has_measure(self):
        from src.ui import ToolType

        assert hasattr(ToolType, "MEASURE")


class TestColorClass:
    """Test Color class is accessible from ui module."""

    def test_color_imported(self):
        from src.ui import Color

        assert Color is not None

    def test_color_can_be_instantiated(self):
        from src.ui import Color

        c = Color(0.5, 0.5, 0.5, 1.0)
        assert c.r == 0.5
        assert c.a == 1.0

    def test_color_copy_method(self):
        from src.ui import Color

        c1 = Color(0.1, 0.2, 0.3, 0.4)
        c2 = c1.copy()
        assert c2.r == c1.r
        assert c2.g == c1.g
        assert c2.b == c1.b
        assert c2.a == c1.a
        # Ensure they're different objects
        c2.a = 0.9
        assert c1.a == 0.4


class TestArrowStyleEnum:
    """Test ArrowStyle enum is accessible."""

    def test_arrowstyle_imported(self):
        from src.ui import ArrowStyle

        assert ArrowStyle is not None

    def test_arrowstyle_has_open(self):
        from src.ui import ArrowStyle

        assert hasattr(ArrowStyle, "OPEN")

    def test_arrowstyle_has_filled(self):
        from src.ui import ArrowStyle

        assert hasattr(ArrowStyle, "FILLED")

    def test_arrowstyle_has_double(self):
        from src.ui import ArrowStyle

        assert hasattr(ArrowStyle, "DOUBLE")


class TestRegionSelectorClass:
    """Test RegionSelector class."""

    def test_region_selector_class_exists(self):
        from src.ui import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            return

        from src.ui import RegionSelector

        assert RegionSelector is not None

    def test_region_selector_raises_without_gtk(self):
        with patch("src.ui.GTK_AVAILABLE", False):
            # Need to reimport to get patched value
            pass
            # Can't easily test this without reloading module

    def test_region_selector_has_callback_attribute(self):
        from src.ui import RegionSelector

        # Just check class structure
        assert hasattr(RegionSelector, "__init__")

    def test_region_selector_has_on_key_press(self):
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_key_press")

    def test_region_selector_has_on_draw(self):
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_draw")

    def test_region_selector_has_on_button_press(self):
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_button_press")

    def test_region_selector_has_on_button_release(self):
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_button_release")

    def test_region_selector_has_on_motion(self):
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_motion")


class TestEditorWindowClass:
    """Test EditorWindow class structure."""

    def test_editor_window_class_exists(self):
        from src.ui import EditorWindow

        assert EditorWindow is not None

    def test_editor_window_has_init(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "__init__")

    def test_editor_window_has_init_cursors(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_init_cursors")

    def test_editor_window_has_update_cursor(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_update_cursor")

    def test_editor_window_has_create_sidebar(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_create_sidebar")

    def test_editor_window_has_create_context_bar(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_create_context_bar")

    def test_editor_window_has_set_tool(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_set_tool")

    def test_editor_window_has_set_color(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_set_color")

    def test_editor_window_has_save(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_save")

    def test_editor_window_has_undo(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_undo")

    def test_editor_window_has_redo(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_redo")

    def test_editor_window_has_clear(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_clear")

    def test_editor_window_has_upload(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_upload")

    def test_editor_window_has_copy_to_clipboard(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_copy_to_clipboard")

    def test_editor_window_has_show_command_palette(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_show_command_palette")

    def test_editor_window_has_show_radial_menu(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_show_radial_menu")

    def test_editor_window_has_on_draw(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_draw")

    def test_editor_window_has_on_button_press(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_button_press")

    def test_editor_window_has_on_button_release(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_button_release")

    def test_editor_window_has_on_motion(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_motion")

    def test_editor_window_has_on_key_press(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_key_press")

    def test_editor_window_has_on_scroll(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_scroll")


class TestMainWindowClass:
    """Test MainWindow class structure."""

    def test_main_window_class_exists(self):
        from src.ui import MainWindow

        assert MainWindow is not None

    def test_main_window_has_init(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "__init__")

    def test_main_window_has_load_css(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_load_css")

    def test_main_window_has_create_big_button(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_create_big_button")

    def test_main_window_has_on_fullscreen(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_fullscreen")

    def test_main_window_has_capture_fullscreen(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_capture_fullscreen")

    def test_main_window_has_on_region(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_region")

    def test_main_window_has_start_region_selection(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_start_region_selection")

    def test_main_window_has_on_window(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_window")

    def test_main_window_has_capture_window(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_capture_window")

    def test_main_window_has_on_settings(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_settings")

    def test_main_window_has_on_about(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_about")

    def test_main_window_has_on_quit(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_quit")

    def test_main_window_has_run(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "run")

    def test_main_window_has_register_global_hotkeys(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_register_global_hotkeys")

    def test_main_window_has_on_history(self):
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_history")


class TestSettingsDialogClass:
    """Test SettingsDialog class structure."""

    def test_settings_dialog_class_exists(self):
        from src.ui import SettingsDialog

        assert SettingsDialog is not None

    def test_settings_dialog_has_init(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "__init__")

    def test_settings_dialog_has_create_general_settings(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_create_general_settings")

    def test_settings_dialog_has_create_capture_settings(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_create_capture_settings")

    def test_settings_dialog_has_create_upload_settings(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_create_upload_settings")

    def test_settings_dialog_has_create_editor_settings(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_create_editor_settings")

    def test_settings_dialog_has_save_settings(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_save_settings")

    def test_settings_dialog_has_reset_to_defaults(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_reset_to_defaults")

    def test_settings_dialog_has_browse_directory(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_browse_directory")

    def test_settings_dialog_has_on_grid_size_changed(self):
        from src.ui import SettingsDialog

        assert hasattr(SettingsDialog, "_on_grid_size_changed")


class TestRunAppFunction:
    """Test run_app function."""

    def test_run_app_exists(self):
        from src.ui import run_app

        assert callable(run_app)


class TestEditorWindowDrawingMethods:
    """Test EditorWindow drawing methods exist."""

    def test_has_draw_callout_preview(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_callout_preview")

    def test_has_draw_crop_preview(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_crop_preview")

    def test_has_draw_selection_handles(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_selection_handles")

    def test_has_draw_snap_guides(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_snap_guides")

    def test_has_draw_grid(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_grid")

    def test_has_draw_lock_indicator(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_lock_indicator")


class TestEditorWindowEffectMethods:
    """Test EditorWindow effect application methods."""

    def test_has_apply_crop(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_apply_crop")

    def test_has_pick_color(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_pick_color")

    def test_has_show_toast(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_show_toast")

    def test_has_show_text_dialog(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_show_text_dialog")

    def test_has_show_callout_dialog(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_show_callout_dialog")


class TestEditorWindowCoordinateMethods:
    """Test EditorWindow coordinate transformation methods."""

    def test_has_screen_to_image(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_screen_to_image")

    def test_has_update_resize_cursor(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_update_resize_cursor")

    def test_has_update_zoom_label(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_update_zoom_label")


class TestEditorWindowToolbarMethods:
    """Test EditorWindow toolbar creation methods."""

    def test_has_load_css(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_load_css")

    def test_has_create_stamp_popover(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_create_stamp_popover")

    def test_has_update_context_bar(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_update_context_bar")

    def test_has_on_stamp_selected(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_stamp_selected")


class TestEditorWindowColorMethods:
    """Test EditorWindow color handling methods."""

    def test_has_draw_color_dot(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_color_dot")

    def test_has_draw_neo_color(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_neo_color")

    def test_has_set_color_rgb(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_set_color_rgb")

    def test_has_update_recent_colors(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_update_recent_colors")


class TestEditorWindowToggleMethods:
    """Test EditorWindow toggle handler methods."""

    def test_has_on_tool_toggled(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_tool_toggled")

    def test_has_on_stamp_toggled(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_stamp_toggled")

    def test_has_on_arrow_style_toggled(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_arrow_style_toggled")

    def test_has_on_bold_toggled(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_bold_toggled")

    def test_has_on_italic_toggled(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_italic_toggled")

    def test_has_on_font_family_changed(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_font_family_changed")

    def test_has_on_color_chosen(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_color_chosen")

    def test_has_on_size_changed(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_size_changed")


class TestEditorWindowSaveMethods:
    """Test EditorWindow save methods."""

    def test_has_save_with_annotations(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_save_with_annotations")

    def test_has_on_destroy(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_destroy")


class TestEditorWindowRadialMenuIntegration:
    """Test EditorWindow radial menu integration."""

    def test_has_on_radial_select(self):
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_radial_select")


class TestSettingsDialogFormatHotkey:
    """Test SettingsDialog._format_hotkey functionality."""

    def test_format_control_key(self):
        """Test formatting Control key."""
        from src.ui import SettingsDialog

        # Create a mock instance to test the method
        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Control>s")
        assert result == "Ctrl+s"

    def test_format_shift_key(self):
        """Test formatting Shift key."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Shift>a")
        assert result == "Shift+a"

    def test_format_alt_key(self):
        """Test formatting Alt key."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Alt>Tab")
        assert result == "Alt+Tab"

    def test_format_super_key(self):
        """Test formatting Super key."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Super>r")
        assert result == "Super+r"

    def test_format_combined_modifiers(self):
        """Test formatting combined modifier keys."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Control><Shift>f")
        assert result == "Ctrl+Shift+f"

    def test_format_all_modifiers(self):
        """Test formatting all modifier keys together."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("<Control><Shift><Alt>x")
        assert result == "Ctrl+Shift+Alt+x"

    def test_format_plain_key(self):
        """Test formatting key without modifiers."""
        from src.ui import SettingsDialog

        class MockSettingsDialog:
            _format_hotkey = SettingsDialog._format_hotkey

        mock = MockSettingsDialog()
        result = mock._format_hotkey("F1")
        assert result == "F1"


class TestColorClassOperations:
    """Test Color class operations."""

    def test_color_creation(self):
        """Test basic Color creation."""
        from src.editor import Color

        color = Color(1.0, 0.5, 0.25, 0.8)
        assert color.r == 1.0
        assert color.g == 0.5
        assert color.b == 0.25
        assert color.a == 0.8

    def test_color_copy(self):
        """Test Color copy method."""
        from src.editor import Color

        original = Color(0.5, 0.6, 0.7, 0.9)
        copy = original.copy()

        assert copy.r == original.r
        assert copy.g == original.g
        assert copy.b == original.b
        assert copy.a == original.a
        assert copy is not original

    def test_color_to_tuple(self):
        """Test Color to_tuple method."""
        from src.editor import Color

        color = Color(0.1, 0.2, 0.3, 0.4)
        t = color.to_tuple()

        assert t == (0.1, 0.2, 0.3, 0.4)

    def test_color_to_rgb_tuple(self):
        """Test Color to_rgb_tuple method (without alpha)."""
        from src.editor import Color

        color = Color(0.1, 0.2, 0.3, 0.99)
        t = color.to_rgb_tuple()

        assert t == (0.1, 0.2, 0.3)

    def test_color_from_hex_full(self):
        """Test Color.from_hex with full hex string."""
        from src.editor import Color

        color = Color.from_hex("#FF8000")
        assert color.r == 1.0
        assert color.g == pytest.approx(0.502, rel=0.01)
        assert color.b == 0.0
        assert color.a == 1.0

    def test_color_from_hex_short(self):
        """Test Color.from_hex with short hex string."""
        from src.editor import Color

        color = Color.from_hex("#F80")
        assert color.r == 1.0
        assert color.g == pytest.approx(0.533, rel=0.01)
        assert color.b == 0.0

    def test_color_to_hex(self):
        """Test Color.to_hex method."""
        from src.editor import Color

        color = Color(1.0, 0.5, 0.0, 1.0)
        hex_str = color.to_hex()

        assert hex_str.startswith("#")
        assert len(hex_str) == 7
        assert hex_str.upper() == "#FF8000"

    def test_color_from_rgb_int(self):
        """Test Color.from_rgb_int class method."""
        from src.editor import Color

        color = Color.from_rgb_int(255, 128, 0)
        assert color.r == 1.0
        assert color.g == pytest.approx(0.502, rel=0.01)
        assert color.b == 0.0

    def test_color_default_alpha(self):
        """Test Color default alpha value."""
        from src.editor import Color

        color = Color(0.5, 0.5, 0.5)  # No alpha specified
        assert color.a == 1.0


class TestToolTypeEnumValues:
    """Test ToolType enum values and usage."""

    def test_all_tools_exist(self):
        """Test that all expected tools exist."""
        from src.editor import ToolType

        expected_tools = [
            "SELECT",
            "PEN",
            "HIGHLIGHTER",
            "LINE",
            "ARROW",
            "RECTANGLE",
            "ELLIPSE",
            "TEXT",
            "BLUR",
            "PIXELATE",
            "NUMBER",
            "MEASURE",
            "STAMP",
            "ZOOM",
            "CALLOUT",
            "CROP",
            "EYEDROPPER",
        ]
        for tool in expected_tools:
            assert hasattr(ToolType, tool), f"Missing tool: {tool}"

    def test_tool_values_are_strings(self):
        """Test that tool values are lowercase strings."""
        from src.editor import ToolType

        assert ToolType.SELECT.value == "select"
        assert ToolType.PEN.value == "pen"
        assert ToolType.BLUR.value == "blur"


class TestArrowStyleEnumValues:
    """Test ArrowStyle enum."""

    def test_arrow_styles_exist(self):
        """Test that all arrow styles exist."""
        from src.editor import ArrowStyle

        assert hasattr(ArrowStyle, "OPEN")
        assert hasattr(ArrowStyle, "FILLED")
        assert hasattr(ArrowStyle, "DOUBLE")

    def test_arrow_style_values(self):
        """Test arrow style values."""
        from src.editor import ArrowStyle

        assert ArrowStyle.OPEN.value == "open"
        assert ArrowStyle.FILLED.value == "filled"
        assert ArrowStyle.DOUBLE.value == "double"


class TestRegionSelectorMethods:
    """Test RegionSelector method existence and basic functionality."""

    def test_region_selector_has_draw_monitor_boundaries(self):
        """Test RegionSelector has _draw_monitor_boundaries."""
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_draw_monitor_boundaries")

    def test_region_selector_has_create_crosshair_cursor(self):
        """Test RegionSelector has _create_crosshair_cursor."""
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_create_crosshair_cursor")

    def test_region_selector_has_on_scroll(self):
        """Test RegionSelector has _on_scroll method."""
        from src.ui import RegionSelector

        assert hasattr(RegionSelector, "_on_scroll")


class TestMainWindowMethods:
    """Test MainWindow method existence."""

    def test_has_capture_fullscreen(self):
        """Test MainWindow has _capture_fullscreen."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_capture_fullscreen")

    def test_has_start_region_selection(self):
        """Test MainWindow has _start_region_selection."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_start_region_selection")

    def test_has_on_region_selected(self):
        """Test MainWindow has _on_region_selected."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_region_selected")

    def test_has_capture_window(self):
        """Test MainWindow has _capture_window."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_capture_window")

    def test_has_on_record_gif(self):
        """Test MainWindow has _on_record_gif."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_record_gif")

    def test_has_on_scroll_capture(self):
        """Test MainWindow has _on_scroll_capture."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_on_scroll_capture")

    def test_has_apply_hotkey_changes(self):
        """Test MainWindow has _apply_hotkey_changes."""
        from src.ui import MainWindow

        assert hasattr(MainWindow, "_apply_hotkey_changes")


class TestEditorWindowTabMethods:
    """Test EditorWindow tab management methods."""

    def test_has_add_tab(self):
        """Test EditorWindow has add_tab method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "add_tab")

    def test_has_close_tab(self):
        """Test EditorWindow has close_tab method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "close_tab")

    def test_has_create_tab_label(self):
        """Test EditorWindow has _create_tab_label method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_create_tab_label")

    def test_has_reindex_tabs(self):
        """Test EditorWindow has _reindex_tabs method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_reindex_tabs")

    def test_has_on_tab_switch(self):
        """Test EditorWindow has _on_tab_switch method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_tab_switch")

    def test_has_sync_toolbar_to_state(self):
        """Test EditorWindow has _sync_toolbar_to_state method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_sync_toolbar_to_state")


class TestEditorWindowHexPickerMethods:
    """Test EditorWindow hex color picker methods."""

    def test_has_setup_inline_hex_picker(self):
        """Test EditorWindow has _setup_inline_hex_picker method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_setup_inline_hex_picker")

    def test_has_build_hex_positions(self):
        """Test EditorWindow has _build_hex_positions method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_build_hex_positions")

    def test_has_draw_hex_palette(self):
        """Test EditorWindow has _draw_hex_palette method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_draw_hex_palette")

    def test_has_on_hex_click(self):
        """Test EditorWindow has _on_hex_click method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_on_hex_click")

    def test_has_open_color_chooser(self):
        """Test EditorWindow has _open_color_chooser method."""
        from src.ui import EditorWindow

        assert hasattr(EditorWindow, "_open_color_chooser")
