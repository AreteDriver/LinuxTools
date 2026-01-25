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
