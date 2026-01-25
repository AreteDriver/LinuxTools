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


class TestUndoRedoButtonsMethods:
    """Test UndoRedoButtons method structure."""

    def test_has_apply_styles_method(self):
        """Test UndoRedoButtons has _apply_styles method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "_apply_styles")

    def test_has_create_undo_popover_method(self):
        """Test UndoRedoButtons has _create_undo_popover method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "_create_undo_popover")

    def test_has_create_redo_popover_method(self):
        """Test UndoRedoButtons has _create_redo_popover method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "_create_redo_popover")

    def test_has_update_sensitivity_method(self):
        """Test UndoRedoButtons has update_sensitivity method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "update_sensitivity")

    def test_has_on_undo_dropdown_toggled_method(self):
        """Test UndoRedoButtons has _on_undo_dropdown_toggled method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "_on_undo_dropdown_toggled")

    def test_has_on_redo_dropdown_toggled_method(self):
        """Test UndoRedoButtons has _on_redo_dropdown_toggled method."""
        from src.undo_history import UndoRedoButtons

        assert hasattr(UndoRedoButtons, "_on_redo_dropdown_toggled")


class TestUndoHistoryEntryComparison:
    """Test UndoHistoryEntry edge cases."""

    def test_entries_are_independent(self):
        """Test that entries are independent objects."""
        from src.undo_history import UndoHistoryEntry

        entry1 = UndoHistoryEntry("Action A", 0)
        entry2 = UndoHistoryEntry("Action B", 1)

        assert entry1.name != entry2.name
        assert entry1.index != entry2.index

    def test_entry_with_negative_index(self):
        """Test UndoHistoryEntry with negative index (edge case)."""
        from src.undo_history import UndoHistoryEntry

        entry = UndoHistoryEntry("Action", -1)
        assert entry.index == -1

    def test_entry_with_large_index(self):
        """Test UndoHistoryEntry with large index."""
        from src.undo_history import UndoHistoryEntry

        entry = UndoHistoryEntry("Action", 999999)
        assert entry.index == 999999


class TestGetActionNameReturnType:
    """Test get_action_name return type consistency."""

    def test_always_returns_string(self):
        """Test that get_action_name always returns a string."""
        from src.undo_history import get_action_name

        test_cases = [
            ([], []),
            (None, None),
            ([MagicMock()], []),
            ([], [MagicMock()]),
            ([MagicMock()], [MagicMock()]),
        ]

        for before, after in test_cases:
            if after and len(after) > 0:
                for elem in after:
                    elem.tool = MagicMock()
                    elem.tool.value = "pen"
            result = get_action_name(before, after)
            assert isinstance(result, str), f"Failed for {before}, {after}"
            assert len(result) > 0, f"Empty result for {before}, {after}"


class TestUndoRedoButtonsSourceInspection:
    """Test UndoRedoButtons implementation via source inspection."""

    def test_init_stores_callbacks(self):
        """Test __init__ stores callback references."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.on_undo = on_undo" in source
        assert "self.on_redo = on_redo" in source
        assert "self.on_undo_to = on_undo_to" in source
        assert "self.on_redo_to = on_redo_to" in source

    def test_init_stores_getter_functions(self):
        """Test __init__ stores getter functions."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.get_undo_stack = get_undo_stack" in source
        assert "self.get_redo_stack = get_redo_stack" in source
        assert "self.get_elements = get_elements" in source

    def test_init_creates_container(self):
        """Test __init__ creates container box."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.container" in source
        assert "Gtk.Box" in source

    def test_init_creates_undo_button(self):
        """Test __init__ creates undo button."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.undo_btn" in source
        assert "Gtk.Button" in source
        assert "undo-btn" in source

    def test_init_creates_redo_button(self):
        """Test __init__ creates redo button."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.redo_btn" in source
        assert "redo-btn" in source

    def test_init_creates_dropdown_buttons(self):
        """Test __init__ creates dropdown buttons."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "self.undo_dropdown" in source
        assert "self.redo_dropdown" in source
        assert "Gtk.MenuButton" in source

    def test_init_connects_click_handlers(self):
        """Test __init__ connects click handlers."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "connect" in source
        assert "clicked" in source
        assert "toggled" in source

    def test_init_creates_popovers(self):
        """Test __init__ creates popover menus."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "_create_undo_popover" in source
        assert "_create_redo_popover" in source

    def test_create_undo_popover_structure(self):
        """Test _create_undo_popover creates popover."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._create_undo_popover)
        assert "Gtk.Popover" in source
        assert "self.undo_popover" in source
        assert "history-popover" in source

    def test_create_undo_popover_creates_list(self):
        """Test _create_undo_popover creates list container."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._create_undo_popover)
        assert "self.undo_list" in source
        assert "Gtk.Box" in source

    def test_create_undo_popover_sets_relative(self):
        """Test _create_undo_popover sets relative widget."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._create_undo_popover)
        assert "set_relative_to" in source
        assert "undo_dropdown" in source

    def test_create_redo_popover_structure(self):
        """Test _create_redo_popover creates popover."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._create_redo_popover)
        assert "Gtk.Popover" in source
        assert "self.redo_popover" in source

    def test_on_undo_dropdown_toggled_checks_active(self):
        """Test _on_undo_dropdown_toggled checks button active state."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "get_active" in source
        assert "if not" in source

    def test_on_undo_dropdown_toggled_clears_children(self):
        """Test _on_undo_dropdown_toggled clears existing items."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "get_children" in source
        assert "remove" in source

    def test_on_undo_dropdown_toggled_populates_list(self):
        """Test _on_undo_dropdown_toggled populates history list."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "get_undo_stack" in source
        assert "get_action_name" in source

    def test_on_undo_dropdown_toggled_limits_items(self):
        """Test _on_undo_dropdown_toggled limits to 10 items."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "9" in source  # if i >= 9
        assert "break" in source

    def test_on_undo_dropdown_toggled_handles_empty(self):
        """Test _on_undo_dropdown_toggled handles empty stack."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "if not undo_stack" in source
        assert "No undo history" in source

    def test_on_redo_dropdown_toggled_checks_active(self):
        """Test _on_redo_dropdown_toggled checks button active state."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_redo_dropdown_toggled)
        assert "get_active" in source

    def test_on_redo_dropdown_toggled_populates_list(self):
        """Test _on_redo_dropdown_toggled populates history list."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_redo_dropdown_toggled)
        assert "get_redo_stack" in source
        assert "get_action_name" in source

    def test_on_redo_dropdown_toggled_handles_empty(self):
        """Test _on_redo_dropdown_toggled handles empty stack."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_redo_dropdown_toggled)
        assert "if not redo_stack" in source
        assert "No redo history" in source

    def test_on_undo_item_clicked_popdown(self):
        """Test _on_undo_item_clicked pops down popover."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_item_clicked)
        assert "popdown" in source
        assert "on_undo_to" in source

    def test_on_redo_item_clicked_popdown(self):
        """Test _on_redo_item_clicked pops down popover."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_redo_item_clicked)
        assert "popdown" in source
        assert "on_redo_to" in source

    def test_update_sensitivity_sets_buttons(self):
        """Test update_sensitivity sets button sensitivity."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.update_sensitivity)
        assert "set_sensitive" in source
        assert "can_undo" in source
        assert "can_redo" in source

    def test_update_sensitivity_sets_all_buttons(self):
        """Test update_sensitivity sets both buttons and dropdowns."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.update_sensitivity)
        assert "undo_btn" in source
        assert "undo_dropdown" in source
        assert "redo_btn" in source
        assert "redo_dropdown" in source

    def test_get_widget_returns_container(self):
        """Test get_widget returns container."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.get_widget)
        assert "return self.container" in source


class TestUndoRedoButtonsCSS:
    """Test UndoRedoButtons CSS handling."""

    def test_apply_styles_uses_global_flag(self):
        """Test _apply_styles uses global flag to prevent duplication."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._apply_styles)
        assert "_css_applied" in source
        assert "global" in source

    def test_apply_styles_creates_css_provider(self):
        """Test _apply_styles creates CSS provider."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._apply_styles)
        assert "CssProvider" in source
        assert "load_from_data" in source

    def test_css_contains_button_styles(self):
        """Test CSS contains button styles."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._apply_styles)
        assert ".undo-btn" in source
        assert ".redo-btn" in source
        assert ".undo-dropdown" in source
        assert ".redo-dropdown" in source

    def test_css_contains_hover_states(self):
        """Test CSS contains hover states."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._apply_styles)
        assert ":hover" in source
        assert ":disabled" in source

    def test_css_contains_popover_styles(self):
        """Test CSS contains popover styles."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._apply_styles)
        assert ".history-popover" in source
        assert ".history-item" in source
        assert ".history-label" in source


class TestGetActionNameSourceInspection:
    """Test get_action_name implementation via source inspection."""

    def test_handles_none_lists(self):
        """Test get_action_name handles None lists."""
        from src.undo_history import get_action_name
        import inspect

        source = inspect.getsource(get_action_name)
        assert "if elements_before" in source or "elements_before else" in source

    def test_uses_tool_name_mapping(self):
        """Test get_action_name uses tool name mapping."""
        from src.undo_history import get_action_name
        import inspect

        source = inspect.getsource(get_action_name)
        assert "tool_names" in source
        assert "pen" in source
        assert "highlighter" in source
        assert "rectangle" in source
        assert "text" in source

    def test_checks_length_difference(self):
        """Test get_action_name checks length difference."""
        from src.undo_history import get_action_name
        import inspect

        source = inspect.getsource(get_action_name)
        assert "len_before" in source
        assert "len_after" in source

    def test_returns_formatted_count(self):
        """Test get_action_name formats count for multiple elements."""
        from src.undo_history import get_action_name
        import inspect

        source = inspect.getsource(get_action_name)
        assert ".format(diff)" in source


class TestUndoHistoryEdgeCases:
    """Test edge cases and error handling."""

    def test_buttons_require_gtk(self):
        """Test UndoRedoButtons raises error without GTK."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "GTK_AVAILABLE" in source
        assert "RuntimeError" in source

    def test_history_reversed_order(self):
        """Test history shows most recent first."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        assert "reversed" in source

    def test_redo_reversed_order(self):
        """Test redo history shows next action first."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_redo_dropdown_toggled)
        assert "reversed" in source


class TestUndoHistoryI18nIntegration:
    """Test internationalization integration."""

    def test_uses_translation_function(self):
        """Test module uses _() translation function."""
        from src import undo_history
        import inspect

        source = inspect.getsource(undo_history)
        assert '_("' in source

    def test_action_names_translated(self):
        """Test action names use translation."""
        from src.undo_history import get_action_name
        import inspect

        source = inspect.getsource(get_action_name)
        assert "_(" in source

    def test_button_tooltips_translated(self):
        """Test button tooltips use translation."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        assert "_(" in source
        assert "Undo" in source or "Redo" in source

    def test_empty_history_message_translated(self):
        """Test empty history messages use translation."""
        from src.undo_history import UndoRedoButtons
        import inspect

        undo_source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        redo_source = inspect.getsource(UndoRedoButtons._on_redo_dropdown_toggled)
        assert "_(" in undo_source
        assert "_(" in redo_source


class TestUndoHistoryButtonLabels:
    """Test button labels and icons."""

    def test_undo_button_uses_unicode(self):
        """Test undo button uses Unicode arrow."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        # Should have Unicode undo arrow ↶
        assert "\\u21b6" in source or "\u21b6" in source

    def test_redo_button_uses_unicode(self):
        """Test redo button uses Unicode arrow."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        # Should have Unicode redo arrow ↷
        assert "\\u21b7" in source or "\u21b7" in source

    def test_dropdown_uses_triangle(self):
        """Test dropdown button uses triangle."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons.__init__)
        # Should have Unicode triangle ▾
        assert "\\u25be" in source or "\u25be" in source

    def test_history_items_use_bullet(self):
        """Test history items use bullet character."""
        from src.undo_history import UndoRedoButtons
        import inspect

        source = inspect.getsource(UndoRedoButtons._on_undo_dropdown_toggled)
        # Should have Unicode bullet •
        assert "\\u2022" in source or "\u2022" in source


# =============================================================================
# Functional GTK Tests (require xvfb or display)
# =============================================================================


class TestUndoRedoButtonsFunctional:
    """Functional tests for UndoRedoButtons."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.undo_history import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return {"Gtk": Gtk}

    def test_create_buttons(self, gtk_setup):
        """Test creating UndoRedoButtons instance."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        assert buttons is not None
        assert buttons.undo_btn is not None
        assert buttons.redo_btn is not None
        assert buttons.undo_dropdown is not None
        assert buttons.redo_dropdown is not None
        assert buttons.container is not None

    def test_get_widget(self, gtk_setup):
        """Test get_widget returns container."""
        from src.undo_history import UndoRedoButtons
        Gtk = gtk_setup["Gtk"]

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        widget = buttons.get_widget()
        assert isinstance(widget, Gtk.Box)
        assert widget == buttons.container

    def test_update_sensitivity_can_undo(self, gtk_setup):
        """Test update_sensitivity with can_undo=True."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        buttons.update_sensitivity(can_undo=True, can_redo=False)

        assert buttons.undo_btn.get_sensitive() is True
        assert buttons.undo_dropdown.get_sensitive() is True
        assert buttons.redo_btn.get_sensitive() is False
        assert buttons.redo_dropdown.get_sensitive() is False

    def test_update_sensitivity_can_redo(self, gtk_setup):
        """Test update_sensitivity with can_redo=True."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        buttons.update_sensitivity(can_undo=False, can_redo=True)

        assert buttons.undo_btn.get_sensitive() is False
        assert buttons.redo_btn.get_sensitive() is True

    def test_update_sensitivity_both(self, gtk_setup):
        """Test update_sensitivity with both enabled."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        buttons.update_sensitivity(can_undo=True, can_redo=True)

        assert buttons.undo_btn.get_sensitive() is True
        assert buttons.redo_btn.get_sensitive() is True

    def test_undo_button_click_calls_callback(self, gtk_setup):
        """Test clicking undo button calls callback."""
        from src.undo_history import UndoRedoButtons

        undo_called = []

        buttons = UndoRedoButtons(
            on_undo=lambda: undo_called.append(True),
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        # Simulate click by calling the callback directly
        buttons.on_undo()

        assert len(undo_called) == 1

    def test_redo_button_click_calls_callback(self, gtk_setup):
        """Test clicking redo button calls callback."""
        from src.undo_history import UndoRedoButtons

        redo_called = []

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: redo_called.append(True),
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        buttons.on_redo()

        assert len(redo_called) == 1

    def test_popovers_created(self, gtk_setup):
        """Test that popovers are created."""
        from src.undo_history import UndoRedoButtons
        Gtk = gtk_setup["Gtk"]

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        assert isinstance(buttons.undo_popover, Gtk.Popover)
        assert isinstance(buttons.redo_popover, Gtk.Popover)

    def test_undo_dropdown_toggle_empty_stack(self, gtk_setup):
        """Test undo dropdown with empty stack."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        # Simulate dropdown toggle
        mock_button = MagicMock()
        mock_button.get_active.return_value = True

        buttons._on_undo_dropdown_toggled(mock_button)

        # Should have created "No undo history" label
        children = buttons.undo_list.get_children()
        assert len(children) == 1

    def test_redo_dropdown_toggle_empty_stack(self, gtk_setup):
        """Test redo dropdown with empty stack."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        mock_button = MagicMock()
        mock_button.get_active.return_value = True

        buttons._on_redo_dropdown_toggled(mock_button)

        children = buttons.redo_list.get_children()
        assert len(children) == 1

    def test_undo_dropdown_with_stack(self, gtk_setup):
        """Test undo dropdown with items in stack."""
        from src.undo_history import UndoRedoButtons

        # Create mock elements
        elem1 = MagicMock()
        elem1.tool.value = "rectangle"

        elem2 = MagicMock()
        elem2.tool.value = "pen"

        undo_stack = [
            [],  # State before first action
            [elem1],  # State after first action
        ]

        current_elements = [elem1, elem2]

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: undo_stack,
            get_redo_stack=lambda: [],
            get_elements=lambda: current_elements,
        )

        mock_button = MagicMock()
        mock_button.get_active.return_value = True

        buttons._on_undo_dropdown_toggled(mock_button)

        # Should have history items
        children = buttons.undo_list.get_children()
        assert len(children) >= 1

    def test_undo_item_clicked(self, gtk_setup):
        """Test clicking undo history item."""
        from src.undo_history import UndoRedoButtons

        undo_to_called = []

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: undo_to_called.append(idx),
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        mock_button = MagicMock()
        buttons._on_undo_item_clicked(mock_button, 2)

        assert undo_to_called == [2]

    def test_redo_item_clicked(self, gtk_setup):
        """Test clicking redo history item."""
        from src.undo_history import UndoRedoButtons

        redo_to_called = []

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: redo_to_called.append(idx),
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        mock_button = MagicMock()
        buttons._on_redo_item_clicked(mock_button, 3)

        assert redo_to_called == [3]

    def test_dropdown_not_active_returns_early(self, gtk_setup):
        """Test dropdown does nothing when not active."""
        from src.undo_history import UndoRedoButtons

        buttons = UndoRedoButtons(
            on_undo=lambda: None,
            on_redo=lambda: None,
            on_undo_to=lambda idx: None,
            on_redo_to=lambda idx: None,
            get_undo_stack=lambda: [],
            get_redo_stack=lambda: [],
            get_elements=lambda: [],
        )

        mock_button = MagicMock()
        mock_button.get_active.return_value = False

        # Clear existing children
        for child in buttons.undo_list.get_children():
            buttons.undo_list.remove(child)

        buttons._on_undo_dropdown_toggled(mock_button)

        # Should not have added any children
        children = buttons.undo_list.get_children()
        assert len(children) == 0
