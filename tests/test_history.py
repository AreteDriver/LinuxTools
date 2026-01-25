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
