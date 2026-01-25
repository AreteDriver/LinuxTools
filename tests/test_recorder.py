"""Tests for the GIF recorder module."""

from enum import Enum
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestRecorderModuleImport:
    """Test recorder module imports."""

    def test_module_imports(self):
        """Test that recorder module imports successfully."""
        from src import recorder

        assert hasattr(recorder, "RecordingState")
        assert hasattr(recorder, "OutputFormat")
        assert hasattr(recorder, "RecordingResult")
        assert hasattr(recorder, "GifRecorder")


class TestRecordingState:
    """Test RecordingState enum."""

    def test_is_enum(self):
        """Test RecordingState is an Enum."""
        from src.recorder import RecordingState

        assert issubclass(RecordingState, Enum)

    def test_has_idle_state(self):
        """Test RecordingState has IDLE."""
        from src.recorder import RecordingState

        assert RecordingState.IDLE.value == "idle"

    def test_has_recording_state(self):
        """Test RecordingState has RECORDING."""
        from src.recorder import RecordingState

        assert RecordingState.RECORDING.value == "recording"

    def test_has_encoding_state(self):
        """Test RecordingState has ENCODING."""
        from src.recorder import RecordingState

        assert RecordingState.ENCODING.value == "encoding"

    def test_has_completed_state(self):
        """Test RecordingState has COMPLETED."""
        from src.recorder import RecordingState

        assert RecordingState.COMPLETED.value == "completed"

    def test_has_error_state(self):
        """Test RecordingState has ERROR."""
        from src.recorder import RecordingState

        assert RecordingState.ERROR.value == "error"

    def test_all_states(self):
        """Test all expected states exist."""
        from src.recorder import RecordingState

        states = [s.value for s in RecordingState]
        assert "idle" in states
        assert "recording" in states
        assert "encoding" in states
        assert "completed" in states
        assert "error" in states


class TestOutputFormat:
    """Test OutputFormat enum."""

    def test_is_enum(self):
        """Test OutputFormat is an Enum."""
        from src.recorder import OutputFormat

        assert issubclass(OutputFormat, Enum)

    def test_has_gif_format(self):
        """Test OutputFormat has GIF."""
        from src.recorder import OutputFormat

        assert OutputFormat.GIF.value == "gif"

    def test_has_mp4_format(self):
        """Test OutputFormat has MP4."""
        from src.recorder import OutputFormat

        assert OutputFormat.MP4.value == "mp4"

    def test_has_webm_format(self):
        """Test OutputFormat has WEBM."""
        from src.recorder import OutputFormat

        assert OutputFormat.WEBM.value == "webm"


class TestRecordingResult:
    """Test RecordingResult dataclass."""

    def test_success_result(self):
        """Test successful RecordingResult."""
        from src.recorder import RecordingResult

        result = RecordingResult(success=True, filepath=Path("/tmp/test.gif"))

        assert result.success is True
        assert result.filepath == Path("/tmp/test.gif")
        assert result.error is None
        assert result.duration == 0.0

    def test_error_result(self):
        """Test error RecordingResult."""
        from src.recorder import RecordingResult

        result = RecordingResult(success=False, error="Recording failed")

        assert result.success is False
        assert result.filepath is None
        assert result.error == "Recording failed"

    def test_result_with_duration(self):
        """Test RecordingResult with duration."""
        from src.recorder import RecordingResult

        result = RecordingResult(
            success=True,
            filepath=Path("/tmp/test.gif"),
            duration=5.5,
        )

        assert result.duration == 5.5

    def test_default_values(self):
        """Test RecordingResult default values."""
        from src.recorder import RecordingResult

        result = RecordingResult(success=True)

        assert result.filepath is None
        assert result.error is None
        assert result.duration == 0.0


class TestGifRecorderClass:
    """Test GifRecorder class structure."""

    def test_class_has_start_recording_method(self):
        """Test GifRecorder has start_recording method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "start_recording")

    def test_class_has_stop_recording_method(self):
        """Test GifRecorder has stop_recording method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "stop_recording")

    def test_class_has_is_available_method(self):
        """Test GifRecorder has is_available method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "is_available")

    def test_class_has_check_methods(self):
        """Test GifRecorder has tool check methods."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_check_ffmpeg")
        assert hasattr(GifRecorder, "_check_wf_recorder")
        assert hasattr(GifRecorder, "_check_gifsicle")


class TestGifRecorderInit:
    """Test GifRecorder initialization."""

    def test_init_sets_idle_state(self):
        """Test GifRecorder starts in IDLE state."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                assert recorder.state == RecordingState.IDLE

    def test_init_checks_tools(self):
        """Test GifRecorder checks for available tools on init."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available") as mock_check:
                mock_check.return_value = True
                recorder = GifRecorder()

                assert recorder.ffmpeg_available is True
                assert recorder.wf_recorder_available is True
                assert recorder.gifsicle_available is True

    def test_init_sets_default_region(self):
        """Test GifRecorder has default region."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                assert recorder.region == (0, 0, 0, 0)


class TestGifRecorderIsAvailable:
    """Test GifRecorder.is_available method."""

    def test_is_available_returns_tuple(self):
        """Test is_available returns (bool, Optional[str])."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=True):
                recorder = GifRecorder()
                result = recorder.is_available()

                assert isinstance(result, tuple)
                assert len(result) == 2
                assert isinstance(result[0], bool)

    def test_is_available_with_ffmpeg_on_x11(self):
        """Test is_available returns True when ffmpeg available on X11."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.recorder.config.check_tool_available") as mock_check:
                mock_check.return_value = True
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is True
                assert error is None

    def test_is_available_without_ffmpeg_on_x11(self):
        """Test is_available returns False when ffmpeg not available on X11."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is False
                assert "ffmpeg" in error.lower()

    def test_is_available_with_wf_recorder_on_wayland(self):
        """Test is_available returns True with wf-recorder on Wayland."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.WAYLAND):
            with patch("src.recorder.config.check_tool_available", return_value=True):
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is True
                assert error is None

    def test_is_available_with_ffmpeg_on_wayland(self):
        """Test is_available returns True with ffmpeg on Wayland (no wf-recorder)."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        def mock_check(cmd):
            # wf-recorder not available, but ffmpeg is
            if "wf-recorder" in cmd:
                return False
            return True

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.WAYLAND):
            with patch("src.recorder.config.check_tool_available", side_effect=mock_check):
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is True

    def test_is_available_without_tools_on_wayland(self):
        """Test is_available returns False without tools on Wayland."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.WAYLAND):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is False
                assert "wf-recorder" in error.lower()

    def test_is_available_unknown_display_server(self):
        """Test is_available returns False for unknown display server."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server", return_value=None):
            with patch("src.recorder.config.check_tool_available", return_value=True):
                recorder = GifRecorder()

                available, error = recorder.is_available()

                assert available is False
                assert "unknown" in error.lower()


class TestGifRecorderStartRecording:
    """Test GifRecorder.start_recording method."""

    def test_start_recording_already_recording(self):
        """Test start_recording fails when already recording."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=True):
                recorder = GifRecorder()
                recorder.state = RecordingState.RECORDING

                success, error = recorder.start_recording(0, 0, 100, 100)

                assert success is False
                assert "already recording" in error.lower()

    def test_start_recording_not_available(self):
        """Test start_recording fails when tools not available."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                success, error = recorder.start_recording(0, 0, 100, 100)

                assert success is False
                assert "ffmpeg" in error.lower()

    def test_start_recording_region_too_small(self):
        """Test start_recording fails with region too small."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        with patch("src.recorder.detect_display_server", return_value=DisplayServer.X11):
            with patch("src.recorder.config.check_tool_available", return_value=True):
                recorder = GifRecorder()

                # Width too small
                success, error = recorder.start_recording(0, 0, 30, 100)
                assert success is False
                assert "too small" in error.lower()

                # Height too small
                success, error = recorder.start_recording(0, 0, 100, 30)
                assert success is False
                assert "too small" in error.lower()


class TestGifRecorderStopRecording:
    """Test GifRecorder.stop_recording method."""

    def test_stop_recording_not_recording(self):
        """Test stop_recording fails when not recording."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                result = recorder.stop_recording()

                assert result.success is False
                assert "not currently recording" in result.error.lower()

    def test_stop_recording_no_process(self):
        """Test stop_recording handles no process gracefully."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()
                recorder.state = RecordingState.RECORDING
                recorder.process = None

                result = recorder.stop_recording()

                assert result.success is False


class TestGifRecorderCancel:
    """Test GifRecorder.cancel method."""

    def test_cancel_with_no_process(self):
        """Test cancel with no active process."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                # Should not raise
                recorder.cancel()

                assert recorder.state == RecordingState.IDLE

    def test_cancel_kills_process(self):
        """Test cancel kills the process."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                mock_process = MagicMock()
                recorder.process = mock_process
                recorder.state = RecordingState.RECORDING

                recorder.cancel()

                mock_process.kill.assert_called_once()
                assert recorder.state == RecordingState.IDLE

    def test_cancel_handles_process_exception(self):
        """Test cancel handles exception when killing process."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                mock_process = MagicMock()
                mock_process.kill.side_effect = Exception("Process error")
                recorder.process = mock_process
                recorder.state = RecordingState.RECORDING

                # Should not raise
                recorder.cancel()

                assert recorder.state == RecordingState.IDLE

    def test_cancel_cleans_up_temp_file(self):
        """Test cancel removes temp video file."""
        import tempfile
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                # Create a real temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
                    temp_path = Path(f.name)

                recorder.temp_video = temp_path
                assert temp_path.exists()

                recorder.cancel()

                assert not temp_path.exists()


class TestGifRecorderGetElapsedTime:
    """Test GifRecorder.get_elapsed_time method."""

    def test_get_elapsed_time_not_recording(self):
        """Test get_elapsed_time returns 0 when not recording."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()
                recorder.state = RecordingState.IDLE

                elapsed = recorder.get_elapsed_time()

                assert elapsed == 0.0

    def test_get_elapsed_time_while_recording(self):
        """Test get_elapsed_time returns elapsed time when recording."""
        import time
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()
                recorder.state = RecordingState.RECORDING
                recorder.start_time = time.time() - 5.0  # Started 5 seconds ago

                elapsed = recorder.get_elapsed_time()

                assert elapsed >= 5.0
                assert elapsed < 6.0  # Allow some tolerance


class TestGifRecorderGetDitherOptions:
    """Test GifRecorder._get_dither_options method."""

    def test_dither_none(self):
        """Test _get_dither_options returns correct string for none."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                result = recorder._get_dither_options("none")
                assert result == "dither=none"

    def test_dither_bayer(self):
        """Test _get_dither_options returns correct string for bayer."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                result = recorder._get_dither_options("bayer")
                assert result == "dither=bayer:bayer_scale=5"

    def test_dither_floyd_steinberg(self):
        """Test _get_dither_options returns correct string for floyd_steinberg."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                result = recorder._get_dither_options("floyd_steinberg")
                assert result == "dither=floyd_steinberg"

    def test_dither_unknown_defaults_to_bayer(self):
        """Test _get_dither_options returns bayer for unknown option."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                result = recorder._get_dither_options("unknown_dither")
                assert result == "dither=bayer:bayer_scale=5"


class TestGifRecorderNotifyStateChange:
    """Test GifRecorder._notify_state_change method."""

    def test_notify_state_change_calls_callback(self):
        """Test _notify_state_change calls the callback."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                callback = MagicMock()
                recorder._on_state_change = callback
                recorder.state = RecordingState.RECORDING

                recorder._notify_state_change()

                callback.assert_called_once_with(RecordingState.RECORDING)

    def test_notify_state_change_no_callback(self):
        """Test _notify_state_change does nothing without callback."""
        from src.recorder import GifRecorder

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()
                recorder._on_state_change = None

                # Should not raise
                recorder._notify_state_change()

    def test_notify_state_change_handles_callback_exception(self):
        """Test _notify_state_change handles exception in callback."""
        from src.recorder import GifRecorder, RecordingState

        with patch("src.recorder.detect_display_server"):
            with patch("src.recorder.config.check_tool_available", return_value=False):
                recorder = GifRecorder()

                callback = MagicMock()
                callback.side_effect = Exception("Callback error")
                recorder._on_state_change = callback
                recorder.state = RecordingState.RECORDING

                # Should not raise
                recorder._notify_state_change()


class TestGifRecorderClassMethods:
    """Test GifRecorder class has all expected methods."""

    def test_has_cancel_method(self):
        """Test GifRecorder has cancel method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "cancel")

    def test_has_get_elapsed_time_method(self):
        """Test GifRecorder has get_elapsed_time method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "get_elapsed_time")

    def test_has_start_x11_recording_method(self):
        """Test GifRecorder has _start_x11_recording method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_start_x11_recording")

    def test_has_start_wayland_recording_method(self):
        """Test GifRecorder has _start_wayland_recording method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_start_wayland_recording")

    def test_has_encode_to_gif_method(self):
        """Test GifRecorder has _encode_to_gif method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_encode_to_gif")

    def test_has_finalize_video_method(self):
        """Test GifRecorder has _finalize_video method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_finalize_video")

    def test_has_optimize_gif_method(self):
        """Test GifRecorder has _optimize_gif method."""
        from src.recorder import GifRecorder

        assert hasattr(GifRecorder, "_optimize_gif")
