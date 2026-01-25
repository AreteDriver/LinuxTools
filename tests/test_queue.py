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
        from src.queue import QueuedCapture
        from src.capture import CaptureMode

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
        from src.queue import QueuedCapture
        from src.capture import CaptureMode

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
        assert callable(getattr(CaptureQueue, "add"))

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
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

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
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for i in range(5):
                mock_result = MagicMock()
                mock_result.success = True
                queue.add(mock_result, CaptureMode.REGION)

            assert queue.count == 5

    def test_queue_get_all(self):
        """Test get_all returns all results."""
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

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
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

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
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for i in range(3):
                queue.add(MagicMock(), CaptureMode.REGION)

            assert queue.count == 3

            queue.clear()

            assert queue.count == 0
            assert queue.is_empty is True

    def test_queue_pop_all(self):
        """Test pop_all returns all and clears queue."""
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for i in range(3):
                queue.add(MagicMock(), CaptureMode.REGION)

            results = queue.pop_all()

            assert len(results) == 3
            assert queue.count == 0

    def test_queue_remove_valid_index(self):
        """Test remove with valid index."""
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

        with patch("src.queue.config.get_setting", return_value=50):
            queue = CaptureQueue()

            for i in range(3):
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
        from src.queue import CaptureQueue
        from src.capture import CaptureMode

        with patch("src.queue.config.get_setting", return_value=5):
            queue = CaptureQueue()

            for i in range(10):
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
