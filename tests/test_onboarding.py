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
