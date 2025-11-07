# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## PosterBot Overview

PosterBot is an automated video content creation and distribution system that generates viral short-form videos (currently focused on car content). It uses AI to generate ideas, write scripts, create voiceovers, collect images, compose videos, and distribute them.

## Running the Application

### Basic Commands
```bash
# Create a single video and email it
python3 main.py

# Create multiple videos
python3 main.py --count 5

# Post video to TikTok
python3 main.py --distribute-to tiktok

# Create video without distribution (for testing)
python3 main.py --no-distribute

# Create video about different topic (requires prompt customization)
python3 main.py --topic tech
```

### Required Setup
- **ffmpeg**: Must be installed (`brew install ffmpeg` on macOS)
- **API Keys**: Configure in `.env` file (OpenAI, Pexels, Email)
- **Dependencies**: `pip install -r requirements.txt`

## Architecture

### Pipeline Flow
The `Pipeline` class (`core/pipeline.py`) orchestrates a 6-step workflow:
1. **ContentIdeaGenerator** → Generates video concept via OpenAI
2. **StoryWriter** → Writes 60-second script
3. **TextToSpeech** → Converts script to audio (OpenAI TTS)
4. **MediaCollector** → Downloads images (Pexels API or DuckDuckGo fallback)
5. **VideoComposer** → Combines images + audio using MoviePy
6. **Distributor** → Sends to platform (email/Instagram/TikTok/YouTube)

### Core Components (`core/` directory)

**`content_generator.py`**: `ContentIdeaGenerator`
- Returns: `{"subject": "car name", "concept": "video hook"}`
- Prompts are embedded in `_get_prompt(topic)` method
- Currently supports "cars" topic with edgy/viral style

**`story_writer.py`**: `StoryWriter`
- Takes concept, returns ~250 word script
- Optimized for 60-second voiceover timing
- Prompts embedded in `_get_prompt()` method

**`text_to_speech.py`**: `TextToSpeech`
- Splits text into sentences, generates audio per sentence
- Returns list of durations (seconds) for video sync
- Randomly selects from 6 OpenAI voices (or use specific voice)
- Outputs: `output/audio/audio_N.mp3` + `output/combined_output.wav`

**`media_collector.py`**: `MediaCollector`
- **Primary source**: Pexels API (200 requests/hour free)
- **Fallback**: DuckDuckGo search (unreliable, heavy rate limiting)
- Query simplification: Removes parentheses, keeps brand/model/years, adds "car"
- Auto-crops/resizes to target dimensions (1280x1280 default)

**`video_composer.py`**: `VideoComposer`
- Uses MoviePy to sequence images with timing from TTS
- Each image displays for duration of corresponding audio segment
- Output: MP4 with H.264 video, AAC audio, FPS=1

**`distributor.py`**: `Distributor`
- **TikTok**: Full integration with Content Posting API (Direct Post)
  - Auto token refresh (access tokens valid 24hrs, refresh tokens 1yr)
  - Videos post as SELF_ONLY (private) in sandbox mode
  - 3-step process: init upload → upload video → check status
- **Email**: via yagmail with Gmail app passwords
- **Placeholder for**: Instagram, YouTube
- **none**: Skip distribution for testing

### Configuration (`config.py`)

Centralized config loaded from `.env`:
- `OPENAI_API_KEY`, `PEXELS_API_KEY`
- `EMAIL_SENDER`, `EMAIL_RECEIVER`, `EMAIL_APP_PASSWORD`
- `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`, `TIKTOK_REFRESH_TOKEN`, `TIKTOK_REDIRECT_URI`
- `VIDEO_WIDTH`, `VIDEO_HEIGHT`, `VIDEO_FPS`
- `IMAGE_SOURCE` (default: "pexels", fallback: "duckduckgo")
- `DEFAULT_VOICE` ("random" or specific: alloy/echo/fable/onyx/nova/shimmer)

## Key Implementation Details

### Image Collection Strategy
- **Pexels** (preferred): Searches for "{brand} {model} {years} car", orientation=landscape
- **DuckDuckGo** (fallback): Multiple search variations with exponential backoff
- Rate limiting: Pexels has generous limits; DuckDuckGo blocks aggressively
- Query simplification removes generation codes (e.g., "(EJ/EK)") but keeps core info

### Audio/Video Sync
1. TTS returns list of durations per sentence: `[2.3, 1.8, 3.1, ...]`
2. VideoComposer matches image count to duration count (truncates if needed)
3. Images displayed sequentially for their corresponding duration
4. Combined audio track (`combined_output.wav`) plays over entire video

### Error Handling
- Pipeline catches exceptions per iteration, logs, and continues
- MediaCollector raises `RuntimeError` if no images collected
- Config validation happens at pipeline start (`Config.validate()`)

## Adding New Topics

1. **Edit `core/content_generator.py`**: Add new prompt in `_get_prompt(topic)`
2. **Edit `core/story_writer.py`**: Add corresponding script template
3. Prompts should return JSON with `{"subject": "...", "concept": "..."}`
4. Test with: `python3 main.py --topic newtopic --no-distribute`

## Adding Distribution Platforms

1. **Edit `core/distributor.py`**: Add method like `_post_to_instagram(video_path, metadata)`
2. **Update `distribute()` method**: Add elif branch for new platform
3. Platform-specific auth/config goes in `.env` and `config.py`

## Switching Image Sources

Set `IMAGE_SOURCE` in `.env` to control how images are collected:

- **`flux-schnell`**: Local AI generation (fast, 4-10s per image) - **NEW!** ⭐
- **`flux-dev`**: Local AI generation (high quality, 15-30s per image) - **NEW!** ⭐
- **`pexels`**: Pexels stock photos (default, fast but limited by API rate)
- **`duckduckgo`**: Web search (not recommended due to rate limits)

### FLUX AI Generation (Recommended for M3 Mac)

PosterBot now supports **local AI image generation** using FLUX models. This eliminates API costs and provides photorealistic car images.

**See [FLUX_SETUP.md](FLUX_SETUP.md) for complete setup instructions.**

Quick setup:
```bash
pip install mflux
# Set in .env:
IMAGE_SOURCE=flux-schnell
FLUX_MODEL=schnell
FLUX_QUANTIZE=8
```

**Benefits:**
- Free forever (no API costs)
- No rate limits
- Photorealistic quality
- Generates any car model (even rare/obscure ones)
- 10 diverse angles per video automatically

**Performance on M3 18GB:**
- FLUX Schnell: ~1-2 minutes for 10 images
- FLUX Dev: ~3-5 minutes for 10 images

To add other sources (e.g., Unsplash, DALL-E):
1. Add API key to `.env` and `config.py`
2. Implement `_collect_images_newsource()` in `media_collector.py`
3. Add conditional in `collect_media()` method

## Output Locations
- **Videos**: `output/videos/*.mp4`
- **Audio**: `output/audio/*.mp3` + `output/combined_output.wav`
- **Images**: `output/images/*.jpg`
- **Logs**: `logs/pipeline_YYYYMMDD_HHMMSS.log`

All output directories auto-created by `Config.create_directories()`.

## TikTok Integration Setup

### Initial Setup (One-Time)
1. **Register TikTok Developer App** at [developers.tiktok.com](https://developers.tiktok.com)
2. **Add Content Posting API** product with Direct Post enabled
3. **Request `video.publish` scope**
4. **Set redirect URI**: `https://maafrank.github.io/webapps/PosterBot/callback.html`
5. **Verify domain/URL** using verification file
6. **Submit for review** with demo video (3-14 day approval)

### Getting Access Tokens
Run the OAuth script once approved (or in sandbox for testing):
```bash
python3 tiktok_auth.py
```
This will:
- Open TikTok authorization in browser
- Get authorization code from callback page
- Exchange for access/refresh tokens
- Save to `.env` automatically

Tokens valid for: Access token (24hrs), Refresh token (1yr). Auto-refresh handled by distributor.

### Posting to TikTok
```bash
python3 main.py --distribute-to tiktok
```

**Important Notes:**
- Sandbox mode posts are **private only** (SELF_ONLY)
- Production mode (after approval) allows public posting
- Videos must be MP4 with H.264 codec
- Max caption length: 2200 characters
- Upload size limit varies by account
