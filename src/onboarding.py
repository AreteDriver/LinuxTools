"""Interactive Onboarding Tooltips for LikX.

Provides a first-run tutorial with progressive tooltips pointing to key features.
"""

from __future__ import annotations

from typing import Callable, List, Optional

try:
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk

    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False

from . import config
from .i18n import _

# Module-level flag to prevent CSS provider accumulation
_css_applied = False


class OnboardingStep:
    """Represents a single onboarding tooltip step."""

    def __init__(
        self,
        target_id: str,
        title: str,
        message: str,
        position: str = "bottom",  # top, bottom, left, right
        highlight: bool = True,
    ):
        self.target_id = target_id
        self.title = title
        self.message = message
        self.position = position
        self.highlight = highlight


class OnboardingTooltip:
    """A styled tooltip window for onboarding."""

    def __init__(self, parent_window: Gtk.Window):
        if not GTK_AVAILABLE:
            raise RuntimeError("GTK is not available")

        self.parent_window = parent_window

        # Create popup window
        self.popup = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.popup.set_type_hint(Gdk.WindowTypeHint.TOOLTIP)
        self.popup.set_decorated(False)
        self.popup.set_skip_taskbar_hint(True)
        self.popup.set_transient_for(parent_window)

        self._apply_styles()

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.get_style_context().add_class("onboarding-tooltip")
        self.popup.add(main_box)

        # Title
        self.title_label = Gtk.Label()
        self.title_label.get_style_context().add_class("onboarding-title")
        self.title_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.title_label, False, False, 0)

        # Message
        self.message_label = Gtk.Label()
        self.message_label.get_style_context().add_class("onboarding-message")
        self.message_label.set_line_wrap(True)
        self.message_label.set_max_width_chars(40)
        self.message_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.message_label, False, False, 0)

        # Step indicator and buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_margin_top(8)
        main_box.pack_start(button_box, False, False, 0)

        self.step_label = Gtk.Label()
        self.step_label.get_style_context().add_class("onboarding-step")
        button_box.pack_start(self.step_label, False, False, 0)

        button_box.pack_start(Gtk.Box(), True, True, 0)  # Spacer

        self.skip_btn = Gtk.Button(label=_("Skip"))
        self.skip_btn.get_style_context().add_class("onboarding-btn")
        self.skip_btn.get_style_context().add_class("skip-btn")
        button_box.pack_start(self.skip_btn, False, False, 0)

        self.next_btn = Gtk.Button(label=_("Next"))
        self.next_btn.get_style_context().add_class("onboarding-btn")
        self.next_btn.get_style_context().add_class("next-btn")
        button_box.pack_start(self.next_btn, False, False, 0)

    def _apply_styles(self) -> None:
        """Apply CSS styles (only once per process)."""
        global _css_applied
        if _css_applied:
            return
        _css_applied = True

        css = b"""
        .onboarding-tooltip {
            background: linear-gradient(135deg, #2d2d44 0%, #1e1e2e 100%);
            border: 2px solid #6688dd;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }
        .onboarding-title {
            color: #ffffff;
            font-size: 15px;
            font-weight: bold;
        }
        .onboarding-message {
            color: #c0c0d0;
            font-size: 13px;
        }
        .onboarding-step {
            color: #8888aa;
            font-size: 11px;
        }
        .onboarding-btn {
            min-width: 60px;
            min-height: 28px;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
        }
        .skip-btn {
            background: transparent;
            border: 1px solid #555577;
            color: #8888aa;
        }
        .skip-btn:hover {
            background: rgba(100, 100, 140, 0.2);
            color: #aaaacc;
        }
        .next-btn {
            background: #6688dd;
            border: none;
            color: #ffffff;
        }
        .next-btn:hover {
            background: #7799ee;
        }
        .onboarding-highlight {
            box-shadow: 0 0 0 3px rgba(102, 136, 221, 0.6),
                        0 0 20px rgba(102, 136, 221, 0.4);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def show(
        self,
        title: str,
        message: str,
        step_num: int,
        total_steps: int,
        target_widget: Optional[Gtk.Widget],
        position: str,
        on_next: Callable[[], None],
        on_skip: Callable[[], None],
    ) -> None:
        """Show the tooltip.

        Args:
            title: Tooltip title
            message: Tooltip message
            step_num: Current step number (1-indexed)
            total_steps: Total number of steps
            target_widget: Widget to point to (None for center of screen)
            position: Position relative to target (top, bottom, left, right)
            on_next: Callback for Next button
            on_skip: Callback for Skip button
        """
        self.title_label.set_text(title)
        self.message_label.set_text(message)
        self.step_label.set_text(f"{step_num}/{total_steps}")

        # Update button labels for last step
        if step_num == total_steps:
            self.next_btn.set_label(_("Got it!"))
        else:
            self.next_btn.set_label(_("Next"))

        # Connect button handlers (disconnect old ones first)
        for handler_id in getattr(self, "_handler_ids", []):
            try:
                self.next_btn.disconnect(handler_id[0])
                self.skip_btn.disconnect(handler_id[1])
            except Exception:
                pass

        next_id = self.next_btn.connect("clicked", lambda b: on_next())
        skip_id = self.skip_btn.connect("clicked", lambda b: on_skip())
        self._handler_ids = [(next_id, skip_id)]

        # Show popup
        self.popup.show_all()

        # Position near target widget
        if target_widget and target_widget.get_realized():
            self._position_near_widget(target_widget, position)
        else:
            self._position_center()

    def _position_near_widget(self, widget: Gtk.Widget, position: str) -> None:
        """Position tooltip near the target widget."""
        # Get widget's screen position
        alloc = widget.get_allocation()
        window = widget.get_window()
        if not window:
            self._position_center()
            return

        origin = window.get_origin()
        if not origin[0]:
            self._position_center()
            return

        win_x, win_y = origin[1], origin[2]

        # Get tooltip size
        self.popup.show_all()
        tip_width = self.popup.get_allocated_width()
        tip_height = self.popup.get_allocated_height()

        # Calculate position
        margin = 12
        if position == "bottom":
            x = win_x + alloc.x + (alloc.width - tip_width) // 2
            y = win_y + alloc.y + alloc.height + margin
        elif position == "top":
            x = win_x + alloc.x + (alloc.width - tip_width) // 2
            y = win_y + alloc.y - tip_height - margin
        elif position == "right":
            x = win_x + alloc.x + alloc.width + margin
            y = win_y + alloc.y + (alloc.height - tip_height) // 2
        elif position == "left":
            x = win_x + alloc.x - tip_width - margin
            y = win_y + alloc.y + (alloc.height - tip_height) // 2
        else:
            x = win_x + alloc.x + (alloc.width - tip_width) // 2
            y = win_y + alloc.y + alloc.height + margin

        # Keep on screen
        screen = Gdk.Screen.get_default()
        x = max(10, min(x, screen.get_width() - tip_width - 10))
        y = max(10, min(y, screen.get_height() - tip_height - 10))

        self.popup.move(x, y)

    def _position_center(self) -> None:
        """Position tooltip in center of parent window."""
        self.popup.show_all()
        tip_width = self.popup.get_allocated_width()
        tip_height = self.popup.get_allocated_height()

        parent_alloc = self.parent_window.get_allocation()
        parent_pos = self.parent_window.get_position()

        x = parent_pos[0] + (parent_alloc.width - tip_width) // 2
        y = parent_pos[1] + (parent_alloc.height - tip_height) // 2

        self.popup.move(x, y)

    def hide(self) -> None:
        """Hide the tooltip."""
        self.popup.hide()


class OnboardingManager:
    """Manages the onboarding tutorial flow."""

    CONFIG_KEY = "onboarding_completed"

    def __init__(self, editor_window):
        """Initialize the onboarding manager.

        Args:
            editor_window: The EditorWindow instance
        """
        self.editor_window = editor_window
        self.tooltip = OnboardingTooltip(editor_window.window)
        self.current_step = 0
        self.steps = self._create_steps()
        self._highlighted_widget: Optional[Gtk.Widget] = None

    def _create_steps(self) -> List[OnboardingStep]:
        """Create the onboarding steps."""
        return [
            OnboardingStep(
                target_id="sidebar",
                title=_("Tool Sidebar"),
                message=_(
                    "Select drawing tools from this sidebar. Each tool has a keyboard shortcut shown in its tooltip."
                ),
                position="right",
            ),
            OnboardingStep(
                target_id="context_bar",
                title=_("Context Toolbar"),
                message=_(
                    "This toolbar adapts to show relevant options for the active tool - colors, sizes, and styles."
                ),
                position="bottom",
            ),
            OnboardingStep(
                target_id="color_picker",
                title=_("Color Picker"),
                message=_(
                    "Click any color to select it. The rainbow hex opens a custom color chooser. Recent colors appear below."
                ),
                position="bottom",
            ),
            OnboardingStep(
                target_id="drawing_area",
                title=_("Right-Click Radial Menu"),
                message=_(
                    "Right-click anywhere on the canvas to open a radial menu for quick tool selection."
                ),
                position="top",
            ),
            OnboardingStep(
                target_id="command_palette",
                title=_("Command Palette"),
                message=_(
                    "Press Ctrl+Shift+P to open the command palette. Search for any action or tool by name."
                ),
                position="bottom",
            ),
            OnboardingStep(
                target_id="actions",
                title=_("Quick Actions"),
                message=_(
                    "Save, copy, or upload your screenshot using these buttons. Keyboard shortcuts: Ctrl+S, Ctrl+C."
                ),
                position="bottom",
            ),
        ]

    def should_show(self) -> bool:
        """Check if onboarding should be shown."""
        cfg = config.load_config()
        return not cfg.get(self.CONFIG_KEY, False)

    def start(self) -> None:
        """Start the onboarding tutorial."""
        if not self.steps:
            return

        self.current_step = 0
        # Delay slightly to ensure window is fully shown
        GLib.timeout_add(500, self._show_current_step)

    def _get_target_widget(self, target_id: str) -> Optional[Gtk.Widget]:
        """Get the widget for the given target ID."""
        targets = {
            "sidebar": getattr(self.editor_window, "sidebar", None),
            "context_bar": getattr(self.editor_window, "context_bar", None),
            "color_picker": getattr(self.editor_window, "_hex_canvas", None),
            "drawing_area": getattr(self.editor_window, "drawing_area", None),
            "command_palette": None,  # No specific widget, show centered
            "actions": None,  # Will find action buttons
        }

        widget = targets.get(target_id)

        # Special handling for action buttons
        if target_id == "actions" and widget is None:
            # Try to find the action button container
            for child in self.editor_window.context_bar.get_children():
                if isinstance(child, Gtk.Box):
                    for btn in child.get_children():
                        if isinstance(btn, Gtk.Button):
                            label = btn.get_label()
                            if label and "\U0001f4be" in label:  # Save icon
                                return child

        return widget

    def _show_current_step(self) -> bool:
        """Show the current onboarding step."""
        if self.current_step >= len(self.steps):
            self._finish()
            return False

        step = self.steps[self.current_step]
        target = self._get_target_widget(step.target_id)

        # Remove previous highlight
        if self._highlighted_widget:
            self._highlighted_widget.get_style_context().remove_class("onboarding-highlight")
            self._highlighted_widget = None

        # Add highlight to target
        if target and step.highlight:
            target.get_style_context().add_class("onboarding-highlight")
            self._highlighted_widget = target

        self.tooltip.show(
            title=step.title,
            message=step.message,
            step_num=self.current_step + 1,
            total_steps=len(self.steps),
            target_widget=target,
            position=step.position,
            on_next=self._next_step,
            on_skip=self._skip,
        )

        return False  # Don't repeat timer

    def _next_step(self) -> None:
        """Advance to the next step."""
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self._finish()
        else:
            self._show_current_step()

    def _skip(self) -> None:
        """Skip the tutorial."""
        self._finish()

    def _finish(self) -> None:
        """Finish the onboarding tutorial."""
        # Remove highlight
        if self._highlighted_widget:
            self._highlighted_widget.get_style_context().remove_class("onboarding-highlight")
            self._highlighted_widget = None

        self.tooltip.hide()

        # Mark as completed
        cfg = config.load_config()
        cfg[self.CONFIG_KEY] = True
        config.save_config(cfg)

    def reset(self) -> None:
        """Reset onboarding to show again on next launch."""
        cfg = config.load_config()
        cfg[self.CONFIG_KEY] = False
        config.save_config(cfg)
