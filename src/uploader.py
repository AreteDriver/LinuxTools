"""Cloud upload functionality for LikX."""

import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from . import config


class Uploader:
    """Handles uploading screenshots to cloud services."""

    def __init__(self):
        self.imgur_client_id = "546c25a59c58ad7"  # Anonymous Imgur uploads

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

    def upload_to_imgur(
        self, filepath: Path
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to Imgur.

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            import base64

            # Read image and encode
            with open(filepath, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Use curl to upload
            result = subprocess.run(
                [
                    "curl",
                    "-X",
                    "POST",
                    "-H",
                    f"Authorization: Client-ID {self.imgur_client_id}",
                    "-F",
                    f"image={image_data}",
                    "https://api.imgur.com/3/image",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("success"):
                    url = response["data"]["link"]
                    return True, url, None
                else:
                    return False, None, "Imgur API returned error"
            else:
                return False, None, "Upload request failed"

        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except FileNotFoundError:
            return False, None, "curl not installed"
        except Exception as e:
            return False, None, str(e)

    def upload_to_file_io(
        self, filepath: Path
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload to file.io (temporary file sharing).

        Args:
            filepath: Path to image file

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            result = subprocess.run(
                ["curl", "-F", f"file=@{filepath}", "https://file.io"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("success"):
                    url = response["link"]
                    return True, url, None
                else:
                    return False, None, "file.io returned error"
            else:
                return False, None, "Upload failed"

        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except FileNotFoundError:
            return False, None, "curl not installed"
        except Exception as e:
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
            # Build S3 key (filename in bucket)
            s3_key = f"screenshots/{filepath.name}"

            # Build aws s3 cp command
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
            )

            if result.returncode == 0:
                # Construct public URL
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
        except Exception as e:
            return False, None, str(e)

    def _dropbox_upload_file(
        self, filepath: Path, access_token: str, dropbox_path: str
    ) -> Tuple[bool, Optional[str]]:
        """Upload file to Dropbox. Returns (success, error_message)."""
        result = subprocess.run(
            [
                "curl", "-X", "POST",
                "https://content.dropboxapi.com/2/files/upload",
                "-H", f"Authorization: Bearer {access_token}",
                "-H", "Content-Type: application/octet-stream",
                "-H", f'Dropbox-API-Arg: {{"path": "{dropbox_path}", "mode": "add"}}',
                "--data-binary", f"@{filepath}",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return False, "Dropbox upload request failed"
        response = json.loads(result.stdout)
        if "error" in response:
            return False, response.get("error_summary", "Upload failed")
        return True, None

    def _dropbox_create_share_link(
        self, access_token: str, dropbox_path: str
    ) -> Optional[str]:
        """Create Dropbox shared link. Returns URL or None."""
        result = subprocess.run(
            [
                "curl", "-X", "POST",
                "https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings",
                "-H", f"Authorization: Bearer {access_token}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"path": dropbox_path}),
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        response = json.loads(result.stdout)
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

    def upload_to_dropbox(
        self, filepath: Path
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload image to Dropbox."""
        cfg = config.load_config()
        access_token = cfg.get("dropbox_token", "")

        if not access_token:
            return (False, None, "Dropbox access token not configured. "
                    "Get one from https://www.dropbox.com/developers/apps")

        try:
            dropbox_path = f"/Screenshots/{filepath.name}"
            success, error = self._dropbox_upload_file(filepath, access_token, dropbox_path)
            if not success:
                return False, None, error

            url = self._dropbox_create_share_link(access_token, dropbox_path)
            return True, url or f"Uploaded to Dropbox: {dropbox_path}", None

        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except FileNotFoundError:
            return False, None, "curl not installed"
        except json.JSONDecodeError:
            return False, None, "Invalid response from Dropbox"
        except Exception as e:
            return False, None, str(e)

    def _gdrive_upload_with_gdrive(
        self, filepath: Path, folder_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload using gdrive CLI. Returns (success, url, error)."""
        cmd = ["gdrive", "files", "upload", str(filepath)]
        if folder_id:
            cmd.extend(["--parent", folder_id])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

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
            capture_output=True, text=True, timeout=60,
        )

        if result.returncode != 0:
            return False, None, result.stderr.strip() or "Upload failed"

        link_result = subprocess.run(
            ["rclone", "link", remote_path],
            capture_output=True, text=True, timeout=30,
        )
        if link_result.returncode == 0 and link_result.stdout.strip():
            return True, link_result.stdout.strip(), None
        return True, f"Uploaded to {remote_path}", None

    def upload_to_gdrive(
        self, filepath: Path
    ) -> Tuple[bool, Optional[str], Optional[str]]:
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
            return (False, None, "Google Drive upload requires gdrive or rclone. "
                    "Install gdrive: https://github.com/glotlabs/gdrive")
        except subprocess.TimeoutExpired:
            return False, None, "Upload timed out"
        except Exception as e:
            return False, None, str(e)

    def copy_url_to_clipboard(self, url: str) -> bool:
        """Copy URL to clipboard.

        Args:
            url: URL to copy

        Returns:
            True if successful
        """
        try:
            # Try xclip first
            subprocess.run(
                ["xclip", "-selection", "clipboard"], input=url.encode(), check=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        try:
            # Try xsel
            subprocess.run(
                ["xsel", "--clipboard", "--input"], input=url.encode(), check=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        return False
