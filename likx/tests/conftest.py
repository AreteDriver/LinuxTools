"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check GTK availability
GTK_AVAILABLE = False
try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk  # noqa: F401

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    pass

# Check AppIndicator availability
APPINDICATOR_AVAILABLE = False
if GTK_AVAILABLE:
    try:
        gi.require_version("AppIndicator3", "0.1")
        from gi.repository import AppIndicator3  # noqa: F401

        APPINDICATOR_AVAILABLE = True
    except (ValueError, ImportError):
        try:
            gi.require_version("AyatanaAppIndicator3", "0.1")
            from gi.repository import AyatanaAppIndicator3  # noqa: F401

            APPINDICATOR_AVAILABLE = True
        except (ValueError, ImportError):
            pass


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "requires_gtk: mark test as requiring GTK")
    config.addinivalue_line("markers", "requires_appindicator: mark test as requiring AppIndicator")


def pytest_collection_modifyitems(config, items):
    """Skip tests based on available dependencies."""
    skip_gtk = pytest.mark.skip(reason="GTK not available")
    skip_appindicator = pytest.mark.skip(reason="AppIndicator not available")

    for item in items:
        if "requires_gtk" in item.keywords and not GTK_AVAILABLE:
            item.add_marker(skip_gtk)
        if "requires_appindicator" in item.keywords and not APPINDICATOR_AVAILABLE:
            item.add_marker(skip_appindicator)
