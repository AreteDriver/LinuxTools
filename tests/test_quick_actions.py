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


class TestCreateSelectionActionsEnabledChecks:
    """Test enabled_check functions in create_selection_actions."""

    def test_has_selection_with_selection(self):
        """Test actions enabled when selection exists."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0, 1]
        mock_editor.editor_state.is_selection_locked.return_value = False

        actions = create_selection_actions(mock_editor)

        # Find the copy action (should be enabled with selection)
        copy_action = next((a for a in actions if "Copy" in a.tooltip or "Ctrl+C" in a.tooltip), None)
        assert copy_action is not None
        assert copy_action.enabled_check() is True

    def test_has_selection_without_selection(self):
        """Test actions disabled when no selection."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        # Find the copy action (should be disabled without selection)
        copy_action = next((a for a in actions if "Copy" in a.tooltip or "Ctrl+C" in a.tooltip), None)
        assert copy_action is not None
        assert copy_action.enabled_check() is False

    def test_has_selection_with_none_editor_state(self):
        """Test actions when editor_state is None."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = None

        actions = create_selection_actions(mock_editor)

        # Actions should be disabled when editor_state is None
        for action in actions:
            # All actions require selection, so all should be disabled
            assert action.enabled_check() is False

    def test_is_unlocked_check(self):
        """Test is_unlocked enabled check."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]
        mock_editor.editor_state.is_selection_locked.return_value = True

        actions = create_selection_actions(mock_editor)

        # Find delete action (requires unlocked)
        delete_action = next((a for a in actions if "Delete" in a.tooltip or "Del" in a.tooltip), None)
        assert delete_action is not None
        # Should be disabled because selection is locked
        assert delete_action.enabled_check() is False

    def test_has_multiple_check(self):
        """Test has_multiple enabled check for group action."""
        from src.quick_actions import create_selection_actions

        # Single selection
        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)
        group_action = next((a for a in actions if "Group" in a.tooltip or "Ctrl+G" in a.tooltip), None)
        assert group_action is not None
        assert group_action.enabled_check() is False  # Single item can't be grouped

        # Multiple selection
        mock_editor.editor_state.selected_indices = [0, 1, 2]
        actions = create_selection_actions(mock_editor)
        group_action = next((a for a in actions if "Group" in a.tooltip or "Ctrl+G" in a.tooltip), None)
        assert group_action.enabled_check() is True

    def test_action_callbacks_are_callable(self):
        """Test that all action callbacks are callable."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)

        for action in actions:
            assert callable(action.callback)

    def test_action_tooltips_are_strings(self):
        """Test that all action tooltips are non-empty strings."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        for action in actions:
            assert isinstance(action.tooltip, str)
            assert len(action.tooltip) > 0


class TestQuickActionEdgeCases:
    """Test edge cases for QuickAction class."""

    def test_action_with_lambda_callback(self):
        """Test QuickAction with lambda callback."""
        from src.quick_actions import QuickAction

        result = []
        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=lambda: result.append("called"),
        )

        action.callback()
        assert result == ["called"]

    def test_action_enabled_check_with_complex_logic(self):
        """Test QuickAction with complex enabled_check."""
        from src.quick_actions import QuickAction

        state = {"count": 0}

        def complex_check():
            return state["count"] > 5

        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=MagicMock(),
            enabled_check=complex_check,
        )

        assert action.enabled_check() is False
        state["count"] = 10
        assert action.enabled_check() is True

    def test_action_with_unicode_icon(self):
        """Test QuickAction with various Unicode icons."""
        from src.quick_actions import QuickAction

        icons = ["\u2715", "\u2750", "\u2398", "\u2191", "\u2193", "\U0001f512", "\u25a3"]

        for icon in icons:
            action = QuickAction(
                icon=icon,
                tooltip="Test",
                callback=MagicMock(),
            )
            assert action.icon == icon
            assert len(action.icon) >= 1

    def test_action_with_long_tooltip(self):
        """Test QuickAction with long tooltip."""
        from src.quick_actions import QuickAction

        long_tooltip = "This is a very long tooltip " * 10
        action = QuickAction(
            icon="X",
            tooltip=long_tooltip,
            callback=MagicMock(),
        )

        assert action.tooltip == long_tooltip


class TestQuickActionsCssApplied:
    """Test CSS provider deduplication flag."""

    def test_css_applied_exists(self):
        """Test _css_applied module variable exists."""
        from src import quick_actions

        assert hasattr(quick_actions, "_css_applied")

    def test_css_applied_is_bool(self):
        """Test _css_applied is boolean."""
        from src.quick_actions import _css_applied

        assert isinstance(_css_applied, bool)


class TestCreateSelectionActionsCallbacks:
    """Test callback behavior in create_selection_actions."""

    def test_delete_action_calls_delete_selected(self):
        """Test delete action calls _delete_selected."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]
        mock_editor.editor_state.is_selection_locked.return_value = False

        actions = create_selection_actions(mock_editor)

        delete_action = next(a for a in actions if "Delete" in a.tooltip or "Del" in a.tooltip)
        delete_action.callback()

        mock_editor._delete_selected.assert_called_once()

    def test_duplicate_action_calls_duplicate_selected(self):
        """Test duplicate action calls _duplicate_selected."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]
        mock_editor.editor_state.is_selection_locked.return_value = False

        actions = create_selection_actions(mock_editor)

        dup_action = next(a for a in actions if "Duplicate" in a.tooltip or "Ctrl+D" in a.tooltip)
        dup_action.callback()

        mock_editor._duplicate_selected.assert_called_once()

    def test_copy_action_calls_copy_annotations(self):
        """Test copy action calls _copy_annotations."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)

        copy_action = next(a for a in actions if "Copy" in a.tooltip or "Ctrl+C" in a.tooltip)
        copy_action.callback()

        mock_editor._copy_annotations.assert_called_once()

    def test_bring_to_front_action(self):
        """Test bring to front action calls _bring_to_front."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)

        front_action = next(a for a in actions if "Front" in a.tooltip)
        front_action.callback()

        mock_editor._bring_to_front.assert_called_once()

    def test_send_to_back_action(self):
        """Test send to back action calls _send_to_back."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)

        back_action = next(a for a in actions if "Back" in a.tooltip)
        back_action.callback()

        mock_editor._send_to_back.assert_called_once()

    def test_lock_action_calls_toggle_lock(self):
        """Test lock action calls _toggle_lock."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]

        actions = create_selection_actions(mock_editor)

        lock_action = next(a for a in actions if "Lock" in a.tooltip)
        lock_action.callback()

        mock_editor._toggle_lock.assert_called_once()

    def test_group_action_calls_group_selected(self):
        """Test group action calls _group_selected."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0, 1, 2]

        actions = create_selection_actions(mock_editor)

        group_action = next(a for a in actions if "Group" in a.tooltip)
        group_action.callback()

        mock_editor._group_selected.assert_called_once()


class TestQuickActionsPanelMethods:
    """Test QuickActionsPanel methods structure."""

    def test_has_rebuild_buttons_method(self):
        """Test QuickActionsPanel has _rebuild_buttons method."""
        from src.quick_actions import QuickActionsPanel

        assert hasattr(QuickActionsPanel, "_rebuild_buttons")

    def test_has_on_leave_handler(self):
        """Test QuickActionsPanel has _on_leave handler."""
        from src.quick_actions import QuickActionsPanel

        assert hasattr(QuickActionsPanel, "_on_leave")

    def test_has_on_enter_handler(self):
        """Test QuickActionsPanel has _on_enter handler."""
        from src.quick_actions import QuickActionsPanel

        assert hasattr(QuickActionsPanel, "_on_enter")

    def test_has_delayed_hide_method(self):
        """Test QuickActionsPanel has _delayed_hide method."""
        from src.quick_actions import QuickActionsPanel

        assert hasattr(QuickActionsPanel, "_delayed_hide")


class TestCreateSelectionActionsCount:
    """Test create_selection_actions returns correct number of actions."""

    def test_returns_exactly_seven_actions(self):
        """Test that exactly 7 actions are returned."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        assert len(actions) == 7

    def test_action_order_is_consistent(self):
        """Test that actions are in consistent order."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = []

        actions = create_selection_actions(mock_editor)

        # Delete should be first
        assert "Delete" in actions[0].tooltip or "Del" in actions[0].tooltip
        # Group should be last
        assert "Group" in actions[-1].tooltip


class TestQuickActionEquality:
    """Test QuickAction object behavior."""

    def test_actions_are_independent(self):
        """Test that QuickAction objects are independent."""
        from src.quick_actions import QuickAction

        action1 = QuickAction(
            icon="A",
            tooltip="Action A",
            callback=MagicMock(),
        )
        action2 = QuickAction(
            icon="B",
            tooltip="Action B",
            callback=MagicMock(),
        )

        assert action1.icon != action2.icon
        assert action1.tooltip != action2.tooltip
        assert action1.callback != action2.callback

    def test_action_callback_can_be_called_multiple_times(self):
        """Test callback can be invoked multiple times."""
        from src.quick_actions import QuickAction

        counter = [0]
        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=lambda: counter.__setitem__(0, counter[0] + 1),
        )

        action.callback()
        action.callback()
        action.callback()

        assert counter[0] == 3


class TestEnabledCheckInteraction:
    """Test enabled_check with various editor states."""

    def test_delete_disabled_when_locked(self):
        """Test delete action disabled when selection is locked."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0, 1]
        mock_editor.editor_state.is_selection_locked.return_value = True

        actions = create_selection_actions(mock_editor)
        delete_action = next(a for a in actions if "Delete" in a.tooltip or "Del" in a.tooltip)

        assert delete_action.enabled_check() is False

    def test_copy_enabled_when_locked(self):
        """Test copy action still enabled when selection is locked."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0, 1]
        mock_editor.editor_state.is_selection_locked.return_value = True

        actions = create_selection_actions(mock_editor)
        copy_action = next(a for a in actions if "Copy" in a.tooltip)

        # Copy should still be enabled (doesn't modify)
        assert copy_action.enabled_check() is True

    def test_bring_to_front_enabled_when_locked(self):
        """Test bring to front enabled when locked."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = MagicMock()
        mock_editor.editor_state.selected_indices = [0]
        mock_editor.editor_state.is_selection_locked.return_value = True

        actions = create_selection_actions(mock_editor)
        front_action = next(a for a in actions if "Front" in a.tooltip)

        # Should be enabled (just changes order)
        assert front_action.enabled_check() is True


class TestQuickActionsPanelSourceInspection:
    """Test QuickActionsPanel implementation via source inspection."""

    def test_init_creates_popup_window(self):
        """Test __init__ creates popup window."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "Gtk.Window" in source
        assert "POPUP" in source

    def test_init_sets_window_hints(self):
        """Test __init__ sets window type hints."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "set_type_hint" in source
        assert "set_decorated" in source
        assert "set_skip_taskbar_hint" in source
        assert "set_skip_pager_hint" in source

    def test_init_creates_container(self):
        """Test __init__ creates container box."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "Gtk.Box" in source
        assert "container" in source

    def test_init_connects_mouse_events(self):
        """Test __init__ connects mouse event handlers."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "leave-notify-event" in source
        assert "enter-notify-event" in source
        assert "_on_leave" in source
        assert "_on_enter" in source

    def test_init_tracks_visibility_and_timer(self):
        """Test __init__ initializes visibility and timer state."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "self.visible" in source
        assert "_hide_timer_id" in source

    def test_set_actions_stores_and_rebuilds(self):
        """Test set_actions stores actions and rebuilds buttons."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.set_actions)
        assert "self._actions = actions" in source
        assert "_rebuild_buttons" in source

    def test_rebuild_buttons_clears_children(self):
        """Test _rebuild_buttons clears existing children."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._rebuild_buttons)
        assert "get_children" in source
        assert "remove" in source

    def test_rebuild_buttons_adds_separators(self):
        """Test _rebuild_buttons adds separators between groups."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._rebuild_buttons)
        assert "Gtk.Separator" in source
        assert "quick-action-sep" in source

    def test_rebuild_buttons_creates_action_buttons(self):
        """Test _rebuild_buttons creates action buttons."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._rebuild_buttons)
        assert "Gtk.Button" in source
        assert "set_tooltip_text" in source
        assert "quick-action-btn" in source
        assert "set_sensitive" in source

    def test_rebuild_buttons_connects_click_handler(self):
        """Test _rebuild_buttons connects click handlers."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._rebuild_buttons)
        assert "connect" in source
        assert "clicked" in source
        assert "_on_action_clicked" in source

    def test_on_action_clicked_hides_and_calls(self):
        """Test _on_action_clicked hides panel and calls callback."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._on_action_clicked)
        assert "self.hide()" in source
        assert "action.callback()" in source

    def test_show_at_checks_empty_actions(self):
        """Test show_at returns early when no actions."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "if not self._actions" in source
        assert "return" in source

    def test_show_at_positions_popup(self):
        """Test show_at positions popup on screen."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "popup.move" in source
        assert "popup.show_all" in source

    def test_show_at_uses_element_bbox(self):
        """Test show_at uses element bounding box for positioning."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "element_bbox" in source
        assert "x1, y1, x2, y2" in source

    def test_show_at_keeps_on_screen(self):
        """Test show_at keeps panel on screen."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "get_width" in source
        assert "max(" in source
        assert "min(" in source

    def test_show_at_cancels_hide_timer(self):
        """Test show_at cancels pending hide timer."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "_hide_timer_id" in source
        assert "source_remove" in source

    def test_hide_removes_timer_and_hides(self):
        """Test hide removes timer and hides popup."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.hide)
        assert "_hide_timer_id" in source
        assert "popup.hide" in source
        assert "self.visible = False" in source

    def test_on_leave_starts_hide_timer(self):
        """Test _on_leave starts hide timer."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._on_leave)
        assert "timeout_add" in source
        assert "_delayed_hide" in source
        assert "800" in source  # 800ms delay

    def test_on_leave_ignores_inferior_events(self):
        """Test _on_leave ignores inferior notify events."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._on_leave)
        assert "NotifyType.INFERIOR" in source or "INFERIOR" in source

    def test_on_enter_cancels_hide_timer(self):
        """Test _on_enter cancels hide timer."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._on_enter)
        assert "_hide_timer_id" in source
        assert "source_remove" in source

    def test_delayed_hide_calls_hide(self):
        """Test _delayed_hide calls hide method."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._delayed_hide)
        assert "self.hide()" in source
        assert "return False" in source  # Don't repeat

    def test_update_position_checks_visibility(self):
        """Test update_position returns early if not visible."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.update_position)
        assert "if not self.visible" in source
        assert "return" in source

    def test_update_position_converts_coordinates(self):
        """Test update_position converts coordinates."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.update_position)
        assert "get_window" in source
        assert "get_origin" in source
        assert "show_at" in source


class TestQuickActionsPanelCSS:
    """Test QuickActionsPanel CSS handling."""

    def test_apply_styles_uses_global_flag(self):
        """Test _apply_styles uses global flag to prevent duplication."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._apply_styles)
        assert "_css_applied" in source
        assert "global" in source

    def test_apply_styles_creates_css_provider(self):
        """Test _apply_styles creates CSS provider."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._apply_styles)
        assert "CssProvider" in source
        assert "load_from_data" in source

    def test_css_contains_panel_styles(self):
        """Test CSS contains panel class styles."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._apply_styles)
        assert ".quick-actions-panel" in source
        assert "background" in source
        assert "border-radius" in source

    def test_css_contains_button_styles(self):
        """Test CSS contains button styles."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._apply_styles)
        assert ".quick-action-btn" in source
        assert ":hover" in source
        assert ":active" in source
        assert ":disabled" in source

    def test_css_contains_separator_style(self):
        """Test CSS contains separator style."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel._apply_styles)
        assert ".quick-action-sep" in source


class TestCreateSelectionActionsSourceInspection:
    """Test create_selection_actions implementation via source inspection."""

    def test_has_selection_helper(self):
        """Test has_selection helper function exists."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "def has_selection" in source
        assert "selected_indices" in source

    def test_is_unlocked_helper(self):
        """Test is_unlocked helper function exists."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "def is_unlocked" in source
        assert "is_selection_locked" in source

    def test_has_multiple_helper(self):
        """Test has_multiple helper function exists."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "def has_multiple" in source
        assert "len(" in source

    def test_delete_action_defined(self):
        """Test delete action is defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_delete_selected" in source
        assert "Delete" in source or "Del" in source

    def test_duplicate_action_defined(self):
        """Test duplicate action is defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_duplicate_selected" in source
        assert "Duplicate" in source

    def test_copy_action_defined(self):
        """Test copy action is defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_copy_annotations" in source
        assert "Copy" in source

    def test_layer_actions_defined(self):
        """Test bring to front and send to back actions are defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_bring_to_front" in source
        assert "_send_to_back" in source

    def test_lock_action_defined(self):
        """Test lock/unlock action is defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_toggle_lock" in source
        assert "Lock" in source

    def test_group_action_defined(self):
        """Test group action is defined."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        assert "_group_selected" in source
        assert "Group" in source


class TestQuickActionsEdgeCases:
    """Test edge cases and error handling."""

    def test_panel_requires_gtk(self):
        """Test QuickActionsPanel raises error without GTK."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.__init__)
        assert "GTK_AVAILABLE" in source
        assert "RuntimeError" in source

    def test_show_at_handles_empty_actions(self):
        """Test show_at handles empty actions list."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "if not self._actions" in source

    def test_show_at_handles_no_bbox(self):
        """Test show_at handles missing bounding box."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.show_at)
        assert "if element_bbox" in source
        assert "else:" in source

    def test_update_position_handles_no_window(self):
        """Test update_position handles missing window."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.update_position)
        assert "if not window" in source

    def test_update_position_handles_origin_failure(self):
        """Test update_position handles get_origin failure."""
        from src.quick_actions import QuickActionsPanel
        import inspect

        source = inspect.getsource(QuickActionsPanel.update_position)
        assert "origin" in source
        # Checks origin[0] for success
        assert "origin[0]" in source


class TestQuickActionsI18nIntegration:
    """Test internationalization integration."""

    def test_uses_translation_function(self):
        """Test module uses _() translation function."""
        from src import quick_actions
        import inspect

        source = inspect.getsource(quick_actions)
        assert '_("' in source

    def test_action_tooltips_translated(self):
        """Test action tooltips use translation."""
        from src.quick_actions import create_selection_actions
        import inspect

        source = inspect.getsource(create_selection_actions)
        # Tooltips should be wrapped in _()
        assert '_("Delete' in source or "_(" in source


# =============================================================================
# Functional GTK Tests (require xvfb or display)
# =============================================================================


class TestQuickActionsPanelFunctional:
    """Functional tests that create real GTK widgets."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.quick_actions import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        window = Gtk.Window()
        return {"Gtk": Gtk, "window": window}

    def test_create_panel(self, gtk_setup):
        """Test creating a QuickActionsPanel instance."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])

        assert panel is not None
        assert panel.visible is False
        assert panel.popup is not None
        assert panel.container is not None

    def test_panel_set_actions(self, gtk_setup):
        """Test setting actions on panel."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])

        actions = [
            QuickAction(icon="X", tooltip="Delete", callback=lambda: None),
            QuickAction(icon="C", tooltip="Copy", callback=lambda: None),
        ]

        panel.set_actions(actions)

        assert panel._actions == actions

    def test_panel_show_at(self, gtk_setup):
        """Test showing panel at coordinates."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])

        actions = [
            QuickAction(icon="X", tooltip="Delete", callback=lambda: None),
        ]
        panel.set_actions(actions)

        panel.show_at(100, 200)

        assert panel.visible is True

    def test_panel_show_at_empty_actions(self, gtk_setup):
        """Test show_at with no actions returns early."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])

        # No actions set
        panel.show_at(100, 200)

        assert panel.visible is False

    def test_panel_hide(self, gtk_setup):
        """Test hiding panel."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])

        actions = [
            QuickAction(icon="X", tooltip="Delete", callback=lambda: None),
        ]
        panel.set_actions(actions)

        panel.show_at(100, 200)
        assert panel.visible is True

        panel.hide()
        assert panel.visible is False

    def test_panel_show_at_with_bbox(self, gtk_setup):
        """Test showing panel with element bounding box."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])

        actions = [
            QuickAction(icon="X", tooltip="Delete", callback=lambda: None),
        ]
        panel.set_actions(actions)

        bbox = (50.0, 100.0, 150.0, 200.0)
        panel.show_at(100, 150, element_bbox=bbox)

        assert panel.visible is True

    def test_panel_rebuild_buttons(self, gtk_setup):
        """Test _rebuild_buttons creates buttons."""
        from src.quick_actions import QuickActionsPanel, QuickAction
        Gtk = gtk_setup["Gtk"]

        panel = QuickActionsPanel(gtk_setup["window"])

        actions = [
            QuickAction(icon="A", tooltip="Action A", callback=lambda: None),
            QuickAction(icon="B", tooltip="Action B", callback=lambda: None),
            QuickAction(icon="C", tooltip="Action C", callback=lambda: None),
        ]
        panel.set_actions(actions)

        # Force rebuild
        panel._rebuild_buttons()

        # Should have buttons in container
        children = panel.container.get_children()
        assert len(children) > 0

    def test_panel_action_clicked(self, gtk_setup):
        """Test action callback is called on click."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        clicked = []

        def on_click():
            clicked.append(True)

        panel = QuickActionsPanel(gtk_setup["window"])

        action = QuickAction(icon="X", tooltip="Test", callback=on_click)
        panel.set_actions([action])

        # Simulate action click
        panel._on_action_clicked(action)

        assert len(clicked) == 1
        assert panel.visible is False

    def test_panel_enabled_check(self, gtk_setup):
        """Test action with enabled_check."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        enabled = [False]

        panel = QuickActionsPanel(gtk_setup["window"])

        action = QuickAction(
            icon="X",
            tooltip="Test",
            callback=lambda: None,
            enabled_check=lambda: enabled[0],
        )
        panel.set_actions([action])

        # Initially disabled
        panel._rebuild_buttons()
        children = panel.container.get_children()
        # Find buttons (not separators)
        buttons = [c for c in children if hasattr(c, "get_sensitive")]
        if buttons:
            assert buttons[0].get_sensitive() is False

        # Now enable
        enabled[0] = True
        panel._rebuild_buttons()
        children = panel.container.get_children()
        buttons = [c for c in children if hasattr(c, "get_sensitive")]
        if buttons:
            assert buttons[0].get_sensitive() is True

    def test_panel_show_at_fallback_position(self, gtk_setup):
        """Test show_at uses fallback position when panel_y < 10."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.set_actions([QuickAction(icon="X", tooltip="Test", callback=lambda: None)])

        # Show at position where y would be < 10
        panel.show_at(100, 5)

        assert panel.visible is True

    def test_panel_hide_clears_timer(self, gtk_setup):
        """Test hide() clears pending timer."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel._hide_timer_id = 12345  # Fake timer ID

        with patch("src.quick_actions.GLib.source_remove") as mock_remove:
            panel.hide()

            mock_remove.assert_called_once_with(12345)
            assert panel._hide_timer_id is None
            assert panel.visible is False

    def test_panel_show_at_cancels_timer(self, gtk_setup):
        """Test show_at() cancels pending hide timer."""
        from src.quick_actions import QuickActionsPanel, QuickAction

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.set_actions([QuickAction(icon="X", tooltip="Test", callback=lambda: None)])
        panel._hide_timer_id = 12345

        with patch("src.quick_actions.GLib.source_remove") as mock_remove:
            panel.show_at(100, 100)

            mock_remove.assert_called_once_with(12345)
            assert panel._hide_timer_id is None

    def test_panel_on_leave_starts_hide_timer(self, gtk_setup):
        """Test _on_leave starts hide timer."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])

        mock_event = MagicMock()
        mock_event.detail = None  # Not INFERIOR

        with patch("src.quick_actions.GLib.timeout_add") as mock_timeout:
            mock_timeout.return_value = 999
            panel._on_leave(panel.popup, mock_event)

            mock_timeout.assert_called_once()
            assert panel._hide_timer_id == 999

    def test_panel_on_leave_ignores_inferior(self, gtk_setup):
        """Test _on_leave ignores INFERIOR events."""
        from src.quick_actions import QuickActionsPanel
        import gi

        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk

        panel = QuickActionsPanel(gtk_setup["window"])

        mock_event = MagicMock()
        mock_event.detail = Gdk.NotifyType.INFERIOR

        with patch("src.quick_actions.GLib.timeout_add") as mock_timeout:
            result = panel._on_leave(panel.popup, mock_event)

            assert result is False
            mock_timeout.assert_not_called()

    def test_panel_on_enter_cancels_timer(self, gtk_setup):
        """Test _on_enter cancels hide timer."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel._hide_timer_id = 12345

        mock_event = MagicMock()

        with patch("src.quick_actions.GLib.source_remove") as mock_remove:
            result = panel._on_enter(panel.popup, mock_event)

            mock_remove.assert_called_once_with(12345)
            assert panel._hide_timer_id is None
            assert result is False

    def test_panel_delayed_hide(self, gtk_setup):
        """Test _delayed_hide hides panel."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.visible = True

        result = panel._delayed_hide()

        assert panel.visible is False
        assert result is False  # Don't repeat timer

    def test_panel_update_position_not_visible(self, gtk_setup):
        """Test update_position does nothing when not visible."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.visible = False

        # Should return early without error
        panel.update_position((0, 0, 100, 100), MagicMock())

    def test_panel_update_position_no_window(self, gtk_setup):
        """Test update_position handles missing window."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.visible = True

        mock_drawing_area = MagicMock()
        mock_drawing_area.get_window.return_value = None

        # Should return early without error
        panel.update_position((0, 0, 100, 100), mock_drawing_area)

    def test_panel_update_position_origin_fails(self, gtk_setup):
        """Test update_position handles failed origin lookup."""
        from src.quick_actions import QuickActionsPanel

        panel = QuickActionsPanel(gtk_setup["window"])
        panel.visible = True

        mock_window = MagicMock()
        mock_window.get_origin.return_value = (False, 0, 0)

        mock_drawing_area = MagicMock()
        mock_drawing_area.get_window.return_value = mock_window

        # Should return early without error
        panel.update_position((0, 0, 100, 100), mock_drawing_area)


class TestCreateSelectionActionsEdgeCases:
    """Test edge cases in create_selection_actions."""

    def test_is_unlocked_no_editor_state(self):
        """Test is_unlocked returns False when no editor_state."""
        from src.quick_actions import create_selection_actions

        mock_editor = MagicMock()
        mock_editor.editor_state = None

        actions = create_selection_actions(mock_editor)

        # Find an action that uses is_unlocked
        lock_action = next((a for a in actions if "Lock" in a.tooltip), None)
        if lock_action and lock_action.enabled_check:
            assert lock_action.enabled_check() is False
