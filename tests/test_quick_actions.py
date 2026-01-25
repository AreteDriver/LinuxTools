"""Tests for the quick actions module."""

from unittest.mock import MagicMock, patch

import pytest


class TestQuickActionsModuleImport:
    """Test quick_actions module imports."""

    def test_module_imports(self):
        """Test that quick_actions module imports successfully."""
        from src import quick_actions

        assert hasattr(quick_actions, "QuickAction")
        assert hasattr(quick_actions, "QuickActionsPanel")
        assert hasattr(quick_actions, "create_selection_actions")
        assert hasattr(quick_actions, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.quick_actions import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestQuickActionClass:
    """Test QuickAction class."""

    def test_quick_action_init(self):
        """Test QuickAction initialization."""
        from src.quick_actions import QuickAction

        callback = MagicMock()
        action = QuickAction(
            icon="X",
            tooltip="Delete",
            callback=callback,
        )

        assert action.icon == "X"
        assert action.tooltip == "Delete"
        assert action.callback == callback

    def test_quick_action_default_enabled_check(self):
        """Test QuickAction has default enabled_check."""
        from src.quick_actions import QuickAction

        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=MagicMock(),
        )

        # Default should always return True
        assert action.enabled_check() is True

    def test_quick_action_custom_enabled_check(self):
        """Test QuickAction with custom enabled_check."""
        from src.quick_actions import QuickAction

        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=MagicMock(),
            enabled_check=lambda: False,
        )

        assert action.enabled_check() is False

    def test_quick_action_callback_callable(self):
        """Test that QuickAction callback is callable."""
        from src.quick_actions import QuickAction

        called = []
        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=lambda: called.append(True),
        )

        action.callback()
        assert called == [True]


class TestQuickActionsPanelClass:
    """Test QuickActionsPanel class structure."""

    def test_class_has_required_methods(self):
        """Test that QuickActionsPanel has required methods."""
        from src.quick_actions import QuickActionsPanel

        assert hasattr(QuickActionsPanel, "set_actions")
        assert hasattr(QuickActionsPanel, "show_at")
        assert hasattr(QuickActionsPanel, "hide")
        assert hasattr(QuickActionsPanel, "update_position")

    def test_gtk_check_in_init(self):
        """Test that QuickActionsPanel checks GTK_AVAILABLE in init."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        # Check that __init__ has GTK check
        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "GTK_AVAILABLE" in source or "RuntimeError" in source


class TestQuickActionsPanelWithGtk:
    """Test QuickActionsPanel with GTK available."""

    def test_show_at_signature(self):
        """Test show_at has correct parameters."""
        from src.quick_actions import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.quick_actions import QuickActionsPanel
        import inspect

        sig = inspect.signature(QuickActionsPanel.show_at)
        params = list(sig.parameters.keys())
        assert "x" in params
        assert "y" in params
        assert "element_bbox" in params

    def test_update_position_signature(self):
        """Test update_position has correct parameters."""
        from src.quick_actions import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.quick_actions import QuickActionsPanel
        import inspect

        sig = inspect.signature(QuickActionsPanel.update_position)
        params = list(sig.parameters.keys())
        assert "bbox" in params
        assert "drawing_area" in params


class TestCreateSelectionActions:
    """Test create_selection_actions factory function."""

    def test_function_exists(self):
        """Test that create_selection_actions function exists."""
        from src.quick_actions import create_selection_actions

        assert callable(create_selection_actions)

    def test_function_has_type_hint(self):
        """Test that create_selection_actions has type hint for editor_window."""
        from src.quick_actions import create_selection_actions
        import inspect

        sig = inspect.signature(create_selection_actions)
        params = list(sig.parameters.keys())
        assert "editor_window" in params

        # Check return type annotation
        annotations = create_selection_actions.__annotations__
        assert "return" in annotations

    def test_returns_list(self):
        """Test that create_selection_actions returns a list."""
        from src.quick_actions import create_selection_actions, QuickAction

        # Create a mock editor_window with necessary attributes
        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        assert isinstance(actions, list)
        assert all(isinstance(a, QuickAction) for a in actions)

    def test_returns_standard_actions(self):
        """Test that create_selection_actions returns standard actions."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        # Should have multiple actions (delete, duplicate, copy, etc.)
        assert len(actions) >= 5

        # Check for expected tooltips
        tooltips = [a.tooltip for a in actions]
        # At least these should exist (with i18n they might be translated)
        assert any("Delete" in t or "Del" in t for t in tooltips)
        assert any("Duplicate" in t or "Ctrl+D" in t for t in tooltips)
        assert any("Copy" in t or "Ctrl+C" in t for t in tooltips)


class TestQuickActionsI18n:
    """Test that quick_actions uses internationalization."""

    def test_imports_i18n(self):
        """Test that quick_actions imports i18n."""
        from src import quick_actions
        import inspect

        source = inspect.getsource(quick_actions)
        assert "from .i18n import _" in source or "from src.i18n import _" in source


class TestQuickActionsIcons:
    """Test quick action icons are valid Unicode."""

    def test_action_icons_are_strings(self):
        """Test that all action icons are non-empty strings."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        for action in actions:
            assert isinstance(action.icon, str)
            assert len(action.icon) > 0
