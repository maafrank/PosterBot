import os
import yagmail
import requests
import time
from dotenv import set_key
from config import Config

class Distributor:
    """Distributes content to various platforms"""
    
    def __init__(self, sender_email=None, receiver_email=None, app_password=None):
        self.sender_email = sender_email or Config.EMAIL_SENDER
        self.receiver_email = receiver_email or Config.EMAIL_RECEIVER
        self.app_password = app_password or Config.EMAIL_APP_PASSWORD
    
    def distribute(self, video_path, platform="email", metadata=None):
        """
        Distribute video to specified platform

        Args:
            video_path: Path to the video file
            platform: Distribution platform ("email", "instagram", "tiktok", "youtube", "none")
            metadata: Optional metadata dict (subject, description, etc.)

        Returns:
            bool: Success status
        """
        if platform == "none":
            print("✓ Skipping distribution (--no-distribute flag set)")
            return True
        elif platform == "email":
            return self._send_email(video_path, metadata)
        elif platform == "instagram":
            raise NotImplementedError("Instagram distribution not yet implemented")
        elif platform == "tiktok":
            return self._post_to_tiktok(video_path, metadata)
        elif platform == "youtube":
            raise NotImplementedError("YouTube distribution not yet implemented")
        else:
            raise ValueError(f"Unknown platform: {platform}")
    
    def _send_email(self, video_path, metadata=None):
        """Send video via email"""
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return False
        
        # Extract metadata
        if metadata is None:
            metadata = {}
        
        subject = metadata.get("subject", "Video from PosterBot")
        body = metadata.get("body", "Please find the attached video.")
        
        try:
            print(f"Sending email to {self.receiver_email}...")
            
            # Initialize yagmail client
            yag = yagmail.SMTP(self.sender_email, self.app_password)
            
            # Send email with attachment
            yag.send(
                to=self.receiver_email,
                subject=subject,
                contents=body,
                attachments=video_path
            )
            
            print("✓ Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False

    def _post_to_tiktok(self, video_path, metadata=None):
        """Post video to TikTok using Content Posting API"""
        if not os.path.exists(video_path):
            print(f"✗ Error: Video file not found: {video_path}")
            return False

        # Extract metadata
        if metadata is None:
            metadata = {}

        title = metadata.get("title", metadata.get("subject", ""))
        description = metadata.get("description", metadata.get("body", ""))

        # Combine title and description for caption
        caption = f"{title}\n\n{description}" if title and description else (title or description)
        caption = caption[:2200] if caption else "Posted by PosterBot"  # TikTok max caption length

        try:
            print("Uploading video to TikTok...")

            # Step 1: Initialize video upload
            publish_id, upload_url = self._init_tiktok_upload(video_path, caption)

            if not publish_id or not upload_url:
                return False

            # Step 2: Upload video file
            if not self._upload_video_to_tiktok(video_path, upload_url):
                return False

            # Step 3: Check upload status
            if not self._check_tiktok_status(publish_id):
                return False

            print("✓ Video posted to TikTok successfully!")
            return True

        except Exception as e:
            print(f"✗ Failed to post to TikTok: {e}")
            return False

    def _refresh_tiktok_token(self):
        """Refresh TikTok access token using refresh token"""
        refresh_token = Config.TIKTOK_REFRESH_TOKEN

        if not refresh_token:
            print("✗ No refresh token available")
            return False

        url = "https://open.tiktokapis.com/v2/oauth/token/"
        data = {
            "client_key": Config.TIKTOK_CLIENT_KEY,
            "client_secret": Config.TIKTOK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            if "access_token" in result:
                # Save new tokens to .env
                set_key(".env", "TIKTOK_ACCESS_TOKEN", result["access_token"])
                set_key(".env", "TIKTOK_REFRESH_TOKEN", result["refresh_token"])

                # Update config in memory
                Config.TIKTOK_ACCESS_TOKEN = result["access_token"]
                Config.TIKTOK_REFRESH_TOKEN = result["refresh_token"]

                print("✓ TikTok access token refreshed")
                return True
            else:
                print(f"✗ Token refresh failed: {result}")
                return False

        except Exception as e:
            print(f"✗ Token refresh error: {e}")
            return False

    def _init_tiktok_upload(self, video_path, caption):
        """Initialize TikTok video upload and get upload URL"""
        access_token = Config.TIKTOK_ACCESS_TOKEN

        if not access_token:
            print("✗ No TikTok access token. Run: python3 tiktok_auth.py")
            return None, None

        # Get video file size
        video_size = os.path.getsize(video_path)

        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

        payload = {
            "post_info": {
                "title": caption,
                "privacy_level": "SELF_ONLY",  # Start with private for sandbox testing
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            # Check for token expiration
            if response.status_code == 401:
                print("⚠️  Access token expired, refreshing...")
                if self._refresh_tiktok_token():
                    # Retry with new token
                    headers["Authorization"] = f"Bearer {Config.TIKTOK_ACCESS_TOKEN}"
                    response = requests.post(url, json=payload, headers=headers)
                else:
                    return None, None

            response.raise_for_status()
            result = response.json()

            if "data" in result:
                publish_id = result["data"].get("publish_id")
                upload_url = result["data"].get("upload_url")
                print(f"✓ Upload initialized (publish_id: {publish_id})")
                return publish_id, upload_url
            else:
                print(f"✗ Upload init failed: {result}")
                return None, None

        except Exception as e:
            print(f"✗ Upload init error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            return None, None

    def _upload_video_to_tiktok(self, video_path, upload_url):
        """Upload video file to TikTok's servers"""
        try:
            with open(video_path, 'rb') as video_file:
                video_data = video_file.read()

            video_size = len(video_data)

            headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{video_size-1}/{video_size}"
            }

            print(f"Uploading {video_size / (1024*1024):.2f} MB...")
            response = requests.put(upload_url, data=video_data, headers=headers)
            response.raise_for_status()

            print("✓ Video uploaded successfully")
            return True

        except Exception as e:
            print(f"✗ Video upload failed: {e}")
            return False

    def _check_tiktok_status(self, publish_id, max_retries=20, retry_delay=3):
        """Check TikTok video processing status"""
        access_token = Config.TIKTOK_ACCESS_TOKEN
        url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

        payload = {
            "publish_id": publish_id
        }

        print("Checking upload status", end="", flush=True)

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()

                if "data" in result:
                    status = result["data"].get("status")

                    if status == "PUBLISH_COMPLETE":
                        print(" ✓")
                        return True
                    elif status == "FAILED":
                        error = result["data"].get("fail_reason", "Unknown error")
                        print(f"\n✗ Upload failed: {error}")
                        return False
                    else:
                        # Still processing
                        print(".", end="", flush=True)
                        time.sleep(retry_delay)
                else:
                    print(f"\n✗ Status check failed: {result}")
                    return False

            except Exception as e:
                print(f"\n✗ Status check error: {e}")
                return False

        print("\n⚠️  Upload status check timed out")
        return False
