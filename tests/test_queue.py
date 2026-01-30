"""Tests for the capture queue module."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestQueueModuleImport:
    """Test queue module imports."""

    def test_module_imports(self):
        """Test that queue module imports successfully."""
        from src import queue

        assert hasattr(queue, "QueuedCapture")
        assert hasattr(queue, "CaptureQueue")
        assert hasattr(queue, "GTK_AVAILABLE")

    def test_gtk_available_is_bool(self):
        """Test that GTK_AVAILABLE is a boolean."""
        from src.queue import GTK_AVAILABLE

        assert isinstance(GTK_AVAILABLE, bool)


class TestQueuedCapture:
    """Test QueuedCapture dataclass."""

    def test_queued_capture_init(self):
        """Test QueuedCapture initialization."""
        from src.capture import CaptureMode
        from src.queue import QueuedCapture

        mock_result = MagicMock()
        timestamp = datetime.now()

        queued = QueuedCapture(
            result=mock_result,
            timestamp=timestamp,
            mode=CaptureMode.REGION,
        )

        assert queued.result == mock_result
        assert queued.timestamp == timestamp
        assert queued.mode == CaptureMode.REGION
        assert queued.temp_path is None

    def test_queued_capture_with_temp_path(self):
        """Test QueuedCapture with temp_path."""
        from src.capture import CaptureMode
        from src.queue import QueuedCapture

        queued = QueuedCapture(
            result=MagicMock(),
            timestamp=datetime.now(),
            mode=CaptureMode.FULLSCREEN,
            temp_path=Path("/tmp/test.png"),
        )

        assert queued.temp_path == Path("/tmp/test.png")


class TestCaptureQueueClass:
    """Test CaptureQueue class structure."""

    def test_class_has_add_method(self):
        """Test CaptureQueue has add method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "add")
        assert callable(CaptureQueue.add)

    def test_class_has_get_all_method(self):
        """Test CaptureQueue has get_all method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "get_all")

    def test_class_has_pop_all_method(self):
        """Test CaptureQueue has pop_all method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "pop_all")

    def test_class_has_get_at_method(self):
        """Test CaptureQueue has get_at method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "get_at")

    def test_class_has_clear_method(self):
        """Test CaptureQueue has clear method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "clear")

    def test_class_has_remove_method(self):
        """Test CaptureQueue has remove method."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "remove")

    def test_class_has_count_property(self):
        """Test CaptureQueue has count property."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "count")

    def test_class_has_is_empty_property(self):
        """Test CaptureQueue has is_empty property."""
        from src.queue import CaptureQueue

        assert hasattr(CaptureQueue, "is_empty")


class TestCaptureQueueOperations:
    """Test CaptureQueue operations."""

    def test_queue_init_empty(self):
        """Test CaptureQueue initializes empty."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            assert queue.count == 0
            assert queue.is_empty is True

    def test_queue_add_capture(self):
        """Test adding capture to queue."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            mock_result = MagicMock()
            mock_result.success = True

            position = queue.add(mock_result, CaptureMode.REGION)

            assert position == 0
            assert queue.count == 1
            assert queue.is_empty is False

    def test_queue_add_multiple_captures(self):
        """Test adding multiple captures."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for _i in range(5):
                mock_result = MagicMock()
                mock_result.success = True
                queue.add(mock_result, CaptureMode.REGION)

            assert queue.count == 5

    def test_queue_get_all(self):
        """Test get_all returns all results."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            results = []
            for i in range(3):
                mock_result = MagicMock()
                mock_result.value = i
                results.append(mock_result)
                queue.add(mock_result, CaptureMode.REGION)

            all_results = queue.get_all()
            assert len(all_results) == 3
            for i, result in enumerate(all_results):
                assert result.value == i

    def test_queue_get_at_valid_index(self):
        """Test get_at with valid index."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            mock_result = MagicMock()
            mock_result.value = 42
            queue.add(mock_result, CaptureMode.REGION)

            result = queue.get_at(0)
            assert result.value == 42

    def test_queue_get_at_invalid_index(self):
        """Test get_at with invalid index returns None."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            result = queue.get_at(0)
            assert result is None

            result = queue.get_at(-1)
            assert result is None

    def test_queue_clear(self):
        """Test clearing the queue."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for _i in range(3):
                queue.add(MagicMock(), CaptureMode.REGION)

            assert queue.count == 3

            queue.clear()

            assert queue.count == 0
            assert queue.is_empty is True

    def test_queue_pop_all(self):
        """Test pop_all returns all and clears queue."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for _i in range(3):
                queue.add(MagicMock(), CaptureMode.REGION)

            results = queue.pop_all()

            assert len(results) == 3
            assert queue.count == 0

    def test_queue_remove_valid_index(self):
        """Test remove with valid index."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for _i in range(3):
                queue.add(MagicMock(), CaptureMode.REGION)

            result = queue.remove(1)

            assert result is True
            assert queue.count == 2

    def test_queue_remove_invalid_index(self):
        """Test remove with invalid index."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            result = queue.remove(0)
            assert result is False

            result = queue.remove(-1)
            assert result is False

    def test_queue_enforces_max_size(self):
        """Test queue enforces max size limit."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=5):
            queue = CaptureQueue()

            for _i in range(10):
                queue.add(MagicMock(), CaptureMode.REGION)

            # Should only keep max_queue_size items
            assert queue.count <= 5


class TestCaptureQueueWithPersistence:
    """Test CaptureQueue with persistence directory."""

    def test_queue_with_persist_dir_init(self):
        """Test queue initialization with persist dir."""
        from src.queue import CaptureQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                assert queue.count == 0

    def test_persist_dir_stores_path(self):
        """Test persist_dir is stored."""
        from src.queue import CaptureQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                assert queue._persist_dir == persist_dir

    def test_add_with_persist_calls_persist_capture(self):
        """Test add with persistence calls _persist_capture."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                mock_result = MagicMock()
                mock_result.success = True
                mock_pixbuf = MagicMock()
                mock_result.pixbuf = mock_pixbuf

                queue.add(mock_result, CaptureMode.REGION)

                # Verify pixbuf.savev was called
                mock_pixbuf.savev.assert_called_once()

    def test_clear_with_persist_removes_files(self):
        """Test clear with persistence removes temp files."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            # Create a temp file
            temp_file = persist_dir / "test.png"
            temp_file.touch()

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                # Manually add a queued capture with temp_path
                queued = QueuedCapture(
                    result=MagicMock(),
                    timestamp=datetime.now(),
                    mode=CaptureMode.REGION,
                    temp_path=temp_file,
                )
                queue._queue.append(queued)

                assert temp_file.exists()

                queue.clear()

                # File should be deleted
                assert not temp_file.exists()

    def test_remove_with_persist_removes_file(self):
        """Test remove with persistence removes temp file."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            temp_file = persist_dir / "test.png"
            temp_file.touch()

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                queued = QueuedCapture(
                    result=MagicMock(),
                    timestamp=datetime.now(),
                    mode=CaptureMode.REGION,
                    temp_path=temp_file,
                )
                queue._queue.append(queued)

                assert temp_file.exists()

                queue.remove(0)

                assert not temp_file.exists()


class TestCaptureQueuePersistCapture:
    """Test CaptureQueue._persist_capture method."""

    def test_persist_capture_raises_without_dir(self):
        """Test _persist_capture raises error without persist_dir."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()  # No persist_dir

            queued = QueuedCapture(
                result=MagicMock(),
                timestamp=datetime.now(),
                mode=CaptureMode.REGION,
            )

            with pytest.raises(ValueError, match="Persist directory not set"):
                queue._persist_capture(queued)

    def test_persist_capture_creates_directory(self):
        """Test _persist_capture creates persist directory if needed."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "new_queue_dir"

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                mock_result = MagicMock()
                mock_pixbuf = MagicMock()
                mock_result.pixbuf = mock_pixbuf

                queued = QueuedCapture(
                    result=mock_result,
                    timestamp=datetime.now(),
                    mode=CaptureMode.REGION,
                )

                queue._persist_capture(queued)

                assert persist_dir.exists()

    def test_persist_capture_handles_savev_exception(self):
        """Test _persist_capture handles pixbuf.savev exception."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                mock_result = MagicMock()
                mock_pixbuf = MagicMock()
                mock_pixbuf.savev.side_effect = Exception("Save failed")
                mock_result.pixbuf = mock_pixbuf

                queued = QueuedCapture(
                    result=mock_result,
                    timestamp=datetime.now(),
                    mode=CaptureMode.REGION,
                )

                # Should return None on failure
                result = queue._persist_capture(queued)
                assert result is None


class TestCaptureQueueLoadPersisted:
    """Test CaptureQueue._load_persisted method."""

    def test_load_persisted_skips_if_no_dir(self):
        """Test _load_persisted does nothing without persist_dir."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            # Should not raise
            queue._load_persisted()
            assert queue.count == 0

    def test_load_persisted_skips_if_dir_not_exists(self):
        """Test _load_persisted does nothing if dir doesn't exist."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue(persist_dir=Path("/nonexistent/path"))

            # Should not raise
            queue._load_persisted()
            assert queue.count == 0

    def test_load_persisted_skips_without_gtk(self):
        """Test _load_persisted skips if GTK not available."""
        from src.queue import CaptureQueue

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            # Create a mock queue file
            queue_file = persist_dir / "queue_20240615_120000_000000.png"
            queue_file.touch()

            with patch("src.queue.config.get_setting", return_value=50):
                with patch("src.queue.GTK_AVAILABLE", False):
                    queue = CaptureQueue(persist_dir=persist_dir)

                    # Should not load anything without GTK
                    assert queue.count == 0


class TestCaptureQueueEdgeCases:
    """Test CaptureQueue edge cases."""

    def test_get_at_negative_index(self):
        """Test get_at with negative index returns None."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()
            queue.add(MagicMock())

            # Python negative indexing should not work here
            result = queue.get_at(-1)
            assert result is None

    def test_get_at_out_of_bounds(self):
        """Test get_at with out of bounds index."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()
            queue.add(MagicMock())

            result = queue.get_at(100)
            assert result is None

    def test_remove_handles_oserror_on_unlink(self):
        """Test remove handles OSError when deleting temp file."""
        from src.capture import CaptureMode
        from src.queue import CaptureQueue, QueuedCapture

        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            persist_dir.mkdir()

            with patch("src.queue.config.get_setting", return_value=50):
                queue = CaptureQueue(persist_dir=persist_dir)

                # Create a mock path that raises OSError on unlink
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                mock_path.unlink.side_effect = OSError("Permission denied")

                queued = QueuedCapture(
                    result=MagicMock(),
                    timestamp=datetime.now(),
                    mode=CaptureMode.REGION,
                    temp_path=mock_path,
                )
                queue._queue.append(queued)

                # Should not raise
                result = queue.remove(0)
                assert result is True
                assert queue.count == 0

    def test_queue_max_size_from_config(self):
        """Test queue uses max size from config."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=10):
            queue = CaptureQueue()
            assert queue._max_queue_size == 10

    def test_add_returns_correct_position(self):
        """Test add returns correct queue position."""
        from src.queue import CaptureQueue

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            pos0 = queue.add(MagicMock())
            pos1 = queue.add(MagicMock())
            pos2 = queue.add(MagicMock())

            assert pos0 == 0
            assert pos1 == 1
            assert pos2 == 2
