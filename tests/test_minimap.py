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
