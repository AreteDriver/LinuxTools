"""Tests for recording overlay module."""

from unittest.mock import MagicMock, patch

import pytest


class TestRecordingOverlayAvailability:
    """Tests for GTK availability checks."""

    def test_gtk_available_flag_is_bool(self):
        """GTK_AVAILABLE is a boolean."""
        from src import recording_overlay

        assert isinstance(recording_overlay.GTK_AVAILABLE, bool)


class TestRecordingOverlayInit:
    """Tests for RecordingOverlay initialization."""

    def test_init_raises_when_gtk_not_available(self):
        """RecordingOverlay raises RuntimeError when GTK not available."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="GTK not available"):
                recording_overlay.RecordingOverlay(on_stop=lambda: None)

    @pytest.mark.requires_gtk
    def test_init_stores_callbacks(self):
        """RecordingOverlay stores callback and region."""
        from src import recording_overlay

        mock_stop = MagicMock()
        region = (100, 100, 400, 300)

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        # Setup mocks
                        mock_window = MagicMock()
                        mock_gtk.Window.return_value = mock_window
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        overlay = recording_overlay.RecordingOverlay(
                            on_stop=mock_stop, region=region
                        )

        assert overlay.on_stop == mock_stop
        assert overlay.region == region
        assert overlay.elapsed_seconds == 0

    @pytest.mark.requires_gtk
    def test_init_without_region(self):
        """RecordingOverlay initializes without region."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        mock_window = MagicMock()
                        mock_gtk.Window.return_value = mock_window
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        overlay = recording_overlay.RecordingOverlay(
                            on_stop=lambda: None
                        )

        assert overlay.region is None
        assert overlay.border_window is None


@pytest.mark.requires_gtk
class TestRecordingOverlayMethods:
    """Tests for RecordingOverlay methods."""

    @pytest.fixture
    def mock_overlay(self):
        """Create a RecordingOverlay with mocked GTK."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        mock_window = MagicMock()
                        mock_gtk.Window.return_value = mock_window
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        overlay = recording_overlay.RecordingOverlay(
                            on_stop=MagicMock()
                        )
                        overlay._mock_glib = mock_glib
                        yield overlay

    def test_update_timer_increments_seconds(self, mock_overlay):
        """_update_timer increments elapsed_seconds."""
        mock_overlay.timer_label = MagicMock()

        with patch("src.recording_overlay.config") as mock_config:
            mock_config.load_config.return_value = {"gif_max_duration": 60}

            result = mock_overlay._update_timer()

        assert mock_overlay.elapsed_seconds == 1
        assert result is True
        mock_overlay.timer_label.set_text.assert_called_with("00:01")

    def test_update_timer_formats_minutes(self, mock_overlay):
        """_update_timer formats minutes correctly."""
        mock_overlay.elapsed_seconds = 59
        mock_overlay.timer_label = MagicMock()

        with patch("src.recording_overlay.config") as mock_config:
            mock_config.load_config.return_value = {"gif_max_duration": 120}

            mock_overlay._update_timer()

        mock_overlay.timer_label.set_text.assert_called_with("01:00")

    def test_update_timer_stops_at_max_duration(self, mock_overlay):
        """_update_timer stops when max duration reached."""
        mock_overlay.elapsed_seconds = 59
        mock_overlay.timer_label = MagicMock()

        with patch("src.recording_overlay.config") as mock_config:
            mock_config.load_config.return_value = {"gif_max_duration": 60}
            with patch.object(mock_overlay, "_on_stop_clicked") as mock_stop:
                result = mock_overlay._update_timer()

        assert result is False
        mock_stop.assert_called_once_with(None)

    def test_pulse_indicator_toggles_state(self, mock_overlay):
        """_pulse_indicator toggles pulse state."""
        mock_ctx = MagicMock()
        mock_overlay.indicator = MagicMock()
        mock_overlay.indicator.get_style_context.return_value = mock_ctx

        initial_state = mock_overlay.pulse_state

        result = mock_overlay._pulse_indicator()

        assert mock_overlay.pulse_state != initial_state
        assert result is True

    def test_on_stop_clicked_calls_callback(self, mock_overlay):
        """_on_stop_clicked calls on_stop callback."""
        mock_stop = MagicMock()
        mock_overlay.on_stop = mock_stop

        with patch.object(mock_overlay, "destroy"):
            mock_overlay._on_stop_clicked(None)

        mock_stop.assert_called_once()

    def test_destroy_removes_timers(self, mock_overlay):
        """destroy removes timer and pulse callbacks."""
        mock_overlay.timer_id = 1
        mock_overlay.pulse_id = 2
        mock_overlay.border_window = None

        from src import recording_overlay

        with patch.object(recording_overlay, "GLib") as mock_glib:
            mock_overlay.destroy()

        mock_glib.source_remove.assert_any_call(1)
        mock_glib.source_remove.assert_any_call(2)
        assert mock_overlay.timer_id is None
        assert mock_overlay.pulse_id is None

    def test_destroy_with_border_window(self, mock_overlay):
        """destroy destroys border window if present."""
        mock_border = MagicMock()
        mock_overlay.border_window = mock_border
        mock_overlay.timer_id = None
        mock_overlay.pulse_id = None

        mock_overlay.destroy()

        mock_border.destroy.assert_called_once()


@pytest.mark.requires_gtk
class TestRecordingOverlayCSS:
    """Tests for CSS loading."""

    def test_load_css_creates_provider(self):
        """_load_css creates and applies CSS provider."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        mock_window = MagicMock()
                        mock_gtk.Window.return_value = mock_window
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_provider = MagicMock()
                        mock_gtk.CssProvider.return_value = mock_provider

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        recording_overlay.RecordingOverlay(on_stop=lambda: None)

        mock_provider.load_from_data.assert_called()
        mock_gtk.StyleContext.add_provider_for_screen.assert_called()


@pytest.mark.requires_gtk
class TestRecordingOverlayRegionBorder:
    """Tests for region border creation."""

    def test_create_region_border(self):
        """_create_region_border creates border window."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        mock_window = MagicMock()
                        mock_border_window = MagicMock()
                        mock_gtk.Window.side_effect = [mock_window, mock_border_window]
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_border_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        overlay = recording_overlay.RecordingOverlay(
                            on_stop=lambda: None, region=(100, 100, 400, 300)
                        )

        assert overlay.border_window is not None
        mock_border_window.show_all.assert_called()


@pytest.mark.requires_gtk
class TestDrawBorder:
    """Tests for border drawing."""

    def test_draw_border_returns_true(self):
        """_draw_border returns True."""
        from src import recording_overlay

        with patch.object(recording_overlay, "GTK_AVAILABLE", True):
            with patch.object(recording_overlay, "Gtk") as mock_gtk:
                with patch.object(recording_overlay, "Gdk") as mock_gdk:
                    with patch.object(recording_overlay, "GLib") as mock_glib:
                        mock_window = MagicMock()
                        mock_gtk.Window.return_value = mock_window
                        mock_gtk.WindowType.POPUP = "POPUP"
                        mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"

                        mock_screen = MagicMock()
                        mock_window.get_screen.return_value = mock_screen
                        mock_screen.get_rgba_visual.return_value = MagicMock()

                        mock_allocation = MagicMock()
                        mock_allocation.width = 200
                        mock_window.get_allocation.return_value = mock_allocation

                        mock_gdk.Screen.get_default.return_value = MagicMock(
                            get_width=MagicMock(return_value=1920)
                        )

                        mock_glib.timeout_add.return_value = 1

                        overlay = recording_overlay.RecordingOverlay(
                            on_stop=lambda: None
                        )

        mock_cr = MagicMock()
        result = overlay._draw_border(None, mock_cr, 400, 300, 3)

        assert result is True
        mock_cr.set_source_rgba.assert_called()
        mock_cr.rectangle.assert_called()
        mock_cr.stroke.assert_called()
