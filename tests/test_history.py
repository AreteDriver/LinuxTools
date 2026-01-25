"""Tests for the history module."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestHistoryModuleImport:
    """Test history module imports."""

    def test_module_imports(self):
        """Test that history module imports successfully."""
        from src import history

        assert hasattr(history, "HistoryEntry")
        assert hasattr(history, "HistoryManager")
        assert hasattr(history, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.history import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestHistoryEntry:
    """Test HistoryEntry class."""

    def test_entry_init(self):
        """Test HistoryEntry initialization."""
        from src.history import HistoryEntry

        filepath = Path("/tmp/test.png")
        timestamp = datetime.now()
        entry = HistoryEntry(filepath, timestamp, "fullscreen")

        assert entry.filepath == filepath
        assert entry.timestamp == timestamp
        assert entry.mode == "fullscreen"
        assert entry.thumbnail is None

    def test_entry_default_mode(self):
        """Test HistoryEntry default mode is 'unknown'."""
        from src.history import HistoryEntry

        entry = HistoryEntry(Path("/tmp/test.png"), datetime.now())
        assert entry.mode == "unknown"

    def test_entry_to_dict(self):
        """Test HistoryEntry.to_dict() method."""
        from src.history import HistoryEntry

        filepath = Path("/tmp/test.png")
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        entry = HistoryEntry(filepath, timestamp, "region")

        result = entry.to_dict()

        assert result["filepath"] == "/tmp/test.png"
        assert result["timestamp"] == "2024-01-15T10:30:00"
        assert result["mode"] == "region"

    def test_entry_from_dict(self):
        """Test HistoryEntry.from_dict() method."""
        from src.history import HistoryEntry

        data = {
            "filepath": "/home/user/screenshot.png",
            "timestamp": "2024-03-20T14:45:30",
            "mode": "window",
        }

        entry = HistoryEntry.from_dict(data)

        assert entry.filepath == Path("/home/user/screenshot.png")
        assert entry.timestamp == datetime(2024, 3, 20, 14, 45, 30)
        assert entry.mode == "window"

    def test_entry_from_dict_missing_mode(self):
        """Test HistoryEntry.from_dict() with missing mode defaults to 'unknown'."""
        from src.history import HistoryEntry

        data = {
            "filepath": "/tmp/test.png",
            "timestamp": "2024-01-01T00:00:00",
        }

        entry = HistoryEntry.from_dict(data)
        assert entry.mode == "unknown"

    def test_entry_roundtrip(self):
        """Test HistoryEntry to_dict/from_dict roundtrip."""
        from src.history import HistoryEntry

        original = HistoryEntry(
            Path("/tmp/screenshot.png"),
            datetime(2024, 6, 15, 12, 0, 0),
            "fullscreen",
        )

        data = original.to_dict()
        restored = HistoryEntry.from_dict(data)

        assert restored.filepath == original.filepath
        assert restored.timestamp == original.timestamp
        assert restored.mode == original.mode


class TestHistoryManager:
    """Test HistoryManager class."""

    def test_manager_init(self):
        """Test HistoryManager initialization."""
        from src.history import HistoryManager

        with patch("src.history.config.get_config_dir") as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())
            manager = HistoryManager()

            assert manager.entries == []
            assert manager.history_file.name == "history.json"

    def test_manager_has_load_method(self):
        """Test HistoryManager has load method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "load")
        assert callable(getattr(HistoryManager, "load"))

    def test_manager_has_save_method(self):
        """Test HistoryManager has save method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "save")
        assert callable(getattr(HistoryManager, "save"))

    def test_manager_has_add_method(self):
        """Test HistoryManager has add method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "add")
        assert callable(getattr(HistoryManager, "add"))

    def test_manager_has_remove_method(self):
        """Test HistoryManager has remove method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "remove")
        assert callable(getattr(HistoryManager, "remove"))

    def test_manager_has_clear_method(self):
        """Test HistoryManager has clear method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "clear")
        assert callable(getattr(HistoryManager, "clear"))

    def test_manager_has_get_recent_method(self):
        """Test HistoryManager has get_recent method."""
        from src.history import HistoryManager

        assert hasattr(HistoryManager, "get_recent")
        assert callable(getattr(HistoryManager, "get_recent"))


class TestHistoryManagerOperations:
    """Test HistoryManager operations with mocked file system."""

    def test_add_entry(self):
        """Test adding entry to history."""
        from src.history import HistoryEntry, HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    # Create a temp file that exists
                    test_file = config_dir / "test.png"
                    test_file.touch()

                    manager.add(test_file, "fullscreen")

                    assert len(manager.entries) == 1
                    assert manager.entries[0].filepath == test_file
                    assert manager.entries[0].mode == "fullscreen"

    def test_add_entry_limits_to_100(self):
        """Test that history is limited to 100 entries."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    # Add 110 entries
                    for i in range(110):
                        test_file = config_dir / f"test_{i}.png"
                        test_file.touch()
                        manager.add(test_file, "test")

                    assert len(manager.entries) <= 100

    def test_get_recent_default_limit(self):
        """Test get_recent with default limit."""
        from src.history import HistoryEntry, HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    # Add 30 entries
                    for i in range(30):
                        test_file = config_dir / f"test_{i}.png"
                        test_file.touch()
                        manager.add(test_file, "test")

                    recent = manager.get_recent()
                    assert len(recent) == 20  # Default limit

    def test_get_recent_custom_limit(self):
        """Test get_recent with custom limit."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    for i in range(10):
                        test_file = config_dir / f"test_{i}.png"
                        test_file.touch()
                        manager.add(test_file, "test")

                    recent = manager.get_recent(limit=5)
                    assert len(recent) == 5

    def test_clear_history(self):
        """Test clearing history."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    test_file = config_dir / "test.png"
                    test_file.touch()
                    manager.add(test_file, "test")
                    assert len(manager.entries) > 0

                    manager.clear()
                    assert len(manager.entries) == 0

    def test_load_filters_deleted_files(self):
        """Test that load() filters out entries for deleted files."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            history_file = config_dir / "history.json"

            # Write history with a non-existent file
            history_data = [
                {
                    "filepath": "/nonexistent/file.png",
                    "timestamp": "2024-01-01T00:00:00",
                    "mode": "test",
                }
            ]
            with open(history_file, "w") as f:
                json.dump(history_data, f)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                manager = HistoryManager()
                # Entry should be filtered out since file doesn't exist
                assert len(manager.entries) == 0

    def test_load_handles_corrupt_json(self):
        """Test that load() handles corrupt JSON gracefully."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            history_file = config_dir / "history.json"

            # Write invalid JSON
            with open(history_file, "w") as f:
                f.write("{ invalid json }")

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                manager = HistoryManager()
                # Should gracefully handle error
                assert manager.entries == []


class TestHistoryWindowClass:
    """Test HistoryWindow class structure."""

    def test_class_exists(self):
        """Test HistoryWindow class exists."""
        from src.history import HistoryWindow

        assert HistoryWindow is not None

    def test_gtk_check_in_init(self):
        """Test that HistoryWindow checks GTK_AVAILABLE in init."""
        from src.history import HistoryWindow
        import inspect

        source = inspect.getsource(HistoryWindow.__init__)
        assert "GTK_AVAILABLE" in source or "RuntimeError" in source

    def test_class_has_create_toolbar_method(self):
        """Test HistoryWindow has _create_toolbar method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_create_toolbar")

    def test_class_has_load_history_method(self):
        """Test HistoryWindow has _load_history method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_load_history")

    def test_class_has_on_item_activated_method(self):
        """Test HistoryWindow has _on_item_activated method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_on_item_activated")

    def test_class_has_on_delete_method(self):
        """Test HistoryWindow has _on_delete method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_on_delete")

    def test_class_has_on_clear_all_method(self):
        """Test HistoryWindow has _on_clear_all method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_on_clear_all")

    def test_class_has_on_open_folder_method(self):
        """Test HistoryWindow has _on_open_folder method."""
        from src.history import HistoryWindow

        assert hasattr(HistoryWindow, "_on_open_folder")


class TestHistoryManagerRemove:
    """Test HistoryManager.remove() method."""

    def test_remove_existing_entry(self):
        """Test removing an existing entry."""
        from src.history import HistoryEntry, HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    test_file = config_dir / "test.png"
                    test_file.touch()
                    manager.add(test_file, "fullscreen")

                    assert len(manager.entries) == 1
                    entry = manager.entries[0]

                    manager.remove(entry)
                    assert len(manager.entries) == 0

    def test_remove_nonexistent_entry(self):
        """Test removing an entry that isn't in the list."""
        from src.history import HistoryEntry, HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    # Create an entry that's not in the manager
                    fake_entry = HistoryEntry(Path("/fake/file.png"), datetime.now())

                    # Should not raise an error
                    manager.remove(fake_entry)
                    assert len(manager.entries) == 0


class TestHistoryManagerSaveLoad:
    """Test HistoryManager save/load cycle."""

    def test_save_creates_file(self):
        """Test that save() creates the history file."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    test_file = config_dir / "test.png"
                    test_file.touch()
                    manager.add(test_file, "region")

                    # Verify the history file was created
                    assert manager.history_file.exists()

    def test_save_load_roundtrip(self):
        """Test that saved data can be loaded correctly."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    # Create manager and add entries
                    manager1 = HistoryManager()

                    test_file1 = config_dir / "test1.png"
                    test_file1.touch()
                    test_file2 = config_dir / "test2.png"
                    test_file2.touch()

                    manager1.add(test_file1, "fullscreen")
                    manager1.add(test_file2, "region")

                    # Create new manager to load the saved data
                    manager2 = HistoryManager()

                    assert len(manager2.entries) == 2
                    # Most recent first
                    assert manager2.entries[0].filepath == test_file2
                    assert manager2.entries[1].filepath == test_file1

    def test_load_empty_file(self):
        """Test loading from empty history file."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            history_file = config_dir / "history.json"

            # Create empty JSON array
            with open(history_file, "w") as f:
                json.dump([], f)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                manager = HistoryManager()
                assert manager.entries == []

    def test_load_valid_entries(self):
        """Test loading valid history entries."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            history_file = config_dir / "history.json"

            # Create a test file that exists
            test_file = config_dir / "existing.png"
            test_file.touch()

            # Write valid history data
            history_data = [
                {
                    "filepath": str(test_file),
                    "timestamp": "2024-06-15T12:00:00",
                    "mode": "window",
                }
            ]
            with open(history_file, "w") as f:
                json.dump(history_data, f)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                manager = HistoryManager()
                assert len(manager.entries) == 1
                assert manager.entries[0].mode == "window"

    def test_save_handles_oserror(self):
        """Test that save() handles OSError gracefully."""
        from src.history import HistoryManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)

            with patch("src.history.config.get_config_dir", return_value=config_dir):
                with patch("src.history.config.ensure_config_dir"):
                    manager = HistoryManager()

                    # Mock open to raise OSError
                    with patch("builtins.open", side_effect=OSError("Permission denied")):
                        # Should not raise
                        manager.save()


class TestHistoryEntryEdgeCases:
    """Test HistoryEntry edge cases."""

    def test_entry_with_special_characters_in_path(self):
        """Test HistoryEntry with special characters in filepath."""
        from src.history import HistoryEntry

        filepath = Path("/tmp/test file (1) [copy].png")
        entry = HistoryEntry(filepath, datetime.now(), "fullscreen")

        data = entry.to_dict()
        restored = HistoryEntry.from_dict(data)

        assert restored.filepath == filepath

    def test_entry_with_unicode_path(self):
        """Test HistoryEntry with unicode characters in filepath."""
        from src.history import HistoryEntry

        filepath = Path("/tmp/截图_日本語.png")
        entry = HistoryEntry(filepath, datetime.now(), "region")

        data = entry.to_dict()
        restored = HistoryEntry.from_dict(data)

        assert restored.filepath == filepath

    def test_entry_timestamp_precision(self):
        """Test HistoryEntry preserves timestamp precision."""
        from src.history import HistoryEntry

        # Timestamp with microseconds
        timestamp = datetime(2024, 6, 15, 12, 30, 45, 123456)
        entry = HistoryEntry(Path("/tmp/test.png"), timestamp, "test")

        data = entry.to_dict()
        restored = HistoryEntry.from_dict(data)

        # isoformat preserves microseconds
        assert restored.timestamp == timestamp


# =============================================================================
# Functional Tests (with temp files and GTK)
# =============================================================================


class TestHistoryManagerFunctional:
    """Functional tests for HistoryManager with real files."""

    @pytest.fixture
    def temp_config(self, tmp_path):
        """Set up temporary config directory."""
        from src import config

        original_dir = config.get_config_dir()

        # Patch config dir
        with patch.object(config, "get_config_dir", return_value=tmp_path):
            with patch.object(config, "ensure_config_dir", return_value=None):
                yield tmp_path

    def test_manager_init_creates_empty_history(self, temp_config):
        """Test HistoryManager initializes with empty history."""
        from src.history import HistoryManager

        manager = HistoryManager()

        assert manager.entries == []
        assert manager.history_file == temp_config / "history.json"

    def test_manager_add_entry(self, temp_config, tmp_path):
        """Test adding an entry to history."""
        from src.history import HistoryManager

        # Create a real file
        test_file = tmp_path / "test_screenshot.png"
        test_file.write_bytes(b"fake image data")

        manager = HistoryManager()
        manager.add(test_file, mode="fullscreen")

        assert len(manager.entries) == 1
        assert manager.entries[0].filepath == test_file
        assert manager.entries[0].mode == "fullscreen"

    def test_manager_save_and_load(self, temp_config, tmp_path):
        """Test saving and loading history."""
        from src.history import HistoryManager

        # Create real files
        file1 = tmp_path / "screenshot1.png"
        file2 = tmp_path / "screenshot2.png"
        file1.write_bytes(b"fake1")
        file2.write_bytes(b"fake2")

        # Add entries
        manager1 = HistoryManager()
        manager1.add(file1, mode="fullscreen")
        manager1.add(file2, mode="region")

        # Load in new manager
        manager2 = HistoryManager()

        assert len(manager2.entries) == 2
        # Most recent first
        assert manager2.entries[0].filepath == file2
        assert manager2.entries[1].filepath == file1

    def test_manager_filters_deleted_files(self, temp_config, tmp_path):
        """Test that load filters out deleted files."""
        from src.history import HistoryManager

        # Create file, add to history, then delete
        test_file = tmp_path / "deleted.png"
        test_file.write_bytes(b"fake")

        manager1 = HistoryManager()
        manager1.add(test_file, mode="test")

        # Delete file
        test_file.unlink()

        # Load fresh manager
        manager2 = HistoryManager()

        # Should have filtered out deleted file
        assert len(manager2.entries) == 0

    def test_manager_remove_entry(self, temp_config, tmp_path):
        """Test removing an entry."""
        from src.history import HistoryManager

        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake")

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        assert len(manager.entries) == 1

        entry = manager.entries[0]
        manager.remove(entry)

        assert len(manager.entries) == 0

    def test_manager_clear(self, temp_config, tmp_path):
        """Test clearing all history."""
        from src.history import HistoryManager

        # Add multiple entries
        for i in range(5):
            f = tmp_path / f"test{i}.png"
            f.write_bytes(b"fake")
            manager = HistoryManager()
            manager.add(f, mode="test")

        manager = HistoryManager()
        assert len(manager.entries) > 0

        manager.clear()

        assert len(manager.entries) == 0

    def test_manager_get_recent(self, temp_config, tmp_path):
        """Test get_recent with limit."""
        from src.history import HistoryManager

        # Add 10 entries
        manager = HistoryManager()
        for i in range(10):
            f = tmp_path / f"test{i}.png"
            f.write_bytes(b"fake")
            manager.add(f, mode="test")

        recent = manager.get_recent(limit=5)

        assert len(recent) == 5

    def test_manager_limits_to_100_entries(self, temp_config, tmp_path):
        """Test that history is limited to 100 entries."""
        from src.history import HistoryManager

        manager = HistoryManager()

        # Add 110 entries
        for i in range(110):
            f = tmp_path / f"test{i}.png"
            f.write_bytes(b"fake")
            manager.add(f, mode="test")

        assert len(manager.entries) == 100

    def test_manager_handles_corrupt_json(self, temp_config):
        """Test manager handles corrupt history file."""
        from src.history import HistoryManager

        # Write corrupt JSON
        history_file = temp_config / "history.json"
        history_file.write_text("not valid json {{{")

        manager = HistoryManager()

        # Should have empty history, not crash
        assert manager.entries == []


class TestHistoryWindowFunctional:
    """Functional tests for HistoryWindow with GTK."""

    @pytest.fixture
    def gtk_setup(self):
        """Set up GTK for testing."""
        from src.history import GTK_AVAILABLE
        if not GTK_AVAILABLE:
            pytest.skip("GTK not available")

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        return {"Gtk": Gtk}

    @pytest.fixture
    def temp_config(self, tmp_path):
        """Set up temporary config directory."""
        from src import config

        with patch.object(config, "get_config_dir", return_value=tmp_path):
            with patch.object(config, "ensure_config_dir", return_value=None):
                yield tmp_path

    def test_create_history_window(self, gtk_setup, temp_config):
        """Test creating a HistoryWindow instance."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        assert window is not None
        assert window.window is not None
        assert window.icon_view is not None
        assert window.store is not None
        assert window.manager is not None

    def test_history_window_with_parent(self, gtk_setup, temp_config):
        """Test creating HistoryWindow with parent."""
        from src.history import HistoryWindow
        Gtk = gtk_setup["Gtk"]

        parent = Gtk.Window()
        window = HistoryWindow(parent=parent)

        assert window.window.get_transient_for() == parent

    def test_history_window_toolbar_created(self, gtk_setup, temp_config):
        """Test that toolbar is created."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        # Window should have children
        children = window.window.get_children()
        assert len(children) > 0

    def test_history_window_load_history(self, gtk_setup, temp_config, tmp_path):
        """Test _load_history populates store."""
        from src.history import HistoryWindow

        # Create a real image file
        test_file = tmp_path / "test.png"
        # Create minimal valid PNG
        import struct
        import zlib

        def create_minimal_png():
            signature = b'\x89PNG\r\n\x1a\n'

            # IHDR chunk
            width = struct.pack('>I', 1)
            height = struct.pack('>I', 1)
            ihdr_data = width + height + b'\x08\x02\x00\x00\x00'
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc

            # IDAT chunk (1x1 red pixel)
            raw_data = b'\x00\xff\x00\x00'
            compressed = zlib.compress(raw_data)
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
            idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc

            # IEND chunk
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc

            return signature + ihdr + idat + iend

        test_file.write_bytes(create_minimal_png())

        # Add to history
        from src.history import HistoryManager
        manager = HistoryManager()
        manager.add(test_file, mode="test")

        # Create window (loads history)
        window = HistoryWindow()

        # Store should have the entry
        assert len(window.store) == 1

    def test_history_window_statusbar(self, gtk_setup, temp_config):
        """Test statusbar shows count."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        assert window.statusbar is not None

    def test_on_item_activated(self, gtk_setup, temp_config, tmp_path):
        """Test _on_item_activated opens file."""
        from src.history import HistoryWindow, HistoryManager

        # Create file and add to history
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake")

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        window = HistoryWindow()

        # Mock subprocess.Popen
        with patch("subprocess.Popen") as mock_popen:
            # Get path from store
            if len(window.store) > 0:
                path = Gtk.TreePath.new_first()
                window._on_item_activated(window.icon_view, path)
                mock_popen.assert_called_once()

    def test_on_item_activated_exception(self, gtk_setup, temp_config, tmp_path):
        """Test _on_item_activated handles exception."""
        from src.history import HistoryWindow, HistoryManager

        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake")

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        window = HistoryWindow()

        with patch("subprocess.Popen", side_effect=Exception("Failed")):
            if len(window.store) > 0:
                path = Gtk.TreePath.new_first()
                # Should not raise
                window._on_item_activated(window.icon_view, path)

    def test_on_delete_no_selection(self, gtk_setup, temp_config):
        """Test _on_delete does nothing with no selection."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        # Clear any selection
        window.icon_view.unselect_all()

        # Should return early without error
        window._on_delete(None)

    def test_on_delete_with_selection_yes(self, gtk_setup, temp_config, tmp_path):
        """Test _on_delete with selection and YES response."""
        from src.history import HistoryWindow, HistoryManager
        Gtk = gtk_setup["Gtk"]

        # Create a valid PNG file
        import struct
        import zlib

        def create_minimal_png():
            signature = b'\x89PNG\r\n\x1a\n'
            width = struct.pack('>I', 1)
            height = struct.pack('>I', 1)
            ihdr_data = width + height + b'\x08\x02\x00\x00\x00'
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
            raw_data = b'\x00\xff\x00\x00'
            compressed = zlib.compress(raw_data)
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
            idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc
            return signature + ihdr + idat + iend

        test_file = tmp_path / "to_delete.png"
        test_file.write_bytes(create_minimal_png())

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        window = HistoryWindow()

        # Select first item
        if len(window.store) > 0:
            path = Gtk.TreePath.new_first()
            window.icon_view.select_path(path)

            # Mock the dialog to return YES
            with patch.object(Gtk.MessageDialog, "run", return_value=Gtk.ResponseType.YES):
                with patch.object(Gtk.MessageDialog, "destroy"):
                    window._on_delete(None)

            # File should be deleted
            assert not test_file.exists()

    def test_on_delete_with_selection_no(self, gtk_setup, temp_config, tmp_path):
        """Test _on_delete with selection and NO response."""
        from src.history import HistoryWindow, HistoryManager
        Gtk = gtk_setup["Gtk"]

        import struct
        import zlib

        def create_minimal_png():
            signature = b'\x89PNG\r\n\x1a\n'
            width = struct.pack('>I', 1)
            height = struct.pack('>I', 1)
            ihdr_data = width + height + b'\x08\x02\x00\x00\x00'
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
            raw_data = b'\x00\xff\x00\x00'
            compressed = zlib.compress(raw_data)
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
            idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc
            return signature + ihdr + idat + iend

        test_file = tmp_path / "keep.png"
        test_file.write_bytes(create_minimal_png())

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        window = HistoryWindow()

        if len(window.store) > 0:
            path = Gtk.TreePath.new_first()
            window.icon_view.select_path(path)

            # Mock the dialog to return NO
            with patch.object(Gtk.MessageDialog, "run", return_value=Gtk.ResponseType.NO):
                with patch.object(Gtk.MessageDialog, "destroy"):
                    window._on_delete(None)

            # File should still exist
            assert test_file.exists()

    def test_on_clear_all_yes(self, gtk_setup, temp_config, tmp_path):
        """Test _on_clear_all with YES response."""
        from src.history import HistoryWindow, HistoryManager
        Gtk = gtk_setup["Gtk"]

        import struct
        import zlib

        def create_minimal_png():
            signature = b'\x89PNG\r\n\x1a\n'
            width = struct.pack('>I', 1)
            height = struct.pack('>I', 1)
            ihdr_data = width + height + b'\x08\x02\x00\x00\x00'
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
            raw_data = b'\x00\xff\x00\x00'
            compressed = zlib.compress(raw_data)
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
            idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc
            return signature + ihdr + idat + iend

        # Add multiple files
        for i in range(3):
            test_file = tmp_path / f"test{i}.png"
            test_file.write_bytes(create_minimal_png())
            manager = HistoryManager()
            manager.add(test_file, mode="test")

        window = HistoryWindow()
        initial_count = len(window.store)

        # Mock dialog to return YES
        with patch.object(Gtk.MessageDialog, "run", return_value=Gtk.ResponseType.YES):
            with patch.object(Gtk.MessageDialog, "destroy"):
                window._on_clear_all(None)

        # Store should be empty
        assert len(window.store) == 0

    def test_on_clear_all_no(self, gtk_setup, temp_config, tmp_path):
        """Test _on_clear_all with NO response keeps history."""
        from src.history import HistoryWindow, HistoryManager
        Gtk = gtk_setup["Gtk"]

        import struct
        import zlib

        def create_minimal_png():
            signature = b'\x89PNG\r\n\x1a\n'
            width = struct.pack('>I', 1)
            height = struct.pack('>I', 1)
            ihdr_data = width + height + b'\x08\x02\x00\x00\x00'
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
            raw_data = b'\x00\xff\x00\x00'
            compressed = zlib.compress(raw_data)
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + compressed) & 0xffffffff)
            idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc
            return signature + ihdr + idat + iend

        test_file = tmp_path / "keep.png"
        test_file.write_bytes(create_minimal_png())

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        window = HistoryWindow()

        # Mock dialog to return NO
        with patch.object(Gtk.MessageDialog, "run", return_value=Gtk.ResponseType.NO):
            with patch.object(Gtk.MessageDialog, "destroy"):
                window._on_clear_all(None)

        # Store should still have entry
        assert len(window.store) == 1

    def test_on_open_folder(self, gtk_setup, temp_config):
        """Test _on_open_folder opens screenshots folder."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        with patch("subprocess.Popen") as mock_popen:
            window._on_open_folder(None)
            mock_popen.assert_called_once()
            # Should call xdg-open with folder path
            call_args = mock_popen.call_args[0][0]
            assert call_args[0] == "xdg-open"

    def test_on_open_folder_exception(self, gtk_setup, temp_config):
        """Test _on_open_folder handles exception."""
        from src.history import HistoryWindow

        window = HistoryWindow()

        with patch("subprocess.Popen", side_effect=Exception("Failed")):
            # Should not raise
            window._on_open_folder(None)

    def test_load_history_exception(self, gtk_setup, temp_config, tmp_path):
        """Test _load_history handles thumbnail exception."""
        from src.history import HistoryWindow, HistoryManager

        # Create file that will fail to create thumbnail
        test_file = tmp_path / "bad.png"
        test_file.write_bytes(b"not a valid image")

        manager = HistoryManager()
        manager.add(test_file, mode="test")

        # Should not raise even with bad image
        window = HistoryWindow()
        assert window is not None
