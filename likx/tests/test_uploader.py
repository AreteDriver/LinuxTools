"""Tests for uploader module."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.uploader import Uploader


class TestUploaderInit:
    """Test Uploader initialization."""

    def test_uploader_init(self):
        uploader = Uploader()
        assert uploader is not None

    def test_uploader_has_client_id(self):
        uploader = Uploader()
        assert hasattr(uploader, "imgur_client_id")
        assert uploader.imgur_client_id is not None

    def test_uploader_client_id_from_env(self):
        with patch.dict("os.environ", {"LIKX_IMGUR_CLIENT_ID": "test-id-123"}):
            uploader = Uploader()
            assert uploader.imgur_client_id == "test-id-123"


class TestUploadToImgur:
    """Test Imgur upload functionality."""

    def _mock_http_upload(self, uploader, response_data, status=200):
        """Patch _http_upload to return given response."""
        return patch.object(
            uploader, "_http_upload", return_value=(status, response_data)
        )

    def test_upload_success(self):
        uploader = Uploader()
        with self._mock_http_upload(
            uploader, {"success": True, "data": {"link": "https://i.imgur.com/abc123.png"}}
        ):
            with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
                success, url, error = uploader.upload_to_imgur(Path("/path/to/image.png"))

        assert success is True
        assert url == "https://i.imgur.com/abc123.png"
        assert error is None

    def test_upload_api_failure(self):
        uploader = Uploader()
        with self._mock_http_upload(
            uploader, {"success": False, "data": {"error": "Rate limit exceeded"}}
        ):
            with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
                success, url, error = uploader.upload_to_imgur(Path("/path/to/image.png"))

        assert success is False
        assert url is None
        assert error is not None

    def test_upload_file_not_found(self):
        uploader = Uploader()

        # Use actual non-existent path - will trigger FileNotFoundError on open
        success, url, error = uploader.upload_to_imgur(Path("/nonexistent/image.png"))

        assert success is False
        assert error is not None

    def test_upload_os_error(self):
        uploader = Uploader()
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            success, url, error = uploader.upload_to_imgur(Path("/path/to/image.png"))

        assert success is False
        assert error is not None


class TestUploadToFileIo:
    """Test file.io upload functionality."""

    def test_upload_success(self):
        uploader = Uploader()
        with patch.object(
            uploader,
            "_http_upload",
            return_value=(200, {"success": True, "link": "https://file.io/abc123"}),
        ):
            with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
                success, url, error = uploader.upload_to_file_io(Path("/path/to/image.png"))

        assert success is True
        assert url == "https://file.io/abc123"
        assert error is None

    def test_upload_api_failure(self):
        uploader = Uploader()
        with patch.object(
            uploader,
            "_http_upload",
            return_value=(200, {"success": False, "error": "File too large"}),
        ):
            with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
                success, url, error = uploader.upload_to_file_io(Path("/path/to/image.png"))

        assert success is False
        assert url is None
        assert error is not None

    def test_upload_file_not_found(self):
        uploader = Uploader()
        success, url, error = uploader.upload_to_file_io(Path("/nonexistent/image.png"))

        assert success is False
        assert error is not None

    def test_upload_os_error(self):
        uploader = Uploader()
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            success, url, error = uploader.upload_to_file_io(Path("/path/to/image.png"))

        assert success is False
        assert error is not None


class TestCopyUrlToClipboard:
    """Test clipboard copy functionality."""

    @patch("src.uploader.subprocess.run")
    def test_copy_with_xclip_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        uploader = Uploader()
        result = uploader.copy_url_to_clipboard("https://example.com/image.png")

        assert result is True
        mock_run.assert_called_once()

    @patch("src.uploader.subprocess.run")
    def test_copy_xclip_not_found_falls_back_to_xsel(self, mock_run):
        mock_run.side_effect = [
            FileNotFoundError(),  # xclip not found
            MagicMock(returncode=0),  # xsel succeeds
        ]

        uploader = Uploader()
        result = uploader.copy_url_to_clipboard("https://example.com/image.png")

        assert result is True
        assert mock_run.call_count == 2

    @patch("src.uploader.subprocess.run")
    def test_copy_both_fail(self, mock_run):
        mock_run.side_effect = [
            FileNotFoundError(),  # xclip not found
            FileNotFoundError(),  # xsel not found
        ]

        uploader = Uploader()
        result = uploader.copy_url_to_clipboard("https://example.com/image.png")

        assert result is False

    @patch("src.uploader.subprocess.run")
    def test_copy_xclip_error(self, mock_run):
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "xclip"),
            FileNotFoundError(),  # xsel not found
        ]

        uploader = Uploader()
        result = uploader.copy_url_to_clipboard("https://example.com/image.png")

        assert result is False

    @patch("src.uploader.subprocess.run")
    def test_copy_xsel_error(self, mock_run):
        mock_run.side_effect = [
            FileNotFoundError(),  # xclip not found
            subprocess.CalledProcessError(1, "xsel"),  # xsel fails
        ]

        uploader = Uploader()
        result = uploader.copy_url_to_clipboard("https://example.com/image.png")

        assert result is False


class TestUnifiedUpload:
    """Test unified upload() method routing."""

    @patch("src.uploader.config.load_config")
    def test_upload_routes_to_imgur(self, mock_config):
        mock_config.return_value = {"upload_service": "imgur"}

        uploader = Uploader()
        with patch.object(
            uploader,
            "_http_upload",
            return_value=(
                200,
                {"success": True, "data": {"link": "https://i.imgur.com/abc.png"}},
            ),
        ):
            with patch("builtins.open", mock_open(read_data=b"data")):
                success, url, error = uploader.upload(Path("/path/to/image.png"))

        assert success is True
        assert "imgur" in url

    @patch("src.uploader.config.load_config")
    def test_upload_disabled(self, mock_config):
        mock_config.return_value = {"upload_service": "none"}

        uploader = Uploader()
        success, url, error = uploader.upload(Path("/path/to/image.png"))

        assert success is False
        assert "disabled" in error.lower()

    @patch("src.uploader.config.load_config")
    def test_upload_unknown_service(self, mock_config):
        mock_config.return_value = {"upload_service": "unknown_provider"}

        uploader = Uploader()
        success, url, error = uploader.upload(Path("/path/to/image.png"))

        assert success is False
        assert "unknown" in error.lower()


class TestUploadToS3:
    """Test S3 upload functionality."""

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_success(self, mock_run, mock_config):
        mock_config.return_value = {
            "s3_bucket": "my-bucket",
            "s3_region": "us-west-2",
            "s3_public": True,
        }
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        uploader = Uploader()
        success, url, error = uploader.upload_to_s3(Path("/path/to/image.png"))

        assert success is True
        assert "my-bucket" in url
        assert "us-west-2" in url
        assert "image.png" in url

    @patch("src.uploader.config.load_config")
    def test_upload_no_bucket_configured(self, mock_config):
        mock_config.return_value = {"s3_bucket": "", "s3_region": "us-east-1"}

        uploader = Uploader()
        success, url, error = uploader.upload_to_s3(Path("/path/to/image.png"))

        assert success is False
        assert "bucket" in error.lower()

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_aws_cli_not_found(self, mock_run, mock_config):
        mock_config.return_value = {
            "s3_bucket": "my-bucket",
            "s3_region": "us-east-1",
            "s3_public": True,
        }
        mock_run.side_effect = FileNotFoundError()

        uploader = Uploader()
        success, url, error = uploader.upload_to_s3(Path("/path/to/image.png"))

        assert success is False
        assert "aws" in error.lower()

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_failure(self, mock_run, mock_config):
        mock_config.return_value = {
            "s3_bucket": "my-bucket",
            "s3_region": "us-east-1",
            "s3_public": True,
        }
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Access Denied")

        uploader = Uploader()
        success, url, error = uploader.upload_to_s3(Path("/path/to/image.png"))

        assert success is False
        assert "Access Denied" in error


class TestUploadToDropbox:
    """Test Dropbox upload functionality."""

    @patch("src.uploader._get_secret")
    def test_upload_no_token(self, mock_secret):
        mock_secret.return_value = ""

        uploader = Uploader()
        success, url, error = uploader.upload_to_dropbox(Path("/path/to/image.png"))

        assert success is False
        assert "token" in error.lower()

    @patch("src.uploader._get_secret")
    def test_upload_success_with_share_link(self, mock_secret):
        mock_secret.return_value = "sl.test-token"

        uploader = Uploader()

        # Mock both HTTP calls: upload + share link
        responses = iter(
            [
                (200, {"path_display": "/Screenshots/image.png"}),
                (200, {"url": "https://www.dropbox.com/s/abc/image.png?dl=0"}),
            ]
        )
        with patch.object(uploader, "_http_upload", side_effect=responses):
            with patch("builtins.open", mock_open(read_data=b"fake_image")):
                success, url, error = uploader.upload_to_dropbox(Path("/path/to/image.png"))

        assert success is True
        assert "dropbox" in url.lower()
        assert "dl=1" in url  # Should be direct download link

    @patch("src.uploader._get_secret")
    def test_upload_json_injection_safe(self, mock_secret):
        """Verify dropbox_path is properly escaped via json.dumps."""
        mock_secret.return_value = "sl.test-token"

        uploader = Uploader()
        call_headers = {}

        def capture_http_call(url, **kwargs):
            if "upload" in url:
                call_headers.update(kwargs.get("headers", {}))
                return 200, {"path_display": "/Screenshots/evil.png"}
            return 200, {"url": "https://dropbox.com/s/x?dl=0"}

        with patch.object(uploader, "_http_upload", side_effect=capture_http_call):
            evil_name = 'evil","mode":"overwrite"}.png'
            with patch("builtins.open", mock_open(read_data=b"data")):
                uploader.upload_to_dropbox(Path(f"/tmp/{evil_name}"))

        # The Dropbox-API-Arg header should contain properly escaped JSON
        api_arg = call_headers.get("Dropbox-API-Arg", "")
        parsed = json.loads(api_arg)
        # mode should still be "add", not overwritten by injection
        assert parsed["mode"] == "add"


class TestUploadToGdrive:
    """Test Google Drive upload functionality."""

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_with_gdrive_success(self, mock_run, mock_config):
        mock_config.return_value = {"gdrive_folder_id": ""}
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Uploaded image.png with id abc123xyz"
        )

        uploader = Uploader()
        success, url, error = uploader.upload_to_gdrive(Path("/path/to/image.png"))

        assert success is True
        assert "abc123xyz" in url or "Google Drive" in url

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_gdrive_not_found_tries_rclone(self, mock_run, mock_config):
        mock_config.return_value = {"gdrive_folder_id": "", "gdrive_rclone_remote": "gdrive"}

        # First call: gdrive not found, Second call: rclone succeeds
        mock_run.side_effect = [
            FileNotFoundError(),  # gdrive not found
            MagicMock(returncode=0, stdout=""),  # rclone copy
            MagicMock(returncode=0, stdout="https://drive.google.com/file/d/xyz"),  # rclone link
        ]

        uploader = Uploader()
        success, url, error = uploader.upload_to_gdrive(Path("/path/to/image.png"))

        assert success is True

    @patch("src.uploader.config.load_config")
    @patch("src.uploader.subprocess.run")
    def test_upload_all_tools_not_found(self, mock_run, mock_config):
        mock_config.return_value = {"gdrive_folder_id": "", "gdrive_rclone_remote": "gdrive"}

        mock_run.side_effect = FileNotFoundError()

        uploader = Uploader()
        success, url, error = uploader.upload_to_gdrive(Path("/path/to/image.png"))

        assert success is False
        assert "gdrive" in error.lower() or "rclone" in error.lower()


class TestUploaderEdgeCases:
    """Test edge cases and error handling."""

    def test_upload_special_characters_in_path(self):
        uploader = Uploader()
        with patch.object(
            uploader,
            "_http_upload",
            return_value=(
                200,
                {"success": True, "data": {"link": "https://i.imgur.com/abc.png"}},
            ),
        ):
            with patch("builtins.open", mock_open(read_data=b"data")):
                success, url, error = uploader.upload_to_imgur(
                    Path("/path with spaces/image.png")
                )

        assert success is True

    @patch("src.uploader.subprocess.run")
    def test_clipboard_with_long_url(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        uploader = Uploader()
        long_url = "https://example.com/" + "a" * 1000
        result = uploader.copy_url_to_clipboard(long_url)

        assert result is True


class TestSecretManagement:
    """Test keyring integration for secret storage."""

    @patch("src.uploader.config.load_config")
    def test_get_secret_fallback_to_config(self, mock_config):
        """When keyring is unavailable, falls back to config."""
        from src.uploader import _get_secret

        mock_config.return_value = {"dropbox_token": "legacy-token"}

        with patch.dict(sys.modules, {"keyring": None}):
            # Force reimport to hit ImportError path
            token = _get_secret("dropbox_token")

        # Should get from config fallback
        assert token == "legacy-token"

    def test_http_upload_handles_network_error(self):
        """_http_upload returns error tuple on network failure."""
        uploader = Uploader()
        # Use an unreachable URL — should return error gracefully
        status, response = uploader._http_upload(
            "http://192.0.2.1:1/unreachable",
            timeout=1,
        )
        assert status == 0
        assert "error" in response
