"""Tests for capture queue manager."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.capture import CaptureMode, CaptureResult
from src.queue import CaptureQueue, QueuedCapture


class TestQueuedCapture:
    """Tests for QueuedCapture dataclass."""

    def test_create_queued_capture(self):
        """QueuedCapture can be created with required fields."""
        result = CaptureResult(success=True)
        timestamp = datetime.now()
        mode = CaptureMode.REGION

        queued = QueuedCapture(result=result, timestamp=timestamp, mode=mode)

        assert queued.result == result
        assert queued.timestamp == timestamp
        assert queued.mode == mode
        assert queued.temp_path is None

    def test_queued_capture_with_temp_path(self):
        """QueuedCapture can have optional temp_path."""
        result = CaptureResult(success=True)
        temp_path = Path("/tmp/test.png")

        queued = QueuedCapture(
            result=result,
            timestamp=datetime.now(),
            mode=CaptureMode.FULLSCREEN,
            temp_path=temp_path,
        )

        assert queued.temp_path == temp_path


class TestCaptureQueueInit:
    """Tests for CaptureQueue initialization."""

    def test_init_without_persist_dir(self):
        """CaptureQueue initializes without persist directory."""
        queue = CaptureQueue()

        assert queue.count == 0
        assert queue.is_empty

    @patch("src.queue.config.get_setting")
    def test_init_uses_config_max_size(self, mock_get_setting):
        """CaptureQueue uses max size from config."""
        mock_get_setting.return_value = 100
        queue = CaptureQueue()

        mock_get_setting.assert_called_with("queue_max_size", 50)
        assert queue._max_queue_size == 100

    def test_init_with_persist_dir_creates_dir(self):
        """CaptureQueue with persist_dir calls _load_persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "queue"
            # Mock _load_persisted since we're just testing init
            with patch.object(CaptureQueue, "_load_persisted"):
                queue = CaptureQueue(persist_dir=persist_dir)
                assert queue._persist_dir == persist_dir


class TestCaptureQueueAdd:
    """Tests for CaptureQueue.add method."""

    def test_add_capture(self):
        """add() adds capture to queue."""
        queue = CaptureQueue()
        result = CaptureResult(success=True)

        position = queue.add(result)

        assert position == 0
        assert queue.count == 1

    def test_add_multiple_captures(self):
        """add() returns correct position for multiple captures."""
        queue = CaptureQueue()

        pos1 = queue.add(CaptureResult(success=True))
        pos2 = queue.add(CaptureResult(success=True))
        pos3 = queue.add(CaptureResult(success=True))

        assert pos1 == 0
        assert pos2 == 1
        assert pos3 == 2
        assert queue.count == 3

    def test_add_with_capture_mode(self):
        """add() stores capture mode."""
        queue = CaptureQueue()
        result = CaptureResult(success=True)

        queue.add(result, mode=CaptureMode.FULLSCREEN)

        assert queue._queue[0].mode == CaptureMode.FULLSCREEN

    @patch("src.queue.config.get_setting")
    def test_add_removes_oldest_when_full(self, mock_get_setting):
        """add() removes oldest capture when queue is full."""
        mock_get_setting.return_value = 3
        queue = CaptureQueue()

        result1 = CaptureResult(success=True, error="first")
        result2 = CaptureResult(success=True, error="second")
        result3 = CaptureResult(success=True, error="third")
        result4 = CaptureResult(success=True, error="fourth")

        queue.add(result1)
        queue.add(result2)
        queue.add(result3)
        queue.add(result4)

        assert queue.count == 3
        # First item should have been removed
        results = queue.get_all()
        assert results[0].error == "second"
        assert results[1].error == "third"
        assert results[2].error == "fourth"


class TestCaptureQueueGet:
    """Tests for CaptureQueue get methods."""

    def test_get_all_empty(self):
        """get_all() returns empty list for empty queue."""
        queue = CaptureQueue()

        results = queue.get_all()

        assert results == []

    def test_get_all_returns_results(self):
        """get_all() returns all CaptureResults."""
        queue = CaptureQueue()
        result1 = CaptureResult(success=True, error="one")
        result2 = CaptureResult(success=True, error="two")

        queue.add(result1)
        queue.add(result2)
        results = queue.get_all()

        assert len(results) == 2
        assert results[0].error == "one"
        assert results[1].error == "two"

    def test_get_at_valid_index(self):
        """get_at() returns capture at valid index."""
        queue = CaptureQueue()
        result1 = CaptureResult(success=True, error="first")
        result2 = CaptureResult(success=True, error="second")

        queue.add(result1)
        queue.add(result2)

        assert queue.get_at(0).error == "first"
        assert queue.get_at(1).error == "second"

    def test_get_at_invalid_index_returns_none(self):
        """get_at() returns None for invalid index."""
        queue = CaptureQueue()
        queue.add(CaptureResult(success=True))

        assert queue.get_at(-1) is None
        assert queue.get_at(1) is None
        assert queue.get_at(100) is None

    def test_get_at_empty_queue(self):
        """get_at() returns None for empty queue."""
        queue = CaptureQueue()

        assert queue.get_at(0) is None


class TestCaptureQueuePopAll:
    """Tests for CaptureQueue.pop_all method."""

    def test_pop_all_returns_and_clears(self):
        """pop_all() returns all captures and clears queue."""
        queue = CaptureQueue()
        queue.add(CaptureResult(success=True, error="one"))
        queue.add(CaptureResult(success=True, error="two"))

        results = queue.pop_all()

        assert len(results) == 2
        assert results[0].error == "one"
        assert results[1].error == "two"
        assert queue.is_empty

    def test_pop_all_empty_queue(self):
        """pop_all() returns empty list for empty queue."""
        queue = CaptureQueue()

        results = queue.pop_all()

        assert results == []
        assert queue.is_empty


class TestCaptureQueueClear:
    """Tests for CaptureQueue.clear method."""

    def test_clear_removes_all(self):
        """clear() removes all items from queue."""
        queue = CaptureQueue()
        queue.add(CaptureResult(success=True))
        queue.add(CaptureResult(success=True))

        queue.clear()

        assert queue.is_empty
        assert queue.count == 0

    def test_clear_empty_queue(self):
        """clear() works on empty queue."""
        queue = CaptureQueue()

        queue.clear()  # Should not raise

        assert queue.is_empty

    def test_clear_removes_temp_files(self):
        """clear() removes temp files when persist_dir is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir)
            temp_file = persist_dir / "test.png"
            temp_file.write_bytes(b"test")

            queue = CaptureQueue()
            queue._persist_dir = persist_dir
            # Manually add a queued capture with temp_path
            queued = QueuedCapture(
                result=CaptureResult(success=True),
                timestamp=datetime.now(),
                mode=CaptureMode.REGION,
                temp_path=temp_file,
            )
            queue._queue.append(queued)

            queue.clear()

            assert not temp_file.exists()


class TestCaptureQueueRemove:
    """Tests for CaptureQueue.remove method."""

    def test_remove_valid_index(self):
        """remove() removes item at valid index."""
        queue = CaptureQueue()
        queue.add(CaptureResult(success=True, error="first"))
        queue.add(CaptureResult(success=True, error="second"))
        queue.add(CaptureResult(success=True, error="third"))

        result = queue.remove(1)

        assert result is True
        assert queue.count == 2
        assert queue.get_at(0).error == "first"
        assert queue.get_at(1).error == "third"

    def test_remove_invalid_index(self):
        """remove() returns False for invalid index."""
        queue = CaptureQueue()
        queue.add(CaptureResult(success=True))

        assert queue.remove(-1) is False
        assert queue.remove(1) is False
        assert queue.remove(100) is False
        assert queue.count == 1

    def test_remove_empty_queue(self):
        """remove() returns False for empty queue."""
        queue = CaptureQueue()

        assert queue.remove(0) is False


class TestCaptureQueueProperties:
    """Tests for CaptureQueue properties."""

    def test_count_property(self):
        """count property returns correct count."""
        queue = CaptureQueue()
        assert queue.count == 0

        queue.add(CaptureResult(success=True))
        assert queue.count == 1

        queue.add(CaptureResult(success=True))
        assert queue.count == 2

    def test_is_empty_property(self):
        """is_empty property returns correct value."""
        queue = CaptureQueue()
        assert queue.is_empty is True

        queue.add(CaptureResult(success=True))
        assert queue.is_empty is False

        queue.clear()
        assert queue.is_empty is True


class TestCaptureQueuePersistence:
    """Tests for CaptureQueue persistence functionality."""

    def test_persist_capture_creates_file(self):
        """_persist_capture creates PNG file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir) / "persist"
            queue = CaptureQueue()
            queue._persist_dir = persist_dir

            mock_pixbuf = MagicMock()
            result = CaptureResult(success=True, pixbuf=mock_pixbuf)
            queued = QueuedCapture(
                result=result,
                timestamp=datetime(2024, 1, 15, 12, 30, 45, 123456),
                mode=CaptureMode.REGION,
            )

            path = queue._persist_capture(queued)

            assert persist_dir.exists()
            mock_pixbuf.savev.assert_called_once()
            assert "queue_20240115_123045_123456.png" in str(path)

    def test_persist_capture_without_persist_dir_raises(self):
        """_persist_capture raises if persist_dir not set."""
        queue = CaptureQueue()
        queued = QueuedCapture(
            result=CaptureResult(success=True),
            timestamp=datetime.now(),
            mode=CaptureMode.REGION,
        )

        with pytest.raises(ValueError, match="Persist directory not set"):
            queue._persist_capture(queued)

    def test_persist_capture_handles_save_error(self):
        """_persist_capture returns None on save error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir)
            queue = CaptureQueue()
            queue._persist_dir = persist_dir

            mock_pixbuf = MagicMock()
            mock_pixbuf.savev.side_effect = Exception("Save failed")
            result = CaptureResult(success=True, pixbuf=mock_pixbuf)
            queued = QueuedCapture(
                result=result,
                timestamp=datetime.now(),
                mode=CaptureMode.REGION,
            )

            path = queue._persist_capture(queued)

            assert path is None

    def test_load_persisted_empty_dir(self):
        """_load_persisted handles empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_dir = Path(tmpdir)
            queue = CaptureQueue()
            queue._persist_dir = persist_dir

            queue._load_persisted()

            assert queue.is_empty

    def test_load_persisted_nonexistent_dir(self):
        """_load_persisted handles nonexistent directory."""
        queue = CaptureQueue()
        queue._persist_dir = Path("/nonexistent/path")

        queue._load_persisted()  # Should not raise

        assert queue.is_empty

    def test_load_persisted_no_persist_dir(self):
        """_load_persisted handles no persist_dir."""
        queue = CaptureQueue()
        queue._persist_dir = None

        queue._load_persisted()  # Should not raise

        assert queue.is_empty


class TestCaptureQueueRemoveAt:
    """Tests for CaptureQueue._remove_at internal method."""

    def test_remove_at_cleans_temp_file(self):
        """_remove_at removes temp file if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "test.png"
            temp_file.write_bytes(b"test")

            queue = CaptureQueue()
            queued = QueuedCapture(
                result=CaptureResult(success=True),
                timestamp=datetime.now(),
                mode=CaptureMode.REGION,
                temp_path=temp_file,
            )
            queue._queue.append(queued)

            queue._remove_at(0)

            assert not temp_file.exists()

    def test_remove_at_handles_missing_temp_file(self):
        """_remove_at handles missing temp file gracefully."""
        queue = CaptureQueue()
        queued = QueuedCapture(
            result=CaptureResult(success=True),
            timestamp=datetime.now(),
            mode=CaptureMode.REGION,
            temp_path=Path("/nonexistent/file.png"),
        )
        queue._queue.append(queued)

        result = queue._remove_at(0)  # Should not raise

        assert result is True
        assert queue.is_empty
