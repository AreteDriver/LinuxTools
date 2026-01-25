"""Tests for the undo history module."""

from unittest.mock import MagicMock, patch

import pytest


class TestGetActionName:
    """Test get_action_name function."""

    def test_function_exists(self):
        """Test that get_action_name function exists."""
        from src.undo_history import get_action_name

        assert callable(get_action_name)

    def test_added_element(self):
        """Test detection of added element."""
        from src.undo_history import get_action_name

        before = []
        after = [MagicMock()]
        after[0].tool.value = "rectangle"

        result = get_action_name(before, after)
        # Should mention rectangle or added
        assert "rectangle" in result.lower() or "added" in result.lower() or "drew" in result.lower()

    def test_deleted_element(self):
        """Test detection of deleted element."""
        from src.undo_history import get_action_name

        before = [MagicMock()]
        after = []

        result = get_action_name(before, after)
        assert "delete" in result.lower()

    def test_modified_element(self):
        """Test detection of modified element."""
        from src.undo_history import get_action_name

        before = [MagicMock()]
        after = [MagicMock()]

        result = get_action_name(before, after)
        assert "modif" in result.lower()

    def test_multiple_added(self):
        """Test detection of multiple added elements."""
        from src.undo_history import get_action_name

        before = []
        after = [MagicMock(), MagicMock(), MagicMock()]

        result = get_action_name(before, after)
        assert "3" in result or "added" in result.lower()

    def test_multiple_deleted(self):
        """Test detection of multiple deleted elements."""
        from src.undo_history import get_action_name

        before = [MagicMock(), MagicMock(), MagicMock()]
        after = []

        result = get_action_name(before, after)
        assert "3" in result or "delete" in result.lower()

    def test_none_before_list(self):
        """Test with None as before list."""
        from src.undo_history import get_action_name

        after = [MagicMock()]
        after[0].tool.value = "pen"

        result = get_action_name(None, after)
        assert "drew" in result.lower() or "line" in result.lower() or "added" in result.lower()

    def test_none_after_list(self):
        """Test with None as after list."""
        from src.undo_history import get_action_name

        before = [MagicMock()]

        result = get_action_name(before, None)
        assert "delete" in result.lower()

    def test_all_tool_types(self):
        """Test all supported tool types."""
        from src.undo_history import get_action_name

        tool_types = [
            ("pen", ["drew", "line"]),
            ("highlighter", ["highlight"]),
            ("line", ["drew", "line"]),
            ("arrow", ["arrow"]),
            ("rectangle", ["rectangle", "drew"]),
            ("ellipse", ["ellipse", "drew"]),
            ("text", ["text"]),
            ("blur", ["blur"]),
            ("pixelate", ["pixelate"]),
            ("number", ["number"]),
            ("stamp", ["stamp"]),
            ("callout", ["callout"]),
        ]

        for tool_value, expected_keywords in tool_types:
            after = [MagicMock()]
            after[0].tool.value = tool_value
            result = get_action_name([], after).lower()
            assert any(kw in result for kw in expected_keywords), f"Tool {tool_value} should match one of {expected_keywords}, got: {result}"

    def test_unknown_tool_type(self):
        """Test unknown tool type fallback."""
        from src.undo_history import get_action_name

        after = [MagicMock()]
        after[0].tool.value = "unknown_tool"

        result = get_action_name([], after)
        assert "added" in result.lower() or "element" in result.lower()

    def test_empty_lists(self):
        """Test with both empty lists."""
        from src.undo_history import get_action_name

        result = get_action_name([], [])
        assert "modif" in result.lower()

    def test_both_none_lists(self):
        """Test with both None lists."""
        from src.undo_history import get_action_name

        result = get_action_name(None, None)
        # Both None means len 0 = 0, so "modified"
        assert "modif" in result.lower()

    def test_single_element_modification(self):
        """Test modification of single element."""
        from src.undo_history import get_action_name

        before = [MagicMock()]
        after = [MagicMock()]
        # Same length = modification
        result = get_action_name(before, after)
        assert "modif" in result.lower()

    def test_large_add_count(self):
        """Test adding many elements."""
        from src.undo_history import get_action_name

        before = []
        after = [MagicMock() for _ in range(10)]

        result = get_action_name(before, after)
        assert "10" in result or "added" in result.lower()

    def test_large_delete_count(self):
        """Test deleting many elements."""
        from src.undo_history import get_action_name

        before = [MagicMock() for _ in range(7)]
        after = []

        result = get_action_name(before, after)
        assert "7" in result or "delete" in result.lower()

    def test_tool_value_access_for_new_element(self):
        """Test that new element's tool.value is accessed for action name."""
        from src.undo_history import get_action_name

        elem = MagicMock()
        elem.tool.value = "rectangle"
        after = [elem]

        result = get_action_name([], after)
        # Should access tool.value and get a rectangle-related message
        assert "rectangle" in result.lower() or "drew" in result.lower()


class TestUndoHistoryEntry:
    """Test UndoHistoryEntry class."""

    def test_entry_exists(self):
        """Test that UndoHistoryEntry class exists."""
        from src.undo_history import UndoHistoryEntry

        entry = UndoHistoryEntry("Test action", 0)
        assert entry.name == "Test action"
        assert entry.index == 0

    def test_entry_with_different_indices(self):
        """Test UndoHistoryEntry with various index values."""
        from src.undo_history import UndoHistoryEntry

        for idx in [0, 1, 5, 10, 100]:
            entry = UndoHistoryEntry(f"Action {idx}", idx)
            assert entry.index == idx
            assert entry.name == f"Action {idx}"

    def test_entry_with_unicode_name(self):
        """Test UndoHistoryEntry with Unicode characters."""
        from src.undo_history import UndoHistoryEntry

        entry = UndoHistoryEntry("Drew rectangle", 0)
        assert entry.name == "Drew rectangle"

    def test_entry_with_empty_name(self):
        """Test UndoHistoryEntry with empty name."""
        from src.undo_history import UndoHistoryEntry

        entry = UndoHistoryEntry("", 0)
        assert entry.name == ""
        assert entry.index == 0


class TestUndoHistoryModuleImport:
    """Test undo_history module imports."""

    def test_module_imports(self):
        """Test that undo_history module imports successfully."""
        from src import undo_history

        assert hasattr(undo_history, "UndoRedoButtons")
        assert hasattr(undo_history, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.undo_history import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestUndoRedoButtonsClass:
    """Test UndoRedoButtons class structure."""

    def test_class_has_required_methods(self):
        """Test that UndoRedoButtons has required methods."""
        from src.undo_history import UndoRedoButtons

        # Check for get_widget method
        assert hasattr(UndoRedoButtons, "get_widget")

    def test_gtk_check_in_init(self):
        """Test that UndoRedoButtons checks GTK_AVAILABLE in init."""
        from src.undo_history import UndoRedoButtons
        import inspect

        # Check that __init__ has GTK check
        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "GTK_AVAILABLE" in source or "RuntimeError" in source


class TestUndoRedoButtonsWithGtk:
    """Test UndoRedoButtons with GTK available."""

    def test_init_signature(self):
        """Test that init has correct signature."""
        from src.undo_history import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.undo_history import UndoRedoButtons
        import inspect

        sig = inspect.signature(UndoRedoButtons.__init__)
        params = list(sig.parameters.keys())
        assert "on_undo" in params
        assert "on_redo" in params
        assert "on_undo_to" in params
        assert "on_redo_to" in params
        assert "get_undo_stack" in params
        assert "get_redo_stack" in params
        assert "get_elements" in params

    def test_get_widget_method(self):
        """Test get_widget method exists."""
        from src.undo_history import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.undo_history import UndoRedoButtons
        import inspect

        assert hasattr(UndoRedoButtons, "get_widget")
        assert callable(getattr(UndoRedoButtons, "get_widget"))


class TestUndoHistoryI18n:
    """Test that undo_history uses internationalization."""

    def test_imports_i18n(self):
        """Test that undo_history imports i18n."""
        from src import undo_history
        import inspect

        source = inspect.getsource(undo_history)
        assert "from .i18n import _" in source or "from src.i18n import _" in source


class TestUndoHistoryModuleStructure:
    """Test undo_history module structure."""

    def test_has_css_provider_flag(self):
        """Test that module has CSS provider deduplication flag."""
        from src import undo_history

        # Check for the _css_applied pattern used in other modules
        assert hasattr(undo_history, "_css_applied")

    def test_css_applied_is_bool(self):
        """Test that _css_applied is boolean."""
        from src.undo_history import _css_applied

        assert isinstance(_css_applied, bool)
