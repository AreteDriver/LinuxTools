"""Tests for MacroPlayer and MacroPlayerThread."""

import pytest
from unittest.mock import MagicMock, patch
from g13_linux.gui.models.macro_player import (
    MacroPlayer,
    MacroPlayerThread,
    PlaybackState,
)
from g13_linux.gui.models.macro_types import (
    Macro,
    MacroStep,
    MacroStepType,
    PlaybackMode,
)


class TestPlaybackState:
    """Tests for PlaybackState enum."""

    def test_idle(self):
        """Test IDLE state value."""
        assert PlaybackState.IDLE.value == "idle"

    def test_playing(self):
        """Test PLAYING state value."""
        assert PlaybackState.PLAYING.value == "playing"

    def test_paused(self):
        """Test PAUSED state value."""
        assert PlaybackState.PAUSED.value == "paused"

    def test_stopping(self):
        """Test STOPPING state value."""
        assert PlaybackState.STOPPING.value == "stopping"


class TestMacroPlayerThreadInit:
    """Tests for MacroPlayerThread initialization."""

    def test_init_with_macro(self):
        """Test thread initialization."""
        macro = Macro(name="Test")
        thread = MacroPlayerThread(macro)

        assert thread.macro is macro
        assert thread._stop_requested is False
        assert thread._pause_requested is False
        assert thread._uinput is None

    def test_request_stop(self):
        """Test stop request flag."""
        macro = Macro(name="Test")
        thread = MacroPlayerThread(macro)

        thread.request_stop()
        assert thread._stop_requested is True

    def test_request_pause(self):
        """Test pause request flag."""
        macro = Macro(name="Test")
        thread = MacroPlayerThread(macro)

        thread.request_pause()
        assert thread._pause_requested is True

    def test_request_resume(self):
        """Test resume clears pause flag."""
        macro = Macro(name="Test")
        thread = MacroPlayerThread(macro)

        thread.request_pause()
        assert thread._pause_requested is True

        thread.request_resume()
        assert thread._pause_requested is False


class TestMacroPlayerThreadDelayCalculation:
    """Tests for delay calculation logic."""

    def test_delay_as_fast_mode(self):
        """Test AS_FAST mode has no delay."""
        macro = Macro(playback_mode=PlaybackMode.AS_FAST)
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=1000
        )
        delay = thread._calculate_delay(step, 0)

        assert delay == 0

    def test_delay_fixed_mode(self):
        """Test FIXED mode uses fixed delay."""
        macro = Macro(playback_mode=PlaybackMode.FIXED, fixed_delay_ms=50)
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=1000
        )
        delay = thread._calculate_delay(step, 0)

        assert delay == 50

    def test_delay_fixed_mode_with_speed(self):
        """Test FIXED mode respects speed multiplier."""
        macro = Macro(
            playback_mode=PlaybackMode.FIXED, fixed_delay_ms=100, speed_multiplier=2.0
        )
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=1000
        )
        delay = thread._calculate_delay(step, 0)

        assert delay == 50  # 100 / 2.0

    def test_delay_recorded_mode(self):
        """Test RECORDED mode uses timestamp delta."""
        macro = Macro(playback_mode=PlaybackMode.RECORDED)
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=500
        )
        delay = thread._calculate_delay(step, 200)

        assert delay == 300  # 500 - 200

    def test_delay_recorded_mode_with_speed(self):
        """Test RECORDED mode respects speed multiplier."""
        macro = Macro(playback_mode=PlaybackMode.RECORDED, speed_multiplier=2.0)
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=400
        )
        delay = thread._calculate_delay(step, 0)

        assert delay == 200  # 400 / 2.0

    def test_delay_recorded_mode_no_negative(self):
        """Test RECORDED mode never returns negative."""
        macro = Macro(playback_mode=PlaybackMode.RECORDED)
        thread = MacroPlayerThread(macro)

        step = MacroStep(
            step_type=MacroStepType.KEY_PRESS, value="KEY_A", timestamp_ms=100
        )
        delay = thread._calculate_delay(step, 500)

        assert delay == 0  # max(0, 100 - 500)


class TestMacroPlayerThreadExecuteStep:
    """Tests for step execution."""

    def test_execute_step_no_uinput(self):
        """Test execution with no UInput is safe."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        step = MacroStep(step_type=MacroStepType.KEY_PRESS, value="KEY_A")
        # Should not raise
        thread._execute_step(step)

    def test_execute_step_delay(self):
        """Test delay step calls interruptible_sleep."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        # Need to set _uinput to prevent early return
        thread._uinput = MagicMock()

        step = MacroStep(step_type=MacroStepType.DELAY, value=100)

        # Verify interruptible_sleep is called with correct value
        with patch.object(thread, "_interruptible_sleep") as mock_sleep:
            thread._execute_step(step)
            mock_sleep.assert_called_once_with(0.1)  # 100ms = 0.1s

    def test_execute_step_g13_button(self):
        """Test G13 button step is handled."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        step = MacroStep(step_type=MacroStepType.G13_BUTTON, value="G5")
        # Should not raise (currently a no-op)
        thread._execute_step(step)


class TestMacroPlayerThreadEmitKey:
    """Tests for key emission."""

    def test_emit_key_no_uinput(self):
        """Test emit with no UInput is safe."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        # Should not raise
        thread._emit_key("KEY_A", True)

    def test_emit_key_with_mock_uinput(self):
        """Test emit with mocked UInput."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        mock_uinput = MagicMock()
        mock_ecodes = MagicMock()
        mock_ecodes.KEY_A = 30
        mock_ecodes.EV_KEY = 1

        thread._uinput = mock_uinput
        thread._ecodes = mock_ecodes

        thread._emit_key("KEY_A", True)

        mock_uinput.write.assert_called_once_with(1, 30, 1)
        mock_uinput.syn.assert_called_once()

    def test_emit_key_release(self):
        """Test emit key release."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        mock_uinput = MagicMock()
        mock_ecodes = MagicMock()
        mock_ecodes.KEY_B = 48
        mock_ecodes.EV_KEY = 1

        thread._uinput = mock_uinput
        thread._ecodes = mock_ecodes

        thread._emit_key("KEY_B", False)

        mock_uinput.write.assert_called_once_with(1, 48, 0)

    def test_emit_key_unknown_code(self):
        """Test emit with unknown key code."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        mock_uinput = MagicMock()
        mock_ecodes = MagicMock(spec=[])  # No attributes

        thread._uinput = mock_uinput
        thread._ecodes = mock_ecodes

        # Should not raise
        thread._emit_key("KEY_UNKNOWN", True)
        mock_uinput.write.assert_not_called()


class TestMacroPlayerThreadCleanup:
    """Tests for UInput cleanup."""

    def test_cleanup_uinput_none(self):
        """Test cleanup with no UInput."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        # Should not raise
        thread._cleanup_uinput()
        assert thread._uinput is None

    def test_cleanup_uinput_closes(self):
        """Test cleanup closes UInput."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        mock_uinput = MagicMock()
        thread._uinput = mock_uinput

        thread._cleanup_uinput()

        mock_uinput.close.assert_called_once()
        assert thread._uinput is None

    def test_cleanup_uinput_handles_exception(self):
        """Test cleanup handles close exception."""
        macro = Macro()
        thread = MacroPlayerThread(macro)

        mock_uinput = MagicMock()
        mock_uinput.close.side_effect = Exception("Close failed")
        thread._uinput = mock_uinput

        # Should not raise
        thread._cleanup_uinput()
        assert thread._uinput is None


class TestMacroPlayerInit:
    """Tests for MacroPlayer initialization."""

    def test_init(self):
        """Test player initialization."""
        player = MacroPlayer()

        assert player.state == PlaybackState.IDLE
        assert player.is_playing is False
        assert player.current_macro is None

    def test_state_property(self):
        """Test state property."""
        player = MacroPlayer()
        assert player.state == PlaybackState.IDLE


class TestMacroPlayerIsPlaying:
    """Tests for is_playing property."""

    def test_is_playing_idle(self):
        """Test is_playing when idle."""
        player = MacroPlayer()
        player._state = PlaybackState.IDLE
        assert player.is_playing is False

    def test_is_playing_playing(self):
        """Test is_playing when playing."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING
        assert player.is_playing is True

    def test_is_playing_paused(self):
        """Test is_playing when paused."""
        player = MacroPlayer()
        player._state = PlaybackState.PAUSED
        assert player.is_playing is True

    def test_is_playing_stopping(self):
        """Test is_playing when stopping."""
        player = MacroPlayer()
        player._state = PlaybackState.STOPPING
        assert player.is_playing is False


class TestMacroPlayerPlay:
    """Tests for play method."""

    def test_play_empty_macro(self, qtbot):
        """Test playing empty macro emits error."""
        player = MacroPlayer()
        macro = Macro(name="Empty")

        errors = []
        player.error_occurred.connect(errors.append)

        player.play(macro)

        assert len(errors) == 1
        assert "no steps" in errors[0]

    def test_play_already_playing(self, qtbot):
        """Test playing while already playing emits error."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING

        macro = Macro(name="Test")
        macro.add_step(MacroStepType.KEY_PRESS, "KEY_A")

        errors = []
        player.error_occurred.connect(errors.append)

        player.play(macro)

        assert len(errors) == 1
        assert "Already playing" in errors[0]

    def test_play_starts_thread(self, qtbot):
        """Test play starts player thread."""
        player = MacroPlayer()
        macro = Macro(name="Test")
        macro.add_step(MacroStepType.KEY_PRESS, "KEY_A")

        with patch.object(MacroPlayerThread, "start"):
            player.play(macro)

            assert player._state == PlaybackState.PLAYING
            assert player._current_macro is macro
            assert player._player_thread is not None


class TestMacroPlayerStop:
    """Tests for stop method."""

    def test_stop_no_thread(self):
        """Test stop with no thread."""
        player = MacroPlayer()

        # Should not raise
        player.stop()
        assert player.state == PlaybackState.IDLE

    def test_stop_clears_state(self):
        """Test stop clears state."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING
        player._current_macro = Macro()

        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = False
        player._player_thread = mock_thread

        player.stop()

        assert player._state == PlaybackState.IDLE
        assert player._current_macro is None


class TestMacroPlayerPauseResume:
    """Tests for pause/resume methods."""

    def test_pause_when_playing(self):
        """Test pause when playing."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING

        mock_thread = MagicMock()
        player._player_thread = mock_thread

        player.pause()

        mock_thread.request_pause.assert_called_once()
        assert player._state == PlaybackState.PAUSED

    def test_pause_when_not_playing(self):
        """Test pause when not playing does nothing."""
        player = MacroPlayer()
        player._state = PlaybackState.IDLE

        player.pause()
        assert player._state == PlaybackState.IDLE

    def test_resume_when_paused(self):
        """Test resume when paused."""
        player = MacroPlayer()
        player._state = PlaybackState.PAUSED

        mock_thread = MagicMock()
        player._player_thread = mock_thread

        player.resume()

        mock_thread.request_resume.assert_called_once()
        assert player._state == PlaybackState.PLAYING

    def test_resume_when_not_paused(self):
        """Test resume when not paused does nothing."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING

        mock_thread = MagicMock()
        player._player_thread = mock_thread

        player.resume()
        mock_thread.request_resume.assert_not_called()


class TestMacroPlayerTogglePause:
    """Tests for toggle_pause method."""

    def test_toggle_pause_from_playing(self):
        """Test toggle from playing to paused."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING

        mock_thread = MagicMock()
        player._player_thread = mock_thread

        player.toggle_pause()

        assert player._state == PlaybackState.PAUSED

    def test_toggle_pause_from_paused(self):
        """Test toggle from paused to playing."""
        player = MacroPlayer()
        player._state = PlaybackState.PAUSED

        mock_thread = MagicMock()
        player._player_thread = mock_thread

        player.toggle_pause()

        assert player._state == PlaybackState.PLAYING


class TestMacroPlayerCallbacks:
    """Tests for callback handling."""

    def test_on_step_executed(self, qtbot):
        """Test step executed callback forwards signal."""
        player = MacroPlayer()

        step = MacroStep(step_type=MacroStepType.KEY_PRESS, value="KEY_A")
        received = []

        player.step_executed.connect(lambda idx, s: received.append((idx, s)))
        player._on_step_executed(5, step)

        assert len(received) == 1
        assert received[0][0] == 5
        assert received[0][1] is step

    def test_on_playback_complete(self, qtbot):
        """Test playback complete resets state."""
        player = MacroPlayer()
        player._state = PlaybackState.PLAYING
        player._current_macro = Macro()
        player._player_thread = MagicMock()

        complete_called = []
        player.playback_complete.connect(lambda: complete_called.append(True))

        player._on_playback_complete()

        assert player._state == PlaybackState.IDLE
        assert player._player_thread is None
        assert player._current_macro is None
        assert len(complete_called) == 1

    def test_on_error(self, qtbot):
        """Test error callback forwards signal."""
        player = MacroPlayer()

        errors = []
        player.error_occurred.connect(errors.append)

        player._on_error("Test error")

        assert errors == ["Test error"]
