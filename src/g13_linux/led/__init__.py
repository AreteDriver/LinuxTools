"""
G13 LED Control Module

Provides RGB color management, effects engine, and LED controller.
"""

from .colors import RGB, NAMED_COLORS, blend, brighten, dim
from .effects import EffectType, solid, pulse, rainbow, fade, alert
from .controller import LEDController

__all__ = [
    "RGB",
    "NAMED_COLORS",
    "blend",
    "brighten",
    "dim",
    "EffectType",
    "solid",
    "pulse",
    "rainbow",
    "fade",
    "alert",
    "LEDController",
]
