# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## PosterBot Overview

PosterBot is an automated video content creation and distribution system that generates viral short-form videos. It uses AI to generate ideas, write scripts, create voiceovers, generate/collect images, compose videos, and distribute them.

**Supported Content Types:**
- **Cars**: Edgy automotive content (reviews, culture, comparisons)
- **Alien Stories**: UFO encounters and mysterious phenomena
- **Extensible**: Easy to add new content types via YAML configs

## Running the Application

### Basic Commands
```bash
# Create a car video using the 'cars' config
python3 main.py --config cars

# Create alien encounter video
python3 main.py --config alien_stories

# Create multiple videos
python3 main.py --config cars --count 5

# Post video to TikTok
python3 main.py --config cars --distribute-to tiktok

# Create video without distribution (for testing)
python3 main.py --config alien_stories --no-distribute

# Legacy mode (still works, uses hardcoded prompts)
python3 main.py --topic cars

# Test FLUX AI image generation (2 test images)
python3 test_flux.py

# List available configs
python3 main.py --config nonexistent  # Shows available configs on error
```

### Required Setup
- **ffmpeg**: Must be installed (`brew install ffmpeg` on macOS)
- **API Keys**: Configure in `.env` file (OpenAI, Pexels, Email)
- **Dependencies**: `pip install -r requirements.txt`

## Architecture

### Pipeline Flow
The `Pipeline` class ([core/pipeline.py](core/pipeline.py:1-199)) orchestrates a 6-step workflow:
1. **ContentIdeaGenerator** → Generates video concept via OpenAI (uses PromptConfig)
2. **StoryWriter** → Writes 60-second script (uses PromptConfig)
3. **TextToSpeech** → Converts script to audio (OpenAI TTS)
4. **MediaCollector** → Generates/downloads images (FLUX AI, Pexels, or DuckDuckGo - uses PromptConfig)
5. **VideoComposer** → Combines images + audio using MoviePy
6. **Distributor** → Sends to platform (email/Instagram/TikTok/YouTube)

### Prompt Configuration System

**NEW**: PosterBot now uses YAML-based prompt configs for easy content type management.

**`core/prompt_config.py`**: `PromptConfig`
- Loads YAML config files from `prompt_configs/` directory
- Validates required sections: `content_idea`, `story_writer`, `image_generation`
- Provides prompts, templates, and settings to all pipeline components
- Usage: `PromptConfig.from_name("cars")` or `PromptConfig("path/to/config.yaml")`

**Available Configs** (in `prompt_configs/` directory):
- **`cars.yaml`**: Automotive content (FLUX Schnell, 10 car shot templates)
- **`alien_stories.yaml`**: UFO/alien encounters (FLUX Dev, 10 sci-fi shot templates)
- See [prompt_configs/README.md](prompt_configs/README.md) for full documentation

### Core Components (`core/` directory)

**`content_generator.py`**: `ContentIdeaGenerator`
- Returns: `{"subject": "...", "concept": "video hook"}`
- **NEW**: Accepts `PromptConfig` object to customize prompts
- **Legacy**: Still supports `topic` parameter with hardcoded prompts
- Prompts now defined in YAML configs or `_get_legacy_prompt(topic)` method

**`story_writer.py`**: `StoryWriter`
- Takes concept, returns ~250 word script
- Optimized for 60-second voiceover timing
- **NEW**: Accepts `PromptConfig` object to customize prompts and tone
- **Legacy**: Still supports `topic` parameter with hardcoded prompts

**`text_to_speech.py`**: `TextToSpeech`
- Splits text into sentences, generates audio per sentence
- Returns list of durations (seconds) for video sync
- Randomly selects from 6 OpenAI voices (or use specific voice)
- Outputs: `output/audio/audio_N.mp3` + `output/combined_output.wav`

**`media_collector.py`**: `MediaCollector`
- **FLUX AI** (new): Local image generation with 10 diverse camera angles
  - Lazy-loads model on first use to save memory
  - Returns GeneratedImage objects (extract with `.image` property)
  - Supports both Schnell (fast) and Dev (quality) variants
- **Pexels API**: 200 requests/hour free, searches "{brand} {model} {years} car"
- **DuckDuckGo** (fallback): Unreliable, heavy rate limiting
- Query handling: Keeps year ranges, removes generation codes in parentheses
- Auto-crops/resizes to target dimensions (default: 576×1024 for TikTok/Reels)

**`ai_prompt_generator.py`**: `AIPromptGenerator`
- **NEW**: Now accepts dynamic shot templates and base style from PromptConfig
- Generates diverse prompts for any content type (cars, aliens, etc.)
- `generate_prompts(subject, count, shot_templates, base_style)` - fully customizable
- **Legacy**: Default car templates still available for backward compatibility
- Cleans subject names (removes generation codes, normalizes formatting)

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
- `VIDEO_WIDTH`, `VIDEO_HEIGHT`, `VIDEO_FPS` (default: 576×1024 for vertical TikTok/Reels format)
- `IMAGE_SOURCE` ("flux-schnell", "flux-dev", "pexels", or "duckduckgo")
- `FLUX_MODEL` ("schnell" for speed or "dev" for quality)
- `FLUX_QUANTIZE` (4-8 bits; lower = faster/less memory, higher = better quality)
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

## Adding New Content Types

**NEW**: Just create a YAML config file - no code changes needed!

### Quick Start (Recommended)
1. Copy an existing config:
   ```bash
   cp prompt_configs/cars.yaml prompt_configs/scary_stories.yaml
   ```

2. Edit the new config:
   - Change `name` and `description`
   - Update `content_idea` section (role, task, examples)
   - Update `story_writer` section (role, structure, tone)
   - Update `image_generation` section (strategy, shot_templates)
   - Update `subject_key` to match your JSON output

3. Test it:
   ```bash
   python3 main.py --config scary_stories --no-distribute
   ```

See [prompt_configs/README.md](prompt_configs/README.md) for detailed documentation.

### Legacy Method (Not Recommended)

If not using configs, edit code directly:
1. **Edit `core/content_generator.py`**: Add new prompt in `_get_legacy_prompt(topic)`
2. **Edit `core/story_writer.py`**: Add corresponding script template
3. **Edit `core/ai_prompt_generator.py`**: Add shot templates for the topic
4. Test with: `python3 main.py --topic newtopic --no-distribute`

## Adding Distribution Platforms

1. **Edit `core/distributor.py`**: Add method like `_post_to_instagram(video_path, metadata)`
2. **Update `distribute()` method**: Add elif branch for new platform
3. Platform-specific auth/config goes in `.env` and `config.py`

## Switching Image Sources

**Per-Config**: Set `image_generation.strategy` in your YAML config (recommended):
```yaml
image_generation:
  strategy: "flux-dev"  # or flux-schnell, pexels, duckduckgo
```

**Globally**: Set `IMAGE_SOURCE` in `.env` (applies to all configs without explicit strategy):

- **`flux-schnell`**: Local AI generation (fast, 4-10s per image) ⭐
- **`flux-dev`**: Local AI generation (high quality, 15-30s per image) ⭐
- **`pexels`**: Pexels stock photos (fast but limited by API rate)
- **`duckduckgo`**: Web search (not recommended due to rate limits)

### FLUX AI Generation (Recommended for M3 Mac)

PosterBot supports **local AI image generation** using FLUX models. This eliminates API costs and provides photorealistic images for any content type.

**See [FLUX_SETUP.md](FLUX_SETUP.md) for complete setup instructions.**

Quick setup:
```bash
pip install mflux
# Set in .env:
IMAGE_SOURCE=flux-schnell
FLUX_MODEL=schnell
FLUX_QUANTIZE=4  # Use 4 for M3 18GB to avoid OOM errors
VIDEO_WIDTH=576
VIDEO_HEIGHT=1024
```

**Benefits:**
- Free forever (no API costs)
- No rate limits
- Photorealistic quality
- Generates any subject (cars, UFOs, creatures, landscapes, etc.)
- Diverse angles/compositions per video (customizable via config)

**Performance on M3 18GB (4-bit quantization, 576×1024 resolution):**
- FLUX Schnell: ~50s per image, ~8-10 minutes for 10 images
- FLUX Dev: ~2-3 minutes per image, ~20-30 minutes for 10 images
- Memory usage: ~7-8GB (safe for 18GB RAM)

**Important Notes:**
- First run downloads ~10-15GB of model weights (one-time, 5-15 minutes)
- Higher resolutions (1080×1920) may cause out-of-memory errors on 18GB RAM
- Use `FLUX_QUANTIZE=4` for M3 18GB, `FLUX_QUANTIZE=8` for M3 Max 36GB+
- Model loads lazily on first image generation to save memory

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
