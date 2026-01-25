#!/usr/bin/env python3
"""LikX - Enhanced screenshot capture and annotation tool for Linux.

Usage:
    likx [OPTIONS]

Options:
    --fullscreen    Capture the entire screen
    --region        Capture a selected region
    --window        Capture the active window
    --delay SECS    Wait SECS seconds before capturing
    --output FILE   Save to FILE instead of default location
    --no-edit       Skip the editor and save directly
    --help          Show this help message
    --version       Show version information
"""

import argparse
import fcntl
import os
import sys
from pathlib import Path

from src import __version__
from src.capture import CaptureMode, capture, copy_to_clipboard, save_capture
from src.config import get_save_path, load_config
from src.notification import show_notification, show_screenshot_saved

LOCK_FILE = Path.home() / ".cache" / "likx" / "likx.lock"


def acquire_single_instance_lock():
    """Acquire a lock to ensure only one instance runs.

    Returns the lock file handle if acquired, None if another instance is running.
    """
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except OSError:
        return None


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="likx",
        description="LikX - A screenshot capture and annotation tool with Wayland support",
    )

    parser.add_argument("--version", action="version", version=f"LikX {__version__}")

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--fullscreen", "-f", action="store_true", help="Capture the entire screen"
    )
    mode_group.add_argument("--region", "-r", action="store_true", help="Capture a selected region")
    mode_group.add_argument("--window", "-w", action="store_true", help="Capture the active window")

    parser.add_argument(
        "--delay",
        "-d",
        type=int,
        default=0,
        metavar="SECS",
        help="Wait SECS seconds before capturing",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        metavar="FILE",
        help="Save to FILE instead of default location",
    )

    parser.add_argument("--no-edit", action="store_true", help="Skip the editor and save directly")

    parser.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="Copy to clipboard (with --no-edit: copy instead of save)",
    )

    return parser.parse_args()


def _run_gui_mode():
    """Launch the GUI application."""
    lock_fd = acquire_single_instance_lock()
    if lock_fd is None:
        print("LikX is already running.", file=sys.stderr)
        sys.exit(0)
    try:
        from src.ui import run_app

        run_app()
    except Exception as e:
        print(f"Error launching GUI: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        lock_fd.close()


def _capture_region(delay):
    """Capture a selected region interactively."""
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from src.ui import RegionSelector

    region_result = [None]

    def on_region_selected(x, y, width, height):
        region_result[0] = (x, y, width, height)
        Gtk.main_quit()

    RegionSelector(on_region_selected)
    Gtk.main()

    if region_result[0] is None:
        print("Region selection cancelled", file=sys.stderr)
        sys.exit(1)

    return capture(CaptureMode.REGION, delay=delay, region=region_result[0])


def _handle_no_edit_output(result, args, output_path):
    """Handle output when --no-edit is specified."""
    if args.copy:
        if copy_to_clipboard(result):
            print("Screenshot copied to clipboard")
            if load_config().get("show_notification", True):
                show_notification("Screenshot Copied", "Image copied to clipboard")
        else:
            print("Failed to copy to clipboard", file=sys.stderr)
            sys.exit(1)
    else:
        result = save_capture(result, output_path)
        if result.success:
            print(f"Screenshot saved to: {result.filepath}")
            if load_config().get("show_notification", True):
                show_screenshot_saved(str(result.filepath))
        else:
            print(f"Failed to save: {result.error}", file=sys.stderr)
            sys.exit(1)


def _open_editor(result, output_path):
    """Open the editor or fall back to direct save."""
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        from src.ui import EditorWindow

        EditorWindow(result)
        Gtk.main()
    except Exception as e:
        print(f"Editor failed: {e}", file=sys.stderr)
        result = save_capture(result, output_path)
        if result.success:
            print(f"Screenshot saved to: {result.filepath}")
            if load_config().get("show_notification", True):
                show_screenshot_saved(str(result.filepath))
        else:
            print(f"Failed to save: {result.error}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for LikX."""
    args = parse_args()

    if not (args.fullscreen or args.region or args.window):
        _run_gui_mode()
        return

    mode = (
        CaptureMode.FULLSCREEN
        if args.fullscreen
        else (CaptureMode.REGION if args.region else CaptureMode.WINDOW)
    )

    try:
        result = (
            _capture_region(args.delay)
            if mode == CaptureMode.REGION
            else capture(mode, delay=args.delay)
        )
    except Exception as e:
        print(f"Error during capture: {e}", file=sys.stderr)
        sys.exit(1)

    if not result.success:
        print(f"Capture failed: {result.error}", file=sys.stderr)
        show_notification("Capture Failed", result.error, icon="dialog-error")
        sys.exit(1)

    output_path = Path(args.output) if args.output else get_save_path()

    if args.no_edit:
        _handle_no_edit_output(result, args, output_path)
    else:
        _open_editor(result, output_path)


if __name__ == "__main__":
    main()
