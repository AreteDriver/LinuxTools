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
