"""Tests for scroll capture overlay module."""

from unittest.mock import MagicMock, patch

import pytest


class TestScrollCaptureOverlayAvailability:
    """Tests for GTK availability checks."""

    def test_gtk_available_flag_is_bool(self):
        """GTK_AVAILABLE is a boolean."""
        from src import scroll_overlay

        assert isinstance(scroll_overlay.GTK_AVAILABLE, bool)


class TestScrollCaptureOverlayInit:
    """Tests for ScrollCaptureOverlay initialization."""

    def test_init_raises_when_gtk_not_available(self):
        """ScrollCaptureOverlay raises RuntimeError when GTK not available."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="GTK not available"):
                scroll_overlay.ScrollCaptureOverlay(on_stop=lambda: None)

    @pytest.mark.requires_gtk
    def test_init_stores_callbacks(self):
        """ScrollCaptureOverlay stores callback and region."""
        from src import scroll_overlay

        mock_stop = MagicMock()
        region = (100, 100, 400, 300)

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    # Setup mocks
                    mock_window = MagicMock()
                    mock_gtk.Window.return_value = mock_window
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

                    mock_screen = MagicMock()
                    mock_window.get_screen.return_value = mock_screen
                    mock_screen.get_rgba_visual.return_value = MagicMock()

                    mock_allocation = MagicMock()
                    mock_allocation.width = 200
                    mock_window.get_allocation.return_value = mock_allocation

                    mock_gdk.Screen.get_default.return_value = MagicMock(
                        get_width=MagicMock(return_value=1920)
                    )

                    overlay = scroll_overlay.ScrollCaptureOverlay(on_stop=mock_stop, region=region)

        assert overlay.on_stop == mock_stop
        assert overlay.region == region
        assert overlay.frame_count == 0
        assert overlay.estimated_height == 0

    @pytest.mark.requires_gtk
    def test_init_without_region(self):
        """ScrollCaptureOverlay initializes without region."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    mock_window = MagicMock()
                    mock_gtk.Window.return_value = mock_window
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

                    mock_screen = MagicMock()
                    mock_window.get_screen.return_value = mock_screen
                    mock_screen.get_rgba_visual.return_value = MagicMock()

                    mock_allocation = MagicMock()
                    mock_allocation.width = 200
                    mock_window.get_allocation.return_value = mock_allocation

                    mock_gdk.Screen.get_default.return_value = MagicMock(
                        get_width=MagicMock(return_value=1920)
                    )

                    overlay = scroll_overlay.ScrollCaptureOverlay(on_stop=lambda: None)

        assert overlay.region is None
        assert overlay.border_window is None


@pytest.mark.requires_gtk
class TestScrollCaptureOverlayMethods:
    """Tests for ScrollCaptureOverlay methods."""

    @pytest.fixture
    def mock_overlay(self):
        """Create a ScrollCaptureOverlay with mocked GTK."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    mock_window = MagicMock()
                    mock_gtk.Window.return_value = mock_window
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

                    mock_screen = MagicMock()
                    mock_window.get_screen.return_value = mock_screen
                    mock_screen.get_rgba_visual.return_value = MagicMock()

                    mock_allocation = MagicMock()
                    mock_allocation.width = 200
                    mock_window.get_allocation.return_value = mock_allocation

                    mock_gdk.Screen.get_default.return_value = MagicMock(
                        get_width=MagicMock(return_value=1920)
                    )

                    overlay = scroll_overlay.ScrollCaptureOverlay(on_stop=MagicMock())
                    yield overlay

    def test_update_progress_updates_labels(self, mock_overlay):
        """update_progress updates frame and height labels."""
        mock_overlay.frame_label = MagicMock()
        mock_overlay.height_label = MagicMock()

        mock_overlay.update_progress(5, 800)

        assert mock_overlay.frame_count == 5
        assert mock_overlay.estimated_height == 800
        mock_overlay.frame_label.set_text.assert_called()
        mock_overlay.height_label.set_text.assert_called()

    def test_update_progress_formats_large_height(self, mock_overlay):
        """update_progress formats height in k px for large values."""
        mock_overlay.frame_label = MagicMock()
        mock_overlay.height_label = MagicMock()

        mock_overlay.update_progress(10, 2500)

        # Should format as "2.5k px"
        call_args = mock_overlay.height_label.set_text.call_args[0][0]
        assert "2.5k" in call_args or "2500" in call_args

    def test_update_progress_small_height(self, mock_overlay):
        """update_progress shows px for small heights."""
        mock_overlay.frame_label = MagicMock()
        mock_overlay.height_label = MagicMock()

        mock_overlay.update_progress(3, 500)

        call_args = mock_overlay.height_label.set_text.call_args[0][0]
        assert "500" in call_args

    def test_on_stop_clicked_calls_callback(self, mock_overlay):
        """_on_stop_clicked calls on_stop callback."""
        mock_stop = MagicMock()
        mock_overlay.on_stop = mock_stop

        mock_overlay._on_stop_clicked(None)

        mock_stop.assert_called_once()

    def test_destroy_destroys_window(self, mock_overlay):
        """destroy destroys main window."""
        mock_overlay.border_window = None

        mock_overlay.destroy()

        mock_overlay.window.destroy.assert_called_once()

    def test_destroy_with_border_window(self, mock_overlay):
        """destroy destroys border window if present."""
        mock_border = MagicMock()
        mock_overlay.border_window = mock_border

        mock_overlay.destroy()

        mock_border.destroy.assert_called_once()
        mock_overlay.window.destroy.assert_called_once()


@pytest.mark.requires_gtk
class TestScrollCaptureOverlayCSS:
    """Tests for CSS loading."""

    def test_load_css_creates_provider(self):
        """_load_css creates and applies CSS provider."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    mock_window = MagicMock()
                    mock_gtk.Window.return_value = mock_window
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

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

                    scroll_overlay.ScrollCaptureOverlay(on_stop=lambda: None)

        mock_provider.load_from_data.assert_called()
        mock_gtk.StyleContext.add_provider_for_screen.assert_called()


@pytest.mark.requires_gtk
class TestScrollCaptureOverlayRegionBorder:
    """Tests for region border creation."""

    def test_create_region_border(self):
        """_create_region_border creates border window."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    mock_window = MagicMock()
                    mock_border_window = MagicMock()
                    mock_gtk.Window.side_effect = [mock_window, mock_border_window]
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

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

                    overlay = scroll_overlay.ScrollCaptureOverlay(
                        on_stop=lambda: None, region=(100, 100, 400, 300)
                    )

        assert overlay.border_window is not None
        mock_border_window.show_all.assert_called()


@pytest.mark.requires_gtk
class TestScrollDrawBorder:
    """Tests for border drawing."""

    def test_draw_border_returns_true(self):
        """_draw_border returns True."""
        from src import scroll_overlay

        with patch.object(scroll_overlay, "GTK_AVAILABLE", True):
            with patch.object(scroll_overlay, "Gtk") as mock_gtk:
                with patch.object(scroll_overlay, "Gdk") as mock_gdk:
                    mock_window = MagicMock()
                    mock_border_window = MagicMock()
                    mock_gtk.Window.side_effect = [mock_window, mock_border_window]
                    mock_gtk.WindowType.POPUP = "POPUP"
                    mock_gtk.Orientation.HORIZONTAL = "HORIZONTAL"
                    mock_gtk.Orientation.VERTICAL = "VERTICAL"

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

                    overlay = scroll_overlay.ScrollCaptureOverlay(
                        on_stop=lambda: None, region=(100, 100, 400, 300)
                    )

        mock_cr = MagicMock()
        result = overlay._draw_border(None, mock_cr)

        assert result is True
        mock_cr.set_source_rgba.assert_called()
        mock_cr.rectangle.assert_called()
        mock_cr.stroke.assert_called()
