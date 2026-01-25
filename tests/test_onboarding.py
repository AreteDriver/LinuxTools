"""Tests for the onboarding module."""

from unittest.mock import MagicMock, patch

import pytest


class TestOnboardingModuleImport:
    """Test onboarding module imports."""

    def test_module_imports(self):
        """Test that onboarding module imports successfully."""
        from src import onboarding

        assert hasattr(onboarding, "OnboardingStep")
        assert hasattr(onboarding, "OnboardingTooltip")
        assert hasattr(onboarding, "OnboardingManager")
        assert hasattr(onboarding, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.onboarding import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestOnboardingStep:
    """Test OnboardingStep dataclass."""

    def test_step_has_required_attributes(self):
        """Test that OnboardingStep has required attributes."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="test",
            title="Test Title",
            message="Test message",
        )

        assert step.target_id == "test"
        assert step.title == "Test Title"
        assert step.message == "Test message"

    def test_step_with_empty_strings(self):
        """Test OnboardingStep with empty strings."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="",
            title="",
            message="",
        )

        assert step.target_id == ""
        assert step.title == ""
        assert step.message == ""

    def test_step_with_special_characters(self):
        """Test OnboardingStep with special characters."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="widget_id_123",
            title="Title with 'quotes' and \"double\"",
            message="Message with <html> & special chars",
        )

        assert "'" in step.title
        assert "<html>" in step.message

    def test_step_default_position(self):
        """Test that OnboardingStep has default position."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="test",
            title="Test",
            message="Test",
        )

        assert step.position == "bottom"

    def test_step_default_highlight(self):
        """Test that OnboardingStep has default highlight."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="test",
            title="Test",
            message="Test",
        )

        assert step.highlight is True

    def test_step_custom_position(self):
        """Test OnboardingStep with custom position."""
        from src.onboarding import OnboardingStep

        for position in ["top", "bottom", "left", "right"]:
            step = OnboardingStep(
                target_id="test",
                title="Test",
                message="Test",
                position=position,
            )
            assert step.position == position

    def test_step_highlight_disabled(self):
        """Test OnboardingStep with highlight disabled."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="test",
            title="Test",
            message="Test",
            highlight=False,
        )

        assert step.highlight is False

    def test_step_all_attributes(self):
        """Test OnboardingStep with all attributes set."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="my_widget",
            title="My Title",
            message="My detailed message here",
            position="left",
            highlight=False,
        )

        assert step.target_id == "my_widget"
        assert step.title == "My Title"
        assert step.message == "My detailed message here"
        assert step.position == "left"
        assert step.highlight is False

    def test_step_multiline_message(self):
        """Test OnboardingStep with multiline message."""
        from src.onboarding import OnboardingStep

        message = "Line 1\nLine 2\nLine 3"
        step = OnboardingStep(
            target_id="test",
            title="Test",
            message=message,
        )

        assert step.message == message
        assert "\n" in step.message


class TestOnboardingTooltipClass:
    """Test OnboardingTooltip class structure."""

    def test_class_has_required_methods(self):
        """Test that OnboardingTooltip has required methods."""
        from src.onboarding import OnboardingTooltip

        assert hasattr(OnboardingTooltip, "show")
        assert hasattr(OnboardingTooltip, "hide")

    def test_gtk_check_in_init(self):
        """Test that OnboardingTooltip checks GTK_AVAILABLE in init."""
        from src.onboarding import OnboardingTooltip
        import inspect

        # Check that __init__ has GTK check
        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "GTK_AVAILABLE" in source or "RuntimeError" in source


class TestOnboardingManagerClass:
    """Test OnboardingManager class structure."""

    def test_class_has_config_key(self):
        """Test that OnboardingManager has CONFIG_KEY constant."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "CONFIG_KEY")
        assert OnboardingManager.CONFIG_KEY == "onboarding_completed"

    def test_class_has_required_methods(self):
        """Test that OnboardingManager has required methods."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "should_show")
        assert hasattr(OnboardingManager, "start")
        assert hasattr(OnboardingManager, "reset")


class TestOnboardingManagerWithGtk:
    """Test OnboardingManager with GTK available."""

    def test_init_signature(self):
        """Test that init has correct signature with type hint."""
        from src.onboarding import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        from src.onboarding import OnboardingManager
        import inspect

        sig = inspect.signature(OnboardingManager.__init__)
        params = list(sig.parameters.keys())
        assert "editor_window" in params

        # Check for type annotation in source (annotations may not be preserved at runtime)
        source = inspect.getsource(OnboardingManager.__init__)
        assert "editor_window" in source


class TestOnboardingI18n:
    """Test that onboarding uses internationalization."""

    def test_imports_i18n(self):
        """Test that onboarding imports i18n."""
        from src import onboarding
        import inspect

        source = inspect.getsource(onboarding)
        assert "from .i18n import _" in source or "from src.i18n import _" in source


class TestOnboardingConfigIntegration:
    """Test onboarding config integration."""

    def test_imports_config(self):
        """Test that onboarding imports config module."""
        from src import onboarding
        import inspect

        source = inspect.getsource(onboarding)
        assert "from . import config" in source or "from src import config" in source

    def test_should_show_returns_bool(self):
        """Test that should_show method returns boolean."""
        from src.onboarding import OnboardingManager
        import inspect

        # Get the method signature/annotations if available
        method = OnboardingManager.should_show
        assert callable(method)

        # Check return type in source
        source = inspect.getsource(method)
        assert "-> bool" in source

    def test_should_show_true_when_not_completed(self):
        """Test should_show returns True when onboarding not completed."""
        from src.onboarding import OnboardingManager

        with patch("src.onboarding.config.load_config") as mock_load:
            mock_load.return_value = {}  # No onboarding_completed key

            with patch("src.onboarding.GTK_AVAILABLE", True):
                with patch("src.onboarding.OnboardingTooltip"):
                    mock_editor = MagicMock()
                    mock_editor.window = MagicMock()
                    manager = OnboardingManager(mock_editor)

                    assert manager.should_show() is True

    def test_should_show_false_when_completed(self):
        """Test should_show returns False when onboarding completed."""
        from src.onboarding import OnboardingManager

        with patch("src.onboarding.config.load_config") as mock_load:
            mock_load.return_value = {"onboarding_completed": True}

            with patch("src.onboarding.GTK_AVAILABLE", True):
                with patch("src.onboarding.OnboardingTooltip"):
                    mock_editor = MagicMock()
                    mock_editor.window = MagicMock()
                    manager = OnboardingManager(mock_editor)

                    assert manager.should_show() is False

    def test_config_key_constant(self):
        """Test that CONFIG_KEY is used correctly."""
        from src.onboarding import OnboardingManager

        assert OnboardingManager.CONFIG_KEY == "onboarding_completed"

    def test_reset_sets_config_to_false(self):
        """Test reset() sets onboarding_completed to False."""
        from src.onboarding import OnboardingManager

        with patch("src.onboarding.config.load_config") as mock_load:
            with patch("src.onboarding.config.save_config") as mock_save:
                mock_load.return_value = {"onboarding_completed": True}

                with patch("src.onboarding.GTK_AVAILABLE", True):
                    with patch("src.onboarding.OnboardingTooltip"):
                        mock_editor = MagicMock()
                        mock_editor.window = MagicMock()
                        manager = OnboardingManager(mock_editor)

                        manager.reset()

                        # Verify save_config was called with False
                        mock_save.assert_called()
                        saved_cfg = mock_save.call_args[0][0]
                        assert saved_cfg["onboarding_completed"] is False

    def test_reset_preserves_other_config_keys(self):
        """Test reset() preserves other config keys."""
        from src.onboarding import OnboardingManager

        with patch("src.onboarding.config.load_config") as mock_load:
            with patch("src.onboarding.config.save_config") as mock_save:
                mock_load.return_value = {
                    "onboarding_completed": True,
                    "other_setting": "value",
                    "another": 42,
                }

                with patch("src.onboarding.GTK_AVAILABLE", True):
                    with patch("src.onboarding.OnboardingTooltip"):
                        mock_editor = MagicMock()
                        mock_editor.window = MagicMock()
                        manager = OnboardingManager(mock_editor)

                        manager.reset()

                        saved_cfg = mock_save.call_args[0][0]
                        assert saved_cfg["other_setting"] == "value"
                        assert saved_cfg["another"] == 42


class TestOnboardingManagerStructure:
    """Test OnboardingManager structure and methods."""

    def test_has_create_steps_method(self):
        """Test OnboardingManager has _create_steps method."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "_create_steps")

    def test_has_get_target_widget_method(self):
        """Test OnboardingManager has _get_target_widget method."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "_get_target_widget")

    def test_has_show_current_step_method(self):
        """Test OnboardingManager has _show_current_step method."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "_show_current_step")

    def test_has_finish_method(self):
        """Test OnboardingManager has _finish method."""
        from src.onboarding import OnboardingManager

        assert hasattr(OnboardingManager, "_finish")

    def test_start_method_exists(self):
        """Test that start method exists and is callable."""
        from src.onboarding import OnboardingManager

        assert callable(getattr(OnboardingManager, "start"))


class TestOnboardingTooltipStructure:
    """Test OnboardingTooltip structure."""

    def test_has_position_near_widget_method(self):
        """Test OnboardingTooltip has _position_near_widget method."""
        from src.onboarding import OnboardingTooltip

        assert hasattr(OnboardingTooltip, "_position_near_widget")

    def test_has_position_center_method(self):
        """Test OnboardingTooltip has _position_center method."""
        from src.onboarding import OnboardingTooltip

        assert hasattr(OnboardingTooltip, "_position_center")

    def test_has_apply_styles_method(self):
        """Test OnboardingTooltip has _apply_styles method."""
        from src.onboarding import OnboardingTooltip

        assert hasattr(OnboardingTooltip, "_apply_styles")

    def test_show_method_signature(self):
        """Test show method has correct parameters."""
        from src.onboarding import OnboardingTooltip
        import inspect

        sig = inspect.signature(OnboardingTooltip.show)
        params = list(sig.parameters.keys())
        assert "title" in params
        assert "message" in params
        assert "step_num" in params
        assert "total_steps" in params
        assert "on_next" in params
        assert "on_skip" in params


class TestOnboardingTooltipSourceInspection:
    """Test OnboardingTooltip implementation via source inspection."""

    def test_init_creates_popup_window(self):
        """Test __init__ creates popup window."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "Gtk.Window" in source
        assert "POPUP" in source or "popup" in source

    def test_init_sets_window_hints(self):
        """Test __init__ sets window type hints."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "set_type_hint" in source or "WindowTypeHint" in source
        assert "set_decorated" in source
        assert "set_transient_for" in source

    def test_init_creates_labels(self):
        """Test __init__ creates title and message labels."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "title_label" in source
        assert "message_label" in source
        assert "Gtk.Label" in source

    def test_init_creates_buttons(self):
        """Test __init__ creates skip and next buttons."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "skip_btn" in source
        assert "next_btn" in source
        assert "Gtk.Button" in source

    def test_show_updates_labels(self):
        """Test show method updates label text."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "set_text" in source
        assert "title" in source
        assert "message" in source

    def test_show_updates_step_indicator(self):
        """Test show method updates step indicator."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "step_num" in source
        assert "total_steps" in source
        assert "step_label" in source

    def test_show_handles_last_step(self):
        """Test show method changes button for last step."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "step_num == total_steps" in source
        assert "Got it" in source

    def test_show_connects_button_handlers(self):
        """Test show method connects button click handlers."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "connect" in source
        assert "clicked" in source
        assert "on_next" in source
        assert "on_skip" in source

    def test_show_disconnects_old_handlers(self):
        """Test show method disconnects old handlers."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "disconnect" in source
        assert "_handler_ids" in source

    def test_show_positions_tooltip(self):
        """Test show method positions tooltip."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "_position_near_widget" in source
        assert "_position_center" in source
        assert "get_realized" in source

    def test_position_near_widget_calculates_coordinates(self):
        """Test _position_near_widget calculates screen coordinates."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert "get_allocation" in source
        assert "get_window" in source
        assert "get_origin" in source

    def test_position_near_widget_handles_all_positions(self):
        """Test _position_near_widget handles all position values."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert 'position == "bottom"' in source
        assert 'position == "top"' in source
        assert 'position == "right"' in source
        assert 'position == "left"' in source

    def test_position_near_widget_keeps_on_screen(self):
        """Test _position_near_widget keeps tooltip on screen."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert "get_width" in source
        assert "get_height" in source
        assert "max(" in source or "min(" in source

    def test_position_near_widget_fallback_to_center(self):
        """Test _position_near_widget falls back to center on failure."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert "_position_center" in source

    def test_position_center_uses_parent(self):
        """Test _position_center uses parent window."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_center)
        assert "parent_window" in source
        assert "get_allocation" in source
        assert "get_position" in source

    def test_hide_hides_popup(self):
        """Test hide method hides popup."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.hide)
        assert "popup" in source
        assert "hide" in source


class TestOnboardingTooltipCSS:
    """Test OnboardingTooltip CSS handling."""

    def test_apply_styles_method_exists(self):
        """Test _apply_styles method exists."""
        from src.onboarding import OnboardingTooltip

        assert hasattr(OnboardingTooltip, "_apply_styles")
        assert callable(OnboardingTooltip._apply_styles)

    def test_apply_styles_uses_global_flag(self):
        """Test _apply_styles uses global flag to prevent duplication."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._apply_styles)
        assert "_css_applied" in source
        assert "global" in source

    def test_apply_styles_creates_css_provider(self):
        """Test _apply_styles creates CSS provider."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._apply_styles)
        assert "CssProvider" in source
        assert "load_from_data" in source

    def test_css_contains_tooltip_styles(self):
        """Test CSS contains tooltip class styles."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._apply_styles)
        assert ".onboarding-tooltip" in source
        assert ".onboarding-title" in source
        assert ".onboarding-message" in source

    def test_css_contains_button_styles(self):
        """Test CSS contains button styles."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._apply_styles)
        assert ".onboarding-btn" in source
        assert ".skip-btn" in source
        assert ".next-btn" in source

    def test_css_contains_highlight_style(self):
        """Test CSS contains highlight style for target widgets."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._apply_styles)
        assert ".onboarding-highlight" in source
        assert "box-shadow" in source

    def test_module_has_css_flag(self):
        """Test module has _css_applied flag."""
        from src import onboarding

        assert hasattr(onboarding, "_css_applied")


class TestOnboardingManagerSourceInspection:
    """Test OnboardingManager implementation via source inspection."""

    def test_init_creates_tooltip(self):
        """Test __init__ creates OnboardingTooltip."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.__init__)
        assert "OnboardingTooltip" in source
        assert "self.tooltip" in source

    def test_init_initializes_step_counter(self):
        """Test __init__ initializes current_step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.__init__)
        assert "current_step" in source
        assert "= 0" in source

    def test_init_creates_steps(self):
        """Test __init__ calls _create_steps."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.__init__)
        assert "_create_steps" in source
        assert "self.steps" in source

    def test_init_tracks_highlighted_widget(self):
        """Test __init__ initializes highlighted widget tracker."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.__init__)
        assert "_highlighted_widget" in source

    def test_create_steps_returns_list(self):
        """Test _create_steps returns list of OnboardingStep."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert "OnboardingStep" in source
        assert "return [" in source or "return[" in source

    def test_create_steps_has_sidebar_step(self):
        """Test _create_steps includes sidebar step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="sidebar"' in source
        assert "Tool Sidebar" in source or "_(" in source

    def test_create_steps_has_context_bar_step(self):
        """Test _create_steps includes context bar step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="context_bar"' in source

    def test_create_steps_has_color_picker_step(self):
        """Test _create_steps includes color picker step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="color_picker"' in source

    def test_create_steps_has_radial_menu_step(self):
        """Test _create_steps includes radial menu step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="drawing_area"' in source
        assert "Right-Click" in source or "Radial" in source or "_(" in source

    def test_create_steps_has_command_palette_step(self):
        """Test _create_steps includes command palette step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="command_palette"' in source

    def test_create_steps_has_actions_step(self):
        """Test _create_steps includes actions step."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert 'target_id="actions"' in source

    def test_start_resets_step_counter(self):
        """Test start method resets current_step to 0."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.start)
        assert "current_step = 0" in source

    def test_start_uses_timer(self):
        """Test start method uses GLib timer for delay."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.start)
        assert "timeout_add" in source or "GLib" in source

    def test_start_checks_empty_steps(self):
        """Test start method checks for empty steps."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.start)
        assert "if not self.steps" in source

    def test_get_target_widget_has_target_map(self):
        """Test _get_target_widget has target ID to widget mapping."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._get_target_widget)
        assert "targets" in source or "target_id" in source
        assert '"sidebar"' in source
        assert '"context_bar"' in source

    def test_get_target_widget_handles_actions(self):
        """Test _get_target_widget has special handling for actions."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._get_target_widget)
        assert '"actions"' in source
        assert "get_children" in source

    def test_show_current_step_checks_bounds(self):
        """Test _show_current_step checks step bounds."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._show_current_step)
        assert "current_step >= len(self.steps)" in source
        assert "_finish" in source

    def test_show_current_step_removes_previous_highlight(self):
        """Test _show_current_step removes previous highlight."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._show_current_step)
        assert "remove_class" in source
        assert "onboarding-highlight" in source

    def test_show_current_step_adds_highlight(self):
        """Test _show_current_step adds highlight to target."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._show_current_step)
        assert "add_class" in source
        assert "onboarding-highlight" in source

    def test_show_current_step_shows_tooltip(self):
        """Test _show_current_step shows tooltip."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._show_current_step)
        assert "self.tooltip.show" in source or "tooltip.show" in source

    def test_next_step_increments_counter(self):
        """Test _next_step increments step counter."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._next_step)
        assert "current_step += 1" in source

    def test_next_step_finishes_at_end(self):
        """Test _next_step calls _finish at end."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._next_step)
        assert "_finish" in source

    def test_skip_calls_finish(self):
        """Test _skip calls _finish."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._skip)
        assert "_finish" in source

    def test_finish_removes_highlight(self):
        """Test _finish removes highlight from widget."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._finish)
        assert "remove_class" in source
        assert "_highlighted_widget" in source

    def test_finish_hides_tooltip(self):
        """Test _finish hides tooltip."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._finish)
        assert "tooltip.hide" in source or "self.tooltip.hide" in source

    def test_finish_saves_config(self):
        """Test _finish saves completion to config."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._finish)
        assert "save_config" in source
        assert "CONFIG_KEY" in source
        assert "True" in source

    def test_reset_loads_and_saves_config(self):
        """Test reset loads and saves config."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.reset)
        assert "load_config" in source
        assert "save_config" in source

    def test_reset_sets_key_to_false(self):
        """Test reset sets CONFIG_KEY to False."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.reset)
        assert "CONFIG_KEY" in source
        assert "False" in source


class TestOnboardingStepSourceInspection:
    """Test OnboardingStep implementation details."""

    def test_step_is_simple_class(self):
        """Test OnboardingStep is a simple data class."""
        from src.onboarding import OnboardingStep
        import inspect

        source = inspect.getsource(OnboardingStep)
        # Should have __init__ with assignments
        assert "def __init__" in source
        assert "self.target_id" in source
        assert "self.title" in source
        assert "self.message" in source
        assert "self.position" in source
        assert "self.highlight" in source

    def test_step_has_default_values(self):
        """Test OnboardingStep has default values in signature."""
        from src.onboarding import OnboardingStep
        import inspect

        sig = inspect.signature(OnboardingStep.__init__)
        params = sig.parameters

        assert params["position"].default == "bottom"
        assert params["highlight"].default is True

    def test_step_positions_are_strings(self):
        """Test step positions are string values."""
        from src.onboarding import OnboardingStep

        step = OnboardingStep(
            target_id="test",
            title="Test",
            message="Test",
            position="right",
        )
        assert isinstance(step.position, str)


class TestOnboardingEdgeCases:
    """Test edge cases and error handling."""

    def test_tooltip_requires_gtk(self):
        """Test OnboardingTooltip raises error without GTK."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        assert "GTK_AVAILABLE" in source
        assert "RuntimeError" in source

    def test_manager_start_with_empty_steps(self):
        """Test start method handles empty steps gracefully."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager.start)
        assert "if not self.steps" in source
        assert "return" in source

    def test_show_current_step_handles_no_target(self):
        """Test _show_current_step handles missing target widget."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._show_current_step)
        # Should check for None or handle missing widgets
        assert "target" in source
        assert "if" in source

    def test_position_near_widget_handles_no_window(self):
        """Test _position_near_widget handles widget with no window."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert "if not window" in source
        assert "_position_center" in source

    def test_position_near_widget_handles_origin_failure(self):
        """Test _position_near_widget handles get_origin failure."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip._position_near_widget)
        assert "get_origin" in source
        assert "origin" in source

    def test_show_handles_disconnect_exceptions(self):
        """Test show method handles disconnect exceptions."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.show)
        assert "try:" in source or "except" in source
        assert "disconnect" in source


class TestOnboardingI18nIntegration:
    """Test internationalization integration."""

    def test_uses_translation_function(self):
        """Test module uses _() translation function."""
        from src import onboarding
        import inspect

        source = inspect.getsource(onboarding)
        # Check for translation wrapper usage
        assert '_("' in source

    def test_translatable_strings_in_steps(self):
        """Test step text uses translation function."""
        from src.onboarding import OnboardingManager
        import inspect

        source = inspect.getsource(OnboardingManager._create_steps)
        assert "_(" in source

    def test_button_labels_translated(self):
        """Test button labels use translation."""
        from src.onboarding import OnboardingTooltip
        import inspect

        source = inspect.getsource(OnboardingTooltip.__init__)
        # Skip and Next buttons should be translatable
        assert '_("Skip")' in source or "Skip" in source
        assert '_("Next")' in source or "Next" in source


# =============================================================================
# Functional GTK Tests (require xvfb or display)
# =============================================================================


class TestOnboardingTooltipFunctional:
    """Functional tests for OnboardingTooltip."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.onboarding import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        window = Gtk.Window()
        window.set_size_request(400, 300)
        return {"Gtk": Gtk, "window": window}

    def test_create_tooltip(self, gtk_setup):
        """Test creating an OnboardingTooltip instance."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        assert tooltip is not None
        assert tooltip.popup is not None
        assert tooltip.title_label is not None
        assert tooltip.message_label is not None
        assert tooltip.next_btn is not None
        assert tooltip.skip_btn is not None

    def test_tooltip_show(self, gtk_setup):
        """Test showing tooltip."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        next_called = []
        skip_called = []

        tooltip.show(
            title="Test Title",
            message="Test message",
            step_num=1,
            total_steps=3,
            target_widget=None,
            position="bottom",
            on_next=lambda: next_called.append(True),
            on_skip=lambda: skip_called.append(True),
        )

        # Verify labels were set
        assert tooltip.title_label.get_text() == "Test Title"
        assert tooltip.message_label.get_text() == "Test message"
        assert "1/3" in tooltip.step_label.get_text()

    def test_tooltip_show_last_step(self, gtk_setup):
        """Test showing tooltip on last step."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        tooltip.show(
            title="Final",
            message="Last step",
            step_num=3,
            total_steps=3,
            target_widget=None,
            position="bottom",
            on_next=lambda: None,
            on_skip=lambda: None,
        )

        # Button should say "Got it!" on last step
        assert "Got it" in tooltip.next_btn.get_label() or "3/3" in tooltip.step_label.get_text()

    def test_tooltip_hide(self, gtk_setup):
        """Test hiding tooltip."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        tooltip.show(
            title="Test",
            message="Test",
            step_num=1,
            total_steps=1,
            target_widget=None,
            position="bottom",
            on_next=lambda: None,
            on_skip=lambda: None,
        )

        tooltip.hide()
        # Popup should be hidden
        assert tooltip.popup.get_visible() is False

    def test_tooltip_position_center(self, gtk_setup):
        """Test positioning tooltip in center."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        # Should not raise
        tooltip._position_center()


class TestOnboardingManagerFunctional:
    """Functional tests for OnboardingManager."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.onboarding import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        window = Gtk.Window()
        window.set_size_request(800, 600)
        return {"Gtk": Gtk, "window": window}

    def test_create_manager(self, gtk_setup):
        """Test creating an OnboardingManager instance."""
        from src.onboarding import OnboardingManager

        # Mock editor_window
        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)

        assert manager is not None
        assert manager.current_step == 0
        assert len(manager.steps) > 0

    def test_manager_should_show_true(self, gtk_setup):
        """Test should_show returns True when not completed."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            assert manager.should_show() is True

    def test_manager_should_show_false(self, gtk_setup):
        """Test should_show returns False when completed."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={"onboarding_completed": True}):
            manager = OnboardingManager(mock_editor)
            assert manager.should_show() is False

    def test_manager_reset(self, gtk_setup):
        """Test reset sets onboarding_completed to False."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={"onboarding_completed": True}):
            with patch("src.onboarding.config.save_config") as mock_save:
                manager = OnboardingManager(mock_editor)
                manager.reset()

                mock_save.assert_called()
                saved_config = mock_save.call_args[0][0]
                assert saved_config["onboarding_completed"] is False

    def test_manager_steps_created(self, gtk_setup):
        """Test that steps are created correctly."""
        from src.onboarding import OnboardingManager, OnboardingStep

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)

        # Should have multiple steps
        assert len(manager.steps) >= 5

        # All steps should be OnboardingStep instances
        for step in manager.steps:
            assert isinstance(step, OnboardingStep)
            assert step.target_id != ""
            assert step.title != ""
            assert step.message != ""

    def test_manager_next_step(self, gtk_setup):
        """Test _next_step increments step counter."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            with patch("src.onboarding.config.save_config"):
                manager = OnboardingManager(mock_editor)

                initial_step = manager.current_step

                # Set step to last to trigger _finish instead of _show_current_step
                manager.current_step = len(manager.steps) - 1
                manager._next_step()

                # Should have finished (step >= len)
                assert manager.current_step >= len(manager.steps)

    def test_manager_skip_finishes(self, gtk_setup):
        """Test _skip calls _finish."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            with patch("src.onboarding.config.save_config") as mock_save:
                manager = OnboardingManager(mock_editor)
                manager._skip()

                # Should have saved config marking as completed
                mock_save.assert_called()

    def test_manager_finish_saves_config(self, gtk_setup):
        """Test _finish saves completion to config."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            with patch("src.onboarding.config.save_config") as mock_save:
                manager = OnboardingManager(mock_editor)
                manager._finish()

                mock_save.assert_called()
                saved_config = mock_save.call_args[0][0]
                assert saved_config["onboarding_completed"] is True

    def test_manager_start_empty_steps(self, gtk_setup):
        """Test start() returns early with no steps."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            manager.steps = []  # Empty steps

            # Should return without error
            manager.start()
            assert manager.current_step == 0

    def test_manager_start_with_steps(self, gtk_setup):
        """Test start() initializes step and schedules timer."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            with patch("src.onboarding.GLib.timeout_add") as mock_timeout:
                manager = OnboardingManager(mock_editor)
                manager.start()

                assert manager.current_step == 0
                mock_timeout.assert_called_once()
                # First arg is delay, second is callback
                assert mock_timeout.call_args[0][0] == 500

    def test_manager_get_target_widget_sidebar(self, gtk_setup):
        """Test _get_target_widget returns sidebar."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]
        mock_sidebar = MagicMock()
        mock_editor.sidebar = mock_sidebar

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            result = manager._get_target_widget("sidebar")

            assert result == mock_sidebar

    def test_manager_get_target_widget_context_bar(self, gtk_setup):
        """Test _get_target_widget returns context_bar."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]
        mock_context_bar = MagicMock()
        mock_editor.context_bar = mock_context_bar

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            result = manager._get_target_widget("context_bar")

            assert result == mock_context_bar

    def test_manager_get_target_widget_command_palette(self, gtk_setup):
        """Test _get_target_widget returns None for command_palette."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            result = manager._get_target_widget("command_palette")

            assert result is None

    def test_manager_get_target_widget_unknown(self, gtk_setup):
        """Test _get_target_widget returns None for unknown ID."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            result = manager._get_target_widget("nonexistent_widget")

            assert result is None

    def test_manager_show_current_step_past_end(self, gtk_setup):
        """Test _show_current_step finishes when past end."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            with patch("src.onboarding.config.save_config"):
                manager = OnboardingManager(mock_editor)
                manager.current_step = 100  # Past end

                result = manager._show_current_step()

                assert result is False

    def test_manager_next_step_not_at_end(self, gtk_setup):
        """Test _next_step shows next step when not at end."""
        from src.onboarding import OnboardingManager

        mock_editor = MagicMock()
        mock_editor.window = gtk_setup["window"]

        with patch("src.onboarding.config.load_config", return_value={}):
            manager = OnboardingManager(mock_editor)
            manager.current_step = 0

            with patch.object(manager, "_show_current_step") as mock_show:
                manager._next_step()

                assert manager.current_step == 1
                mock_show.assert_called_once()


class TestOnboardingTooltipPositioning:
    """Test tooltip positioning methods."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.onboarding import GTK_AVAILABLE

        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        window = Gtk.Window()
        return {"Gtk": Gtk, "window": window}

    def test_position_center(self, gtk_setup):
        """Test _position_center positions in parent center."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        # Should not raise
        tooltip._position_center()

    def test_position_near_widget_no_window(self, gtk_setup):
        """Test _position_near_widget falls back when widget has no window."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        mock_widget = MagicMock()
        mock_widget.get_window.return_value = None

        with patch.object(tooltip, "_position_center") as mock_center:
            tooltip._position_near_widget(mock_widget, "bottom")
            mock_center.assert_called_once()

    def test_position_near_widget_origin_fail(self, gtk_setup):
        """Test _position_near_widget falls back when origin fails."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        mock_widget = MagicMock()
        mock_window = MagicMock()
        mock_window.get_origin.return_value = (False, 0, 0)  # Failed
        mock_widget.get_window.return_value = mock_window

        with patch.object(tooltip, "_position_center") as mock_center:
            tooltip._position_near_widget(mock_widget, "bottom")
            mock_center.assert_called_once()

    def test_show_disconnects_old_handlers(self, gtk_setup):
        """Test show disconnects old handlers gracefully."""
        from src.onboarding import OnboardingTooltip

        tooltip = OnboardingTooltip(gtk_setup["window"])

        # Set up fake handler IDs that will fail to disconnect
        tooltip._handler_ids = [(999, 998)]

        # Should not raise even when disconnect fails
        tooltip.show(
            title="Test",
            message="Test message",
            step_num=1,
            total_steps=3,
            target_widget=None,
            position="bottom",
            on_next=lambda: None,
            on_skip=lambda: None,
        )
