"""Configuration module for LikX."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "save_directory": str(Path.home() / "Pictures" / "Screenshots"),
    "default_format": "png",
    "supported_formats": ["png", "jpg", "jpeg", "bmp", "gif"],
    "hotkey_fullscreen": "<Control><Shift>F",
    "hotkey_region": "<Control><Shift>R",
    "hotkey_window": "<Control><Shift>W",
    "auto_save": False,
    "copy_to_clipboard": True,
    "show_notification": True,
    "include_cursor": False,
    "delay_seconds": 0,
    "editor_enabled": True,
    "theme": "system",
    "upload_service": "imgur",  # imgur, fileio, s3, dropbox, gdrive, none
    "auto_upload": False,
    # S3 settings
    "s3_bucket": "",
    "s3_region": "us-east-1",
    "s3_public": True,  # Make uploaded files public
    # Dropbox settings
    "dropbox_token": "",  # Access token from https://www.dropbox.com/developers/apps
    # Google Drive settings
    "gdrive_folder_id": "",  # Optional folder ID to upload to
    "gdrive_rclone_remote": "gdrive",  # rclone remote name if using rclone
    # Editor settings
    "grid_size": 20,  # Grid snap size in pixels (5-100)
    "snap_to_grid": False,  # Whether grid snap is enabled by default
    # GIF recording settings
    "gif_fps": 15,  # Frames per second (10-30)
    "gif_quality": "medium",  # low, medium, high
    "gif_max_duration": 60,  # Safety limit in seconds
    "gif_colors": 256,  # Color palette size (64-256)
    "gif_scale_factor": 1.0,  # Downscale factor (0.25-1.0)
    "gif_dither": "bayer",  # none, bayer, floyd_steinberg, sierra2
    "gif_loop": 0,  # Loop count: 0=infinite, 1=once, 2+=specific count
    "gif_optimize": True,  # Use gifsicle optimization if available
    "hotkey_record_gif": "<Control><Alt>G",
    "hotkey_record_video": "<Control><Alt>V",
    # Video recording settings
    "video_format": "mp4",  # mp4, webm
    "video_quality": "medium",  # low, medium, high
    # Scroll capture settings
    "scroll_delay_ms": 300,  # Delay between scroll+capture cycles
    "scroll_max_frames": 50,  # Safety limit
    "scroll_overlap_search": 150,  # Max pixels to search for overlap
    "scroll_ignore_top": 0.15,  # Ignore top 15% (fixed headers)
    "scroll_ignore_bottom": 0.15,  # Ignore bottom 15% (fixed footers)
    "scroll_confidence": 0.7,  # Template matching confidence threshold
    "hotkey_scroll_capture": "<Control><Alt>S",
    # Language settings
    "language": "system",  # "system" or language code like "en", "es", "fr"
    # Queue mode settings
    "queue_mode_enabled": False,
    "queue_persist": False,  # Save queue across restarts
    "queue_max_size": 50,
    # System tray settings
    "tray_enabled": True,
    "close_to_tray": True,  # Close button minimizes to tray
    "start_minimized": False,  # Start hidden in tray
}

# Configuration file path
CONFIG_DIR = Path.home() / ".config" / "likx"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    return CONFIG_DIR


def get_config_file() -> Path:
    """Get the configuration file path."""
    return CONFIG_FILE


def ensure_config_dir() -> bool:
    """Ensure the configuration directory exists."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                user_config = json.load(f)
                config.update(user_config)
        except (OSError, json.JSONDecodeError):
            pass

    return config


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    if not ensure_config_dir():
        return False

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except OSError:
        return False


def get_setting(key: str, default: Optional[Any] = None) -> Any:
    """Get a specific configuration setting."""
    config = load_config()
    return config.get(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Set a specific configuration setting."""
    config = load_config()
    config[key] = value
    return save_config(config)


def reset_config() -> bool:
    """Reset configuration to defaults."""
    return save_config(DEFAULT_CONFIG.copy())


def validate_format(format_str: str) -> bool:
    """Validate if a format string is supported."""
    config = load_config()
    supported = config.get("supported_formats", DEFAULT_CONFIG["supported_formats"])
    return format_str.lower() in [fmt.lower() for fmt in supported]


def get_save_path(
    filename: Optional[str] = None, format_str: Optional[str] = None
) -> Path:
    """Generate a save path for a screenshot."""
    config = load_config()
    save_dir = Path(config.get("save_directory", DEFAULT_CONFIG["save_directory"]))

    save_dir = Path(save_dir).expanduser()
    save_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}"

    if format_str is None:
        format_str = config.get("default_format", DEFAULT_CONFIG["default_format"])

    return save_dir / f"{filename}.{format_str}"


def check_tool_available(command: List[str], timeout: int = 2) -> bool:
    """Check if an external tool is available.

    Args:
        command: Command to run (e.g., ["ffmpeg", "-version"])
        timeout: Timeout in seconds (default: 2)

    Returns:
        True if the tool is available and returns exit code 0
    """
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# --- Annotation Templates ---

TEMPLATES_FILE = CONFIG_DIR / "templates.json"

# Default templates for common annotation styles
DEFAULT_TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "Red Arrow",
        "tool": "ARROW",
        "color": [255, 0, 0, 255],
        "stroke_width": 3.0,
        "arrow_style": "FILLED",
    },
    {
        "name": "Yellow Highlight",
        "tool": "HIGHLIGHTER",
        "color": [255, 255, 0, 128],
        "stroke_width": 20.0,
    },
    {
        "name": "Blue Box",
        "tool": "RECTANGLE",
        "color": [0, 100, 255, 255],
        "stroke_width": 2.0,
    },
    {
        "name": "Text Label",
        "tool": "TEXT",
        "color": [0, 0, 0, 255],
        "font_size": 18,
        "font_bold": True,
        "font_family": "Sans",
    },
    {
        "name": "Blur Sensitive",
        "tool": "BLUR",
        "stroke_width": 30.0,
    },
]


def load_templates() -> List[Dict[str, Any]]:
    """Load annotation templates from file."""
    if TEMPLATES_FILE.exists():
        try:
            with open(TEMPLATES_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return DEFAULT_TEMPLATES.copy()


def save_templates(templates: List[Dict[str, Any]]) -> bool:
    """Save annotation templates to file."""
    if not ensure_config_dir():
        return False
    try:
        with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2)
        return True
    except OSError:
        return False


def add_template(template: Dict[str, Any]) -> bool:
    """Add a new annotation template."""
    templates = load_templates()
    templates.append(template)
    return save_templates(templates)


def delete_template(name: str) -> bool:
    """Delete an annotation template by name."""
    templates = load_templates()
    templates = [t for t in templates if t.get("name") != name]
    return save_templates(templates)


def get_template(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific template by name."""
    templates = load_templates()
    for t in templates:
        if t.get("name") == name:
            return t
    return None


# --- Color Palette Presets ---

COLOR_PALETTES: Dict[str, List[List[int]]] = {
    "Default": [
        [255, 0, 0, 255],      # Red
        [0, 255, 0, 255],      # Green
        [0, 0, 255, 255],      # Blue
        [255, 255, 0, 255],    # Yellow
        [255, 165, 0, 255],    # Orange
        [128, 0, 128, 255],    # Purple
        [0, 255, 255, 255],    # Cyan
        [255, 192, 203, 255],  # Pink
        [0, 0, 0, 255],        # Black
        [255, 255, 255, 255],  # White
    ],
    "Pastel": [
        [255, 179, 186, 255],  # Pastel pink
        [255, 223, 186, 255],  # Pastel peach
        [255, 255, 186, 255],  # Pastel yellow
        [186, 255, 201, 255],  # Pastel green
        [186, 225, 255, 255],  # Pastel blue
        [218, 186, 255, 255],  # Pastel purple
        [255, 186, 255, 255],  # Pastel magenta
        [186, 255, 255, 255],  # Pastel cyan
        [230, 230, 230, 255],  # Light gray
        [100, 100, 100, 255],  # Dark gray
    ],
    "Neon": [
        [255, 0, 102, 255],    # Neon pink
        [255, 102, 0, 255],    # Neon orange
        [204, 255, 0, 255],    # Neon yellow
        [0, 255, 102, 255],    # Neon green
        [0, 204, 255, 255],    # Neon cyan
        [102, 0, 255, 255],    # Neon purple
        [255, 0, 255, 255],    # Neon magenta
        [0, 255, 255, 255],    # Neon aqua
        [255, 255, 255, 255],  # White
        [0, 0, 0, 255],        # Black
    ],
    "Monochrome": [
        [0, 0, 0, 255],        # Black
        [32, 32, 32, 255],
        [64, 64, 64, 255],
        [96, 96, 96, 255],
        [128, 128, 128, 255],
        [160, 160, 160, 255],
        [192, 192, 192, 255],
        [224, 224, 224, 255],
        [240, 240, 240, 255],
        [255, 255, 255, 255],  # White
    ],
    "Earth": [
        [139, 90, 43, 255],    # Saddle brown
        [160, 82, 45, 255],    # Sienna
        [210, 180, 140, 255],  # Tan
        [107, 142, 35, 255],   # Olive drab
        [85, 107, 47, 255],    # Dark olive
        [34, 139, 34, 255],    # Forest green
        [46, 139, 87, 255],    # Sea green
        [70, 130, 180, 255],   # Steel blue
        [112, 128, 144, 255],  # Slate gray
        [47, 79, 79, 255],     # Dark slate
    ],
}


def get_color_palettes() -> Dict[str, List[List[int]]]:
    """Get all available color palettes."""
    return COLOR_PALETTES.copy()


def get_palette(name: str) -> List[List[int]]:
    """Get a specific color palette by name."""
    return COLOR_PALETTES.get(name, COLOR_PALETTES["Default"])
