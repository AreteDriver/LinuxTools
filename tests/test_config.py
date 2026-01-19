"""Tests for config module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    COLOR_PALETTES,
    CONFIG_DIR,
    CONFIG_FILE,
    DEFAULT_CONFIG,
    DEFAULT_TEMPLATES,
    add_template,
    check_tool_available,
    delete_template,
    ensure_config_dir,
    get_color_palettes,
    get_config_dir,
    get_config_file,
    get_palette,
    get_save_path,
    get_setting,
    get_template,
    load_config,
    load_templates,
    reset_config,
    save_config,
    save_templates,
    set_setting,
    validate_format,
)


class TestDefaultConfig:
    """Test default configuration values."""

    def test_default_config_has_required_keys(self):
        required_keys = [
            "save_directory",
            "default_format",
            "supported_formats",
            "copy_to_clipboard",
            "show_notification",
        ]
        for key in required_keys:
            assert key in DEFAULT_CONFIG

    def test_default_format_is_png(self):
        assert DEFAULT_CONFIG["default_format"] == "png"

    def test_supported_formats_includes_common_types(self):
        formats = DEFAULT_CONFIG["supported_formats"]
        assert "png" in formats
        assert "jpg" in formats


class TestLoadConfig:
    """Test config loading."""

    def test_load_config_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)

    def test_load_config_has_default_values(self):
        config = load_config()
        assert "default_format" in config
        assert "save_directory" in config

    @patch("src.config.CONFIG_FILE")
    def test_load_config_with_missing_file(self, mock_file):
        mock_file.exists.return_value = False
        config = load_config()
        assert config == DEFAULT_CONFIG


class TestValidateFormat:
    """Test format validation."""

    def test_validate_png(self):
        assert validate_format("png") is True

    def test_validate_jpg(self):
        assert validate_format("jpg") is True

    def test_validate_jpeg(self):
        assert validate_format("jpeg") is True

    def test_validate_invalid_format(self):
        assert validate_format("xyz") is False

    def test_validate_case_insensitive(self):
        assert validate_format("PNG") is True
        assert validate_format("Png") is True


class TestGetSavePath:
    """Test save path generation."""

    def test_get_save_path_returns_path(self):
        path = get_save_path()
        assert isinstance(path, Path)

    def test_get_save_path_has_correct_extension(self):
        path = get_save_path(format_str="png")
        assert path.suffix == ".png"

    def test_get_save_path_with_custom_filename(self):
        path = get_save_path(filename="test_image", format_str="png")
        assert path.name == "test_image.png"

    def test_get_save_path_with_jpg_format(self):
        path = get_save_path(format_str="jpg")
        assert path.suffix == ".jpg"


class TestGetSetting:
    """Test getting individual settings."""

    def test_get_existing_setting(self):
        value = get_setting("default_format")
        assert value is not None

    def test_get_missing_setting_returns_default(self):
        value = get_setting("nonexistent_key", default="fallback")
        assert value == "fallback"

    def test_get_missing_setting_without_default(self):
        value = get_setting("nonexistent_key")
        assert value is None


class TestEditorSettings:
    """Test editor-related settings."""

    def test_default_config_has_grid_size(self):
        assert "grid_size" in DEFAULT_CONFIG
        assert DEFAULT_CONFIG["grid_size"] == 20

    def test_default_config_has_snap_to_grid(self):
        assert "snap_to_grid" in DEFAULT_CONFIG
        assert DEFAULT_CONFIG["snap_to_grid"] is False

    def test_grid_size_has_valid_range(self):
        grid_size = DEFAULT_CONFIG["grid_size"]
        assert 5 <= grid_size <= 100

    def test_load_config_includes_editor_settings(self):
        cfg = load_config()
        assert "grid_size" in cfg
        assert "snap_to_grid" in cfg


class TestCheckToolAvailable:
    """Test check_tool_available utility function."""

    def test_check_tool_available_with_existing_tool(self):
        """Test check with a tool that should exist (python)."""
        result = check_tool_available(["python3", "--version"])
        assert result is True

    def test_check_tool_available_with_nonexistent_tool(self):
        """Test check with a tool that doesn't exist."""
        result = check_tool_available(["nonexistent_tool_xyz", "--version"])
        assert result is False

    @patch("subprocess.run")
    def test_check_tool_available_with_timeout(self, mock_run):
        """Test handling of timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 2)
        result = check_tool_available(["slow_tool", "--version"])
        assert result is False

    @patch("subprocess.run")
    def test_check_tool_available_with_failure(self, mock_run):
        """Test handling of non-zero exit code."""
        from unittest.mock import MagicMock

        mock_run.return_value = MagicMock(returncode=1)
        result = check_tool_available(["failing_tool", "--version"])
        assert result is False

    @patch("subprocess.run")
    def test_check_tool_available_with_success(self, mock_run):
        """Test handling of successful exit."""
        from unittest.mock import MagicMock

        mock_run.return_value = MagicMock(returncode=0)
        result = check_tool_available(["working_tool", "--version"])
        assert result is True


class TestConfigPaths:
    """Test config path functions."""

    def test_get_config_dir_returns_path(self):
        """get_config_dir returns Path object."""
        result = get_config_dir()
        assert isinstance(result, Path)
        assert result == CONFIG_DIR

    def test_get_config_file_returns_path(self):
        """get_config_file returns Path object."""
        result = get_config_file()
        assert isinstance(result, Path)
        assert result == CONFIG_FILE


class TestEnsureConfigDir:
    """Test ensure_config_dir function."""

    @patch("src.config.CONFIG_DIR")
    def test_ensure_config_dir_creates_directory(self, mock_dir):
        """ensure_config_dir creates directory."""
        mock_dir.mkdir = MagicMock()
        result = ensure_config_dir()
        assert result is True
        mock_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("src.config.CONFIG_DIR")
    def test_ensure_config_dir_handles_error(self, mock_dir):
        """ensure_config_dir returns False on error."""
        mock_dir.mkdir.side_effect = OSError("Permission denied")
        result = ensure_config_dir()
        assert result is False


class TestSaveConfig:
    """Test save_config function."""

    def test_save_config_writes_file(self):
        """save_config writes config to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            test_config = {"test_key": "test_value"}

            with patch("src.config.CONFIG_FILE", config_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = save_config(test_config)

            assert result is True
            assert config_file.exists()
            with open(config_file) as f:
                saved = json.load(f)
            assert saved["test_key"] == "test_value"

    def test_save_config_returns_false_when_dir_fails(self):
        """save_config returns False when ensure_config_dir fails."""
        with patch("src.config.ensure_config_dir", return_value=False):
            result = save_config({"key": "value"})
        assert result is False

    def test_save_config_handles_write_error(self):
        """save_config returns False on write error."""
        with patch("src.config.ensure_config_dir", return_value=True):
            with patch("builtins.open", side_effect=OSError("Write failed")):
                result = save_config({"key": "value"})
        assert result is False


class TestLoadConfigFile:
    """Test load_config with actual file reading."""

    def test_load_config_reads_existing_file(self):
        """load_config reads and merges existing config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text('{"custom_setting": "custom_value"}')

            with patch("src.config.CONFIG_FILE", config_file):
                config = load_config()

            assert config["custom_setting"] == "custom_value"
            # Should also have defaults
            assert "default_format" in config

    def test_load_config_handles_invalid_json(self):
        """load_config handles invalid JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text("invalid json {{{")

            with patch("src.config.CONFIG_FILE", config_file):
                config = load_config()

            # Should return defaults on error
            assert config == DEFAULT_CONFIG


class TestSetSetting:
    """Test set_setting function."""

    def test_set_setting_saves_value(self):
        """set_setting saves a single setting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"

            with patch("src.config.CONFIG_FILE", config_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = set_setting("my_setting", "my_value")

            assert result is True
            with open(config_file) as f:
                saved = json.load(f)
            assert saved["my_setting"] == "my_value"


class TestResetConfig:
    """Test reset_config function."""

    def test_reset_config_saves_defaults(self):
        """reset_config saves default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            # Write custom config first
            config_file.write_text('{"custom": "value"}')

            with patch("src.config.CONFIG_FILE", config_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = reset_config()

            assert result is True
            with open(config_file) as f:
                saved = json.load(f)
            assert "custom" not in saved
            assert saved["default_format"] == "png"


class TestTemplates:
    """Test annotation template functions."""

    def test_load_templates_returns_defaults_when_no_file(self):
        """load_templates returns defaults when file doesn't exist."""
        with patch("src.config.TEMPLATES_FILE") as mock_file:
            mock_file.exists.return_value = False
            templates = load_templates()

        assert templates == DEFAULT_TEMPLATES

    def test_load_templates_reads_file(self):
        """load_templates reads templates from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            custom_templates = [{"name": "Custom", "tool": "ARROW"}]
            templates_file.write_text(json.dumps(custom_templates))

            with patch("src.config.TEMPLATES_FILE", templates_file):
                templates = load_templates()

            assert templates == custom_templates

    def test_load_templates_handles_invalid_json(self):
        """load_templates returns defaults on invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            templates_file.write_text("invalid {{{")

            with patch("src.config.TEMPLATES_FILE", templates_file):
                templates = load_templates()

            assert templates == DEFAULT_TEMPLATES

    def test_save_templates_writes_file(self):
        """save_templates writes templates to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            custom_templates = [{"name": "Test", "tool": "TEXT"}]

            with patch("src.config.TEMPLATES_FILE", templates_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = save_templates(custom_templates)

            assert result is True
            with open(templates_file) as f:
                saved = json.load(f)
            assert saved == custom_templates

    def test_save_templates_returns_false_on_dir_error(self):
        """save_templates returns False when ensure_config_dir fails."""
        with patch("src.config.ensure_config_dir", return_value=False):
            result = save_templates([])
        assert result is False

    def test_save_templates_handles_write_error(self):
        """save_templates returns False on write error."""
        with patch("src.config.ensure_config_dir", return_value=True):
            with patch("builtins.open", side_effect=OSError("Write failed")):
                result = save_templates([])
        assert result is False

    def test_add_template_appends_template(self):
        """add_template adds a new template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            templates_file.write_text("[]")

            with patch("src.config.TEMPLATES_FILE", templates_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = add_template({"name": "New", "tool": "BLUR"})

            assert result is True
            with open(templates_file) as f:
                saved = json.load(f)
            assert len(saved) == 1
            assert saved[0]["name"] == "New"

    def test_delete_template_removes_by_name(self):
        """delete_template removes template by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            initial = [{"name": "Keep"}, {"name": "Delete"}, {"name": "Also Keep"}]
            templates_file.write_text(json.dumps(initial))

            with patch("src.config.TEMPLATES_FILE", templates_file):
                with patch("src.config.ensure_config_dir", return_value=True):
                    result = delete_template("Delete")

            assert result is True
            with open(templates_file) as f:
                saved = json.load(f)
            assert len(saved) == 2
            names = [t["name"] for t in saved]
            assert "Delete" not in names
            assert "Keep" in names
            assert "Also Keep" in names

    def test_get_template_returns_matching_template(self):
        """get_template returns template by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_file = Path(tmpdir) / "templates.json"
            templates = [{"name": "Target", "tool": "ARROW", "color": [255, 0, 0]}]
            templates_file.write_text(json.dumps(templates))

            with patch("src.config.TEMPLATES_FILE", templates_file):
                template = get_template("Target")

            assert template is not None
            assert template["name"] == "Target"
            assert template["tool"] == "ARROW"

    def test_get_template_returns_none_for_missing(self):
        """get_template returns None for nonexistent template."""
        with patch("src.config.TEMPLATES_FILE") as mock_file:
            mock_file.exists.return_value = False
            template = get_template("Nonexistent")

        assert template is None


class TestColorPalettes:
    """Test color palette functions."""

    def test_get_color_palettes_returns_dict(self):
        """get_color_palettes returns dictionary of palettes."""
        palettes = get_color_palettes()
        assert isinstance(palettes, dict)
        assert "Default" in palettes
        assert "Pastel" in palettes
        assert "Neon" in palettes

    def test_get_color_palettes_returns_copy(self):
        """get_color_palettes returns a copy."""
        palettes = get_color_palettes()
        palettes["Custom"] = []
        assert "Custom" not in COLOR_PALETTES

    def test_get_palette_returns_named_palette(self):
        """get_palette returns specified palette."""
        palette = get_palette("Monochrome")
        assert palette == COLOR_PALETTES["Monochrome"]

    def test_get_palette_returns_default_for_unknown(self):
        """get_palette returns Default for unknown name."""
        palette = get_palette("Unknown Palette Name")
        assert palette == COLOR_PALETTES["Default"]

    def test_get_palette_earth(self):
        """get_palette returns Earth palette."""
        palette = get_palette("Earth")
        assert palette == COLOR_PALETTES["Earth"]
        assert len(palette) == 10
