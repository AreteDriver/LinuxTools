"""Tests for the scroll capture module."""

from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestScrollCaptureModuleImport:
    """Test scroll_capture module imports."""

    def test_module_imports(self):
        """Test that scroll_capture module imports successfully."""
        from src import scroll_capture

        assert hasattr(scroll_capture, "ScrollState")
        assert hasattr(scroll_capture, "ScrollCaptureResult")
        assert hasattr(scroll_capture, "ScrollCaptureManager")
        assert hasattr(scroll_capture, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.scroll_capture import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestEnsureOpencv:
    """Test _ensure_opencv function."""

    def test_function_exists(self):
        """Test _ensure_opencv function exists."""
        from src.scroll_capture import _ensure_opencv

        assert callable(_ensure_opencv)

    def test_returns_bool(self):
        """Test _ensure_opencv returns boolean."""
        from src.scroll_capture import _ensure_opencv

        result = _ensure_opencv()
        assert isinstance(result, bool)


class TestScrollState:
    """Test ScrollState enum."""

    def test_is_enum(self):
        """Test ScrollState is an Enum."""
        from src.scroll_capture import ScrollState

        assert issubclass(ScrollState, Enum)

    def test_has_idle_state(self):
        """Test ScrollState has IDLE."""
        from src.scroll_capture import ScrollState

        assert ScrollState.IDLE.value == "idle"

    def test_has_capturing_state(self):
        """Test ScrollState has CAPTURING."""
        from src.scroll_capture import ScrollState

        assert ScrollState.CAPTURING.value == "capturing"

    def test_has_stitching_state(self):
        """Test ScrollState has STITCHING."""
        from src.scroll_capture import ScrollState

        assert ScrollState.STITCHING.value == "stitching"

    def test_has_completed_state(self):
        """Test ScrollState has COMPLETED."""
        from src.scroll_capture import ScrollState

        assert ScrollState.COMPLETED.value == "completed"

    def test_has_error_state(self):
        """Test ScrollState has ERROR."""
        from src.scroll_capture import ScrollState

        assert ScrollState.ERROR.value == "error"

    def test_all_states(self):
        """Test all expected states exist."""
        from src.scroll_capture import ScrollState

        states = [s.value for s in ScrollState]
        assert "idle" in states
        assert "capturing" in states
        assert "stitching" in states
        assert "completed" in states
        assert "error" in states


class TestScrollCaptureResult:
    """Test ScrollCaptureResult dataclass."""

    def test_success_result(self):
        """Test successful ScrollCaptureResult."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(
            success=True,
            pixbuf=MagicMock(),
            frame_count=5,
            total_height=2000,
        )

        assert result.success is True
        assert result.pixbuf is not None
        assert result.frame_count == 5
        assert result.total_height == 2000
        assert result.error is None

    def test_error_result(self):
        """Test error ScrollCaptureResult."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(success=False, error="Capture failed")

        assert result.success is False
        assert result.pixbuf is None
        assert result.error == "Capture failed"

    def test_default_values(self):
        """Test ScrollCaptureResult default values."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(success=True)

        assert result.pixbuf is None
        assert result.filepath is None
        assert result.error is None
        assert result.frame_count == 0
        assert result.total_height == 0

    def test_result_with_filepath(self):
        """Test ScrollCaptureResult with filepath."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(
            success=True,
            filepath=Path("/tmp/scroll.png"),
        )

        assert result.filepath == Path("/tmp/scroll.png")


class TestScrollCaptureManagerClass:
    """Test ScrollCaptureManager class structure."""

    def test_class_has_is_available_method(self):
        """Test ScrollCaptureManager has is_available method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "is_available")

    def test_class_has_start_capture_method(self):
        """Test ScrollCaptureManager has start_capture method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "start_capture")

    def test_class_has_stop_capture_method(self):
        """Test ScrollCaptureManager has stop_capture method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "stop_capture")

    def test_class_has_finish_capture_method(self):
        """Test ScrollCaptureManager has finish_capture method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "finish_capture")

    def test_class_has_reset_method(self):
        """Test ScrollCaptureManager has reset method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "reset")

    def test_class_has_check_methods(self):
        """Test ScrollCaptureManager has tool check methods."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_check_xdotool")
        assert hasattr(ScrollCaptureManager, "_check_ydotool")
        assert hasattr(ScrollCaptureManager, "_check_wtype")


class TestScrollCaptureManagerInit:
    """Test ScrollCaptureManager initialization."""

    def test_init_sets_idle_state(self):
        """Test ScrollCaptureManager starts in IDLE state."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                assert manager.state == ScrollState.IDLE

    def test_init_sets_empty_frames(self):
        """Test ScrollCaptureManager starts with empty frames."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                assert manager.frames == []
                assert manager.overlaps == []

    def test_init_sets_default_region(self):
        """Test ScrollCaptureManager has default region."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                assert manager.region == (0, 0, 0, 0)

    def test_init_stop_not_requested(self):
        """Test ScrollCaptureManager starts with stop_requested False."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                assert manager.stop_requested is False


class TestScrollCaptureManagerIsAvailable:
    """Test ScrollCaptureManager.is_available method."""

    def test_is_available_returns_tuple(self):
        """Test is_available returns (bool, Optional[str])."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                result = manager.is_available()

                assert isinstance(result, tuple)
                assert len(result) == 2
                assert isinstance(result[0], bool)

    def test_is_available_checks_gtk(self):
        """Test is_available checks GTK availability."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.GTK_AVAILABLE", False):
            with patch("src.scroll_capture.detect_display_server"):
                with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                    manager = ScrollCaptureManager()
                    available, error = manager.is_available()

                    assert available is False
                    assert "GTK" in error


class TestScrollCaptureManagerToolChecks:
    """Test ScrollCaptureManager tool availability checks."""

    def test_check_xdotool_uses_config(self):
        """Test _check_xdotool uses config.check_tool_available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available") as mock_check:
                mock_check.return_value = True
                manager = ScrollCaptureManager()

                assert manager.xdotool_available is True

    def test_check_ydotool_uses_config(self):
        """Test _check_ydotool uses config.check_tool_available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available") as mock_check:
                mock_check.return_value = True
                manager = ScrollCaptureManager()

                assert manager.ydotool_available is True
