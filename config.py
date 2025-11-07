import os
from dotenv import load_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv()

# Fallback: use dotenv_values for variables that don't load properly
_env_values = dotenv_values(".env")

class Config:
    """Configuration class for PosterBot"""
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Pexels API
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

    # Email settings
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    
    # Video settings
    VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
    VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1280"))
    VIDEO_FPS = int(os.getenv("VIDEO_FPS", "1"))
    
    # Content settings
    DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "random")
    IMAGE_COUNT = int(os.getenv("IMAGE_COUNT", "10"))
    IMAGE_SOURCE = os.getenv("IMAGE_SOURCE", "pexels")  # "flux-schnell", "flux-dev", "pexels", or "duckduckgo"

    # FLUX AI Image Generation settings
    FLUX_MODEL = os.getenv("FLUX_MODEL", "schnell")  # "schnell" (fast) or "dev" (quality)
    FLUX_QUANTIZE = int(os.getenv("FLUX_QUANTIZE", "8"))  # 4-8 bits (lower = faster, less memory)

    # TikTok API settings
    TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY") or _env_values.get("TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET") or _env_values.get("TIKTOK_CLIENT_SECRET")
    TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN") or _env_values.get("TIKTOK_ACCESS_TOKEN")
    TIKTOK_REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN") or _env_values.get("TIKTOK_REFRESH_TOKEN")
    TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI") or _env_values.get("TIKTOK_REDIRECT_URI", "http://localhost:8080/callback")

    # Directories
    OUTPUT_DIR = "output"
    AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
    IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
    VIDEOS_DIR = os.path.join(OUTPUT_DIR, "videos")
    LOGS_DIR = "logs"
    
    # Voice options
    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "EMAIL_SENDER": cls.EMAIL_SENDER,
            "EMAIL_RECEIVER": cls.EMAIL_RECEIVER,
            "EMAIL_APP_PASSWORD": cls.EMAIL_APP_PASSWORD,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.OUTPUT_DIR, cls.AUDIO_DIR, cls.IMAGES_DIR, 
                         cls.VIDEOS_DIR, cls.LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)
