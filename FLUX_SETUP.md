# FLUX AI Image Generation Setup Guide

## Overview

PosterBot now supports **local AI image generation** using FLUX models from Black Forest Labs. This eliminates API costs and rate limits while providing photorealistic car images.

## Requirements

- **Apple Silicon Mac** (M1/M2/M3/M4)
- **18GB+ RAM** recommended for FLUX Schnell (16GB minimum)
- **macOS Monterey or later**
- **~15GB disk space** for model weights (downloaded on first run)

## Installation

### 1. Install mflux

```bash
pip install -r requirements.txt
```

Or install mflux directly:

```bash
pip install mflux
```

### 2. Configure .env

Add these settings to your `.env` file:

```bash
# Image Source Options:
# - "flux-schnell" = Fast AI generation (4-10 seconds/image)
# - "flux-dev" = High-quality AI generation (15-30 seconds/image)
# - "pexels" = Stock photos from Pexels API (default)
# - "duckduckgo" = Web search fallback
IMAGE_SOURCE=flux-schnell

# FLUX Model Settings (only used if IMAGE_SOURCE is flux-schnell or flux-dev)
FLUX_MODEL=schnell  # "schnell" or "dev"
FLUX_QUANTIZE=8     # 4-8 bits (lower = faster, less memory)
```

### 3. First Run

On first run, mflux will automatically download the FLUX model weights (~10-15GB). This takes 5-15 minutes depending on your internet connection.

```bash
python3 main.py --no-distribute
```

## Configuration Options

### IMAGE_SOURCE

| Value | Description | Speed | Quality | Cost |
|-------|-------------|-------|---------|------|
| `flux-schnell` | Fast AI generation | ⚡⚡⚡ | ⭐⭐⭐⭐ | Free |
| `flux-dev` | Quality AI generation | ⚡ | ⭐⭐⭐⭐⭐ | Free |
| `pexels` | Pexels stock photos | ⚡⚡⚡⚡ | ⭐⭐⭐ | Free (200/hr limit) |
| `duckduckgo` | Web search | ⚡⚡ | ⭐⭐ | Free (rate limited) |

### FLUX_MODEL

- **`schnell`** (recommended): Fast model, 4 inference steps, 4-10 seconds per image
- **`dev`**: High-quality model, 20 inference steps, 15-30 seconds per image

### FLUX_QUANTIZE

Controls memory usage and speed:

- **`4`**: Fastest, lowest quality (uses ~6GB RAM)
- **`6`**: Balanced (uses ~7GB RAM)
- **`8`**: Best quality (uses ~8GB RAM) ← **Recommended for M3 18GB**

## Performance Benchmarks (M3 18GB RAM)

### FLUX Schnell (Recommended)

- **Load time**: ~30 seconds (first time only)
- **Generation**: ~5-10 seconds per image
- **Total for 10 images**: ~1-2 minutes
- **Memory usage**: ~8GB

### FLUX Dev (High Quality)

- **Load time**: ~30 seconds (first time only)
- **Generation**: ~15-30 seconds per image
- **Total for 10 images**: ~3-5 minutes
- **Memory usage**: ~10GB

## Automatic Fallback System

If `IMAGE_SOURCE` is set to anything other than the explicit options above, PosterBot will try sources in this order:

1. **FLUX** (Schnell or Dev based on FLUX_MODEL)
2. **Pexels** (if FLUX fails)
3. **DuckDuckGo** (if both fail)

This ensures reliability even if FLUX encounters issues.

## Image Prompt Strategy

For each car, FLUX generates **10 diverse angles** automatically:

1. **Hero Front** - Front 3/4 view, studio lighting
2. **Side Profile** - Clean side view
3. **Rear Angle** - Back 3/4 showing taillights
4. **Detail Closeup** - Headlights, grille, badges
5. **Action Motion** - Car driving with motion blur
6. **Lifestyle Context** - Urban/scenic environment
7. **Interior Cabin** - Dashboard and steering wheel
8. **Aerial Top** - Drone perspective
9. **Low Angle** - Ground-level aggressive stance
10. **Night Scene** - Dramatic nighttime lighting

All prompts are automatically optimized for photorealism with professional automotive photography keywords.

## Usage Examples

### Generate video with FLUX Schnell (fast)

```bash
# Set in .env: IMAGE_SOURCE=flux-schnell
python3 main.py --no-distribute
```

### Generate video with FLUX Dev (quality)

```bash
# Set in .env: IMAGE_SOURCE=flux-dev, FLUX_MODEL=dev
python3 main.py --no-distribute
```

### Use FLUX for rare cars, Pexels for common ones

Edit [media_collector.py](core/media_collector.py) line 51-70 to add conditional logic based on car name.

## Troubleshooting

### "mflux is not installed"

```bash
pip install mflux
```

### "Out of memory" errors

Lower the quantization level in `.env`:

```bash
FLUX_QUANTIZE=4  # Use 4-bit quantization
```

Or reduce image resolution:

```bash
VIDEO_WIDTH=1024
VIDEO_HEIGHT=1024
```

### First generation is very slow

This is normal - the model needs to load and compile on first run. Subsequent generations will be much faster.

### Images don't look photorealistic

Try these adjustments:

1. Switch to `FLUX_MODEL=dev` for higher quality
2. Ensure `FLUX_QUANTIZE=8` for best quality
3. Check that prompts in [ai_prompt_generator.py](core/ai_prompt_generator.py) include photorealism keywords

### FLUX fails to load

Ensure you have:
- Apple Silicon Mac (M1/M2/M3/M4)
- At least 16GB RAM (18GB+ recommended)
- Sufficient disk space (~15GB for models)

## Cost Comparison

### Per Video (10 images)

| Source | Cost | Speed | Rate Limit |
|--------|------|-------|------------|
| FLUX Schnell | **$0.00** | 1-2 min | None |
| FLUX Dev | **$0.00** | 3-5 min | None |
| Pexels | $0.00 | 5-10 sec | 200/hour |
| DALL-E 3 | $0.40-0.80 | 5-10 min | None |

### For 100 videos/month

- **FLUX**: $0 (free forever)
- **Pexels**: $0 (if under rate limit)
- **DALL-E 3**: $40-80/month

## Advanced: Customizing Prompts

To modify the image prompts, edit [core/ai_prompt_generator.py](core/ai_prompt_generator.py).

Example: Add a "sunset" shot type:

```python
{
    "name": "sunset_shot",
    "template": "{car_name}, golden hour sunset lighting, scenic mountain road, {base_style}",
    "description": "Sunset scene"
}
```

## Next Steps

1. Run a test generation: `python3 main.py --no-distribute`
2. Review images in `output/images/`
3. If satisfied, run full pipeline: `python3 main.py`
4. For production, consider FLUX Schnell for speed or FLUX Dev for quality

## Support

- FLUX Documentation: https://github.com/filipstrand/mflux
- PosterBot Issues: Create an issue in this repository
