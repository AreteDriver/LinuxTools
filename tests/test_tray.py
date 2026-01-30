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


class TestSystemTraySourceInspection:
    """Test SystemTray implementation via source inspection."""

    def test_init_stores_callbacks(self):
        """Test __init__ stores callback references."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.__init__)
        assert "self._on_show_window = on_show_window" in source
        assert "self._on_fullscreen = on_fullscreen" in source
        assert "self._on_region = on_region" in source
        assert "self._on_window = on_window" in source
        assert "self._on_quit = on_quit" in source

    def test_init_stores_optional_callbacks(self):
        """Test __init__ stores optional callbacks."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.__init__)
        assert "self._get_queue_count = get_queue_count" in source
        assert "self._on_edit_queue = on_edit_queue" in source

    def test_init_initializes_state(self):
        """Test __init__ initializes state variables."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.__init__)
        assert "self._indicator = None" in source
        assert "self._menu = None" in source
        assert "self._queue_item = None" in source
        assert "self._show_item = None" in source
        assert "self._window_visible = True" in source

    def test_init_creates_indicator(self):
        """Test __init__ calls _create_indicator."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.__init__)
        assert "self._create_indicator()" in source

    def test_create_indicator_structure(self):
        """Test _create_indicator creates indicator."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_indicator)
        assert "Indicator.new" in source
        assert "likx" in source
        assert "set_status" in source
        assert "set_title" in source

    def test_create_indicator_uses_icon_path(self):
        """Test _create_indicator uses icon path."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_indicator)
        assert "_get_icon_path" in source
        assert "camera-photo" in source  # Fallback icon

    def test_create_indicator_sets_menu(self):
        """Test _create_indicator sets menu."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_indicator)
        assert "_create_menu" in source
        assert "set_menu" in source

    def test_get_icon_path_checks_locations(self):
        """Test _get_icon_path checks multiple locations."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._get_icon_path)
        assert "locations" in source
        assert "exists()" in source

    def test_get_icon_path_returns_string_or_none(self):
        """Test _get_icon_path returns string or None."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._get_icon_path)
        assert "return str(loc)" in source
        assert "return None" in source

    def test_create_menu_creates_gtk_menu(self):
        """Test _create_menu creates Gtk.Menu."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "Gtk.Menu()" in source
        assert "Gtk.MenuItem" in source

    def test_create_menu_adds_show_item(self):
        """Test _create_menu adds show/hide item."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "self._show_item" in source

    def test_create_menu_adds_capture_options(self):
        """Test _create_menu adds capture options."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "fullscreen_item" in source
        assert "region_item" in source
        assert "window_item" in source

    def test_create_menu_adds_quit_item(self):
        """Test _create_menu adds quit item."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "quit_item" in source
        assert "_on_quit" in source

    def test_create_menu_adds_queue_item_conditionally(self):
        """Test _create_menu adds queue item if callbacks provided."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "self._queue_item" in source
        assert "_get_queue_count" in source
        assert "_on_edit_queue" in source

    def test_create_menu_connects_handlers(self):
        """Test _create_menu connects signal handlers."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "connect" in source
        assert "activate" in source

    def test_create_menu_shows_all(self):
        """Test _create_menu shows all items."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "show_all()" in source

    def test_update_queue_count_checks_item(self):
        """Test update_queue_count checks queue item exists."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_queue_count)
        assert "if self._queue_item" in source

    def test_update_queue_count_updates_label(self):
        """Test update_queue_count updates label text."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_queue_count)
        assert "set_label" in source
        assert "count" in source

    def test_update_queue_count_sets_sensitivity(self):
        """Test update_queue_count sets sensitivity based on count."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_queue_count)
        assert "set_sensitive" in source
        assert "count > 0" in source

    def test_update_visibility_stores_state(self):
        """Test update_visibility stores visibility state."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_visibility)
        assert "self._window_visible = window_visible" in source

    def test_update_visibility_updates_label(self):
        """Test update_visibility updates show/hide label."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_visibility)
        assert "set_label" in source

    def test_set_active_checks_indicator(self):
        """Test set_active checks indicator exists."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.set_active)
        assert "if self._indicator" in source

    def test_set_active_changes_status(self):
        """Test set_active changes indicator status."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.set_active)
        assert "set_status" in source
        assert "ACTIVE" in source
        assert "PASSIVE" in source

    def test_is_available_returns_flag(self):
        """Test is_available returns APPINDICATOR_AVAILABLE."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.is_available)
        assert "APPINDICATOR_AVAILABLE" in source


class TestTrayClassStructure:
    """Test SystemTray class structure."""

    def test_class_has_required_methods(self):
        """Test that SystemTray has required methods."""
        from src.tray import SystemTray

        assert hasattr(SystemTray, "update_queue_count")
        assert hasattr(SystemTray, "update_visibility")
        assert hasattr(SystemTray, "set_active")
        assert hasattr(SystemTray, "is_available")

    def test_class_has_private_methods(self):
        """Test that SystemTray has private methods."""
        from src.tray import SystemTray

        assert hasattr(SystemTray, "_create_indicator")
        assert hasattr(SystemTray, "_get_icon_path")
        assert hasattr(SystemTray, "_create_menu")

    def test_is_available_is_static(self):
        """Test that is_available is a static method."""
        from src.tray import SystemTray

        result = SystemTray.is_available()
        assert isinstance(result, bool)


class TestTrayI18n:
    """Test that tray uses internationalization."""

    def test_imports_i18n(self):
        """Test that tray imports i18n."""
        import inspect

        from src import tray

        source = inspect.getsource(tray)
        assert "from .i18n import _" in source or "from src.i18n import _" in source

    def test_uses_translation_function(self):
        """Test module uses _() translation function."""
        import inspect

        from src import tray

        source = inspect.getsource(tray)
        assert '_("' in source

    def test_menu_items_translated(self):
        """Test menu item labels use translation."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "_(" in source


class TestTrayIconPaths:
    """Test icon path handling."""

    def test_get_icon_path_uses_pathlib(self):
        """Test _get_icon_path uses pathlib.Path."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._get_icon_path)
        assert "Path" in source

    def test_get_icon_path_checks_resources(self):
        """Test _get_icon_path checks resources directory."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._get_icon_path)
        assert "resources" in source

    def test_get_icon_path_checks_system_paths(self):
        """Test _get_icon_path checks system icon paths."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._get_icon_path)
        assert "/usr/share/icons" in source or "/usr/share/pixmaps" in source


class TestTrayAppIndicatorFallback:
    """Test AppIndicator fallback to AyatanaAppIndicator."""

    def test_module_tries_appindicator3(self):
        """Test module tries AppIndicator3 first."""
        import inspect

        from src import tray

        source = inspect.getsource(tray)
        assert "AppIndicator3" in source

    def test_module_falls_back_to_ayatana(self):
        """Test module falls back to AyatanaAppIndicator3."""
        import inspect

        from src import tray

        source = inspect.getsource(tray)
        assert "AyatanaAppIndicator3" in source


class TestTrayEdgeCases:
    """Test edge cases and error handling."""

    def test_requires_appindicator(self):
        """Test SystemTray raises error without AppIndicator."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.__init__)
        assert "APPINDICATOR_AVAILABLE" in source
        assert "RuntimeError" in source

    def test_queue_item_optional(self):
        """Test queue item is optional based on callbacks."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "if self._get_queue_count and self._on_edit_queue" in source

    def test_update_queue_count_handles_missing_item(self):
        """Test update_queue_count handles missing queue item."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_queue_count)
        assert "if self._queue_item" in source

    def test_update_visibility_handles_missing_show_item(self):
        """Test update_visibility handles missing show item."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.update_visibility)
        assert "if self._show_item" in source

    def test_set_active_handles_missing_indicator(self):
        """Test set_active handles missing indicator."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray.set_active)
        assert "if self._indicator" in source


class TestTrayMenuSeparators:
    """Test menu structure with separators."""

    def test_menu_has_separators(self):
        """Test menu includes separator items."""
        import inspect

        from src.tray import SystemTray

        source = inspect.getsource(SystemTray._create_menu)
        assert "SeparatorMenuItem" in source
