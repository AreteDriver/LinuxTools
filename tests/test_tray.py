"""Tests for system tray integration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestSystemTrayAvailability:
    """Tests for SystemTray availability checks."""

    def test_is_available_returns_bool(self):
        """is_available returns boolean."""
        from src import tray

        result = tray.SystemTray.is_available()
        assert isinstance(result, bool)

    @patch.dict("src.tray.__dict__", {"APPINDICATOR_AVAILABLE": True})
    def test_is_available_when_appindicator_available(self):
        """is_available returns True when AppIndicator is available."""
        from src import tray

        # Reload to pick up patched value
        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            result = tray.SystemTray.is_available()
        assert result is True

    @patch.dict("src.tray.__dict__", {"APPINDICATOR_AVAILABLE": False})
    def test_is_available_when_appindicator_not_available(self):
        """is_available returns False when AppIndicator is not available."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", False):
            result = tray.SystemTray.is_available()
        assert result is False


class TestSystemTrayInit:
    """Tests for SystemTray initialization."""

    def test_init_raises_when_appindicator_not_available(self):
        """SystemTray raises RuntimeError when AppIndicator not available."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", False):
            with pytest.raises(RuntimeError, match="AppIndicator3 not available"):
                tray.SystemTray(
                    on_show_window=lambda: None,
                    on_fullscreen=lambda: None,
                    on_region=lambda: None,
                    on_window=lambda: None,
                    on_quit=lambda: None,
                )

    @pytest.mark.requires_gtk
    def test_init_stores_callbacks(self):
        """SystemTray stores callback functions."""
        from src import tray

        callbacks = {
            "show": MagicMock(),
            "fullscreen": MagicMock(),
            "region": MagicMock(),
            "window": MagicMock(),
            "quit": MagicMock(),
            "get_queue": MagicMock(return_value=5),
            "edit_queue": MagicMock(),
        }

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_indicator = MagicMock()
                mock_ai.Indicator.new.return_value = mock_indicator
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_menu = MagicMock()
                    mock_gtk.Menu.return_value = mock_menu

                    st = tray.SystemTray(
                        on_show_window=callbacks["show"],
                        on_fullscreen=callbacks["fullscreen"],
                        on_region=callbacks["region"],
                        on_window=callbacks["window"],
                        on_quit=callbacks["quit"],
                        get_queue_count=callbacks["get_queue"],
                        on_edit_queue=callbacks["edit_queue"],
                    )

        assert st._on_show_window == callbacks["show"]
        assert st._on_fullscreen == callbacks["fullscreen"]
        assert st._on_region == callbacks["region"]
        assert st._on_window == callbacks["window"]
        assert st._on_quit == callbacks["quit"]
        assert st._get_queue_count == callbacks["get_queue"]
        assert st._on_edit_queue == callbacks["edit_queue"]


@pytest.mark.requires_gtk
class TestSystemTrayMethods:
    """Tests for SystemTray methods with mocked GTK."""

    @pytest.fixture
    def mock_tray(self):
        """Create a SystemTray with mocked GTK."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_indicator = MagicMock()
                mock_ai.Indicator.new.return_value = mock_indicator
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1
                mock_ai.IndicatorStatus.PASSIVE = 0

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_menu = MagicMock()
                    mock_gtk.Menu.return_value = mock_menu
                    mock_gtk.MenuItem.return_value = MagicMock()
                    mock_gtk.SeparatorMenuItem.return_value = MagicMock()

                    st = tray.SystemTray(
                        on_show_window=MagicMock(),
                        on_fullscreen=MagicMock(),
                        on_region=MagicMock(),
                        on_window=MagicMock(),
                        on_quit=MagicMock(),
                        get_queue_count=MagicMock(return_value=0),
                        on_edit_queue=MagicMock(),
                    )
                    st._mock_ai = mock_ai
                    yield st

    def test_update_queue_count_updates_label(self, mock_tray):
        """update_queue_count updates queue item label."""
        mock_queue_item = MagicMock()
        mock_tray._queue_item = mock_queue_item

        mock_tray.update_queue_count(5)

        mock_queue_item.set_label.assert_called()
        mock_queue_item.set_sensitive.assert_called_with(True)

    def test_update_queue_count_disables_when_zero(self, mock_tray):
        """update_queue_count disables queue item when count is 0."""
        mock_queue_item = MagicMock()
        mock_tray._queue_item = mock_queue_item

        mock_tray.update_queue_count(0)

        mock_queue_item.set_sensitive.assert_called_with(False)

    def test_update_queue_count_skips_when_no_queue_item(self, mock_tray):
        """update_queue_count does nothing when queue item is None."""
        mock_tray._queue_item = None
        # Should not raise
        mock_tray.update_queue_count(5)

    def test_update_visibility_shows_hide_when_visible(self, mock_tray):
        """update_visibility shows 'Hide LikX' when window is visible."""
        mock_show_item = MagicMock()
        mock_tray._show_item = mock_show_item

        mock_tray.update_visibility(True)

        assert mock_tray._window_visible is True
        mock_show_item.set_label.assert_called()

    def test_update_visibility_shows_show_when_hidden(self, mock_tray):
        """update_visibility shows 'Show LikX' when window is hidden."""
        mock_show_item = MagicMock()
        mock_tray._show_item = mock_show_item

        mock_tray.update_visibility(False)

        assert mock_tray._window_visible is False
        mock_show_item.set_label.assert_called()

    def test_update_visibility_skips_when_no_show_item(self, mock_tray):
        """update_visibility does nothing when show item is None."""
        mock_tray._show_item = None
        # Should not raise
        mock_tray.update_visibility(True)

    def test_set_active_true_shows_indicator(self, mock_tray):
        """set_active(True) sets indicator to ACTIVE."""
        mock_indicator = MagicMock()
        mock_tray._indicator = mock_indicator

        from src import tray

        with patch.object(tray, "AppIndicator3") as mock_ai:
            mock_ai.IndicatorStatus.ACTIVE = "ACTIVE"
            mock_tray.set_active(True)

        mock_indicator.set_status.assert_called()

    def test_set_active_false_hides_indicator(self, mock_tray):
        """set_active(False) sets indicator to PASSIVE."""
        mock_indicator = MagicMock()
        mock_tray._indicator = mock_indicator

        from src import tray

        with patch.object(tray, "AppIndicator3") as mock_ai:
            mock_ai.IndicatorStatus.PASSIVE = "PASSIVE"
            mock_tray.set_active(False)

        mock_indicator.set_status.assert_called()

    def test_set_active_skips_when_no_indicator(self, mock_tray):
        """set_active does nothing when indicator is None."""
        mock_tray._indicator = None
        # Should not raise
        mock_tray.set_active(True)


@pytest.mark.requires_gtk
class TestGetIconPath:
    """Tests for _get_icon_path method."""

    def test_get_icon_path_returns_existing_path(self):
        """_get_icon_path returns path when icon exists."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_ai.Indicator.new.return_value = MagicMock()
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_gtk.Menu.return_value = MagicMock()
                    mock_gtk.MenuItem.return_value = MagicMock()
                    mock_gtk.SeparatorMenuItem.return_value = MagicMock()

                    st = tray.SystemTray(
                        on_show_window=lambda: None,
                        on_fullscreen=lambda: None,
                        on_region=lambda: None,
                        on_window=lambda: None,
                        on_quit=lambda: None,
                    )

                    # Mock Path.exists to return True for first location
                    with patch.object(Path, "exists", return_value=True):
                        result = st._get_icon_path()

        assert result is not None

    def test_get_icon_path_returns_none_when_no_icon(self):
        """_get_icon_path returns None when no icon exists."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_ai.Indicator.new.return_value = MagicMock()
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_gtk.Menu.return_value = MagicMock()
                    mock_gtk.MenuItem.return_value = MagicMock()
                    mock_gtk.SeparatorMenuItem.return_value = MagicMock()

                    st = tray.SystemTray(
                        on_show_window=lambda: None,
                        on_fullscreen=lambda: None,
                        on_region=lambda: None,
                        on_window=lambda: None,
                        on_quit=lambda: None,
                    )

                    # Mock Path.exists to return False for all locations
                    with patch.object(Path, "exists", return_value=False):
                        result = st._get_icon_path()

        assert result is None


@pytest.mark.requires_gtk
class TestCreateMenu:
    """Tests for _create_menu method."""

    def test_create_menu_creates_menu_items(self):
        """_create_menu creates expected menu items."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_ai.Indicator.new.return_value = MagicMock()
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_menu = MagicMock()
                    mock_gtk.Menu.return_value = mock_menu
                    mock_menu_item = MagicMock()
                    mock_gtk.MenuItem.return_value = mock_menu_item
                    mock_gtk.SeparatorMenuItem.return_value = MagicMock()

                    tray.SystemTray(
                        on_show_window=lambda: None,
                        on_fullscreen=lambda: None,
                        on_region=lambda: None,
                        on_window=lambda: None,
                        on_quit=lambda: None,
                    )

        # Menu should have items appended
        assert mock_menu.append.called
        # Menu should be shown
        mock_menu.show_all.assert_called_once()

    def test_create_menu_with_queue_functions(self):
        """_create_menu adds queue item when queue functions provided."""
        from src import tray

        with patch.object(tray, "APPINDICATOR_AVAILABLE", True):
            with patch.object(tray, "AppIndicator3") as mock_ai:
                mock_ai.Indicator.new.return_value = MagicMock()
                mock_ai.IndicatorCategory.APPLICATION_STATUS = 0
                mock_ai.IndicatorStatus.ACTIVE = 1

                with patch.object(tray, "Gtk") as mock_gtk:
                    mock_menu = MagicMock()
                    mock_gtk.Menu.return_value = mock_menu
                    mock_menu_item = MagicMock()
                    mock_gtk.MenuItem.return_value = mock_menu_item
                    mock_gtk.SeparatorMenuItem.return_value = MagicMock()

                    st = tray.SystemTray(
                        on_show_window=lambda: None,
                        on_fullscreen=lambda: None,
                        on_region=lambda: None,
                        on_window=lambda: None,
                        on_quit=lambda: None,
                        get_queue_count=lambda: 0,
                        on_edit_queue=lambda: None,
                    )

        # Queue item should be set
        assert st._queue_item is not None


class TestModuleImports:
    """Tests for module-level import behavior."""

    def test_gtk_not_available_flag(self):
        """GTK_AVAILABLE flag is set based on import success."""
        from src import tray

        # The flag should be a boolean
        assert isinstance(tray.GTK_AVAILABLE, bool)

    def test_appindicator_not_available_flag(self):
        """APPINDICATOR_AVAILABLE flag is set based on import success."""
        from src import tray

        # The flag should be a boolean
        assert isinstance(tray.APPINDICATOR_AVAILABLE, bool)
