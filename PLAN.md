# PosterBot Refactoring Plan

## Current Workflow Analysis
The existing script performs the following steps:
1. **Story Idea Generation** → Generate a car video concept using OpenAI
2. **Story Writing** → Write a 60-second script based on the concept
3. **Text-to-Speech** → Convert the story into audio using OpenAI TTS
4. **Image Collection** → Download relevant car images via DuckDuckGo
5. **Video Creation** → Combine images and audio into a video
6. **Distribution** → Email the video (future: post to Instagram/TikTok/YouTube)

## Refactoring Goals
- **Modularity**: Separate concerns into distinct classes
- **Extensibility**: Easy to switch topics (cars → anything)
- **Configurability**: Environment-based configuration
- **Platform Independence**: Remove Google Colab dependencies
- **Scalability**: Easy to add new content sources and distribution channels

---

## New Architecture

### 1. Configuration Management
**File**: `.env`
- Store API keys and sensitive credentials
- Email configuration
- Default settings (voice preferences, video dimensions, etc.)

**File**: `config.py`
- Load environment variables
- Provide configuration constants
- Validate required keys are present

### 2. Core Classes

#### `ContentIdeaGenerator`
**Responsibility**: Generate content ideas for videos
- Method: `generate_idea(topic="cars")` → returns `{"subject": "...", "concept": "..."}`
- Uses OpenAI API
- Configurable prompts for different topics
- Future: Support multiple AI providers

#### `StoryWriter`
**Responsibility**: Write video scripts from concepts
- Method: `write_script(concept, duration=60)` → returns script text
- Uses OpenAI API
- Configurable tone, style, length
- Future: Template-based writing for different platforms

#### `TextToSpeech`
**Responsibility**: Convert text to audio
- Method: `generate_audio(text, output_dir="audio")` → returns `[durations]`
- Handles sentence splitting
- Random or specified voice selection
- Returns timing information for video sync

#### `MediaCollector`
**Responsibility**: Collect images/videos for content
- Method: `collect_media(query, count=10, media_type="image")` → returns `[file_paths]`
- Current: DuckDuckGo image search
- Handles resizing/cropping to target dimensions
- Future: Support for AI-generated images, stock video APIs, etc.

#### `VideoComposer`
**Responsibility**: Combine media and audio into video
- Method: `create_video(media_files, audio_file, durations, output_path)` → returns video path
- Syncs images with audio timing
- Handles encoding and format settings
- Configurable resolution, fps, codec

#### `Distributor`
**Responsibility**: Publish content to various platforms
- Method: `distribute(video_path, platform="email")` → returns status
- Current: Email distribution
- Future: Instagram, TikTok, YouTube APIs
- Platform-specific metadata and formatting

#### `Pipeline`
**Responsibility**: Orchestrate the entire workflow
- Method: `run(iterations=1, topic="cars")` → executes full pipeline
- Connects all components
- Error handling and retry logic
- Logging and progress tracking

---

## Project Structure
```
PosterBot/
├── .env                          # Environment variables (API keys, credentials)
├── .gitignore                    # Exclude .env, generated files
├── PLAN.md                       # This file
├── requirements.txt              # Python dependencies
├── config.py                     # Configuration loader
├── main.py                       # Entry point, runs the pipeline
├── core/
│   ├── __init__.py
│   ├── content_generator.py     # ContentIdeaGenerator class
│   ├── story_writer.py          # StoryWriter class
│   ├── text_to_speech.py        # TextToSpeech class
│   ├── media_collector.py       # MediaCollector class
│   ├── video_composer.py        # VideoComposer class
│   ├── distributor.py           # Distributor class
│   └── pipeline.py              # Pipeline orchestrator
├── prompts/                      # Prompt templates for different topics
│   ├── cars.json
│   └── general.json
├── output/                       # Generated content (gitignored)
│   ├── audio/
│   ├── images/
│   └── videos/
└── logs/                         # Application logs (gitignored)
```

---

## Implementation Steps

### Phase 1: Foundation ✓
- [x] Create PLAN.md
- [ ] Create `.env` file with API keys
- [ ] Create `.gitignore` (exclude .env, output/, logs/)
- [ ] Create `requirements.txt`
- [ ] Create `config.py` with env loading

### Phase 2: Core Classes
- [ ] Implement `ContentIdeaGenerator`
- [ ] Implement `StoryWriter`
- [ ] Implement `TextToSpeech`
- [ ] Implement `MediaCollector`
- [ ] Implement `VideoComposer`
- [ ] Implement `Distributor` (email first)

### Phase 3: Orchestration
- [ ] Implement `Pipeline` class
- [ ] Create `main.py` entry point
- [ ] Add error handling and logging
- [ ] Test end-to-end workflow

### Phase 4: Polish & Testing
- [ ] Test with car content
- [ ] Add prompt templates for other topics
- [ ] Documentation and README
- [ ] Optimization and cleanup

---

## Key Design Decisions

1. **Separation of Concerns**: Each class has one clear responsibility
2. **Dependency Injection**: Classes receive configuration, not hard-coded values
3. **File-based Organization**: Separate files for each major component
4. **Environment Configuration**: All secrets in .env, never committed
5. **Extensibility Points**:
   - Different AI providers (OpenAI, Anthropic, etc.)
   - Different media sources (DuckDuckGo, Pexels, AI generation)
   - Different distribution platforms (Email, Instagram, TikTok, YouTube)
   - Different content topics (cars, tech, cooking, etc.)

---

## Future Enhancements
- Web UI for generating videos on-demand
- Scheduling system for automated posting
- Analytics tracking (views, engagement)
- Multi-platform posting in one go
- AI-generated images/videos instead of search
- Custom voice cloning
- Subtitle generation
- Multiple language support
