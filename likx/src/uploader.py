"""Cloud upload functionality for LikX."""

import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from . import config


def _get_secret(key: str) -> str:
    """Retrieve a secret from system keyring, falling back to config.

    Uses the Secret Service API (GNOME Keyring / KDE Wallet) when available.
    Falls back to config.json for backwards compatibility.
    """
    try:
        import keyring

        value = keyring.get_password("likx", key)
        if value:
            return value
    except ImportError:
        pass

    # Fallback to config (legacy / no keyring installed)
    cfg = config.load_config()
    return cfg.get(key, "")


def _set_secret(key: str, value: str) -> bool:
    """Store a secret in system keyring.

    Returns True if stored in keyring, False if falling back to config.
    """
    try:
        import keyring

        keyring.set_password("likx", key, value)
        return True
    except ImportError:
        # No keyring available — store in config (with warning)
        cfg = config.load_config()
        cfg[key] = value
        config.save_config(cfg)
        return False


class Uploader:
    """Handles uploading screenshots to cloud services."""

    def __init__(self):
        import os

        cfg = config.load_config()
        self.imgur_client_id = (
            os.environ.get("LIKX_IMGUR_CLIENT_ID")
            or cfg.get("imgur_client_id")
            or "546c25a59c58ad7"
        )

    def upload(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image using configured service.

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        cfg = config.load_config()
        service = cfg.get("upload_service", "imgur")

        if service == "imgur":
            return self.upload_to_imgur(filepath)
        elif service == "fileio":
            return self.upload_to_file_io(filepath)
        elif service == "s3":
            return self.upload_to_s3(filepath)
        elif service == "dropbox":
            return self.upload_to_dropbox(filepath)
        elif service == "gdrive":
            return self.upload_to_gdrive(filepath)
        elif service == "none":
            return False, None, "Upload disabled"
        else:
            return False, None, f"Unknown upload service: {service}"

    def _http_upload(
        self,
        url: str,
        *,
        method: str = "POST",
        headers: Optional[dict] = None,
        data: Optional[bytes] = None,
        files: Optional[dict] = None,
        json_body: Optional[dict] = None,
        timeout: int = 30,
    ) -> Tuple[int, dict]:
        """HTTP upload using urllib (stdlib). Returns (status_code, response_json).

        Falls back to curl only if absolutely necessary.
        """
        import urllib.error
        import urllib.request

        req_headers = headers or {}

        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        elif files is not None:
            # Multipart form data
            boundary = "----LikXBoundary"
            parts = []
            for field_name, (filename, file_data, content_type) in files.items():
                parts.append(f"--{boundary}\r\n".encode())
                parts.append(
                    f'Content-Disposition: form-data; name="{field_name}"; '
                    f'filename="{filename}"\r\n'.encode()
                )
                parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
                parts.append(file_data)
                parts.append(b"\r\n")
            parts.append(f"--{boundary}--\r\n".encode())
            body = b"".join(parts)
            req_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        elif data is not None:
            body = data
        else:
            body = None

        req = urllib.request.Request(url, data=body, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                response_body = resp.read().decode("utf-8")
                try:
                    return resp.status, json.loads(response_body)
                except json.JSONDecodeError:
                    return resp.status, {"raw": response_body}
        except urllib.error.HTTPError as e:
            response_body = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(response_body)
            except json.JSONDecodeError:
                return e.code, {"error": response_body}
        except urllib.error.URLError as e:
            return 0, {"error": str(e.reason)}

    def upload_to_imgur(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to Imgur.

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            import base64

            with open(filepath, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            status, response = self._http_upload(
                "https://api.imgur.com/3/image",
                headers={"Authorization": f"Client-ID {self.imgur_client_id}"},
                data=f"image={image_data}".encode(),
                timeout=30,
            )

            if response.get("success"):
                url = response["data"]["link"]
                return True, url, None
            else:
                return False, None, "Imgur API returned error"

        except FileNotFoundError:
            return False, None, f"Image file not found: {filepath}"
        except OSError as e:
            return False, None, str(e)

    def upload_to_file_io(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload to file.io (temporary file sharing).

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            with open(filepath, "rb") as f:
                file_data = f.read()

            status, response = self._http_upload(
                "https://file.io",
                files={"file": (filepath.name, file_data, "application/octet-stream")},
                timeout=30,
            )

            if response.get("success"):
                url = response.get("link", "")
                return True, url, None
            else:
                return False, None, "file.io returned error"

        except FileNotFoundError:
            return False, None, f"Image file not found: {filepath}"
        except OSError as e:
            return False, None, str(e)

    def upload_to_s3(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to AWS S3.

        Requires AWS CLI configured or environment variables:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - S3 bucket configured in LikX settings

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        cfg = config.load_config()
        bucket = cfg.get("s3_bucket", "")
        region = cfg.get("s3_region", "us-east-1")
        make_public = cfg.get("s3_public", True)

        if not bucket:
            return False, None, "S3 bucket not configured in settings"

        try:
            s3_key = f"screenshots/{filepath.name}"

            cmd = [
                "aws",
                "s3",
                "cp",
                str(filepath),
                f"s3://{bucket}/{s3_key}",
                "--region",
                region,
            ]

            if make_public:
                cmd.extend(["--acl", "public-read"])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                shell=False,
            )

            if result.returncode == 0:
                if make_public:
                    url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
                else:
                    url = f"s3://{bucket}/{s3_key}"
                return True, url, None
            else:
                error = result.stderr.strip() or "Upload failed"
                return False, None, error

        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except FileNotFoundError:
            return (
                False,
                None,
                "AWS CLI not installed. Install with: pip install awscli",
            )
        except OSError as e:
            return False, None, str(e)

    def _dropbox_upload_file(
        self, filepath: Path, access_token: str, dropbox_path: str
    ) -> Tuple[bool, Optional[str]]:
        """Upload file to Dropbox. Returns (success, error_message)."""
        with open(filepath, "rb") as f:
            file_data = f.read()

        # Use json.dumps for safe serialization (prevents JSON injection)
        api_arg = json.dumps({"path": dropbox_path, "mode": "add"})

        status, response = self._http_upload(
            "https://content.dropboxapi.com/2/files/upload",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": api_arg,
            },
            data=file_data,
            timeout=60,
        )

        if "error" in response:
            return False, response.get("error_summary", "Upload failed")
        if status == 0:
            return False, response.get("error", "Upload request failed")
        return True, None

    def _dropbox_create_share_link(self, access_token: str, dropbox_path: str) -> Optional[str]:
        """Create Dropbox shared link. Returns URL or None."""
        status, response = self._http_upload(
            "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json_body={"path": dropbox_path},
            timeout=30,
        )

        if "url" in response:
            return response["url"].replace("dl=0", "dl=1")
        if "shared_link_already_exists" in str(response):
            existing = (
                response.get("error", {})
                .get("shared_link_already_exists", {})
                .get("metadata", {})
                .get("url", "")
            )
            if existing:
                return existing.replace("dl=0", "dl=1")
        return None

    def upload_to_dropbox(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to Dropbox."""
        access_token = _get_secret("dropbox_token")

        if not access_token:
            return (
                False,
                None,
                "Dropbox access token not configured. "
                "Get one from https://www.dropbox.com/developers/apps",
            )

        try:
            dropbox_path = f"/Screenshots/{filepath.name}"
            success, error = self._dropbox_upload_file(filepath, access_token, dropbox_path)
            if not success:
                return False, None, error

            url = self._dropbox_create_share_link(access_token, dropbox_path)
            return True, url or f"Uploaded to Dropbox: {dropbox_path}", None

        except json.JSONDecodeError:
            return False, None, "Invalid response from Dropbox"
        except OSError as e:
            return False, None, str(e)

    def _gdrive_upload_with_gdrive(
        self, filepath: Path, folder_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload using gdrive CLI. Returns (success, url, error)."""
        cmd = ["gdrive", "files", "upload", str(filepath)]
        if folder_id:
            cmd.extend(["--parent", folder_id])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=False)

        if result.returncode == 0:
            output = result.stdout
            if "id" in output.lower():
                parts = output.split()
                for i, part in enumerate(parts):
                    if part.lower() == "id" and i + 1 < len(parts):
                        file_id = parts[i + 1].strip()
                        return True, f"https://drive.google.com/file/d/{file_id}/view", None
            return True, "Uploaded to Google Drive", None

        error = result.stderr.strip() or "Upload failed"
        if "not found" in error.lower() or result.returncode == 127:
            raise FileNotFoundError("gdrive not found")
        return False, None, error

    def _gdrive_upload_with_rclone(
        self, filepath: Path, remote: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload using rclone. Returns (success, url, error)."""
        remote_path = f"{remote}:Screenshots/{filepath.name}"
        result = subprocess.run(
            ["rclone", "copyto", str(filepath), remote_path],
            capture_output=True,
            text=True,
            timeout=60,
            shell=False,
        )

        if result.returncode != 0:
            return False, None, result.stderr.strip() or "Upload failed"

        link_result = subprocess.run(
            ["rclone", "link", remote_path],
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
        if link_result.returncode == 0 and link_result.stdout.strip():
            return True, link_result.stdout.strip(), None
        return True, f"Uploaded to {remote_path}", None

    def upload_to_gdrive(self, filepath: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to Google Drive."""
        cfg = config.load_config()
        folder_id = cfg.get("gdrive_folder_id", "")

        try:
            return self._gdrive_upload_with_gdrive(filepath, folder_id)
        except FileNotFoundError:
            pass  # Try rclone next

        try:
            remote = cfg.get("gdrive_rclone_remote", "gdrive")
            return self._gdrive_upload_with_rclone(filepath, remote)
        except FileNotFoundError:
            return (
                False,
                None,
                "Google Drive upload requires gdrive or rclone. "
                "Install gdrive: https://github.com/glotlabs/gdrive",
            )
        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except OSError as e:
            return False, None, str(e)

    def copy_url_to_clipboard(self, url: str) -> bool:
        """Copy URL to clipboard.

        Args:
            url: URL to copy

        Returns:
            True if successful
        """
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=url.encode(),
                check=True,
                shell=False,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        try:
            subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=url.encode(),
                check=True,
                shell=False,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        return False
