"""Tests for the GIF recorder module."""

import subprocess
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


# =============================================================================
# Functional Tests
# =============================================================================


class TestGifRecorderFunctional:
    """Functional tests for GifRecorder."""

    def test_create_recorder(self):
        """Test creating a GifRecorder instance."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()

        assert recorder is not None
        assert recorder.state == RecordingState.IDLE
        assert recorder.process is None

    def test_recorder_initial_state(self):
        """Test recorder initial state."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        assert recorder.temp_video is None
        assert recorder.start_time == 0
        assert recorder._on_state_change is None

    def test_set_on_state_change(self):
        """Test setting state change callback."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()

        called = []
        recorder._on_state_change = lambda state: called.append(state)

        # Set state and trigger change
        recorder.state = RecordingState.RECORDING
        recorder._notify_state_change()

        assert len(called) == 1
        assert called[0] == RecordingState.RECORDING

    def test_get_elapsed_time_not_recording(self):
        """Test get_elapsed_time when not recording."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        elapsed = recorder.get_elapsed_time()

        assert elapsed == 0.0

    def test_get_elapsed_time_recording(self):
        """Test get_elapsed_time while recording."""
        from src.recorder import GifRecorder, RecordingState
        import time

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING
        recorder.start_time = time.time() - 5.0  # Started 5 seconds ago

        elapsed = recorder.get_elapsed_time()

        assert 4.9 < elapsed < 5.2

    def test_region_storage(self):
        """Test region is stored correctly."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        assert recorder.region == (0, 0, 0, 0)

    def test_cancel_not_recording(self):
        """Test cancel when not recording."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()

        # Should not raise
        recorder.cancel()

        assert recorder.state == RecordingState.IDLE

    def test_cancel_cleans_up_temp_file(self, tmp_path):
        """Test cancel removes temp file."""
        from src.recorder import GifRecorder, RecordingState
        from pathlib import Path

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING

        # Create a fake temp file
        temp_file = tmp_path / "temp_video.mp4"
        temp_file.write_bytes(b"fake video data")
        recorder.temp_video = temp_file

        # Mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        recorder.process = mock_process

        recorder.cancel()

        assert recorder.state == RecordingState.IDLE
        # Temp file should be deleted
        assert not temp_file.exists()

    def test_is_available_returns_tuple(self):
        """Test is_available returns tuple of (bool, str)."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()
        result = recorder.is_available()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)

    def test_tool_check_flags(self):
        """Test tool availability flags are set."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        # These are booleans
        assert isinstance(recorder.ffmpeg_available, bool)
        assert isinstance(recorder.wf_recorder_available, bool)
        assert isinstance(recorder.gifsicle_available, bool)


class TestGifRecorderWithMocks:
    """Tests for GifRecorder with mocked subprocess."""

    def test_start_recording_when_already_recording(self):
        """Test start_recording returns error when already recording."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING

        success, error = recorder.start_recording(0, 0, 100, 100)

        assert success is False
        assert "Already recording" in error

    def test_start_recording_region_too_small(self):
        """Test start_recording returns error for tiny region."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()
        recorder.ffmpeg_available = True

        success, error = recorder.start_recording(0, 0, 5, 5)

        assert success is False
        assert "too small" in error

    def test_stop_recording_when_not_recording(self):
        """Test stop_recording returns error when not recording."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()

        result = recorder.stop_recording()

        assert result.success is False
        assert "Not currently recording" in result.error

    def test_stop_recording_terminates_process(self, tmp_path):
        """Test stop_recording terminates the subprocess."""
        from src.recorder import GifRecorder, RecordingState
        from pathlib import Path

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.returncode = 0
        recorder.process = mock_process

        # Create a real temp file
        temp_file = tmp_path / "test.mp4"
        temp_file.write_bytes(b"fake video")
        recorder.temp_video = temp_file

        with patch.object(recorder, "_finalize_video", return_value=Path("/tmp/output.gif")):
            result = recorder.stop_recording()

        # Process should have been signaled
        assert mock_process.send_signal.called or mock_process.terminate.called


class TestRecorderStateNotification:
    """Test state notification functionality."""

    def test_notify_state_change_with_callback(self):
        """Test _notify_state_change calls callback."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()

        states = []
        recorder._on_state_change = lambda s: states.append(s)

        recorder.state = RecordingState.RECORDING
        recorder._notify_state_change()
        recorder.state = RecordingState.ENCODING
        recorder._notify_state_change()
        recorder.state = RecordingState.COMPLETED
        recorder._notify_state_change()

        assert len(states) == 3

    def test_notify_state_change_without_callback(self):
        """Test _notify_state_change without callback doesn't crash."""
        from src.recorder import GifRecorder, RecordingState

        recorder = GifRecorder()
        recorder._on_state_change = None
        recorder.state = RecordingState.RECORDING

        # Should not raise
        recorder._notify_state_change()


class TestRecorderToolChecks:
    """Test tool availability checks."""

    def test_check_ffmpeg(self):
        """Test _check_ffmpeg detects ffmpeg."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        # Result depends on actual ffmpeg installation
        result = recorder._check_ffmpeg()
        assert isinstance(result, bool)

    def test_check_wf_recorder(self):
        """Test _check_wf_recorder detects wf-recorder."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        result = recorder._check_wf_recorder()
        assert isinstance(result, bool)

    def test_check_gifsicle(self):
        """Test _check_gifsicle detects gifsicle."""
        from src.recorder import GifRecorder

        recorder = GifRecorder()

        result = recorder._check_gifsicle()
        assert isinstance(result, bool)

    def test_is_available_x11_with_ffmpeg(self):
        """Test is_available on X11 with ffmpeg."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        recorder = GifRecorder()
        recorder.display_server = DisplayServer.X11
        recorder.ffmpeg_available = True

        available, error = recorder.is_available()

        assert available is True
        assert error is None

    def test_is_available_wayland_with_wf_recorder(self):
        """Test is_available on Wayland with wf-recorder."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        recorder = GifRecorder()
        recorder.display_server = DisplayServer.WAYLAND
        recorder.wf_recorder_available = True

        available, error = recorder.is_available()

        assert available is True

    def test_is_available_no_tools(self):
        """Test is_available with no tools available."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        recorder = GifRecorder()
        recorder.display_server = DisplayServer.X11
        recorder.ffmpeg_available = False
        recorder.wf_recorder_available = False

        available, error = recorder.is_available()

        assert available is False
        assert "ffmpeg" in error.lower()


class TestRecordingStateEnum:
    """Test RecordingState enum."""

    def test_recording_states_exist(self):
        """Test all recording states exist."""
        from src.recorder import RecordingState

        assert RecordingState.IDLE is not None
        assert RecordingState.RECORDING is not None
        assert RecordingState.ENCODING is not None
        assert RecordingState.COMPLETED is not None
        assert RecordingState.ERROR is not None

    def test_state_values(self):
        """Test state values are strings."""
        from src.recorder import RecordingState

        assert RecordingState.IDLE.value == "idle"
        assert RecordingState.RECORDING.value == "recording"


class TestOutputFormatEnum:
    """Test OutputFormat enum."""

    def test_output_formats_exist(self):
        """Test all output formats exist."""
        from src.recorder import OutputFormat

        assert OutputFormat.GIF is not None
        assert OutputFormat.MP4 is not None
        assert OutputFormat.WEBM is not None


class TestRecordingResultDataclass:
    """Test RecordingResult dataclass."""

    def test_create_success_result(self):
        """Test creating a success result."""
        from src.recorder import RecordingResult
        from pathlib import Path

        result = RecordingResult(
            success=True,
            filepath=Path("/tmp/test.gif"),
            duration=5.5
        )

        assert result.success is True
        assert result.filepath == Path("/tmp/test.gif")
        assert result.error is None
        assert result.duration == 5.5

    def test_create_error_result(self):
        """Test creating an error result."""
        from src.recorder import RecordingResult

        result = RecordingResult(
            success=False,
            error="Recording failed"
        )

        assert result.success is False
        assert result.filepath is None
        assert result.error == "Recording failed"


class TestRecorderStartRecordingFull:
    """Test start_recording with mocked subprocess."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("subprocess.Popen")
    @patch("tempfile.mkstemp")
    def test_start_x11_recording_success(
        self, mock_mkstemp, mock_popen, mock_config, mock_check, mock_detect
    ):
        """Test successful X11 recording start."""
        from src.recorder import GifRecorder, RecordingState
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"gif_fps": 15}
        mock_mkstemp.return_value = (5, "/tmp/test.mp4")
        mock_popen.return_value = MagicMock()

        with patch("os.close"):
            recorder = GifRecorder()
            success, error = recorder.start_recording(100, 100, 800, 600)

        assert success is True
        assert error is None
        assert recorder.state == RecordingState.RECORDING
        assert recorder.region == (100, 100, 800, 600)

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("subprocess.Popen")
    @patch("tempfile.mkstemp")
    def test_start_wayland_recording_with_wf_recorder(
        self, mock_mkstemp, mock_popen, mock_config, mock_check, mock_detect
    ):
        """Test Wayland recording start with wf-recorder."""
        from src.recorder import GifRecorder, RecordingState
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.WAYLAND
        mock_check.return_value = True
        mock_config.return_value = {"gif_fps": 15}
        mock_mkstemp.return_value = (5, "/tmp/test.mp4")
        mock_popen.return_value = MagicMock()

        with patch("os.close"):
            recorder = GifRecorder()
            success, error = recorder.start_recording(100, 100, 800, 600)

        assert success is True
        assert recorder.state == RecordingState.RECORDING

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("subprocess.Popen", side_effect=Exception("Process failed"))
    @patch("tempfile.mkstemp")
    def test_start_recording_exception(
        self, mock_mkstemp, mock_popen, mock_config, mock_check, mock_detect
    ):
        """Test start_recording handles exception."""
        from src.recorder import GifRecorder, RecordingState
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"gif_fps": 15}
        mock_mkstemp.return_value = (5, "/tmp/test.mp4")

        with patch("os.close"):
            recorder = GifRecorder()
            success, error = recorder.start_recording(100, 100, 800, 600)

        assert success is False
        assert "Process failed" in error
        assert recorder.state == RecordingState.ERROR


class TestRecorderStopRecordingFull:
    """Test stop_recording with mocked subprocess."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    def test_stop_recording_temp_file_not_created(self, mock_check, mock_detect):
        """Test stop_recording when temp file doesn't exist."""
        import signal
        from src.recorder import GifRecorder, RecordingState
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING
        recorder.temp_video = Path("/nonexistent/path.mp4")
        recorder.start_time = 100

        mock_process = MagicMock()
        recorder.process = mock_process

        result = recorder.stop_recording()

        assert result.success is False
        assert "not created" in result.error.lower()
        assert recorder.state == RecordingState.ERROR

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    def test_stop_recording_process_timeout(self, mock_check, mock_detect, tmp_path):
        """Test stop_recording handles process timeout."""
        import signal
        import subprocess
        from src.recorder import GifRecorder, RecordingState, OutputFormat
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING
        temp_file = tmp_path / "test.mp4"
        temp_file.write_bytes(b"video data")
        recorder.temp_video = temp_file
        recorder.start_time = 100
        recorder.region = (0, 0, 800, 600)

        mock_process = MagicMock()
        mock_process.wait.side_effect = [subprocess.TimeoutExpired("ffmpeg", 5), None]
        recorder.process = mock_process

        with patch.object(recorder, "_encode_to_gif") as mock_encode:
            mock_encode.return_value = MagicMock(success=True)
            result = recorder.stop_recording(OutputFormat.GIF)

        # Should have killed the process after timeout
        mock_process.kill.assert_called()

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    def test_stop_recording_mp4_format(self, mock_check, mock_detect, tmp_path):
        """Test stop_recording with MP4 format."""
        from src.recorder import GifRecorder, RecordingState, OutputFormat
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING
        temp_file = tmp_path / "test.mp4"
        temp_file.write_bytes(b"video data")
        recorder.temp_video = temp_file
        recorder.start_time = 100
        recorder.region = (0, 0, 800, 600)

        mock_process = MagicMock()
        recorder.process = mock_process

        with patch.object(recorder, "_finalize_video") as mock_finalize:
            mock_finalize.return_value = MagicMock(success=True)
            result = recorder.stop_recording(OutputFormat.MP4)

        mock_finalize.assert_called()

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    def test_stop_recording_webm_format(self, mock_check, mock_detect, tmp_path):
        """Test stop_recording with WebM format."""
        from src.recorder import GifRecorder, RecordingState, OutputFormat
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        recorder = GifRecorder()
        recorder.state = RecordingState.RECORDING
        temp_file = tmp_path / "test.mp4"
        temp_file.write_bytes(b"video data")
        recorder.temp_video = temp_file
        recorder.start_time = 100
        recorder.region = (0, 0, 800, 600)

        mock_process = MagicMock()
        recorder.process = mock_process

        with patch.object(recorder, "_finalize_video") as mock_finalize:
            mock_finalize.return_value = MagicMock(success=True)
            result = recorder.stop_recording(OutputFormat.WEBM)

        mock_finalize.assert_called()


class TestRecorderFinalizeVideo:
    """Test _finalize_video method."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    def test_finalize_video_mp4_success(
        self, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _finalize_video with MP4 format succeeds."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"video_quality": "medium"}
        output_path = tmp_path / "output.mp4"
        mock_save_path.return_value = output_path
        mock_run.return_value = MagicMock(returncode=0)

        recorder = GifRecorder()
        recorder.temp_video = tmp_path / "temp.mp4"

        result = recorder._finalize_video(5.0, "mp4")

        assert result.success is True
        assert result.filepath == output_path
        assert result.duration == 5.0

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    def test_finalize_video_webm_success(
        self, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _finalize_video with WebM format succeeds."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"video_quality": "high"}
        output_path = tmp_path / "output.webm"
        mock_save_path.return_value = output_path
        mock_run.return_value = MagicMock(returncode=0)

        recorder = GifRecorder()
        recorder.temp_video = tmp_path / "temp.mp4"

        result = recorder._finalize_video(3.0, "webm")

        assert result.success is True

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    def test_finalize_video_failure(
        self, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _finalize_video handles ffmpeg failure."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"video_quality": "low"}
        mock_save_path.return_value = tmp_path / "output.mp4"
        mock_run.return_value = MagicMock(returncode=1, stderr=b"encoding error")

        recorder = GifRecorder()
        recorder.temp_video = tmp_path / "temp.mp4"

        result = recorder._finalize_video(5.0, "mp4")

        assert result.success is False
        assert "encoding failed" in result.error.lower()

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 300))
    def test_finalize_video_timeout(
        self, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _finalize_video handles timeout."""
        import subprocess
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {"video_quality": "medium"}
        mock_save_path.return_value = tmp_path / "output.mp4"

        recorder = GifRecorder()
        recorder.temp_video = tmp_path / "temp.mp4"

        result = recorder._finalize_video(5.0, "mp4")

        assert result.success is False
        assert "timed out" in result.error.lower()


class TestRecorderEncodeToGif:
    """Test _encode_to_gif method."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    @patch("tempfile.mkstemp")
    def test_encode_to_gif_success(
        self, mock_mkstemp, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _encode_to_gif success."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {
            "gif_quality": "medium",
            "gif_colors": 256,
            "gif_scale_factor": 1.0,
            "gif_fps": 15,
            "gif_dither": "bayer",
            "gif_loop": 0,
            "gif_optimize": False,
        }
        output_path = tmp_path / "output.gif"
        mock_save_path.return_value = output_path
        mock_run.return_value = MagicMock(returncode=0)

        # Create fake palette file
        palette_file = tmp_path / "palette.png"
        palette_file.write_bytes(b"fake palette")
        mock_mkstemp.return_value = (5, str(palette_file))

        with patch("os.close"):
            recorder = GifRecorder()
            recorder.temp_video = tmp_path / "temp.mp4"
            recorder.region = (0, 0, 800, 600)

            result = recorder._encode_to_gif(5.0)

        assert result.success is True

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    @patch("tempfile.mkstemp")
    def test_encode_to_gif_low_quality(
        self, mock_mkstemp, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _encode_to_gif with low quality preset."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {
            "gif_quality": "low",
            "gif_colors": 256,
            "gif_scale_factor": 1.0,
            "gif_fps": 15,
            "gif_dither": "none",
            "gif_loop": 0,
            "gif_optimize": False,
        }
        mock_save_path.return_value = tmp_path / "output.gif"
        mock_run.return_value = MagicMock(returncode=0)

        palette_file = tmp_path / "palette.png"
        palette_file.write_bytes(b"fake palette")
        mock_mkstemp.return_value = (5, str(palette_file))

        with patch("os.close"):
            recorder = GifRecorder()
            recorder.temp_video = tmp_path / "temp.mp4"
            recorder.region = (0, 0, 800, 600)

            result = recorder._encode_to_gif(5.0)

        assert result.success is True

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    @patch("tempfile.mkstemp")
    def test_encode_to_gif_high_quality(
        self, mock_mkstemp, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _encode_to_gif with high quality preset."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {
            "gif_quality": "high",
            "gif_colors": 256,
            "gif_scale_factor": 1.0,
            "gif_fps": 15,
            "gif_dither": "floyd_steinberg",
            "gif_loop": 0,
            "gif_optimize": False,
        }
        mock_save_path.return_value = tmp_path / "output.gif"
        mock_run.return_value = MagicMock(returncode=0)

        palette_file = tmp_path / "palette.png"
        palette_file.write_bytes(b"fake palette")
        mock_mkstemp.return_value = (5, str(palette_file))

        with patch("os.close"):
            recorder = GifRecorder()
            recorder.temp_video = tmp_path / "temp.mp4"
            recorder.region = (0, 0, 800, 600)

            result = recorder._encode_to_gif(5.0)

        assert result.success is True

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("src.recorder.config.get_save_path")
    @patch("subprocess.run")
    @patch("tempfile.mkstemp")
    def test_encode_to_gif_with_scale(
        self, mock_mkstemp, mock_run, mock_save_path, mock_config, mock_check, mock_detect, tmp_path
    ):
        """Test _encode_to_gif with scaling."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_config.return_value = {
            "gif_quality": "medium",
            "gif_colors": 128,
            "gif_scale_factor": 0.5,  # Scale down
            "gif_fps": 10,
            "gif_dither": "bayer",
            "gif_loop": 0,
            "gif_optimize": False,
        }
        mock_save_path.return_value = tmp_path / "output.gif"
        mock_run.return_value = MagicMock(returncode=0)

        palette_file = tmp_path / "palette.png"
        palette_file.write_bytes(b"fake palette")
        mock_mkstemp.return_value = (5, str(palette_file))

        with patch("os.close"):
            recorder = GifRecorder()
            recorder.temp_video = tmp_path / "temp.mp4"
            recorder.region = (0, 0, 800, 600)

            result = recorder._encode_to_gif(5.0)

        assert result.success is True


class TestRecorderOptimizeGif:
    """Test _optimize_gif method."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("subprocess.run")
    def test_optimize_gif_success(self, mock_run, mock_check, mock_detect, tmp_path):
        """Test _optimize_gif succeeds."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        # Create fake GIF and optimized version
        gif_file = tmp_path / "test.gif"
        gif_file.write_bytes(b"fake gif")
        optimized_file = tmp_path / "test.opt.gif"

        def create_optimized(cmd, *args, **kwargs):
            optimized_file.write_bytes(b"optimized gif")
            return MagicMock(returncode=0)

        mock_run.side_effect = create_optimized

        recorder = GifRecorder()
        result = recorder._optimize_gif(gif_file)

        assert result is True

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("subprocess.run")
    def test_optimize_gif_failure(self, mock_run, mock_check, mock_detect, tmp_path):
        """Test _optimize_gif handles failure."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True
        mock_run.return_value = MagicMock(returncode=1)

        gif_file = tmp_path / "test.gif"
        gif_file.write_bytes(b"fake gif")

        recorder = GifRecorder()
        result = recorder._optimize_gif(gif_file)

        assert result is False

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("subprocess.run", side_effect=Exception("gifsicle error"))
    def test_optimize_gif_exception(self, mock_run, mock_check, mock_detect, tmp_path):
        """Test _optimize_gif handles exception."""
        from src.recorder import GifRecorder
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.X11
        mock_check.return_value = True

        gif_file = tmp_path / "test.gif"
        gif_file.write_bytes(b"fake gif")

        recorder = GifRecorder()
        result = recorder._optimize_gif(gif_file)

        assert result is False


class TestRecorderWaylandFallback:
    """Test Wayland recording with ffmpeg fallback."""

    @patch("src.recorder.detect_display_server")
    @patch("src.recorder.config.check_tool_available")
    @patch("src.recorder.config.load_config")
    @patch("subprocess.Popen")
    @patch("tempfile.mkstemp")
    def test_wayland_ffmpeg_fallback(
        self, mock_mkstemp, mock_popen, mock_config, mock_check, mock_detect
    ):
        """Test Wayland uses ffmpeg when wf-recorder not available."""
        from src.recorder import GifRecorder, RecordingState
        from src.capture import DisplayServer

        mock_detect.return_value = DisplayServer.WAYLAND
        # ffmpeg available, wf-recorder not
        mock_check.side_effect = [True, False, False]  # ffmpeg, wf-recorder, gifsicle
        mock_config.return_value = {"gif_fps": 15}
        mock_mkstemp.return_value = (5, "/tmp/test.mp4")
        mock_popen.return_value = MagicMock()

        with patch("os.close"):
            recorder = GifRecorder()
            # Force wf-recorder unavailable
            recorder.wf_recorder_available = False
            success, error = recorder.start_recording(100, 100, 800, 600)

        assert success is True
