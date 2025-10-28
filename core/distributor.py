import os
import yagmail
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
            raise NotImplementedError("TikTok distribution not yet implemented")
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
