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

    def test_check_wtype_available(self):
        """Test _check_wtype returns True when wtype is installed."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    manager = ScrollCaptureManager()

                    assert manager.wtype_available is True

    def test_check_wtype_not_found(self):
        """Test _check_wtype returns False when wtype not found."""
        from src.scroll_capture import ScrollCaptureManager
        import subprocess

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                with patch("subprocess.run", side_effect=FileNotFoundError):
                    manager = ScrollCaptureManager()

                    assert manager.wtype_available is False

    def test_check_wtype_timeout(self):
        """Test _check_wtype returns False on timeout."""
        from src.scroll_capture import ScrollCaptureManager
        import subprocess

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("wtype", 2)):
                    manager = ScrollCaptureManager()

                    assert manager.wtype_available is False


class TestScrollCaptureManagerIsAvailableScenarios:
    """Test is_available for different scenarios."""

    def test_is_available_opencv_not_installed(self):
        """Test is_available returns False when OpenCV not installed."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=False):
                with patch("src.scroll_capture.detect_display_server"):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                        manager = ScrollCaptureManager()
                        available, error = manager.is_available()

                        assert available is False
                        assert "opencv" in error.lower()

    def test_is_available_x11_without_xdotool(self):
        """Test is_available on X11 without xdotool."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                        with patch("subprocess.run", side_effect=FileNotFoundError):
                            manager = ScrollCaptureManager()
                            available, error = manager.is_available()

                            assert available is False
                            assert "xdotool" in error.lower()

    def test_is_available_x11_with_xdotool(self):
        """Test is_available on X11 with xdotool."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                        with patch("subprocess.run"):
                            manager = ScrollCaptureManager()
                            available, error = manager.is_available()

                            assert available is True
                            assert error is None

    def test_is_available_wayland_with_ydotool(self):
        """Test is_available on Wayland with ydotool."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.WAYLAND):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                        with patch("subprocess.run"):
                            manager = ScrollCaptureManager()
                            available, error = manager.is_available()

                            assert available is True

    def test_is_available_wayland_without_tools(self):
        """Test is_available on Wayland without scroll tools."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.WAYLAND):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                        with patch("subprocess.run", side_effect=FileNotFoundError):
                            manager = ScrollCaptureManager()
                            available, error = manager.is_available()

                            assert available is False
                            assert "ydotool" in error.lower() or "wtype" in error.lower()

    def test_is_available_unknown_display_server(self):
        """Test is_available with unknown display server falls back to X11."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=None):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                        with patch("subprocess.run", side_effect=FileNotFoundError):
                            manager = ScrollCaptureManager()
                            available, error = manager.is_available()

                            assert available is False
                            assert "xdotool" in error.lower()


class TestScrollCaptureManagerStartCapture:
    """Test ScrollCaptureManager.start_capture method."""

    def test_start_capture_already_capturing(self):
        """Test start_capture fails when already capturing."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                with patch("subprocess.run"):
                    manager = ScrollCaptureManager()
                    manager.state = ScrollState.CAPTURING

                    success, error = manager.start_capture(0, 0, 100, 100)

                    assert success is False
                    assert "already capturing" in error.lower()

    def test_start_capture_region_too_small(self):
        """Test start_capture fails with region too small."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                        with patch("subprocess.run"):
                            manager = ScrollCaptureManager()

                            # Width too small
                            success, error = manager.start_capture(0, 0, 30, 100)
                            assert success is False
                            assert "too small" in error.lower()

                            # Height too small
                            success, error = manager.start_capture(0, 0, 100, 30)
                            assert success is False
                            assert "too small" in error.lower()

    def test_start_capture_sets_region(self):
        """Test start_capture sets the region correctly."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState
        from src.capture import DisplayServer

        with patch("src.scroll_capture.GTK_AVAILABLE", True):
            with patch("src.scroll_capture._ensure_opencv", return_value=True):
                with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
                    with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                        with patch("subprocess.run"):
                            manager = ScrollCaptureManager()

                            success, error = manager.start_capture(100, 200, 300, 400)

                            assert success is True
                            assert manager.region == (100, 200, 300, 400)
                            assert manager.state == ScrollState.CAPTURING


class TestScrollCaptureManagerStopCapture:
    """Test ScrollCaptureManager.stop_capture method."""

    def test_stop_capture_sets_flag(self):
        """Test stop_capture sets stop_requested flag."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                manager.stop_requested = False

                manager.stop_capture()

                assert manager.stop_requested is True


class TestScrollCaptureManagerFinishCapture:
    """Test ScrollCaptureManager.finish_capture method."""

    def test_finish_capture_no_frames(self):
        """Test finish_capture with no frames returns error."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                manager.frames = []

                result = manager.finish_capture()

                assert result.success is False
                assert "no frames" in result.error.lower()
                assert manager.state == ScrollState.ERROR

    def test_finish_capture_single_frame(self):
        """Test finish_capture with single frame returns it directly."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                mock_pixbuf = MagicMock()
                mock_pixbuf.get_height.return_value = 500
                manager.frames = [mock_pixbuf]

                result = manager.finish_capture()

                assert result.success is True
                assert result.pixbuf == mock_pixbuf
                assert result.frame_count == 1
                assert result.total_height == 500
                assert manager.state == ScrollState.COMPLETED


class TestScrollCaptureManagerReset:
    """Test ScrollCaptureManager.reset method."""

    def test_reset_clears_state(self):
        """Test reset clears all state."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                # Set some state
                manager.state = ScrollState.CAPTURING
                manager.frames = [MagicMock(), MagicMock()]
                manager.overlaps = [50]
                manager.stop_requested = True

                manager.reset()

                assert manager.state == ScrollState.IDLE
                assert manager.frames == []
                assert manager.overlaps == []
                assert manager.stop_requested is False


class TestScrollCaptureManagerEstimateHeight:
    """Test ScrollCaptureManager._estimate_total_height method."""

    def test_estimate_height_no_frames(self):
        """Test _estimate_total_height with no frames."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                manager.frames = []

                height = manager._estimate_total_height()

                assert height == 0

    def test_estimate_height_single_frame(self):
        """Test _estimate_total_height with single frame."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                mock_pixbuf = MagicMock()
                mock_pixbuf.get_height.return_value = 500
                manager.frames = [mock_pixbuf]

                height = manager._estimate_total_height()

                assert height == 500

    def test_estimate_height_multiple_frames_with_overlap(self):
        """Test _estimate_total_height with multiple frames and overlaps."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()

                mock_pixbuf1 = MagicMock()
                mock_pixbuf1.get_height.return_value = 500
                mock_pixbuf2 = MagicMock()
                mock_pixbuf2.get_height.return_value = 500
                mock_pixbuf3 = MagicMock()
                mock_pixbuf3.get_height.return_value = 500

                manager.frames = [mock_pixbuf1, mock_pixbuf2, mock_pixbuf3]
                manager.overlaps = [100, 100]  # 100px overlap between each pair

                height = manager._estimate_total_height()

                # 500 + (500-100) + (500-100) = 500 + 400 + 400 = 1300
                assert height == 1300


class TestScrollCaptureManagerCaptureFrame:
    """Test ScrollCaptureManager.capture_frame method."""

    def test_capture_frame_not_capturing(self):
        """Test capture_frame fails when not in capturing state."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                manager.state = ScrollState.IDLE

                should_continue, error = manager.capture_frame()

                assert should_continue is False
                assert "not in capturing state" in error.lower()

    def test_capture_frame_stop_requested(self):
        """Test capture_frame stops when stop_requested is True."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        with patch("src.scroll_capture.detect_display_server"):
            with patch("src.scroll_capture.config.check_tool_available", return_value=False):
                manager = ScrollCaptureManager()
                manager.state = ScrollState.CAPTURING
                manager.stop_requested = True

                should_continue, error = manager.capture_frame()

                assert should_continue is False
                assert error is None


class TestScrollCaptureManagerScrollDown:
    """Test ScrollCaptureManager.scroll_down method."""

    def test_scroll_down_x11(self):
        """Test scroll_down on X11 uses xdotool."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                with patch("subprocess.run") as mock_run:
                    manager = ScrollCaptureManager()

                    result = manager.scroll_down()

                    assert result is True
                    # xdotool click 5 called 3 times
                    assert mock_run.call_count >= 3

    def test_scroll_down_x11_exception(self):
        """Test scroll_down on X11 handles exceptions."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                # Let init succeed, then patch subprocess.run for scroll_down
                with patch("subprocess.run") as mock_run:
                    manager = ScrollCaptureManager()

                # Now patch to throw exception during scroll
                with patch("subprocess.run", side_effect=Exception("Error")):
                    result = manager.scroll_down()

                    assert result is False

    def test_scroll_down_wayland_ydotool(self):
        """Test scroll_down on Wayland uses ydotool first."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.WAYLAND):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                with patch("subprocess.run") as mock_run:
                    manager = ScrollCaptureManager()

                    result = manager.scroll_down()

                    assert result is True

    def test_scroll_down_wayland_fallback_wtype(self):
        """Test scroll_down on Wayland falls back to wtype."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        def mock_check(cmd):
            # ydotool not available, wtype is
            if "ydotool" in cmd:
                return False
            return True

        with patch("src.scroll_capture.detect_display_server", return_value=DisplayServer.WAYLAND):
            with patch("src.scroll_capture.config.check_tool_available", side_effect=mock_check):
                # Let init succeed with wtype check passing
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    manager = ScrollCaptureManager()
                    manager.ydotool_available = False  # Force ydotool unavailable
                    manager.wtype_available = True  # Force wtype available

                # Now test scroll_down uses wtype
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    result = manager.scroll_down()

                    assert result is True

    def test_scroll_down_unknown_display_server(self):
        """Test scroll_down with unknown display server uses X11."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("src.scroll_capture.detect_display_server", return_value=None):
            with patch("src.scroll_capture.config.check_tool_available", return_value=True):
                with patch("subprocess.run") as mock_run:
                    manager = ScrollCaptureManager()

                    result = manager.scroll_down()

                    # Should use xdotool (X11 fallback)
                    assert result is True


class TestScrollCaptureManagerClassMethods:
    """Test ScrollCaptureManager has all expected methods."""

    def test_has_capture_frame_method(self):
        """Test ScrollCaptureManager has capture_frame method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "capture_frame")

    def test_has_scroll_down_method(self):
        """Test ScrollCaptureManager has scroll_down method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "scroll_down")

    def test_has_scroll_x11_method(self):
        """Test ScrollCaptureManager has _scroll_x11 method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_scroll_x11")

    def test_has_scroll_wayland_method(self):
        """Test ScrollCaptureManager has _scroll_wayland method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_scroll_wayland")

    def test_has_find_overlap_method(self):
        """Test ScrollCaptureManager has _find_overlap method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_find_overlap")

    def test_has_stitch_frames_method(self):
        """Test ScrollCaptureManager has _stitch_frames method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_stitch_frames")

    def test_has_pixbuf_to_numpy_method(self):
        """Test ScrollCaptureManager has _pixbuf_to_numpy method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_pixbuf_to_numpy")

    def test_has_surface_to_pixbuf_method(self):
        """Test ScrollCaptureManager has _surface_to_pixbuf method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_surface_to_pixbuf")

    def test_has_estimate_total_height_method(self):
        """Test ScrollCaptureManager has _estimate_total_height method."""
        from src.scroll_capture import ScrollCaptureManager

        assert hasattr(ScrollCaptureManager, "_estimate_total_height")
