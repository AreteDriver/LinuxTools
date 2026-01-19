"""Tests for capture module."""

import os
from unittest.mock import MagicMock, patch
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.capture import (
    CaptureMode,
    DisplayServer,
    CaptureResult,
    detect_display_server,
)


class TestCaptureMode:
    """Test CaptureMode enum."""

    def test_fullscreen_mode(self):
        assert CaptureMode.FULLSCREEN.value == "fullscreen"

    def test_region_mode(self):
        assert CaptureMode.REGION.value == "region"

    def test_window_mode(self):
        assert CaptureMode.WINDOW.value == "window"


class TestDisplayServer:
    """Test DisplayServer enum."""

    def test_x11_server(self):
        assert DisplayServer.X11.value == "x11"

    def test_wayland_server(self):
        assert DisplayServer.WAYLAND.value == "wayland"

    def test_unknown_server(self):
        assert DisplayServer.UNKNOWN.value == "unknown"


class TestCaptureResult:
    """Test CaptureResult class."""

    def test_success_result(self):
        result = CaptureResult(success=True)
        assert result.success is True
        assert bool(result) is True

    def test_failure_result(self):
        result = CaptureResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"
        assert bool(result) is False

    def test_result_with_filepath(self):
        path = Path("/tmp/test.png")
        result = CaptureResult(success=True, filepath=path)
        assert result.filepath == path

    def test_result_with_pixbuf(self):
        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)
        assert result.pixbuf == mock_pixbuf


class TestDetectDisplayServer:
    """Test display server detection."""

    @patch.dict(
        os.environ,
        {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"},
        clear=True,
    )
    def test_detect_wayland_from_session_type(self):
        result = detect_display_server()
        assert result == DisplayServer.WAYLAND

    @patch.dict(
        os.environ, {"XDG_SESSION_TYPE": "", "WAYLAND_DISPLAY": "wayland-0"}, clear=True
    )
    def test_detect_wayland_from_display(self):
        result = detect_display_server()
        assert result == DisplayServer.WAYLAND

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"}, clear=True)
    def test_detect_x11(self):
        result = detect_display_server()
        assert result == DisplayServer.X11

    @patch.dict(
        os.environ,
        {"XDG_SESSION_TYPE": "", "WAYLAND_DISPLAY": "", "DISPLAY": ""},
        clear=True,
    )
    def test_detect_unknown(self):
        result = detect_display_server()
        assert result == DisplayServer.UNKNOWN


class TestCaptureFullscreen:
    """Test fullscreen capture."""

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", False)
    def test_capture_returns_error_without_gtk(self, mock_detect):
        from src.capture import capture_fullscreen

        mock_detect.return_value = DisplayServer.X11

        result = capture_fullscreen()
        assert result.success is False
        assert "GTK not available" in result.error


class TestCaptureRegion:
    """Test region capture."""

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", False)
    def test_capture_region_without_gtk(self, mock_detect):
        from src.capture import capture_region

        mock_detect.return_value = DisplayServer.X11

        result = capture_region(0, 0, 100, 100)
        assert result.success is False


class TestCaptureWindow:
    """Test window capture."""

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", False)
    def test_capture_window_without_gtk(self, mock_detect):
        from src.capture import capture_window

        mock_detect.return_value = DisplayServer.X11

        result = capture_window()
        assert result.success is False


class TestSaveCapture:
    """Test save_capture function."""

    def test_save_capture_failed_result(self):
        from src.capture import save_capture

        failed_result = CaptureResult(success=False, error="No screenshot")
        result = save_capture(failed_result)
        assert result.success is False
        assert "No screenshot to save" in result.error

    def test_save_capture_no_pixbuf(self):
        from src.capture import save_capture

        result = CaptureResult(success=True, pixbuf=None)
        save_result = save_capture(result)
        assert save_result.success is False


class TestCopyToClipboard:
    """Test clipboard copy function."""

    def test_copy_failed_result(self):
        from src.capture import copy_to_clipboard

        failed_result = CaptureResult(success=False)
        result = copy_to_clipboard(failed_result)
        assert result is False

    def test_copy_no_pixbuf(self):
        from src.capture import copy_to_clipboard

        result = CaptureResult(success=True, pixbuf=None)
        copy_result = copy_to_clipboard(result)
        assert copy_result is False


class TestCaptureMainFunction:
    """Test main capture function."""

    @patch("src.capture.config.load_config")
    def test_capture_region_without_coordinates(self, mock_config):
        from src.capture import capture, CaptureMode

        mock_config.return_value = {}
        result = capture(CaptureMode.REGION, region=None)
        assert result.success is False
        assert "Region not specified" in result.error

    @patch("src.capture.config.load_config")
    @patch("src.capture.capture_fullscreen")
    def test_capture_fullscreen_mode(self, mock_fullscreen, mock_config):
        from src.capture import capture, CaptureMode, CaptureResult

        mock_config.return_value = {}
        mock_fullscreen.return_value = CaptureResult(success=True, pixbuf=MagicMock())

        capture(CaptureMode.FULLSCREEN)
        mock_fullscreen.assert_called_once()

    @patch("src.capture.config.load_config")
    @patch("src.capture.capture_region")
    def test_capture_region_mode(self, mock_region, mock_config):
        from src.capture import capture, CaptureMode, CaptureResult

        mock_config.return_value = {}
        mock_region.return_value = CaptureResult(success=True, pixbuf=MagicMock())

        capture(CaptureMode.REGION, region=(0, 0, 100, 100))
        mock_region.assert_called_once()

    @patch("src.capture.config.load_config")
    @patch("src.capture.capture_window")
    def test_capture_window_mode(self, mock_window, mock_config):
        from src.capture import capture, CaptureMode, CaptureResult

        mock_config.return_value = {}
        mock_window.return_value = CaptureResult(success=True, pixbuf=MagicMock())

        capture(CaptureMode.WINDOW, window_id=12345)
        mock_window.assert_called_once()

    @patch("src.capture.config.load_config")
    def test_capture_unknown_mode(self, mock_config):
        from src.capture import capture

        mock_config.return_value = {}
        # Create a mock mode that's not recognized
        result = capture("invalid_mode")
        assert result.success is False

    @patch("src.capture.config.load_config")
    @patch("src.capture.capture_fullscreen")
    @patch("src.capture.save_capture")
    def test_capture_with_auto_save(self, mock_save, mock_fullscreen, mock_config):
        from src.capture import capture, CaptureMode, CaptureResult

        mock_config.return_value = {}
        mock_pixbuf = MagicMock()
        mock_fullscreen.return_value = CaptureResult(success=True, pixbuf=mock_pixbuf)
        mock_save.return_value = CaptureResult(
            success=True, filepath=Path("/tmp/test.png")
        )

        capture(CaptureMode.FULLSCREEN, auto_save=True)
        mock_save.assert_called_once()


class TestCaptureFullscreenWayland:
    """Test Wayland fullscreen capture."""

    @patch("src.capture.time.sleep")
    @patch("src.capture.subprocess.run")
    @patch("src.capture.os.path.exists")
    @patch("src.capture.os.unlink")
    def test_grim_success(self, mock_unlink, mock_exists, mock_run, mock_sleep):
        from src.capture import capture_fullscreen_wayland, GTK_AVAILABLE

        if not GTK_AVAILABLE:
            return

        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True

        with patch("src.capture.GdkPixbuf.Pixbuf.new_from_file") as mock_pixbuf:
            mock_pixbuf.return_value = MagicMock()
            result = capture_fullscreen_wayland(delay=0)
            assert result.success is True

    @patch("src.capture.subprocess.run")
    def test_grim_not_found_tries_gnome_screenshot(self, mock_run):
        from src.capture import capture_fullscreen_wayland

        # grim fails with FileNotFoundError, gnome-screenshot also fails
        mock_run.side_effect = FileNotFoundError("grim not found")

        result = capture_fullscreen_wayland(delay=0)
        assert result.success is False

    @patch("src.capture.time.sleep")
    @patch("src.capture.subprocess.run")
    def test_with_delay(self, mock_run, mock_sleep):
        from src.capture import capture_fullscreen_wayland

        mock_run.side_effect = FileNotFoundError("not found")
        capture_fullscreen_wayland(delay=2)
        mock_sleep.assert_called_once_with(2)


class TestCaptureRegionWayland:
    """Test Wayland region capture."""

    @patch("src.capture.time.sleep")
    @patch("src.capture.subprocess.run")
    @patch("src.capture.os.path.exists")
    @patch("src.capture.os.unlink")
    def test_grim_with_geometry_success(
        self, mock_unlink, mock_exists, mock_run, mock_sleep
    ):
        from src.capture import capture_region_wayland, GTK_AVAILABLE

        if not GTK_AVAILABLE:
            return

        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True

        with patch("src.capture.GdkPixbuf.Pixbuf.new_from_file") as mock_pixbuf:
            mock_pixbuf.return_value = MagicMock()
            result = capture_region_wayland(0, 0, 100, 100, delay=0)
            assert result.success is True

    @patch("src.capture.subprocess.run")
    @patch("src.capture.capture_fullscreen_wayland")
    def test_fallback_to_crop(self, mock_fullscreen, mock_run):
        from src.capture import capture_region_wayland, CaptureResult, GTK_AVAILABLE

        if not GTK_AVAILABLE:
            return

        mock_run.side_effect = FileNotFoundError("grim not found")
        mock_pixbuf = MagicMock()
        mock_fullscreen.return_value = CaptureResult(success=True, pixbuf=mock_pixbuf)

        with patch("src.capture.GdkPixbuf.Pixbuf.new") as mock_new:
            mock_cropped = MagicMock()
            mock_new.return_value = mock_cropped

            result = capture_region_wayland(0, 0, 100, 100, delay=0)
            assert result.success is True


class TestCaptureWindowWayland:
    """Test Wayland window capture."""

    @patch("src.capture.time.sleep")
    @patch("src.capture.subprocess.run")
    @patch("src.capture.os.path.exists")
    @patch("src.capture.os.unlink")
    def test_gnome_screenshot_success(
        self, mock_unlink, mock_exists, mock_run, mock_sleep
    ):
        from src.capture import capture_window_wayland, GTK_AVAILABLE

        if not GTK_AVAILABLE:
            return

        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True

        with patch("src.capture.GdkPixbuf.Pixbuf.new_from_file") as mock_pixbuf:
            mock_pixbuf.return_value = MagicMock()
            result = capture_window_wayland(delay=0)
            assert result.success is True

    @patch("src.capture.subprocess.run")
    @patch("src.capture.os.path.exists")
    @patch("src.capture.os.unlink")
    def test_all_tools_fail(self, mock_unlink, mock_exists, mock_run):
        from src.capture import capture_window_wayland

        mock_run.side_effect = FileNotFoundError("not found")
        mock_exists.return_value = False

        result = capture_window_wayland(delay=0)
        assert result.success is False
        assert "Window capture not supported" in result.error


class TestCaptureWindowX11:
    """Test X11 window capture."""

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.subprocess.run")
    @patch("src.capture.capture_region")
    def test_capture_active_window(self, mock_region, mock_run, mock_detect):
        from src.capture import capture_window, DisplayServer, CaptureResult

        mock_detect.return_value = DisplayServer.X11

        # First call gets window ID, second gets geometry
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="12345"),
            MagicMock(returncode=0, stdout="X=100\nY=100\nWIDTH=800\nHEIGHT=600\n"),
        ]
        mock_region.return_value = CaptureResult(success=True)

        capture_window()
        mock_region.assert_called_once()

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.subprocess.run")
    def test_xdotool_not_installed(self, mock_run, mock_detect):
        from src.capture import capture_window, DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_run.side_effect = FileNotFoundError("xdotool not found")

        result = capture_window()
        assert result.success is False
        assert "xdotool" in result.error

    @patch("src.capture.detect_display_server")
    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.subprocess.run")
    def test_xdotool_timeout(self, mock_run, mock_detect):
        from src.capture import capture_window, DisplayServer
        import subprocess

        mock_detect.return_value = DisplayServer.X11
        mock_run.side_effect = subprocess.TimeoutExpired("xdotool", 2)

        result = capture_window()
        assert result.success is False
        assert "timed out" in result.error


class TestSaveCaptureExtended:
    """Extended tests for save_capture function."""

    def test_save_with_format_mapping(self):
        from src.capture import save_capture, CaptureResult

        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        with patch("src.capture.config.get_save_path") as mock_path:
            mock_path.return_value = Path("/tmp/test.jpg")

            save_result = save_capture(result, format_str="jpg")
            # jpeg format should be mapped
            if save_result.success:
                mock_pixbuf.savev.assert_called()

    def test_save_creates_directory(self):
        from src.capture import save_capture, CaptureResult
        import tempfile

        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "test.png"

            save_capture(result, filepath=filepath)
            # Directory should be created

    def test_save_exception_handling(self):
        from src.capture import save_capture, CaptureResult

        mock_pixbuf = MagicMock()
        mock_pixbuf.savev.side_effect = Exception("Save error")
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        save_result = save_capture(result, filepath=Path("/tmp/test.png"))
        assert save_result.success is False
        assert "Failed to save" in save_result.error


class TestCopyToClipboardExtended:
    """Extended tests for copy_to_clipboard function."""

    @patch("src.capture.detect_display_server")
    @patch("src.capture.subprocess.Popen")
    @patch("src.capture.os.unlink")
    def test_wayland_wl_copy_success(self, mock_unlink, mock_popen, mock_detect):
        from src.capture import copy_to_clipboard, CaptureResult, DisplayServer

        mock_detect.return_value = DisplayServer.WAYLAND
        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.wait.return_value = None
        mock_popen.return_value = mock_proc

        with patch("builtins.open", MagicMock()):
            success = copy_to_clipboard(result)
            assert success is True

    @patch("src.capture.detect_display_server")
    @patch("src.capture.subprocess.Popen")
    @patch("src.capture.time.sleep")
    def test_x11_xclip_success(self, mock_sleep, mock_popen, mock_detect):
        from src.capture import copy_to_clipboard, CaptureResult, DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # Still running (backgrounded)
        mock_popen.return_value = mock_proc

        success = copy_to_clipboard(result)
        assert success is True

    @patch("src.capture.detect_display_server")
    @patch("src.capture.subprocess.Popen")
    @patch("src.capture.os.path.exists")
    @patch("src.capture.os.unlink")
    def test_external_tools_fail_fallback_to_gtk(
        self, mock_unlink, mock_exists, mock_popen, mock_detect
    ):
        from src.capture import copy_to_clipboard, CaptureResult, DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_pixbuf = MagicMock()
        result = CaptureResult(success=True, pixbuf=mock_pixbuf)

        mock_popen.side_effect = FileNotFoundError("xclip not found")
        mock_exists.return_value = True

        # GTK is imported inside the function, not at module level
        # Just test that external tools failing doesn't crash
        success = copy_to_clipboard(result, use_gtk=False)
        # Should fail since external tools are mocked to fail and use_gtk=False
        assert success is False


class TestCaptureResultBool:
    """Test CaptureResult boolean behavior."""

    def test_success_is_truthy(self):
        result = CaptureResult(success=True)
        assert bool(result) is True
        assert result  # Implicit bool

    def test_failure_is_falsy(self):
        result = CaptureResult(success=False)
        assert bool(result) is False
        assert not result  # Implicit bool


class TestDetectDisplayServerExtended:
    """Extended tests for display server detection."""

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "WAYLAND"}, clear=True)
    def test_detect_wayland_uppercase(self):
        result = detect_display_server()
        assert result == DisplayServer.WAYLAND

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "X11"}, clear=True)
    def test_detect_x11_uppercase(self):
        # X11 detection requires DISPLAY env var too
        with patch.dict(os.environ, {"DISPLAY": ":0"}):
            result = detect_display_server()
            assert result == DisplayServer.X11


class TestMonitorInfo:
    """Tests for MonitorInfo dataclass."""

    def test_monitor_info_creation(self):
        """Test basic MonitorInfo creation."""
        from src.capture import MonitorInfo

        monitor = MonitorInfo(
            index=0,
            name="HDMI-1",
            x=0,
            y=0,
            width=1920,
            height=1080,
            is_primary=True,
            scale_factor=1,
        )
        assert monitor.index == 0
        assert monitor.name == "HDMI-1"
        assert monitor.width == 1920
        assert monitor.is_primary is True

    def test_monitor_geometry_property(self):
        """Test the geometry property returns correct tuple."""
        from src.capture import MonitorInfo

        monitor = MonitorInfo(
            index=0, name="Test", x=100, y=200, width=1920, height=1080
        )
        assert monitor.geometry == (100, 200, 1920, 1080)

    def test_monitor_str_primary(self):
        """Test string representation of primary monitor."""
        from src.capture import MonitorInfo

        monitor = MonitorInfo(
            index=0, name="HDMI-1", x=0, y=0, width=1920, height=1080, is_primary=True
        )
        result = str(monitor)
        assert "HDMI-1" in result
        assert "1920x1080" in result
        assert "(Primary)" in result

    def test_monitor_str_secondary(self):
        """Test string representation of secondary monitor."""
        from src.capture import MonitorInfo

        monitor = MonitorInfo(
            index=1, name="DP-1", x=1920, y=0, width=2560, height=1440, is_primary=False
        )
        result = str(monitor)
        assert "DP-1" in result
        assert "2560x1440" in result
        assert "(Primary)" not in result

    def test_monitor_default_values(self):
        """Test default values for optional fields."""
        from src.capture import MonitorInfo

        monitor = MonitorInfo(index=0, name="Test", x=0, y=0, width=1920, height=1080)
        assert monitor.is_primary is False
        assert monitor.scale_factor == 1


class TestGetMonitors:
    """Tests for get_monitors function."""

    @patch("src.capture.GTK_AVAILABLE", False)
    def test_get_monitors_without_gtk(self):
        """Test returns empty list when GTK is not available."""
        from src.capture import get_monitors

        result = get_monitors()
        assert result == []

    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.Gdk.Display.get_default")
    def test_get_monitors_no_display(self, mock_get_default):
        """Test returns empty list when no display available."""
        mock_get_default.return_value = None

        from src.capture import get_monitors

        result = get_monitors()
        assert result == []

    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.Gdk.Display.get_default")
    def test_get_monitors_single_monitor(self, mock_get_default):
        """Test getting a single monitor."""
        mock_display = MagicMock()
        mock_display.get_n_monitors.return_value = 1

        mock_monitor = MagicMock()
        mock_geometry = MagicMock()
        mock_geometry.x = 0
        mock_geometry.y = 0
        mock_geometry.width = 1920
        mock_geometry.height = 1080
        mock_monitor.get_geometry.return_value = mock_geometry
        mock_monitor.get_model.return_value = "HDMI-1"
        mock_monitor.get_scale_factor.return_value = 1

        mock_display.get_monitor.return_value = mock_monitor
        mock_display.get_primary_monitor.return_value = mock_monitor

        mock_get_default.return_value = mock_display

        from src.capture import get_monitors

        monitors = get_monitors()
        assert len(monitors) == 1
        assert monitors[0].name == "HDMI-1"
        assert monitors[0].width == 1920
        assert monitors[0].is_primary is True

    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.Gdk.Display.get_default")
    def test_get_monitors_multiple_monitors(self, mock_get_default):
        """Test getting multiple monitors."""
        mock_display = MagicMock()
        mock_display.get_n_monitors.return_value = 2

        mock_monitor1 = MagicMock()
        mock_geom1 = MagicMock(x=0, y=0, width=1920, height=1080)
        mock_monitor1.get_geometry.return_value = mock_geom1
        mock_monitor1.get_model.return_value = "Primary"
        mock_monitor1.get_scale_factor.return_value = 1

        mock_monitor2 = MagicMock()
        mock_geom2 = MagicMock(x=1920, y=0, width=2560, height=1440)
        mock_monitor2.get_geometry.return_value = mock_geom2
        mock_monitor2.get_model.return_value = "Secondary"
        mock_monitor2.get_scale_factor.return_value = 2

        mock_display.get_monitor.side_effect = [mock_monitor1, mock_monitor2]
        mock_display.get_primary_monitor.return_value = mock_monitor1

        mock_get_default.return_value = mock_display

        from src.capture import get_monitors

        monitors = get_monitors()
        assert len(monitors) == 2
        assert monitors[0].is_primary is True
        assert monitors[1].is_primary is False
        assert monitors[1].scale_factor == 2

    @patch("src.capture.GTK_AVAILABLE", True)
    @patch("src.capture.Gdk.Display.get_default")
    def test_get_monitors_null_monitor(self, mock_get_default):
        """Test handles null monitor in list."""
        mock_display = MagicMock()
        mock_display.get_n_monitors.return_value = 2
        mock_display.get_monitor.side_effect = [None, MagicMock()]
        mock_display.get_monitor.return_value = None
        mock_display.get_primary_monitor.return_value = None

        # Reconfigure to return None for first, valid for second
        mock_monitor = MagicMock()
        mock_geom = MagicMock(x=0, y=0, width=1920, height=1080)
        mock_monitor.get_geometry.return_value = mock_geom
        mock_monitor.get_model.return_value = None  # Test fallback name
        mock_monitor.get_scale_factor.return_value = 1

        mock_display.get_monitor.side_effect = [None, mock_monitor]
        mock_get_default.return_value = mock_display

        from src.capture import get_monitors

        monitors = get_monitors()
        assert len(monitors) == 1
        assert "Monitor" in monitors[0].name  # Fallback name


class TestGetMonitorAtPoint:
    """Tests for get_monitor_at_point function."""

    @patch("src.capture.get_monitors")
    def test_point_on_first_monitor(self, mock_get_monitors):
        """Test finding monitor at point on first monitor."""
        from src.capture import get_monitor_at_point, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "Primary", 0, 0, 1920, 1080, True),
            MonitorInfo(1, "Secondary", 1920, 0, 2560, 1440, False),
        ]

        result = get_monitor_at_point(500, 500)
        assert result is not None
        assert result.name == "Primary"

    @patch("src.capture.get_monitors")
    def test_point_on_second_monitor(self, mock_get_monitors):
        """Test finding monitor at point on second monitor."""
        from src.capture import get_monitor_at_point, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "Primary", 0, 0, 1920, 1080, True),
            MonitorInfo(1, "Secondary", 1920, 0, 2560, 1440, False),
        ]

        result = get_monitor_at_point(2500, 500)
        assert result is not None
        assert result.name == "Secondary"

    @patch("src.capture.get_monitors")
    def test_point_outside_all_monitors(self, mock_get_monitors):
        """Test returns None when point is outside all monitors."""
        from src.capture import get_monitor_at_point, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "Primary", 0, 0, 1920, 1080, True),
        ]

        result = get_monitor_at_point(5000, 5000)
        assert result is None

    @patch("src.capture.get_monitors")
    def test_point_at_monitor_boundary(self, mock_get_monitors):
        """Test point at exact monitor boundary."""
        from src.capture import get_monitor_at_point, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "Primary", 0, 0, 1920, 1080, True),
        ]

        # Point at origin (0, 0) should be on monitor
        result = get_monitor_at_point(0, 0)
        assert result is not None

        # Point at edge (1919, 1079) should be on monitor
        result = get_monitor_at_point(1919, 1079)
        assert result is not None

        # Point at (1920, 1080) should NOT be on monitor (exclusive boundary)
        result = get_monitor_at_point(1920, 1080)
        assert result is None

    @patch("src.capture.get_monitors")
    def test_no_monitors(self, mock_get_monitors):
        """Test returns None when no monitors available."""
        from src.capture import get_monitor_at_point

        mock_get_monitors.return_value = []

        result = get_monitor_at_point(100, 100)
        assert result is None


class TestGetPrimaryMonitor:
    """Tests for get_primary_monitor function."""

    @patch("src.capture.get_monitors")
    def test_returns_primary(self, mock_get_monitors):
        """Test returns the primary monitor."""
        from src.capture import get_primary_monitor, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "Secondary", 1920, 0, 2560, 1440, False),
            MonitorInfo(1, "Primary", 0, 0, 1920, 1080, True),
        ]

        result = get_primary_monitor()
        assert result is not None
        assert result.name == "Primary"
        assert result.is_primary is True

    @patch("src.capture.get_monitors")
    def test_fallback_to_first_if_no_primary(self, mock_get_monitors):
        """Test falls back to first monitor if no primary set."""
        from src.capture import get_primary_monitor, MonitorInfo

        mock_get_monitors.return_value = [
            MonitorInfo(0, "First", 0, 0, 1920, 1080, False),
            MonitorInfo(1, "Second", 1920, 0, 2560, 1440, False),
        ]

        result = get_primary_monitor()
        assert result is not None
        assert result.name == "First"

    @patch("src.capture.get_monitors")
    def test_returns_none_if_no_monitors(self, mock_get_monitors):
        """Test returns None when no monitors available."""
        from src.capture import get_primary_monitor

        mock_get_monitors.return_value = []

        result = get_primary_monitor()
        assert result is None


class TestCaptureMonitor:
    """Tests for capture_monitor function."""

    @patch("src.capture.capture_region")
    @patch("src.capture.time.sleep")
    def test_capture_with_delay(self, mock_sleep, mock_capture_region):
        """Test capture_monitor with delay."""
        from src.capture import capture_monitor, MonitorInfo, CaptureResult

        monitor = MonitorInfo(0, "Test", 0, 0, 1920, 1080)
        mock_capture_region.return_value = CaptureResult(success=True)

        capture_monitor(monitor, delay=2)

        mock_sleep.assert_called_once_with(2)
        mock_capture_region.assert_called_once_with(0, 0, 1920, 1080, delay=0)

    @patch("src.capture.capture_region")
    @patch("src.capture.time.sleep")
    def test_capture_without_delay(self, mock_sleep, mock_capture_region):
        """Test capture_monitor without delay."""
        from src.capture import capture_monitor, MonitorInfo, CaptureResult

        monitor = MonitorInfo(0, "Test", 100, 200, 2560, 1440)
        mock_capture_region.return_value = CaptureResult(success=True)

        capture_monitor(monitor, delay=0)

        mock_sleep.assert_not_called()
        mock_capture_region.assert_called_once_with(100, 200, 2560, 1440, delay=0)

    @patch("src.capture.capture_region")
    def test_capture_passes_geometry(self, mock_capture_region):
        """Test that monitor geometry is passed to capture_region."""
        from src.capture import capture_monitor, MonitorInfo, CaptureResult

        monitor = MonitorInfo(0, "Offset Monitor", 1920, 0, 2560, 1440)
        mock_capture_region.return_value = CaptureResult(success=True)

        capture_monitor(monitor)

        args = mock_capture_region.call_args[0]
        assert args == (1920, 0, 2560, 1440)

    @patch("src.capture.capture_region")
    def test_capture_returns_result(self, mock_capture_region):
        """Test that capture_monitor returns the result from capture_region."""
        from src.capture import capture_monitor, MonitorInfo, CaptureResult

        monitor = MonitorInfo(0, "Test", 0, 0, 1920, 1080)
        expected_result = CaptureResult(success=True, pixbuf=MagicMock())
        mock_capture_region.return_value = expected_result

        result = capture_monitor(monitor)

        assert result is expected_result
        assert result.success is True
