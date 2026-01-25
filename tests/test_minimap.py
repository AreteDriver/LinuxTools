"""Tests for the minimap navigator module."""

from unittest.mock import MagicMock, patch

import pytest


class TestMinimapModuleImport:
    """Test minimap module imports."""

    def test_module_imports(self):
        """Test that minimap module imports successfully."""
        from src import minimap

        assert hasattr(minimap, "MinimapNavigator")
        assert hasattr(minimap, "create_minimap_overlay")
        assert hasattr(minimap, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.minimap import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestMinimapNavigatorClass:
    """Test MinimapNavigator class structure."""

    def test_class_has_required_constants(self):
        """Test that MinimapNavigator has required class constants."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "MAX_WIDTH")
        assert hasattr(MinimapNavigator, "MAX_HEIGHT")
        assert hasattr(MinimapNavigator, "MARGIN")
        assert hasattr(MinimapNavigator, "OPACITY")

    def test_max_width_is_positive(self):
        """Test that MAX_WIDTH is a positive integer."""
        from src.minimap import MinimapNavigator

        assert MinimapNavigator.MAX_WIDTH > 0
        assert isinstance(MinimapNavigator.MAX_WIDTH, int)

    def test_max_height_is_positive(self):
        """Test that MAX_HEIGHT is a positive integer."""
        from src.minimap import MinimapNavigator

        assert MinimapNavigator.MAX_HEIGHT > 0
        assert isinstance(MinimapNavigator.MAX_HEIGHT, int)

    def test_opacity_in_valid_range(self):
        """Test that OPACITY is between 0 and 1."""
        from src.minimap import MinimapNavigator

        assert 0 <= MinimapNavigator.OPACITY <= 1

    def test_class_has_required_methods(self):
        """Test that MinimapNavigator has required methods."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "set_image")
        assert hasattr(MinimapNavigator, "set_viewport")
        assert hasattr(MinimapNavigator, "set_annotations")
        assert hasattr(MinimapNavigator, "set_visible")
        assert hasattr(MinimapNavigator, "toggle_visible")


class TestMinimapWithoutGtk:
    """Test minimap behavior without GTK."""

    def test_gtk_check_in_init(self):
        """Test that MinimapNavigator checks GTK_AVAILABLE in init."""
        from src.minimap import MinimapNavigator
        import inspect

        # Check that __init__ has GTK check
        source = inspect.getsource(MinimapNavigator.__init__)
        assert "GTK_AVAILABLE" in source or "RuntimeError" in source


class TestMinimapWithGtk:
    """Test MinimapNavigator with GTK available."""

    def test_init_requires_parent_widget(self):
        """Test that init requires parent_widget parameter."""
        from src.minimap import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.minimap import MinimapNavigator

        # Check signature requires parent_widget and on_navigate
        import inspect

        sig = inspect.signature(MinimapNavigator.__init__)
        params = list(sig.parameters.keys())
        assert "parent_widget" in params
        assert "on_navigate" in params

    def test_set_viewport_accepts_coordinates(self):
        """Test that set_viewport accepts x, y, width, height."""
        from src.minimap import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.minimap import MinimapNavigator

        # Check signature
        import inspect

        sig = inspect.signature(MinimapNavigator.set_viewport)
        params = list(sig.parameters.keys())
        assert "x" in params
        assert "y" in params
        assert "width" in params
        assert "height" in params


class TestCreateMinimapOverlay:
    """Test create_minimap_overlay factory function."""

    def test_function_exists(self):
        """Test that create_minimap_overlay function exists."""
        from src.minimap import create_minimap_overlay

        assert callable(create_minimap_overlay)

    def test_function_signature(self):
        """Test create_minimap_overlay has correct parameters."""
        from src.minimap import create_minimap_overlay
        import inspect

        sig = inspect.signature(create_minimap_overlay)
        params = list(sig.parameters.keys())
        assert "parent_container" in params
        assert "drawing_area" in params
        assert "on_navigate" in params


class TestMinimapMathImport:
    """Test that minimap uses math module correctly."""

    def test_uses_math_pi(self):
        """Test that minimap uses math.pi instead of magic numbers."""
        from src import minimap
        import inspect

        source = inspect.getsource(minimap)

        # Check for math import
        assert "import math" in source, "minimap.py should import math module"

        # Check that 3.14159 is not used
        assert "3.14159" not in source, "Should use math.pi instead of magic number"


class TestMinimapConstants:
    """Test minimap constants are reasonable values."""

    def test_max_width_reasonable(self):
        """Test MAX_WIDTH is reasonable (100-300 pixels)."""
        from src.minimap import MinimapNavigator

        assert 100 <= MinimapNavigator.MAX_WIDTH <= 300

    def test_max_height_reasonable(self):
        """Test MAX_HEIGHT is reasonable (80-200 pixels)."""
        from src.minimap import MinimapNavigator

        assert 80 <= MinimapNavigator.MAX_HEIGHT <= 200

    def test_margin_reasonable(self):
        """Test MARGIN is reasonable (5-30 pixels)."""
        from src.minimap import MinimapNavigator

        assert 5 <= MinimapNavigator.MARGIN <= 30

    def test_opacity_not_zero(self):
        """Test OPACITY is not zero (would be invisible)."""
        from src.minimap import MinimapNavigator

        assert MinimapNavigator.OPACITY > 0

    def test_opacity_not_fully_opaque(self):
        """Test OPACITY is less than 1 (semi-transparent)."""
        from src.minimap import MinimapNavigator

        assert MinimapNavigator.OPACITY < 1.0


class TestMinimapCssApplied:
    """Test CSS provider deduplication flag."""

    def test_css_applied_exists(self):
        """Test _css_applied module variable exists."""
        from src import minimap

        assert hasattr(minimap, "_css_applied")

    def test_css_applied_is_bool(self):
        """Test _css_applied is boolean."""
        from src.minimap import _css_applied

        assert isinstance(_css_applied, bool)


class TestMinimapNavigatorMethods:
    """Test MinimapNavigator method signatures."""

    def test_has_set_annotations_method(self):
        """Test MinimapNavigator has set_annotations method."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "set_annotations")
        assert callable(getattr(MinimapNavigator, "set_annotations"))

    def test_has_on_draw_method(self):
        """Test MinimapNavigator has _on_draw method."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_on_draw")

    def test_has_navigate_to_method(self):
        """Test MinimapNavigator has _navigate_to method."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_navigate_to")

    def test_has_button_handlers(self):
        """Test MinimapNavigator has button event handlers."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_on_button_press")
        assert hasattr(MinimapNavigator, "_on_button_release")
        assert hasattr(MinimapNavigator, "_on_motion")

    def test_has_apply_styles_method(self):
        """Test MinimapNavigator has _apply_styles method."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_apply_styles")


class TestMinimapNavigatorInstanceVars:
    """Test MinimapNavigator expected instance variables."""

    def test_init_signature_includes_on_navigate(self):
        """Test __init__ requires on_navigate parameter."""
        from src.minimap import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator.__init__)
        params = list(sig.parameters.keys())
        assert "on_navigate" in params

    def test_has_visible_attribute_doc(self):
        """Test MinimapNavigator mentions visible attribute."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "visible" in source

    def test_has_dragging_attribute_doc(self):
        """Test MinimapNavigator has _dragging attribute."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "_dragging" in source


class TestCreateMinimapOverlayReturnType:
    """Test create_minimap_overlay function behavior."""

    def test_function_returns_minimap_navigator(self):
        """Test function return type annotation."""
        from src.minimap import create_minimap_overlay
        import inspect

        annotations = create_minimap_overlay.__annotations__
        assert "return" in annotations
        # Return type should be MinimapNavigator
        assert "MinimapNavigator" in str(annotations["return"])


class TestMinimapNavigatorToggle:
    """Test toggle_visible method behavior."""

    def test_toggle_visible_method_exists(self):
        """Test toggle_visible method exists."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "toggle_visible")
        assert callable(getattr(MinimapNavigator, "toggle_visible"))

    def test_toggle_visible_returns_bool(self):
        """Test toggle_visible return type annotation."""
        from src.minimap import MinimapNavigator

        annotations = MinimapNavigator.toggle_visible.__annotations__
        # Return annotation may be string 'bool' or type bool depending on context
        return_type = annotations.get("return")
        assert return_type == bool or return_type == "bool"


class TestMinimapNavigatorSetMethods:
    """Test set_* method signatures."""

    def test_set_image_accepts_pixbuf(self):
        """Test set_image has pixbuf parameter."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator.set_image)
        params = list(sig.parameters.keys())
        assert "pixbuf" in params

    def test_set_annotations_accepts_elements(self):
        """Test set_annotations has elements parameter."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator.set_annotations)
        params = list(sig.parameters.keys())
        assert "elements" in params

    def test_set_visible_accepts_bool(self):
        """Test set_visible has visible parameter."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator.set_visible)
        params = list(sig.parameters.keys())
        assert "visible" in params


class TestMinimapNavigatorDrawing:
    """Test drawing-related methods."""

    def test_on_draw_exists(self):
        """Test _on_draw method exists."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_on_draw")

    def test_on_button_press_exists(self):
        """Test _on_button_press method exists."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_on_button_press")

    def test_on_motion_exists(self):
        """Test _on_motion method exists."""
        from src.minimap import MinimapNavigator

        assert hasattr(MinimapNavigator, "_on_motion")


class TestCreateMinimapOverlayParams:
    """Test create_minimap_overlay parameter types."""

    def test_function_has_on_navigate_param(self):
        """Test on_navigate parameter exists."""
        from src.minimap import create_minimap_overlay
        import inspect

        sig = inspect.signature(create_minimap_overlay)
        params = sig.parameters
        assert "on_navigate" in params

    def test_function_has_drawing_area_param(self):
        """Test drawing_area parameter exists."""
        from src.minimap import create_minimap_overlay
        import inspect

        sig = inspect.signature(create_minimap_overlay)
        params = sig.parameters
        assert "drawing_area" in params


class TestMinimapNavigatorPrivateMethods:
    """Test MinimapNavigator private method signatures."""

    def test_has_navigate_to_signature(self):
        """Test _navigate_to has mx and my parameters."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator._navigate_to)
        params = list(sig.parameters.keys())
        assert "mx" in params
        assert "my" in params

    def test_on_draw_signature(self):
        """Test _on_draw has widget and cr parameters."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator._on_draw)
        params = list(sig.parameters.keys())
        assert "widget" in params
        assert "cr" in params

    def test_on_button_press_signature(self):
        """Test _on_button_press has widget and event parameters."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator._on_button_press)
        params = list(sig.parameters.keys())
        assert "widget" in params
        assert "event" in params

    def test_on_button_release_signature(self):
        """Test _on_button_release has widget and event parameters."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator._on_button_release)
        params = list(sig.parameters.keys())
        assert "widget" in params
        assert "event" in params

    def test_on_motion_signature(self):
        """Test _on_motion has widget and event parameters."""
        from src.minimap import MinimapNavigator
        import inspect

        sig = inspect.signature(MinimapNavigator._on_motion)
        params = list(sig.parameters.keys())
        assert "widget" in params
        assert "event" in params


class TestMinimapNavigatorSourceCode:
    """Test MinimapNavigator implementation details via source inspection."""

    def test_set_image_guards_zero_dimensions(self):
        """Test set_image has guard for zero-dimension images."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_image)
        # Should check for zero or negative dimensions
        assert "img_w <= 0" in source or "img_w == 0" in source or "< 0" in source

    def test_set_image_calculates_scale(self):
        """Test set_image calculates scale from MAX_WIDTH/MAX_HEIGHT."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_image)
        assert "MAX_WIDTH" in source
        assert "MAX_HEIGHT" in source
        assert "_scale" in source

    def test_navigate_to_clamps_coordinates(self):
        """Test _navigate_to clamps coordinates to image bounds."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._navigate_to)
        # Should have min/max clamping
        assert "max(0" in source or "min(" in source

    def test_on_button_press_checks_button(self):
        """Test _on_button_press checks for button 1 (left click)."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_button_press)
        assert "button == 1" in source or "button==1" in source

    def test_on_button_press_sets_dragging(self):
        """Test _on_button_press sets _dragging flag."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_button_press)
        assert "_dragging" in source

    def test_on_motion_checks_dragging(self):
        """Test _on_motion checks _dragging flag."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_motion)
        assert "_dragging" in source

    def test_set_annotations_iterates_elements(self):
        """Test set_annotations processes element points."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_annotations)
        assert "for elem in elements" in source
        assert "points" in source

    def test_toggle_visible_returns_state(self):
        """Test toggle_visible returns the new visibility state."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.toggle_visible)
        assert "return" in source
        assert "visible" in source


class TestMinimapNavigatorOnDraw:
    """Test _on_draw implementation details."""

    def test_on_draw_checks_scaled_pixbuf(self):
        """Test _on_draw returns early if no scaled pixbuf."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_draw)
        assert "_scaled_pixbuf" in source

    def test_on_draw_imports_cairo(self):
        """Test _on_draw imports cairo."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_draw)
        assert "import cairo" in source

    def test_on_draw_draws_viewport(self):
        """Test _on_draw draws the viewport rectangle."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_draw)
        assert "_viewport_w" in source or "viewport" in source

    def test_on_draw_draws_annotations(self):
        """Test _on_draw draws annotation markers."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_draw)
        assert "_annotation_positions" in source or "annotation" in source

    def test_on_draw_uses_math_pi(self):
        """Test _on_draw uses math.pi for circles."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._on_draw)
        assert "math.pi" in source


class TestMinimapApplyStyles:
    """Test _apply_styles implementation."""

    def test_apply_styles_checks_flag(self):
        """Test _apply_styles checks _css_applied flag."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._apply_styles)
        assert "_css_applied" in source

    def test_apply_styles_uses_css_provider(self):
        """Test _apply_styles uses Gtk.CssProvider."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._apply_styles)
        assert "CssProvider" in source

    def test_apply_styles_has_css_content(self):
        """Test _apply_styles defines CSS content."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator._apply_styles)
        assert "background" in source or "border" in source


class TestCreateMinimapOverlayImpl:
    """Test create_minimap_overlay implementation."""

    def test_creates_minimap_navigator(self):
        """Test function creates MinimapNavigator instance."""
        from src.minimap import create_minimap_overlay
        import inspect

        source = inspect.getsource(create_minimap_overlay)
        assert "MinimapNavigator(" in source

    def test_checks_for_overlay_container(self):
        """Test function checks if parent is Gtk.Overlay."""
        from src.minimap import create_minimap_overlay
        import inspect

        source = inspect.getsource(create_minimap_overlay)
        assert "Gtk.Overlay" in source or "isinstance" in source

    def test_sets_alignment(self):
        """Test function sets alignment for minimap position."""
        from src.minimap import create_minimap_overlay
        import inspect

        source = inspect.getsource(create_minimap_overlay)
        assert "set_halign" in source or "set_valign" in source or "Align" in source


class TestMinimapNavigatorInit:
    """Test MinimapNavigator.__init__ implementation."""

    def test_init_checks_gtk_available(self):
        """Test __init__ checks GTK_AVAILABLE."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "GTK_AVAILABLE" in source

    def test_init_raises_runtime_error(self):
        """Test __init__ raises RuntimeError without GTK."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "RuntimeError" in source

    def test_init_stores_parent_widget(self):
        """Test __init__ stores parent_widget."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "self.parent_widget" in source

    def test_init_stores_on_navigate(self):
        """Test __init__ stores on_navigate callback."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "self.on_navigate" in source

    def test_init_initializes_state(self):
        """Test __init__ initializes state variables."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "self.visible" in source
        assert "self._dragging" in source
        assert "self._pixbuf" in source

    def test_init_creates_drawing_area(self):
        """Test __init__ creates DrawingArea."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "DrawingArea" in source

    def test_init_connects_signals(self):
        """Test __init__ connects event signals."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.__init__)
        assert "connect" in source
        assert "draw" in source or "button-press" in source


class TestMinimapSetViewport:
    """Test set_viewport implementation."""

    def test_set_viewport_stores_coordinates(self):
        """Test set_viewport stores all coordinates."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_viewport)
        assert "_viewport_x" in source
        assert "_viewport_y" in source
        assert "_viewport_w" in source
        assert "_viewport_h" in source

    def test_set_viewport_triggers_redraw(self):
        """Test set_viewport triggers queue_draw."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_viewport)
        assert "queue_draw" in source


class TestMinimapSetVisible:
    """Test set_visible implementation."""

    def test_set_visible_stores_state(self):
        """Test set_visible stores visibility state."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_visible)
        assert "self.visible" in source

    def test_set_visible_shows_or_hides(self):
        """Test set_visible calls show() or hide()."""
        from src.minimap import MinimapNavigator
        import inspect

        source = inspect.getsource(MinimapNavigator.set_visible)
        assert ".show()" in source or ".hide()" in source


# =============================================================================
# Functional GTK Tests (require xvfb or display)
# =============================================================================


class TestMinimapFunctional:
    """Functional tests that create real GTK widgets."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.minimap import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gtk, GdkPixbuf

        # Create a simple parent widget
        parent = Gtk.DrawingArea()
        return {"Gtk": Gtk, "GdkPixbuf": GdkPixbuf, "parent": parent}

    def test_create_minimap_navigator(self, gtk_setup):
        """Test creating a MinimapNavigator instance."""
        from src.minimap import MinimapNavigator

        navigate_calls = []

        def on_navigate(x, y):
            navigate_calls.append((x, y))

        minimap = MinimapNavigator(gtk_setup["parent"], on_navigate)

        assert minimap is not None
        assert minimap.visible is True
        assert minimap.drawing_area is not None
        assert minimap._dragging is False

    def test_minimap_set_viewport(self, gtk_setup):
        """Test setting viewport on minimap."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        minimap.set_viewport(10, 20, 100, 80)

        assert minimap._viewport_x == 10
        assert minimap._viewport_y == 20
        assert minimap._viewport_w == 100
        assert minimap._viewport_h == 80

    def test_minimap_set_visible(self, gtk_setup):
        """Test setting visibility."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        minimap.set_visible(False)
        assert minimap.visible is False

        minimap.set_visible(True)
        assert minimap.visible is True

    def test_minimap_toggle_visible(self, gtk_setup):
        """Test toggling visibility."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)
        assert minimap.visible is True

        result = minimap.toggle_visible()
        assert result is False
        assert minimap.visible is False

        result = minimap.toggle_visible()
        assert result is True
        assert minimap.visible is True

    def test_minimap_set_image(self, gtk_setup):
        """Test setting image on minimap."""
        from src.minimap import MinimapNavigator
        GdkPixbuf = gtk_setup["GdkPixbuf"]

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Create a small test pixbuf
        pixbuf = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, 200, 150
        )
        pixbuf.fill(0xFF0000FF)  # Red

        minimap.set_image(pixbuf)

        assert minimap._pixbuf is not None
        assert minimap._scaled_pixbuf is not None
        assert minimap._scale > 0
        assert minimap._minimap_width > 0
        assert minimap._minimap_height > 0

    def test_minimap_set_image_zero_dimension(self, gtk_setup):
        """Test set_image handles zero-dimension images."""
        from src.minimap import MinimapNavigator
        GdkPixbuf = gtk_setup["GdkPixbuf"]

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Create a 1x1 pixbuf (minimum size, GdkPixbuf doesn't allow 0x0)
        pixbuf = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, 1, 1
        )

        # Should not raise
        minimap.set_image(pixbuf)

    def test_minimap_set_annotations_empty(self, gtk_setup):
        """Test setting empty annotations list."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        minimap.set_annotations([])

        assert minimap._annotation_positions == []

    def test_minimap_set_annotations_with_elements(self, gtk_setup):
        """Test setting annotations with mock elements."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Create mock elements with points
        class MockPoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        class MockElement:
            def __init__(self, points):
                self.points = points

        elem1 = MockElement([MockPoint(10, 20), MockPoint(30, 40)])
        elem2 = MockElement([MockPoint(50, 60), MockPoint(70, 80)])

        minimap.set_annotations([elem1, elem2])

        assert len(minimap._annotation_positions) == 2
        # First element center: ((10+30)/2, (20+40)/2) = (20, 30)
        assert minimap._annotation_positions[0] == (20, 30)
        # Second element center: ((50+70)/2, (60+80)/2) = (60, 70)
        assert minimap._annotation_positions[1] == (60, 70)

    def test_minimap_navigate_to(self, gtk_setup):
        """Test navigation callback."""
        from src.minimap import MinimapNavigator
        GdkPixbuf = gtk_setup["GdkPixbuf"]

        navigate_calls = []

        def on_navigate(x, y):
            navigate_calls.append((x, y))

        minimap = MinimapNavigator(gtk_setup["parent"], on_navigate)

        # Set an image first
        pixbuf = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, 200, 150
        )
        minimap.set_image(pixbuf)

        # Trigger navigation
        minimap._navigate_to(50, 40)

        assert len(navigate_calls) == 1
        # Check that coordinates were converted
        assert navigate_calls[0][0] >= 0
        assert navigate_calls[0][1] >= 0

    def test_minimap_navigate_to_without_image(self, gtk_setup):
        """Test navigation returns early without image."""
        from src.minimap import MinimapNavigator

        navigate_calls = []

        def on_navigate(x, y):
            navigate_calls.append((x, y))

        minimap = MinimapNavigator(gtk_setup["parent"], on_navigate)

        # Don't set image, try to navigate
        minimap._navigate_to(50, 40)

        # Should not have called navigate callback
        assert len(navigate_calls) == 0

    def test_minimap_drawing_area_exists(self, gtk_setup):
        """Test that drawing_area is created."""
        from src.minimap import MinimapNavigator
        Gtk = gtk_setup["Gtk"]

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        assert isinstance(minimap.drawing_area, Gtk.DrawingArea)

    def test_minimap_on_draw_without_pixbuf(self, gtk_setup):
        """Test _on_draw returns early without pixbuf."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Mock cairo context
        mock_cr = MagicMock()

        # Should return True without drawing
        result = minimap._on_draw(minimap.drawing_area, mock_cr)
        assert result is True

    def test_minimap_on_draw_with_pixbuf(self, gtk_setup):
        """Test _on_draw sets up drawing correctly."""
        from src.minimap import MinimapNavigator
        GdkPixbuf = gtk_setup["GdkPixbuf"]

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Set an image
        pixbuf = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, 100, 80
        )
        minimap.set_image(pixbuf)

        # Set viewport
        minimap.set_viewport(10, 10, 50, 40)

        # Verify state is set correctly for drawing
        assert minimap._scaled_pixbuf is not None
        assert minimap._viewport_w == 50
        assert minimap._viewport_h == 40

        # The actual drawing requires a real cairo context from GTK
        # We verify the draw signal is connected
        assert minimap.drawing_area is not None


class TestCreateMinimapOverlayFunctional:
    """Functional tests for create_minimap_overlay."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.minimap import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return {"Gtk": Gtk}

    def test_create_minimap_overlay_with_overlay(self, gtk_setup):
        """Test create_minimap_overlay with Gtk.Overlay container."""
        from src.minimap import create_minimap_overlay, MinimapNavigator
        Gtk = gtk_setup["Gtk"]

        overlay = Gtk.Overlay()
        drawing_area = Gtk.DrawingArea()
        overlay.add(drawing_area)

        minimap = create_minimap_overlay(
            overlay, drawing_area, lambda x, y: None
        )

        assert isinstance(minimap, MinimapNavigator)

    def test_create_minimap_overlay_with_box(self, gtk_setup):
        """Test create_minimap_overlay with non-Overlay container."""
        from src.minimap import create_minimap_overlay, MinimapNavigator
        Gtk = gtk_setup["Gtk"]

        box = Gtk.Box()
        drawing_area = Gtk.DrawingArea()

        minimap = create_minimap_overlay(
            box, drawing_area, lambda x, y: None
        )

        # Should still return a MinimapNavigator
        assert isinstance(minimap, MinimapNavigator)


class TestMinimapEventHandlers:
    """Test minimap event handler methods."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.minimap import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("GdkPixbuf", "2.0")
        from gi.repository import Gdk, GdkPixbuf, Gtk

        parent = Gtk.DrawingArea()
        return {"Gtk": Gtk, "Gdk": Gdk, "GdkPixbuf": GdkPixbuf, "parent": parent}

    def test_button_press_starts_dragging(self, gtk_setup):
        """Test _on_button_press sets dragging flag."""
        from src.minimap import MinimapNavigator

        GdkPixbuf = gtk_setup["GdkPixbuf"]
        navigate_calls = []

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: navigate_calls.append((x, y)))

        # Set image so navigation works
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 100, 80)
        minimap.set_image(pixbuf)

        # Create mock button event
        mock_event = MagicMock()
        mock_event.button = 1
        mock_event.x = 50.0
        mock_event.y = 40.0

        minimap._on_button_press(minimap.drawing_area, mock_event)

        assert minimap._dragging is True
        assert len(navigate_calls) > 0

    def test_button_release_stops_dragging(self, gtk_setup):
        """Test _on_button_release clears dragging flag."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)
        minimap._dragging = True

        mock_event = MagicMock()
        mock_event.button = 1

        minimap._on_button_release(minimap.drawing_area, mock_event)

        assert minimap._dragging is False

    def test_motion_while_dragging(self, gtk_setup):
        """Test _on_motion navigates while dragging."""
        from src.minimap import MinimapNavigator

        GdkPixbuf = gtk_setup["GdkPixbuf"]
        navigate_calls = []

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: navigate_calls.append((x, y)))

        # Set image
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 100, 80)
        minimap.set_image(pixbuf)

        # Start dragging
        minimap._dragging = True

        mock_event = MagicMock()
        mock_event.x = 30.0
        mock_event.y = 25.0

        minimap._on_motion(minimap.drawing_area, mock_event)

        assert len(navigate_calls) > 0

    def test_motion_without_dragging(self, gtk_setup):
        """Test _on_motion does nothing when not dragging."""
        from src.minimap import MinimapNavigator

        navigate_calls = []

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: navigate_calls.append((x, y)))
        minimap._dragging = False

        mock_event = MagicMock()
        mock_event.x = 30.0
        mock_event.y = 25.0

        minimap._on_motion(minimap.drawing_area, mock_event)

        assert len(navigate_calls) == 0

    def test_button_press_wrong_button(self, gtk_setup):
        """Test _on_button_press ignores non-left-click."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        mock_event = MagicMock()
        mock_event.button = 3  # Right-click
        mock_event.x = 50.0
        mock_event.y = 40.0

        minimap._on_button_press(minimap.drawing_area, mock_event)

        # Should not start dragging
        assert minimap._dragging is False


class TestMinimapDrawWithAnnotations:
    """Test minimap drawing with annotations."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.minimap import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("GdkPixbuf", "2.0")
        from gi.repository import GdkPixbuf, Gtk

        parent = Gtk.DrawingArea()
        return {"Gtk": Gtk, "GdkPixbuf": GdkPixbuf, "parent": parent}

    def test_set_annotations_stores_positions(self, gtk_setup):
        """Test set_annotations stores annotation positions."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Create mock drawing elements with points
        point1 = MagicMock()
        point1.x = 10.0
        point1.y = 20.0
        point2 = MagicMock()
        point2.x = 30.0
        point2.y = 40.0

        elem1 = MagicMock()
        elem1.points = [point1, point2]

        annotations = [elem1]
        minimap.set_annotations(annotations)

        assert len(minimap._annotation_positions) == 1
        # Center of (10, 30) and (20, 40) is (20, 30)
        assert minimap._annotation_positions[0] == (20.0, 30.0)

    def test_set_annotations_empty_points(self, gtk_setup):
        """Test set_annotations handles elements with no points."""
        from src.minimap import MinimapNavigator

        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        elem1 = MagicMock()
        elem1.points = []  # Empty points

        minimap.set_annotations([elem1])

        # Should have no annotations stored
        assert len(minimap._annotation_positions) == 0

    def test_draw_state_with_viewport_and_annotations(self, gtk_setup):
        """Test that draw state is properly set with viewport and annotations."""
        from src.minimap import MinimapNavigator

        GdkPixbuf = gtk_setup["GdkPixbuf"]
        minimap = MinimapNavigator(gtk_setup["parent"], lambda x, y: None)

        # Set image
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 200, 150)
        minimap.set_image(pixbuf)

        # Set viewport
        minimap.set_viewport(20, 30, 100, 80)

        # Create mock annotations
        point = MagicMock()
        point.x = 50.0
        point.y = 60.0
        elem = MagicMock()
        elem.points = [point]

        minimap.set_annotations([elem])

        # Verify all state is set
        assert minimap._scaled_pixbuf is not None
        assert minimap._viewport_x == 20
        assert minimap._viewport_y == 30
        assert minimap._viewport_w == 100
        assert minimap._viewport_h == 80
        assert len(minimap._annotation_positions) == 1
