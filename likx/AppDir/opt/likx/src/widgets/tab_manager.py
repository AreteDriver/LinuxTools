"""Tab management for LikX editor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, List, Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from ..i18n import _  # noqa: E402

if TYPE_CHECKING:
    from ..capture import CaptureResult
    from ..editor import EditorState


@dataclass
class TabContent:
    """Content for a single editor tab."""

    result: CaptureResult
    editor_state: EditorState
    drawing_area: Gtk.DrawingArea
    scrolled_window: Gtk.ScrolledWindow
    tab_label: Gtk.Box
    filepath: Optional[str] = None
    modified: bool = False


class TabManager:
    """Manages editor tabs in a Gtk.Notebook.

    Uses callback-based design to avoid direct coupling to EditorWindow.
    """

    def __init__(
        self,
        notebook: Gtk.Notebook,
        window: Gtk.Window,
        create_editor_state: Callable[[CaptureResult], EditorState],
        connect_drawing_area_events: Callable[[Gtk.DrawingArea], None],
        on_tab_switched: Callable[[int, TabContent], None],
        update_title: Callable[[], None],
    ):
        """Initialize the tab manager.

        Args:
            notebook: The Gtk.Notebook widget to manage
            window: Parent window for dialogs
            create_editor_state: Callback to create EditorState from CaptureResult
            connect_drawing_area_events: Callback to connect drawing area events
            on_tab_switched: Callback when tab is switched (index, tab_content)
            update_title: Callback to update window title
        """
        self._notebook = notebook
        self._window = window
        self._create_editor_state = create_editor_state
        self._connect_drawing_area_events = connect_drawing_area_events
        self._on_tab_switched = on_tab_switched
        self._update_title = update_title

        self._tabs: List[TabContent] = []
        self._current_tab_index: int = 0

        # Connect notebook signals
        self._notebook.connect("switch-page", self._on_notebook_switch_page)

    @property
    def tabs(self) -> List[TabContent]:
        """Get the list of tabs."""
        return self._tabs

    @property
    def current_tab_index(self) -> int:
        """Get the current tab index."""
        return self._current_tab_index

    @current_tab_index.setter
    def current_tab_index(self, value: int) -> None:
        """Set the current tab index."""
        self._current_tab_index = value

    @property
    def current_tab(self) -> Optional[TabContent]:
        """Get the current tab content."""
        if 0 <= self._current_tab_index < len(self._tabs):
            return self._tabs[self._current_tab_index]
        return None

    def add_tab(self, result: CaptureResult, switch_to: bool = True) -> int:
        """Add a new tab with capture result.

        Args:
            result: The capture result to add.
            switch_to: Whether to switch to the new tab.

        Returns:
            The index of the new tab.
        """
        editor_state = self._create_editor_state(result)

        # Create drawing area for this tab
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(
            result.pixbuf.get_width(), result.pixbuf.get_height()
        )

        # Connect events via callback
        self._connect_drawing_area_events(drawing_area)

        drawing_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.SCROLL_MASK
        )

        # Scrolled window for this tab
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(drawing_area)

        # Create tab label with close button
        tab_label = self._create_tab_label(len(self._tabs))

        # Create tab content
        tab = TabContent(
            result=result,
            editor_state=editor_state,
            drawing_area=drawing_area,
            scrolled_window=scrolled,
            tab_label=tab_label,
        )
        self._tabs.append(tab)

        # Add to notebook
        page_num = self._notebook.append_page(scrolled, tab_label)
        self._notebook.set_tab_reorderable(scrolled, True)

        # Show the new widgets
        scrolled.show_all()
        tab_label.show_all()

        # Update tab bar visibility
        self._notebook.set_show_tabs(len(self._tabs) > 1)

        if switch_to:
            self._notebook.set_current_page(page_num)
            self._current_tab_index = page_num

        self._update_title()
        return page_num

    def _create_tab_label(self, index: int) -> Gtk.Box:
        """Create tab label with title and close button."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        label = Gtk.Label(label=f"Capture {index + 1}")
        box.pack_start(label, True, True, 0)

        close_btn = Gtk.Button()
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.set_focus_on_click(False)
        close_img = Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        close_btn.add(close_img)
        close_btn.connect("clicked", self._on_close_tab_clicked, index)
        box.pack_end(close_btn, False, False, 0)

        box.show_all()
        return box

    def _on_close_tab_clicked(self, button: Gtk.Button, index: int) -> None:
        """Handle close button click on tab."""
        # Find the actual tab index (might have changed due to reordering)
        for i, tab in enumerate(self._tabs):
            if tab.tab_label == button.get_parent():
                self.close_tab(i)
                return

    def close_tab(self, index: int) -> bool:
        """Close tab at index.

        Returns:
            False if cancelled, True if closed.
        """
        if index < 0 or index >= len(self._tabs):
            return False

        tab = self._tabs[index]

        # Check for unsaved changes (if modified flag is set)
        if tab.modified:
            dialog = Gtk.MessageDialog(
                transient_for=self._window,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Unsaved Changes"),
                secondary_text=_("This capture has unsaved changes. Close anyway?"),
            )
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.YES:
                return False

        # Remove tab
        self._notebook.remove_page(index)
        self._tabs.pop(index)

        # Update remaining tab indices in labels
        self._reindex_tabs()

        # If no tabs left, close window
        if len(self._tabs) == 0:
            self._window.destroy()
            return True

        # Update current tab index
        self._current_tab_index = min(self._current_tab_index, len(self._tabs) - 1)
        self._notebook.set_current_page(self._current_tab_index)

        # Update tab bar visibility
        self._notebook.set_show_tabs(len(self._tabs) > 1)

        self._update_title()
        return True

    def _reindex_tabs(self) -> None:
        """Update tab label numbers after tab removal."""
        for i, tab in enumerate(self._tabs):
            # Find the label widget in the tab_label box
            for child in tab.tab_label.get_children():
                if isinstance(child, Gtk.Label):
                    child.set_text(f"Capture {i + 1}")
                    break

    def _on_notebook_switch_page(
        self, notebook: Gtk.Notebook, page: Gtk.Widget, page_num: int
    ) -> None:
        """Handle tab switching - sync UI with new tab's state."""
        if page_num >= len(self._tabs):
            return

        self._current_tab_index = page_num
        tab = self._tabs[page_num]

        # Notify parent of tab switch
        self._on_tab_switched(page_num, tab)

    def get_current_drawing_area(self) -> Optional[Gtk.DrawingArea]:
        """Get the drawing area of the current tab."""
        tab = self.current_tab
        return tab.drawing_area if tab else None

    def get_current_editor_state(self) -> Optional[EditorState]:
        """Get the editor state of the current tab."""
        tab = self.current_tab
        return tab.editor_state if tab else None

    def get_current_result(self) -> Optional[CaptureResult]:
        """Get the capture result of the current tab."""
        tab = self.current_tab
        return tab.result if tab else None
