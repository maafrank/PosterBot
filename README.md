# PosterBot

Automated video content creation and distribution system. Generate viral short-form videos for TikTok, Instagram, YouTube, and more.

## Features

- 🤖 AI-powered content idea generation
- ✍️ Automated script writing
- 🎙️ Text-to-speech with multiple voices
- 🖼️ Automatic image collection
- 🎬 Video composition with audio sync
- 📧 Multi-platform distribution (Email, Instagram*, TikTok*, YouTube*)

\* Coming soon

## Project Structure

```
PosterBot/
├── .env                    # Environment variables (API keys)
├── config.py              # Configuration management
├── main.py                # Main entry point
├── core/                  # Core modules
│   ├── content_generator.py
│   ├── story_writer.py
│   ├── text_to_speech.py
│   ├── media_collector.py
│   ├── video_composer.py
│   ├── distributor.py
│   └── pipeline.py
├── output/               # Generated content (gitignored)
│   ├── audio/
│   ├── images/
│   └── videos/
└── logs/                 # Application logs (gitignored)
```

## Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install ffmpeg (required for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### 2. Configure Environment

Update the `.env` file with your API keys and settings:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_key_here

# Email Configuration (for distribution)
EMAIL_SENDER=your_email@gmail.com
EMAIL_RECEIVER=recipient@gmail.com
EMAIL_APP_PASSWORD=your_app_password_here

# Video Settings (optional)
VIDEO_WIDTH=1280
VIDEO_HEIGHT=1280
VIDEO_FPS=1

# Content Settings (optional)
DEFAULT_VOICE=random  # or: alloy, echo, fable, onyx, nova, shimmer
IMAGE_COUNT=10
```

**Note:** For Gmail, you'll need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 3. Test Setup

```bash
python test_setup.py
```

## Usage

### Basic Usage

```bash
# Create 1 car video and email it
python main.py

# Create 5 car videos
python main.py --count 5

# Create video but don't distribute
python main.py --no-distribute
```

### Advanced Usage

```bash
# Create videos about a different topic (requires updating prompts)
python main.py --topic tech

# Specify distribution platform
python main.py --distribute-to email
```

## How It Works

1. **Idea Generation**: AI generates a viral content concept
2. **Script Writing**: AI writes a 60-second video script
3. **Text-to-Speech**: Converts script to audio with random voice
4. **Media Collection**: Downloads relevant images via DuckDuckGo
5. **Video Composition**: Combines images and audio into a video
6. **Distribution**: Sends via email (or other platforms)

## Extending PosterBot

### Adding New Topics

1. Edit `core/content_generator.py` - add a new prompt template
2. Edit `core/story_writer.py` - add a new script template

### Adding New Distribution Platforms

1. Edit `core/distributor.py`
2. Add a new method like `_post_to_instagram()`
3. Update the `distribute()` method

### Using AI-Generated Images

Replace `MediaCollector` implementation to use DALL-E or Midjourney instead of DuckDuckGo search.

## Troubleshooting

**OpenAI API Quota Error**
- Check your OpenAI account has available credits
- Update your API key in `.env`

**ffmpeg Not Found**
- Install ffmpeg (see Setup section)
- Restart your terminal after installation

**Email Not Sending**
- Make sure you're using a Gmail App Password, not your regular password
- Enable "Less secure app access" if using a non-Gmail provider

## Future Enhancements

- [ ] Instagram/TikTok/YouTube posting
- [ ] AI-generated images (DALL-E integration)
- [ ] Web UI for on-demand generation
- [ ] Scheduling system
- [ ] Multiple language support
- [ ] Custom voice cloning
- [ ] Subtitle generation

## License

MIT
