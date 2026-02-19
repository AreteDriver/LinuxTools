"""Settings dialog and related widgets for LikX."""

from pathlib import Path
from typing import Callable, Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from .. import config  # noqa: E402
from ..i18n import _  # noqa: E402
from ..notification import show_notification  # noqa: E402


class HotkeyEntry(Gtk.Button):
    """A button widget that captures keyboard shortcuts.

    Click the button, then press a key combination to set the hotkey.
    """

    def __init__(self, initial_value: str = ""):
        super().__init__()
        self._hotkey = initial_value
        self._capturing = False
        self._update_label()

        self.set_size_request(180, -1)
        self.connect("clicked", self._on_clicked)
        self.connect("key-press-event", self._on_key_press)
        self.connect("focus-out-event", self._on_focus_out)

    def _update_label(self) -> None:
        """Update button label to show current hotkey."""
        if self._capturing:
            self.set_label("Press a key combination...")
        elif self._hotkey:
            # Convert GTK format to readable format
            display = self._hotkey_to_display(self._hotkey)
            self.set_label(display)
        else:
            self.set_label("Click to set...")

    def _hotkey_to_display(self, hotkey: str) -> str:
        """Convert GTK hotkey format to human-readable format."""
        display = hotkey
        display = display.replace("<Control>", "Ctrl+")
        display = display.replace("<Shift>", "Shift+")
        display = display.replace("<Alt>", "Alt+")
        display = display.replace("<Super>", "Super+")
        return display

    def _display_to_hotkey(self, display: str) -> str:
        """Convert human-readable format to GTK hotkey format."""
        hotkey = display
        hotkey = hotkey.replace("Ctrl+", "<Control>")
        hotkey = hotkey.replace("Shift+", "<Shift>")
        hotkey = hotkey.replace("Alt+", "<Alt>")
        hotkey = hotkey.replace("Super+", "<Super>")
        return hotkey

    def _on_clicked(self, button: Gtk.Button) -> None:
        """Start capturing key combination."""
        self._capturing = True
        self._update_label()
        self.grab_focus()

    def _on_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """Handle key press to capture hotkey."""
        if not self._capturing:
            return False

        # Get modifiers
        modifiers = []
        state = event.state

        if state & Gdk.ModifierType.CONTROL_MASK:
            modifiers.append("<Control>")
        if state & Gdk.ModifierType.SHIFT_MASK:
            modifiers.append("<Shift>")
        if state & Gdk.ModifierType.MOD1_MASK:  # Alt
            modifiers.append("<Alt>")
        if state & Gdk.ModifierType.SUPER_MASK:
            modifiers.append("<Super>")

        # Get the key
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)

        # Ignore modifier-only keys
        if keyname in (
            "Control_L",
            "Control_R",
            "Shift_L",
            "Shift_R",
            "Alt_L",
            "Alt_R",
            "Super_L",
            "Super_R",
            "Meta_L",
            "Meta_R",
        ):
            return True

        # Escape cancels
        if keyname == "Escape":
            self._capturing = False
            self._update_label()
            return True

        # Require at least one modifier
        if not modifiers:
            return True

        # Build hotkey string
        self._hotkey = "".join(modifiers) + keyname.upper()
        self._capturing = False
        self._update_label()
        return True

    def _on_focus_out(self, widget: Gtk.Widget, event: Gdk.Event) -> bool:
        """Cancel capture if focus is lost."""
        if self._capturing:
            self._capturing = False
            self._update_label()
        return False

    def get_hotkey(self) -> str:
        """Get the current hotkey value in GTK format."""
        return self._hotkey

    def set_hotkey(self, hotkey: str) -> None:
        """Set the hotkey value."""
        self._hotkey = hotkey
        self._update_label()


class SettingsDialog:
    """Settings dialog window with all options."""

    def __init__(self, parent: Gtk.Window, on_hotkeys_changed: Optional[Callable] = None):
        self.on_hotkeys_changed = on_hotkeys_changed
        self.dialog = Gtk.Dialog(title=_("Settings"), parent=parent, flags=Gtk.DialogFlags.MODAL)
        self.dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            _("Reset to Defaults"),
            Gtk.ResponseType.REJECT,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )
        self.dialog.set_default_size(500, 450)

        content = self.dialog.get_content_area()
        content.set_border_width(10)
        content.set_spacing(10)

        self.cfg = config.load_config()

        # Create notebook for tabs
        notebook = Gtk.Notebook()
        content.pack_start(notebook, True, True, 0)

        # General settings tab
        general_box = self._create_general_settings()
        notebook.append_page(general_box, Gtk.Label(label=_("General")))

        # Capture settings tab
        capture_box = self._create_capture_settings()
        notebook.append_page(capture_box, Gtk.Label(label=_("Capture")))

        # GIF settings tab
        gif_box = self._create_gif_settings()
        notebook.append_page(gif_box, Gtk.Label(label=_("GIF")))

        # Upload settings tab
        upload_box = self._create_upload_settings()
        notebook.append_page(upload_box, Gtk.Label(label=_("Upload")))

        # Editor settings tab
        editor_box = self._create_editor_settings()
        notebook.append_page(editor_box, Gtk.Label(label=_("Editor")))

        # Hotkeys settings tab
        hotkey_box = self._create_hotkey_settings()
        notebook.append_page(hotkey_box, Gtk.Label(label=_("Hotkeys")))

        # Language settings tab
        language_box = self._create_language_settings()
        notebook.append_page(language_box, Gtk.Label(label=_("Language")))

        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self._save_settings()
        elif response == Gtk.ResponseType.REJECT:
            self._reset_to_defaults()

        self.dialog.destroy()

    def _create_general_settings(self) -> Gtk.Box:
        """Create general settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Save directory
        dir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        dir_label = Gtk.Label(label=_("Save directory:"), xalign=0)
        dir_label.set_size_request(150, -1)
        self.dir_entry = Gtk.Entry()
        self.dir_entry.set_text(str(self.cfg.get("save_directory", "")))
        dir_button = Gtk.Button(label=_("Browse..."))
        dir_button.connect("clicked", self._browse_directory)
        dir_box.pack_start(dir_label, False, False, 0)
        dir_box.pack_start(self.dir_entry, True, True, 0)
        dir_box.pack_start(dir_button, False, False, 0)
        box.pack_start(dir_box, False, False, 0)

        # Default format
        format_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        format_label = Gtk.Label(label=_("Default format:"), xalign=0)
        format_label.set_size_request(150, -1)
        self.format_combo = Gtk.ComboBoxText()
        for fmt in ["png", "jpg", "bmp", "gif"]:
            self.format_combo.append_text(fmt)
        current_fmt = self.cfg.get("default_format", "png")
        self.format_combo.set_active(["png", "jpg", "bmp", "gif"].index(current_fmt))
        format_box.pack_start(format_label, False, False, 0)
        format_box.pack_start(self.format_combo, False, False, 0)
        box.pack_start(format_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # Checkboxes
        self.auto_save_check = Gtk.CheckButton(label=_("Auto-save screenshots (skip editor)"))
        self.auto_save_check.set_active(self.cfg.get("auto_save", False))
        box.pack_start(self.auto_save_check, False, False, 0)

        self.clipboard_check = Gtk.CheckButton(label=_("Copy to clipboard automatically"))
        self.clipboard_check.set_active(self.cfg.get("copy_to_clipboard", True))
        box.pack_start(self.clipboard_check, False, False, 0)

        self.notification_check = Gtk.CheckButton(label=_("Show desktop notifications"))
        self.notification_check.set_active(self.cfg.get("show_notification", True))
        box.pack_start(self.notification_check, False, False, 0)

        self.editor_check = Gtk.CheckButton(label=_("Open editor after capture"))
        self.editor_check.set_active(self.cfg.get("editor_enabled", True))
        box.pack_start(self.editor_check, False, False, 0)

        return box

    def _create_capture_settings(self) -> Gtk.Box:
        """Create capture settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Delay
        delay_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        delay_label = Gtk.Label(label=_("Capture delay (seconds):"), xalign=0)
        delay_label.set_size_request(200, -1)
        self.delay_spin = Gtk.SpinButton()
        self.delay_spin.set_range(0, 10)
        self.delay_spin.set_value(self.cfg.get("delay_seconds", 0))
        self.delay_spin.set_increments(1, 1)
        delay_box.pack_start(delay_label, False, False, 0)
        delay_box.pack_start(self.delay_spin, False, False, 0)
        box.pack_start(delay_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        self.cursor_check = Gtk.CheckButton(label=_("Include mouse cursor in screenshots"))
        self.cursor_check.set_active(self.cfg.get("include_cursor", False))
        box.pack_start(self.cursor_check, False, False, 0)

        return box

    def _create_gif_settings(self) -> Gtk.Box:
        """Create GIF recording settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Quality preset
        quality_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        quality_label = Gtk.Label(label=_("Quality preset:"), xalign=0)
        quality_label.set_size_request(150, -1)
        self.gif_quality_combo = Gtk.ComboBoxText()
        qualities = [
            ("low", _("Low (smaller file)")),
            ("medium", _("Medium (balanced)")),
            ("high", _("High (best quality)")),
        ]
        for qid, qname in qualities:
            self.gif_quality_combo.append(qid, qname)
        self.gif_quality_combo.set_active_id(self.cfg.get("gif_quality", "medium"))
        quality_box.pack_start(quality_label, False, False, 0)
        quality_box.pack_start(self.gif_quality_combo, False, False, 0)
        box.pack_start(quality_box, False, False, 0)

        # FPS
        fps_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fps_label = Gtk.Label(label=_("Frame rate (FPS):"), xalign=0)
        fps_label.set_size_request(150, -1)
        self.gif_fps_spin = Gtk.SpinButton()
        self.gif_fps_spin.set_range(5, 30)
        self.gif_fps_spin.set_value(self.cfg.get("gif_fps", 15))
        self.gif_fps_spin.set_increments(1, 5)
        fps_box.pack_start(fps_label, False, False, 0)
        fps_box.pack_start(self.gif_fps_spin, False, False, 0)
        box.pack_start(fps_box, False, False, 0)

        # Colors
        colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        colors_label = Gtk.Label(label=_("Color palette size:"), xalign=0)
        colors_label.set_size_request(150, -1)
        self.gif_colors_combo = Gtk.ComboBoxText()
        for c in ["64", "128", "192", "256"]:
            self.gif_colors_combo.append(c, c + _(" colors"))
        self.gif_colors_combo.set_active_id(str(self.cfg.get("gif_colors", 256)))
        colors_box.pack_start(colors_label, False, False, 0)
        colors_box.pack_start(self.gif_colors_combo, False, False, 0)
        box.pack_start(colors_box, False, False, 0)

        # Scale factor
        scale_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        scale_label = Gtk.Label(label=_("Scale factor:"), xalign=0)
        scale_label.set_size_request(150, -1)
        self.gif_scale_combo = Gtk.ComboBoxText()
        scales = [("1.0", "100%"), ("0.75", "75%"), ("0.5", "50%"), ("0.25", "25%")]
        for sid, sname in scales:
            self.gif_scale_combo.append(sid, sname)
        self.gif_scale_combo.set_active_id(str(self.cfg.get("gif_scale_factor", 1.0)))
        scale_box.pack_start(scale_label, False, False, 0)
        scale_box.pack_start(self.gif_scale_combo, False, False, 0)
        box.pack_start(scale_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # Dithering algorithm
        dither_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        dither_label = Gtk.Label(label=_("Dithering:"), xalign=0)
        dither_label.set_size_request(150, -1)
        self.gif_dither_combo = Gtk.ComboBoxText()
        dithers = [
            ("none", _("None (sharp, may band)")),
            ("bayer", _("Bayer (ordered, fast)")),
            ("floyd_steinberg", _("Floyd-Steinberg (smooth)")),
            ("sierra2", _("Sierra (quality)")),
        ]
        for did, dname in dithers:
            self.gif_dither_combo.append(did, dname)
        self.gif_dither_combo.set_active_id(self.cfg.get("gif_dither", "bayer"))
        dither_box.pack_start(dither_label, False, False, 0)
        dither_box.pack_start(self.gif_dither_combo, False, False, 0)
        box.pack_start(dither_box, False, False, 0)

        # Loop count
        loop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        loop_label = Gtk.Label(label=_("Loop:"), xalign=0)
        loop_label.set_size_request(150, -1)
        self.gif_loop_combo = Gtk.ComboBoxText()
        loops = [
            ("0", _("Infinite")),
            ("1", _("Play once")),
            ("2", _("2 times")),
            ("3", _("3 times")),
        ]
        for lid, lname in loops:
            self.gif_loop_combo.append(lid, lname)
        self.gif_loop_combo.set_active_id(str(self.cfg.get("gif_loop", 0)))
        loop_box.pack_start(loop_label, False, False, 0)
        loop_box.pack_start(self.gif_loop_combo, False, False, 0)
        box.pack_start(loop_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # Optimization checkbox
        self.gif_optimize_check = Gtk.CheckButton(
            label=_("Optimize with gifsicle (smaller file size)")
        )
        self.gif_optimize_check.set_active(self.cfg.get("gif_optimize", True))
        box.pack_start(self.gif_optimize_check, False, False, 0)

        # Max duration
        duration_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        duration_label = Gtk.Label(label=_("Max duration (seconds):"), xalign=0)
        duration_label.set_size_request(150, -1)
        self.gif_max_duration_spin = Gtk.SpinButton()
        self.gif_max_duration_spin.set_range(5, 300)
        self.gif_max_duration_spin.set_value(self.cfg.get("gif_max_duration", 60))
        self.gif_max_duration_spin.set_increments(5, 30)
        duration_box.pack_start(duration_label, False, False, 0)
        duration_box.pack_start(self.gif_max_duration_spin, False, False, 0)
        box.pack_start(duration_box, False, False, 0)

        return box

    def _create_upload_settings(self) -> Gtk.Box:
        """Create upload settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Upload service
        service_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        service_label = Gtk.Label(label=_("Upload service:"), xalign=0)
        service_label.set_size_request(150, -1)
        self.service_combo = Gtk.ComboBoxText()
        services = ["none", "imgur", "fileio", "s3", "dropbox", "gdrive"]
        for service in services:
            self.service_combo.append_text(service)
        current_service = self.cfg.get("upload_service", "imgur")
        if current_service in services:
            self.service_combo.set_active(services.index(current_service))
        else:
            self.service_combo.set_active(1)  # Default to imgur
        self.service_combo.connect("changed", self._on_upload_service_changed)
        service_box.pack_start(service_label, False, False, 0)
        service_box.pack_start(self.service_combo, False, False, 0)
        box.pack_start(service_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        self.auto_upload_check = Gtk.CheckButton(label=_("Automatically upload after save"))
        self.auto_upload_check.set_active(self.cfg.get("auto_upload", False))
        box.pack_start(self.auto_upload_check, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # S3 settings frame
        self.s3_frame = Gtk.Frame(label=_("S3 Settings"))
        s3_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        s3_box.set_border_width(5)

        s3_bucket_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        s3_bucket_label = Gtk.Label(label=_("Bucket:"), xalign=0)
        s3_bucket_label.set_size_request(100, -1)
        self.s3_bucket_entry = Gtk.Entry()
        self.s3_bucket_entry.set_text(self.cfg.get("s3_bucket", ""))
        self.s3_bucket_entry.set_placeholder_text("my-screenshots-bucket")
        s3_bucket_box.pack_start(s3_bucket_label, False, False, 0)
        s3_bucket_box.pack_start(self.s3_bucket_entry, True, True, 0)
        s3_box.pack_start(s3_bucket_box, False, False, 0)

        s3_region_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        s3_region_label = Gtk.Label(label=_("Region:"), xalign=0)
        s3_region_label.set_size_request(100, -1)
        self.s3_region_entry = Gtk.Entry()
        self.s3_region_entry.set_text(self.cfg.get("s3_region", "us-east-1"))
        s3_region_box.pack_start(s3_region_label, False, False, 0)
        s3_region_box.pack_start(self.s3_region_entry, True, True, 0)
        s3_box.pack_start(s3_region_box, False, False, 0)

        self.s3_public_check = Gtk.CheckButton(label=_("Make uploaded files public"))
        self.s3_public_check.set_active(self.cfg.get("s3_public", True))
        s3_box.pack_start(self.s3_public_check, False, False, 0)

        self.s3_frame.add(s3_box)
        box.pack_start(self.s3_frame, False, False, 0)

        # Dropbox settings frame
        self.dropbox_frame = Gtk.Frame(label=_("Dropbox Settings"))
        dropbox_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        dropbox_box.set_border_width(5)

        dropbox_token_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        dropbox_token_label = Gtk.Label(label=_("Access Token:"), xalign=0)
        dropbox_token_label.set_size_request(100, -1)
        self.dropbox_token_entry = Gtk.Entry()
        self.dropbox_token_entry.set_text(self.cfg.get("dropbox_token", ""))
        self.dropbox_token_entry.set_visibility(False)  # Hide token
        self.dropbox_token_entry.set_placeholder_text("sl.xxxxx...")
        dropbox_token_box.pack_start(dropbox_token_label, False, False, 0)
        dropbox_token_box.pack_start(self.dropbox_token_entry, True, True, 0)
        dropbox_box.pack_start(dropbox_token_box, False, False, 0)

        dropbox_help = Gtk.Label(xalign=0)
        dropbox_help.set_markup(
            '<small><a href="https://www.dropbox.com/developers/apps">'
            + _("Get token from Dropbox Developer Console")
            + "</a></small>"
        )
        dropbox_box.pack_start(dropbox_help, False, False, 0)

        self.dropbox_frame.add(dropbox_box)
        box.pack_start(self.dropbox_frame, False, False, 0)

        # Google Drive settings frame
        self.gdrive_frame = Gtk.Frame(label=_("Google Drive Settings"))
        gdrive_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        gdrive_box.set_border_width(5)

        gdrive_folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        gdrive_folder_label = Gtk.Label(label=_("Folder ID:"), xalign=0)
        gdrive_folder_label.set_size_request(100, -1)
        self.gdrive_folder_entry = Gtk.Entry()
        self.gdrive_folder_entry.set_text(self.cfg.get("gdrive_folder_id", ""))
        self.gdrive_folder_entry.set_placeholder_text("(optional)")
        gdrive_folder_box.pack_start(gdrive_folder_label, False, False, 0)
        gdrive_folder_box.pack_start(self.gdrive_folder_entry, True, True, 0)
        gdrive_box.pack_start(gdrive_folder_box, False, False, 0)

        gdrive_help = Gtk.Label(xalign=0)
        gdrive_help.set_markup("<small>Requires: <b>gdrive</b> CLI or <b>rclone</b></small>")
        gdrive_box.pack_start(gdrive_help, False, False, 0)

        self.gdrive_frame.add(gdrive_box)
        box.pack_start(self.gdrive_frame, False, False, 0)

        # Info
        self.upload_info_label = Gtk.Label(xalign=0)
        self.upload_info_label.set_line_wrap(True)
        box.pack_start(self.upload_info_label, False, False, 0)

        # Update visibility based on current service
        self._update_upload_settings_visibility()

        return box

    def _on_upload_service_changed(self, combo: Gtk.ComboBoxText) -> None:
        """Update visibility of provider-specific settings."""
        self._update_upload_settings_visibility()

    def _update_upload_settings_visibility(self) -> None:
        """Show/hide provider-specific settings based on selected service."""
        service = self.service_combo.get_active_text() or "imgur"

        self.s3_frame.set_visible(service == "s3")
        self.dropbox_frame.set_visible(service == "dropbox")
        self.gdrive_frame.set_visible(service == "gdrive")

        # Update info text
        info_texts = {
            "none": "<i>Upload disabled</i>",
            "imgur": (
                "<b>Imgur</b>: Free anonymous image hosting\n"
                "URL is copied to clipboard automatically\n"
                "<i>Requires: curl</i>"
            ),
            "fileio": (
                "<b>file.io</b>: Temporary file sharing\n"
                "Files are deleted after first download\n"
                "<i>Requires: curl</i>"
            ),
            "s3": (
                "<b>Amazon S3</b>: Cloud storage\n"
                "Configure AWS CLI with credentials first\n"
                "<i>Requires: aws-cli</i>"
            ),
            "dropbox": (
                "<b>Dropbox</b>: Cloud storage with sharing\n"
                "Create an app and generate access token\n"
                "<i>Requires: curl</i>"
            ),
            "gdrive": (
                "<b>Google Drive</b>: Cloud storage\n"
                "Configure gdrive or rclone first\n"
                "<i>Requires: gdrive or rclone</i>"
            ),
        }
        self.upload_info_label.set_markup(info_texts.get(service, ""))

    def _create_editor_settings(self) -> Gtk.Box:
        """Create editor settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Grid settings header
        grid_header = Gtk.Label(xalign=0)
        grid_header.set_markup(_("<b>Grid Settings</b>"))
        box.pack_start(grid_header, False, False, 0)

        # Grid size slider
        size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        size_label = Gtk.Label(label=_("Grid size (pixels):"), xalign=0)
        size_label.set_size_request(150, -1)

        # Value label that updates with slider
        self.grid_size_value = Gtk.Label(label=f"{self.cfg.get('grid_size', 20)}px")
        self.grid_size_value.set_size_request(50, -1)

        # Slider for grid size (5-100 pixels)
        self.grid_size_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 5, 100, 5)
        self.grid_size_scale.set_value(self.cfg.get("grid_size", 20))
        self.grid_size_scale.set_draw_value(False)  # We use our own label
        self.grid_size_scale.set_hexpand(True)
        self.grid_size_scale.connect("value-changed", self._on_grid_size_changed)

        size_box.pack_start(size_label, False, False, 0)
        size_box.pack_start(self.grid_size_scale, True, True, 0)
        size_box.pack_start(self.grid_size_value, False, False, 0)
        box.pack_start(size_box, False, False, 0)

        # Snap to grid default checkbox
        self.snap_grid_check = Gtk.CheckButton(
            label=_("Enable grid snap by default (Ctrl+' to toggle)")
        )
        self.snap_grid_check.set_active(self.cfg.get("snap_to_grid", False))
        box.pack_start(self.snap_grid_check, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Grid info
        info_label = Gtk.Label(xalign=0)
        info_label.set_markup(
            _("<b>Keyboard Shortcuts:</b>")
            + "\n\n"
            + _("• <b>Ctrl+'</b>: Toggle grid snap on/off")
            + "\n"
            + _("• <b>Arrow keys</b>: Nudge 1px (or snap to grid)")
            + "\n"
            + _("• <b>Shift+Arrow</b>: Nudge 10px")
            + "\n\n"
            + _("<i>Grid snap helps align elements precisely.</i>")
        )
        info_label.set_line_wrap(True)
        box.pack_start(info_label, False, False, 0)

        return box

    def _on_grid_size_changed(self, scale: Gtk.Scale) -> None:
        """Update grid size value label."""
        value = int(scale.get_value())
        self.grid_size_value.set_text(f"{value}px")

    def _create_hotkey_settings(self) -> Gtk.Box:
        """Create hotkey settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Header
        header = Gtk.Label(xalign=0)
        header.set_markup(
            _("<b>Global Keyboard Shortcuts</b>")
            + "\n"
            + _("<small>Click a field, then press your desired key combination</small>")
        )
        box.pack_start(header, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # Create grid for hotkey entries
        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(10)

        # Hotkey definitions: (config_key, label, default)
        hotkeys = [
            ("hotkey_fullscreen", _("Fullscreen Capture:"), "<Control><Shift>F"),
            ("hotkey_region", _("Region Capture:"), "<Control><Shift>R"),
            ("hotkey_window", _("Window Capture:"), "<Control><Shift>W"),
            ("hotkey_record_gif", _("Record GIF:"), "<Control><Alt>G"),
            ("hotkey_scroll_capture", _("Scroll Capture:"), "<Control><Alt>S"),
        ]

        self.hotkey_entries = {}

        for row, (key, label_text, default) in enumerate(hotkeys):
            label = Gtk.Label(label=label_text, xalign=0)
            label.set_size_request(150, -1)
            grid.attach(label, 0, row, 1, 1)

            entry = HotkeyEntry(self.cfg.get(key, default))
            self.hotkey_entries[key] = entry
            grid.attach(entry, 1, row, 1, 1)

            # Reset button for this hotkey
            reset_btn = Gtk.Button(label=_("Reset"))
            reset_btn.set_tooltip_text(f"Reset to default: {self._format_hotkey(default)}")
            reset_btn.connect("clicked", self._on_reset_hotkey, key, default)
            grid.attach(reset_btn, 2, row, 1, 1)

        box.pack_start(grid, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Info section
        info_label = Gtk.Label(xalign=0)
        info_label.set_markup(
            _("<b>Notes:</b>")
            + "\n\n"
            + _("• Hotkeys require at least one modifier (Ctrl, Alt, Shift, Super)")
            + "\n"
            + _("• Press Escape to cancel while setting a hotkey")
            + "\n"
            + _("• Hotkeys work globally on GNOME desktop")
            + "\n"
            + _("• Restart LikX after changing hotkeys for them to take effect")
        )
        info_label.set_line_wrap(True)
        box.pack_start(info_label, False, False, 0)

        return box

    def _format_hotkey(self, hotkey: str) -> str:
        """Format hotkey for display."""
        display = hotkey
        display = display.replace("<Control>", "Ctrl+")
        display = display.replace("<Shift>", "Shift+")
        display = display.replace("<Alt>", "Alt+")
        display = display.replace("<Super>", "Super+")
        return display

    def _create_language_settings(self) -> Gtk.Box:
        """Create language settings tab."""
        from ..i18n import get_available_languages

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # Header
        header = Gtk.Label(xalign=0)
        header.set_markup(_("<b>Language Settings</b>"))
        box.pack_start(header, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 5)

        # Language selection
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lang_label = Gtk.Label(label=_("Interface language:"), xalign=0)
        lang_label.set_size_request(150, -1)

        self.language_combo = Gtk.ComboBoxText()

        # Add system default option
        self.language_combo.append("system", _("System Default"))

        # Add available languages
        languages = get_available_languages()
        for code, name in languages:
            self.language_combo.append(code, name)

        # Set current language
        current_lang = self.cfg.get("language", "system")
        self.language_combo.set_active_id(current_lang)

        lang_box.pack_start(lang_label, False, False, 0)
        lang_box.pack_start(self.language_combo, False, False, 0)
        box.pack_start(lang_box, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 10)

        # Info
        info_label = Gtk.Label(xalign=0)
        info_label.set_markup(
            _(
                "<b>Note:</b> Restart LikX after changing the language\n"
                "for the changes to take full effect."
            )
        )
        info_label.set_line_wrap(True)
        box.pack_start(info_label, False, False, 0)

        # Help contribute
        contribute_label = Gtk.Label(xalign=0)
        contribute_label.set_markup(
            _(
                "\n<b>Help translate LikX!</b>\n"
                "Translation files are in the <tt>locale/</tt> directory."
            )
        )
        contribute_label.set_line_wrap(True)
        box.pack_start(contribute_label, False, False, 0)

        return box

    def _on_reset_hotkey(self, button: Gtk.Button, key: str, default: str) -> None:
        """Reset a single hotkey to its default value."""
        if key in self.hotkey_entries:
            self.hotkey_entries[key].set_hotkey(default)

    def _browse_directory(self, button: Gtk.Button) -> None:
        """Browse for save directory."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select Save Directory"),
            parent=self.dialog,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        current_dir = Path(self.dir_entry.get_text()).expanduser()
        if current_dir.exists():
            dialog.set_current_folder(str(current_dir))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.dir_entry.set_text(dialog.get_filename())

        dialog.destroy()

    def _save_settings(self) -> None:
        """Save the settings."""
        self.cfg["save_directory"] = self.dir_entry.get_text()
        self.cfg["default_format"] = self.format_combo.get_active_text() or "png"
        self.cfg["auto_save"] = self.auto_save_check.get_active()
        self.cfg["copy_to_clipboard"] = self.clipboard_check.get_active()
        self.cfg["show_notification"] = self.notification_check.get_active()
        self.cfg["editor_enabled"] = self.editor_check.get_active()
        self.cfg["delay_seconds"] = int(self.delay_spin.get_value())
        self.cfg["include_cursor"] = self.cursor_check.get_active()
        self.cfg["upload_service"] = self.service_combo.get_active_text() or "imgur"
        self.cfg["auto_upload"] = self.auto_upload_check.get_active()
        # S3 settings
        self.cfg["s3_bucket"] = self.s3_bucket_entry.get_text().strip()
        self.cfg["s3_region"] = self.s3_region_entry.get_text().strip() or "us-east-1"
        self.cfg["s3_public"] = self.s3_public_check.get_active()
        # Dropbox settings
        self.cfg["dropbox_token"] = self.dropbox_token_entry.get_text().strip()
        # Google Drive settings
        self.cfg["gdrive_folder_id"] = self.gdrive_folder_entry.get_text().strip()
        # Editor settings
        self.cfg["grid_size"] = int(self.grid_size_scale.get_value())
        self.cfg["snap_to_grid"] = self.snap_grid_check.get_active()
        # GIF settings
        self.cfg["gif_quality"] = self.gif_quality_combo.get_active_id() or "medium"
        self.cfg["gif_fps"] = int(self.gif_fps_spin.get_value())
        self.cfg["gif_colors"] = int(self.gif_colors_combo.get_active_id() or "256")
        self.cfg["gif_scale_factor"] = float(self.gif_scale_combo.get_active_id() or "1.0")
        self.cfg["gif_dither"] = self.gif_dither_combo.get_active_id() or "bayer"
        self.cfg["gif_loop"] = int(self.gif_loop_combo.get_active_id() or "0")
        self.cfg["gif_optimize"] = self.gif_optimize_check.get_active()
        self.cfg["gif_max_duration"] = int(self.gif_max_duration_spin.get_value())
        # Hotkey settings - collect changes for live update
        hotkey_updates = {}
        for key, entry in self.hotkey_entries.items():
            hotkey = entry.get_hotkey()
            if hotkey:
                # Track if hotkey changed
                if hotkey != self.cfg.get(key):
                    hotkey_updates[key] = hotkey
                self.cfg[key] = hotkey
        # Language settings
        self.cfg["language"] = self.language_combo.get_active_id() or "system"

        if config.save_config(self.cfg):
            # Apply hotkey changes immediately if callback provided
            if self.on_hotkeys_changed and hotkey_updates:
                self.on_hotkeys_changed(hotkey_updates)

            show_notification(
                _("Settings Saved"),
                _("Your preferences have been saved."),
            )

    def _reset_to_defaults(self) -> None:
        """Reset settings to defaults."""
        if config.reset_config():
            show_notification(_("Settings Reset"), _("All settings reset to defaults"))
