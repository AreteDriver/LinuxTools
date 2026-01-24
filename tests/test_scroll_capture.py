"""Tests for the scroll capture module."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestScrollCaptureModuleImport:
    """Test scroll capture module imports."""

    def test_module_imports(self):
        """Test that scroll_capture module imports successfully."""
        from src import scroll_capture

        assert hasattr(scroll_capture, "ScrollCaptureManager")
        assert hasattr(scroll_capture, "ScrollCaptureResult")

    def test_scroll_capture_result_dataclass(self):
        """Test ScrollCaptureResult dataclass."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(
            success=True,
            filepath=Path("/tmp/test.png"),
            frame_count=5,
            total_height=1000,
        )
        assert result.success is True
        assert result.filepath == Path("/tmp/test.png")
        assert result.frame_count == 5
        assert result.total_height == 1000
        assert result.error is None

    def test_scroll_capture_result_with_error(self):
        """Test ScrollCaptureResult with error."""
        from src.scroll_capture import ScrollCaptureResult

        result = ScrollCaptureResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"


class TestScrollCaptureManagerInit:
    """Test ScrollCaptureManager initialization."""

    def test_init_creates_instance(self):
        """Test that ScrollCaptureManager can be instantiated."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert manager is not None

    def test_init_has_required_attributes(self):
        """Test that manager has required attributes."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "frames")
        assert hasattr(manager, "overlaps")

    def test_init_frames_empty(self):
        """Test that frames list starts empty."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert manager.frames == []

    def test_init_checks_tools(self):
        """Test that init checks for required tools."""
        from src.scroll_capture import ScrollCaptureManager, _ensure_opencv

        manager = ScrollCaptureManager()
        assert hasattr(manager, "xdotool_available")
        assert hasattr(manager, "ydotool_available")
        assert hasattr(manager, "wtype_available")
        # OpenCV is lazy-loaded, trigger it and check result
        result = _ensure_opencv()
        assert isinstance(result, bool)

    def test_init_detects_display_server(self):
        """Test that init detects display server."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "display_server")


class TestIsAvailable:
    """Test is_available method."""

    def test_is_available_returns_tuple(self):
        """Test that is_available returns a tuple."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        result = manager.is_available()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_is_available_format(self):
        """Test is_available tuple format."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        available, error = manager.is_available()
        assert isinstance(available, bool)
        if not available:
            assert isinstance(error, str)
        else:
            assert error is None

    @pytest.mark.requires_gtk
    def test_is_available_x11_with_xdotool(self):
        """Test availability on X11 with xdotool."""
        from src.scroll_capture import ScrollCaptureManager, OPENCV_AVAILABLE
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.X11
        manager.xdotool_available = True

        available, error = manager.is_available()
        if OPENCV_AVAILABLE:
            assert available is True
            assert error is None

    @pytest.mark.requires_gtk
    def test_is_available_x11_without_xdotool(self):
        """Test availability on X11 without xdotool."""
        from src.scroll_capture import ScrollCaptureManager, OPENCV_AVAILABLE
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.X11
        manager.xdotool_available = False

        available, error = manager.is_available()
        if OPENCV_AVAILABLE:
            assert available is False
            assert "xdotool" in error.lower()

    @pytest.mark.requires_gtk
    def test_is_available_wayland_with_ydotool(self):
        """Test availability on Wayland with ydotool."""
        from src.scroll_capture import ScrollCaptureManager, OPENCV_AVAILABLE
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.WAYLAND
        manager.ydotool_available = True
        manager.wtype_available = False

        available, error = manager.is_available()
        if OPENCV_AVAILABLE:
            assert available is True
            assert error is None

    @pytest.mark.requires_gtk
    def test_is_available_wayland_with_wtype(self):
        """Test availability on Wayland with wtype."""
        from src.scroll_capture import ScrollCaptureManager, OPENCV_AVAILABLE
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.WAYLAND
        manager.ydotool_available = False
        manager.wtype_available = True

        available, error = manager.is_available()
        if OPENCV_AVAILABLE:
            assert available is True
            assert error is None

    @pytest.mark.requires_gtk
    def test_is_available_wayland_without_tools(self):
        """Test availability on Wayland without scroll tools."""
        from src.scroll_capture import ScrollCaptureManager, OPENCV_AVAILABLE
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.WAYLAND
        manager.ydotool_available = False
        manager.wtype_available = False

        available, error = manager.is_available()
        if OPENCV_AVAILABLE:
            assert available is False
            assert "ydotool" in error.lower() or "wtype" in error.lower()


class TestCheckTools:
    """Test tool availability checks."""

    def test_check_xdotool_available(self):
        """Test xdotool check when available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            manager = ScrollCaptureManager()
            result = manager._check_xdotool()
            assert result is True

    def test_check_xdotool_not_available(self):
        """Test xdotool check when not available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager = ScrollCaptureManager()
            result = manager._check_xdotool()
            assert result is False

    def test_check_opencv(self):
        """Test OpenCV availability check."""
        from src.scroll_capture import _ensure_opencv

        # OpenCV is lazy-loaded, trigger it and check result
        result = _ensure_opencv()
        assert isinstance(result, bool)

    def test_check_ydotool_available(self):
        """Test ydotool check when available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            manager = ScrollCaptureManager()
            result = manager._check_ydotool()
            assert result is True

    def test_check_ydotool_not_available(self):
        """Test ydotool check when not available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager = ScrollCaptureManager()
            result = manager._check_ydotool()
            assert result is False

    def test_check_wtype_available(self):
        """Test wtype check when available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            manager = ScrollCaptureManager()
            result = manager._check_wtype()
            assert result is True

    def test_check_wtype_not_available(self):
        """Test wtype check when not available."""
        from src.scroll_capture import ScrollCaptureManager

        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager = ScrollCaptureManager()
            result = manager._check_wtype()
            assert result is False


class TestStartCapture:
    """Test start_capture method."""

    def test_start_capture_returns_tuple(self):
        """Test that start_capture returns success tuple."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.xdotool_available = False

        result = manager.start_capture(0, 0, 100, 100)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_start_capture_stores_region(self):
        """Test that start_capture stores region."""
        from unittest.mock import patch
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.xdotool_available = True
        manager.opencv_available = True

        # Mock is_available to return True (avoids opencv/xdotool checks)
        with patch.object(manager, "is_available", return_value=(True, None)):
            manager.start_capture(10, 20, 100, 200)
        assert manager.region == (10, 20, 100, 200)


class TestCaptureFrame:
    """Test capture_frame method."""

    def test_capture_frame_method_exists(self):
        """Test that capture_frame method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "capture_frame")
        assert callable(manager.capture_frame)


class TestScrollDown:
    """Test scroll_down method."""

    def test_scroll_down_method_exists(self):
        """Test that scroll_down method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "scroll_down")
        assert callable(manager.scroll_down)

    def test_scroll_x11_method_exists(self):
        """Test that _scroll_x11 method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "_scroll_x11")
        assert callable(manager._scroll_x11)

    def test_scroll_wayland_method_exists(self):
        """Test that _scroll_wayland method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "_scroll_wayland")
        assert callable(manager._scroll_wayland)

    def test_scroll_x11_uses_xdotool(self):
        """Test that X11 scroll uses xdotool."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            manager._scroll_x11()
            # Should call xdotool click 5 (scroll down)
            assert mock_run.called
            call_args = mock_run.call_args_list[0][0][0]
            assert "xdotool" in call_args

    def test_scroll_wayland_uses_ydotool(self):
        """Test that Wayland scroll uses ydotool when available."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.ydotool_available = True
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = manager._scroll_wayland()
            assert result is True
            # Should call ydotool
            call_args = mock_run.call_args_list[0][0][0]
            assert "ydotool" in call_args

    def test_scroll_wayland_falls_back_to_wtype(self):
        """Test that Wayland scroll falls back to wtype."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.ydotool_available = False
        manager.wtype_available = True
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = manager._scroll_wayland()
            assert result is True
            # Should call wtype
            call_args = mock_run.call_args_list[0][0][0]
            assert "wtype" in call_args

    def test_scroll_wayland_returns_false_when_no_tools(self):
        """Test that Wayland scroll returns False when no tools available."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.ydotool_available = False
        manager.wtype_available = False
        result = manager._scroll_wayland()
        assert result is False


class TestFindOverlap:
    """Test find_overlap method."""

    def test_find_overlap_requires_opencv(self):
        """Test that find_overlap requires OpenCV."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        # Should handle case where OpenCV is not available
        assert hasattr(manager, "_find_overlap")


class TestStitchFrames:
    """Test stitch_frames method."""

    def test_stitch_frames_exists(self):
        """Test that stitch_frames method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "_stitch_frames")


class TestStopCapture:
    """Test stop_capture method."""

    def test_stop_capture_method_exists(self):
        """Test that stop_capture method exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "stop_capture")
        assert callable(manager.stop_capture)

    def test_stop_requested_flag(self):
        """Test that stop_requested flag exists."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert hasattr(manager, "stop_requested")
        assert manager.stop_requested is False

    def test_stop_capture_sets_flag(self):
        """Test that stop_capture sets stop_requested flag."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        assert manager.stop_requested is False

        manager.stop_capture()

        assert manager.stop_requested is True


class TestConfigIntegration:
    """Test integration with config module."""

    def test_uses_config_delay(self):
        """Test that manager uses config for delay."""
        from src import config

        cfg = config.load_config()
        assert "scroll_delay_ms" in cfg

    def test_uses_config_max_frames(self):
        """Test that manager uses config for max frames."""
        from src import config

        cfg = config.load_config()
        assert "scroll_max_frames" in cfg

    def test_uses_config_overlap_search(self):
        """Test that manager uses config for overlap search."""
        from src import config

        cfg = config.load_config()
        assert "scroll_overlap_search" in cfg

    def test_uses_config_confidence(self):
        """Test that manager uses config for confidence threshold."""
        from src import config

        cfg = config.load_config()
        assert "scroll_confidence" in cfg

    def test_uses_config_ignore_regions(self):
        """Test that manager uses config for ignore regions."""
        from src import config

        cfg = config.load_config()
        assert "scroll_ignore_top" in cfg
        assert "scroll_ignore_bottom" in cfg


class TestScrollState:
    """Test ScrollState enum."""

    def test_scroll_state_values(self):
        """Test ScrollState enum values."""
        from src.scroll_capture import ScrollState

        assert ScrollState.IDLE.value == "idle"
        assert ScrollState.CAPTURING.value == "capturing"
        assert ScrollState.STITCHING.value == "stitching"
        assert ScrollState.COMPLETED.value == "completed"
        assert ScrollState.ERROR.value == "error"


class TestFinishCapture:
    """Test finish_capture method."""

    def test_finish_capture_no_frames(self):
        """Test finish_capture with no frames."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.frames = []

        result = manager.finish_capture()

        assert result.success is False
        assert "No frames" in result.error
        assert manager.state == ScrollState.ERROR

    def test_finish_capture_one_frame(self):
        """Test finish_capture with single frame."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        mock_pixbuf = MagicMock()
        mock_pixbuf.get_height.return_value = 500
        manager.frames = [mock_pixbuf]

        result = manager.finish_capture()

        assert result.success is True
        assert result.frame_count == 1
        assert result.total_height == 500
        assert manager.state == ScrollState.COMPLETED

    def test_finish_capture_multiple_frames(self):
        """Test finish_capture with multiple frames."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        mock_pixbuf1 = MagicMock()
        mock_pixbuf1.get_height.return_value = 500
        mock_pixbuf1.get_width.return_value = 800
        mock_pixbuf2 = MagicMock()
        mock_pixbuf2.get_height.return_value = 500
        mock_pixbuf2.get_width.return_value = 800
        manager.frames = [mock_pixbuf1, mock_pixbuf2]
        manager.overlaps = [100]

        with patch.object(manager, "_stitch_frames") as mock_stitch:
            mock_stitched = MagicMock()
            mock_stitched.get_height.return_value = 900
            mock_stitch.return_value = mock_stitched

            result = manager.finish_capture()

        assert result.success is True
        assert result.frame_count == 2
        assert manager.state == ScrollState.COMPLETED

    def test_finish_capture_stitch_error(self):
        """Test finish_capture when stitching fails."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        mock_pixbuf = MagicMock()
        manager.frames = [mock_pixbuf, mock_pixbuf]
        manager.overlaps = [50]

        with patch.object(
            manager, "_stitch_frames", side_effect=Exception("Stitch error")
        ):
            result = manager.finish_capture()

        assert result.success is False
        assert "Stitch" in result.error
        assert manager.state == ScrollState.ERROR


class TestReset:
    """Test reset method."""

    def test_reset_clears_state(self):
        """Test that reset clears manager state."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.state = ScrollState.CAPTURING
        manager.frames = [MagicMock()]
        manager.overlaps = [50]
        manager.stop_requested = True

        manager.reset()

        assert manager.state == ScrollState.IDLE
        assert manager.frames == []
        assert manager.overlaps == []
        assert manager.stop_requested is False


class TestEstimateTotalHeight:
    """Test _estimate_total_height method."""

    def test_estimate_height_no_frames(self):
        """Test height estimation with no frames."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.frames = []

        result = manager._estimate_total_height()

        assert result == 0

    def test_estimate_height_one_frame(self):
        """Test height estimation with one frame."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        mock_pixbuf = MagicMock()
        mock_pixbuf.get_height.return_value = 600
        manager.frames = [mock_pixbuf]
        manager.overlaps = []

        result = manager._estimate_total_height()

        assert result == 600

    def test_estimate_height_multiple_frames(self):
        """Test height estimation with multiple frames."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        mock_pixbuf1 = MagicMock()
        mock_pixbuf1.get_height.return_value = 600
        mock_pixbuf2 = MagicMock()
        mock_pixbuf2.get_height.return_value = 600
        mock_pixbuf3 = MagicMock()
        mock_pixbuf3.get_height.return_value = 600
        manager.frames = [mock_pixbuf1, mock_pixbuf2, mock_pixbuf3]
        manager.overlaps = [100, 100]

        result = manager._estimate_total_height()

        # 600 + (600-100) + (600-100) = 1600
        assert result == 1600


class TestCaptureFrameDetailed:
    """Detailed tests for capture_frame method."""

    def test_capture_frame_wrong_state(self):
        """Test capture_frame when not in capturing state."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.state = ScrollState.IDLE

        should_continue, error = manager.capture_frame()

        assert should_continue is False
        assert "Not in capturing state" in error

    def test_capture_frame_stop_requested(self):
        """Test capture_frame when stop is requested."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.state = ScrollState.CAPTURING
        manager.stop_requested = True

        should_continue, error = manager.capture_frame()

        assert should_continue is False
        assert error is None

    def test_capture_frame_max_frames_reached(self):
        """Test capture_frame when max frames reached."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.state = ScrollState.CAPTURING
        manager.frames = [MagicMock() for _ in range(50)]  # Default max

        with patch(
            "src.scroll_capture.config.load_config",
            return_value={"scroll_max_frames": 50},
        ):
            should_continue, error = manager.capture_frame()

        assert should_continue is False
        assert error is None


class TestStartCaptureDetailed:
    """Detailed tests for start_capture method."""

    def test_start_capture_already_capturing(self):
        """Test start_capture when already capturing."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        manager.state = ScrollState.CAPTURING

        success, error = manager.start_capture(0, 0, 100, 100)

        assert success is False
        assert "Already capturing" in error

    def test_start_capture_region_too_small(self):
        """Test start_capture with region too small."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()

        with patch.object(manager, "is_available", return_value=(True, None)):
            success, error = manager.start_capture(0, 0, 30, 30)

        assert success is False
        assert "too small" in error.lower()

    def test_start_capture_success(self):
        """Test start_capture success."""
        from src.scroll_capture import ScrollCaptureManager, ScrollState

        manager = ScrollCaptureManager()
        on_progress = MagicMock()
        on_complete = MagicMock()

        with patch.object(manager, "is_available", return_value=(True, None)):
            success, error = manager.start_capture(
                100, 100, 400, 300, on_progress=on_progress, on_complete=on_complete
            )

        assert success is True
        assert error is None
        assert manager.region == (100, 100, 400, 300)
        assert manager.state == ScrollState.CAPTURING
        assert manager._on_progress == on_progress
        assert manager._on_complete == on_complete


class TestScrollDownDetailed:
    """Detailed tests for scroll_down method."""

    def test_scroll_down_x11(self):
        """Test scroll_down on X11."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.X11

        with patch.object(manager, "_scroll_x11", return_value=True) as mock_scroll:
            result = manager.scroll_down()

        assert result is True
        mock_scroll.assert_called_once()

    def test_scroll_down_wayland(self):
        """Test scroll_down on Wayland."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.WAYLAND

        with patch.object(manager, "_scroll_wayland", return_value=True) as mock_scroll:
            result = manager.scroll_down()

        assert result is True
        mock_scroll.assert_called_once()

    def test_scroll_down_unknown_uses_x11(self):
        """Test scroll_down with unknown display server uses X11."""
        from src.scroll_capture import ScrollCaptureManager
        from src.capture import DisplayServer

        manager = ScrollCaptureManager()
        manager.display_server = DisplayServer.UNKNOWN

        with patch.object(manager, "_scroll_x11", return_value=True) as mock_scroll:
            result = manager.scroll_down()

        assert result is True
        mock_scroll.assert_called_once()


class TestScrollX11Detailed:
    """Detailed tests for _scroll_x11 method."""

    def test_scroll_x11_timeout(self):
        """Test _scroll_x11 handles timeout."""
        import subprocess
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 1)):
            result = manager._scroll_x11()

        assert result is False

    def test_scroll_x11_exception(self):
        """Test _scroll_x11 handles exception."""
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()

        with patch("subprocess.run", side_effect=Exception("Error")):
            result = manager._scroll_x11()

        assert result is False


class TestScrollWaylandDetailed:
    """Detailed tests for _scroll_wayland method."""

    def test_scroll_wayland_ydotool_timeout(self):
        """Test _scroll_wayland handles ydotool timeout."""
        import subprocess
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.ydotool_available = True
        manager.wtype_available = False

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 1)):
            result = manager._scroll_wayland()

        assert result is False

    def test_scroll_wayland_wtype_timeout(self):
        """Test _scroll_wayland handles wtype timeout."""
        import subprocess
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()
        manager.ydotool_available = False
        manager.wtype_available = True

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 1)):
            result = manager._scroll_wayland()

        assert result is False


class TestIsAvailableDetailed:
    """Detailed tests for is_available method."""

    def test_is_available_gtk_not_available(self):
        """Test is_available when GTK not available."""
        from src import scroll_capture as sc

        manager = sc.ScrollCaptureManager()

        with patch.object(sc, "GTK_AVAILABLE", False):
            available, error = manager.is_available()

        assert available is False
        assert "GTK" in error

    def test_is_available_opencv_not_available(self):
        """Test is_available when OpenCV not available."""
        from src import scroll_capture as sc

        manager = sc.ScrollCaptureManager()

        with patch.object(sc, "GTK_AVAILABLE", True):
            with patch.object(sc, "_ensure_opencv", return_value=False):
                available, error = manager.is_available()

        assert available is False
        assert "OpenCV" in error

    def test_is_available_unknown_display_without_xdotool(self):
        """Test is_available with unknown display and no xdotool."""
        from src import scroll_capture as sc
        from src.capture import DisplayServer

        manager = sc.ScrollCaptureManager()
        manager.display_server = DisplayServer.UNKNOWN
        manager.xdotool_available = False

        with patch.object(sc, "GTK_AVAILABLE", True):
            with patch.object(sc, "_ensure_opencv", return_value=True):
                available, error = manager.is_available()

        assert available is False
        assert "xdotool" in error.lower()


class TestCheckWtypeDetailed:
    """Detailed tests for _check_wtype method."""

    def test_check_wtype_timeout(self):
        """Test _check_wtype handles timeout."""
        import subprocess
        from src.scroll_capture import ScrollCaptureManager

        manager = ScrollCaptureManager()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 2)):
            result = manager._check_wtype()

        assert result is False
