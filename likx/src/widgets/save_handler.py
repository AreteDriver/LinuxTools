"""Save/export handler for LikX editor."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gtk  # noqa: E402

from .. import config  # noqa: E402
from ..editor import render_elements  # noqa: E402
from ..notification import (  # noqa: E402
    show_screenshot_copied,
    show_screenshot_saved,
    show_upload_error,
    show_upload_success,
)

if TYPE_CHECKING:
    from ..editor import EditorElement
    from ..uploader import Uploader


class SaveHandler:
    """Handles save, upload, and clipboard operations for the editor.

    Uses callback-based design to avoid direct coupling to EditorWindow.
    """

    def __init__(
        self,
        get_pixbuf: Callable[[], GdkPixbuf.Pixbuf],
        get_elements: Callable[[], List[EditorElement]],
        get_parent_window: Callable[[], Optional[Gtk.Window]],
        set_status: Callable[[str], None],
        get_uploader: Callable[[], Uploader],
    ):
        """Initialize the save handler.

        Args:
            get_pixbuf: Callback to get the source pixbuf
            get_elements: Callback to get the list of annotation elements
            get_parent_window: Callback to get the parent window for dialogs
            set_status: Callback to update the status bar
            get_uploader: Callback to get the uploader instance
        """
        self._get_pixbuf = get_pixbuf
        self._get_elements = get_elements
        self._get_parent_window = get_parent_window
        self._set_status = set_status
        self._get_uploader = get_uploader

    def save_with_annotations(self, filepath: Path) -> bool:
        """Save the image with annotations rendered.

        Args:
            filepath: Path to save the image to

        Returns:
            True if save was successful, False otherwise
        """
        try:
            import cairo

            pixbuf = self._get_pixbuf()
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)

            # Draw original image
            Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
            ctx.paint()

            # Render annotations
            elements = self._get_elements()
            if elements:
                render_elements(surface, elements, pixbuf)

            # Convert to pixbuf and save
            data = surface.get_data()
            new_pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data,
                GdkPixbuf.Colorspace.RGB,
                True,
                8,
                width,
                height,
                cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, width),
            )

            # Determine format
            format_str = filepath.suffix.lstrip(".").lower()
            format_map = {
                "jpg": "jpeg",
                "jpeg": "jpeg",
                "png": "png",
                "bmp": "bmp",
                "gif": "gif",
            }
            pixbuf_format = format_map.get(format_str, "png")

            filepath.parent.mkdir(parents=True, exist_ok=True)
            new_pixbuf.savev(str(filepath), pixbuf_format, [], [])

            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def save(self) -> None:
        """Save the edited screenshot with a file dialog."""
        parent = self._get_parent_window()
        dialog = Gtk.FileChooserDialog(
            title="Save Screenshot",
            parent=parent,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        dialog.set_do_overwrite_confirmation(True)

        # Add filters
        for fmt_name, fmt_ext in [
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
        ]:
            filter_fmt = Gtk.FileFilter()
            filter_fmt.set_name(f"{fmt_name} images")
            filter_fmt.add_pattern(fmt_ext)
            dialog.add_filter(filter_fmt)

        # Set default filename
        default_path = config.get_save_path()
        dialog.set_current_folder(str(default_path.parent))
        dialog.set_current_name(default_path.name)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = Path(dialog.get_filename())
            if self.save_with_annotations(filepath):
                self._set_status(f"Saved to {filepath.name}")
                cfg = config.load_config()
                if cfg.get("show_notification", True):
                    show_screenshot_saved(str(filepath))

        dialog.destroy()

    def upload(self) -> None:
        """Upload the screenshot to cloud service."""
        import os
        import tempfile

        fd, temp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        temp_file = Path(temp_path)

        if not self.save_with_annotations(temp_file):
            show_upload_error("Failed to prepare image for upload")
            return

        self._set_status("Uploading...")

        # Upload
        uploader = self._get_uploader()
        success, url, error = uploader.upload(temp_file)

        # Cleanup
        if temp_file.exists():
            temp_file.unlink()

        if success and url:
            uploader.copy_url_to_clipboard(url)
            self._set_status(f"Uploaded: {url}")
            show_upload_success(url)
        else:
            err_msg = error or "Unknown error"
            self._set_status(f"Upload failed: {err_msg}")
            show_upload_error(err_msg)

    def copy_to_clipboard(self) -> None:
        """Copy the edited screenshot to clipboard."""
        try:
            import cairo

            pixbuf = self._get_pixbuf()
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)

            Gdk.cairo_set_source_pixbuf(ctx, pixbuf, 0, 0)
            ctx.paint()

            elements = self._get_elements()
            if elements:
                render_elements(surface, elements, pixbuf)

            # Convert to pixbuf
            data = surface.get_data()
            new_pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data,
                GdkPixbuf.Colorspace.RGB,
                True,
                8,
                width,
                height,
                cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, width),
            )

            # Copy to clipboard
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_image(new_pixbuf)
            clipboard.store()

            self._set_status("Copied to clipboard")
            cfg = config.load_config()
            if cfg.get("show_notification", True):
                show_screenshot_copied()
        except Exception as e:
            self._set_status(f"Copy failed: {e}")
