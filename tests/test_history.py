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
