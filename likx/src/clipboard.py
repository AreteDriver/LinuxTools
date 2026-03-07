"""Clipboard operations for LikX — split from capture.py for separation of concerns."""

import os
import subprocess
import time

try:
    import gi

    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False


def _copy_wayland_clipboard(temp_file: str) -> bool:
    """Copy image to Wayland clipboard using wl-copy."""
    try:
        with open(temp_file, "rb") as f:
            proc = subprocess.Popen(
                ["wl-copy", "--type", "image/png"],
                stdin=f,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
            )
            proc.wait(timeout=5)
            if proc.returncode == 0:
                os.unlink(temp_file)
                return True
    except subprocess.TimeoutExpired:
        proc.kill()
    except OSError:
        pass
    return False


def _copy_x11_clipboard(temp_file: str) -> bool:
    """Copy image to X11 clipboard using xclip."""
    proc = subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-t", "image/png", temp_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )
    time.sleep(0.1)  # Brief wait for xclip to read file
    # Keep temp file for xclip to serve (cleaned up by /tmp)
    return proc.poll() is None or proc.returncode == 0


def _copy_gtk_clipboard(pixbuf) -> bool:
    """Copy image to GTK clipboard."""
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    if not Gtk.init_check()[0]:
        Gtk.init([])

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_image(pixbuf)
    clipboard.store()

    while Gtk.events_pending():
        Gtk.main_iteration_do(False)

    return True


def _detect_display_server() -> str:
    """Detect display server. Returns 'wayland', 'x11', or 'unknown'."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

    if "wayland" in session_type or wayland_display:
        return "wayland"
    elif os.environ.get("DISPLAY"):
        return "x11"
    return "unknown"


def copy_to_clipboard(result, use_gtk: bool = True) -> bool:
    """Copy a captured screenshot to the clipboard.

    Args:
        result: A CaptureResult (or any object with .success and .pixbuf attributes).
        use_gtk: If True, try GTK clipboard first. Set False for CLI mode.

    Returns:
        True if successful, False otherwise.
    """
    if not result.success or result.pixbuf is None:
        return False

    display_server = _detect_display_server()
    temp_file = None

    try:
        temp_file = f"/tmp/likx_clip_{int(time.time())}.png"
        result.pixbuf.savev(temp_file, "png", [], [])

        if display_server == "wayland":
            if _copy_wayland_clipboard(temp_file):
                return True
        elif _copy_x11_clipboard(temp_file):
            return True
    except (FileNotFoundError, OSError):
        pass

    if temp_file and os.path.exists(temp_file):
        os.unlink(temp_file)

    if use_gtk and GTK_AVAILABLE:
        try:
            return _copy_gtk_clipboard(result.pixbuf)
        except (RuntimeError, OSError):
            pass

    return False
