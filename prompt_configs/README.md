# Prompt Configurations

This directory contains YAML configuration files that define how PosterBot generates different types of content.

## Available Configs

### `cars.yaml`
- **Description**: Edgy automotive content about cars
- **Style**: Viral TikTok/Instagram, opinionated, humorous
- **Image Strategy**: FLUX Schnell (fast AI generation)
- **Shot Templates**: 10 diverse car photography angles
- **Use Case**: Car reviews, automotive culture, vehicle comparisons

### `alien_stories.yaml`
- **Description**: UFO encounters and alien stories
- **Style**: Mysterious, suspenseful, documentary-style
- **Image Strategy**: FLUX Dev (high quality AI generation)
- **Shot Templates**: 10 atmospheric sci-fi images
- **Use Case**: UFO sightings, alien encounters, unexplained phenomena

## Configuration File Structure

Each config file has 4 main sections:

### 1. Content Idea Generation
Defines how the AI generates video concepts:
```yaml
content_idea:
  model: "gpt-4o-mini"
  temperature: 2.0
  subject_key: "car"  # JSON key for the subject
  role: |
    Your role description...
  task: |
    Your task instructions...
  examples:
    - Example JSON outputs
```

### 2. Story/Script Writing
Defines how the AI writes the video script:
```yaml
story_writer:
  model: "gpt-4o-mini"
  temperature: 1.9
  max_words: 250
  tone: "first-person, opinionated, humorous"
  role: |
    Your role description...
  structure:
    - Hook
    - Build tension
    - Main point
    - Conclusion
```

### 3. Image Generation
Defines how images are generated for the video.

**Two Modes Available:**

#### Mode 1: `templated` (Static Shot Templates)
Best for: Product content, consistent styling (e.g., cars)
```yaml
image_generation:
  strategy: "flux-schnell"
  mode: "templated"  # Use predefined shot templates
  base_style: "professional automotive photography, 8k uhd..."

  shot_templates:
    - name: "hero_shot"
      description: "Main hero angle"
      template: "{subject}, cinematic angle, {base_style}"
    # ... more templates (10 total)
```
The `{subject}` placeholder is replaced with the video subject (e.g., "2020 Toyota Supra").

#### Mode 2: `ai_generated` (Story-Based Prompts) ⭐ NEW!
Best for: Storytelling content where images should match narrative (e.g., alien encounters, scary stories)
```yaml
image_generation:
  strategy: "flux-dev"
  mode: "ai_generated"  # AI generates prompts based on script
  count: 10  # Number of images
  base_style: "cinematic sci-fi photography, photorealistic..."

  # Optional: Custom instructions for AI (uses smart defaults if omitted)
  ai_prompt_instructions: |
    Generate 10 cinematic image prompts that follow the story...
    [Custom rules and guidelines]

  # Fallback templates (if AI generation fails)
  shot_templates: [...]
```

**How AI Mode Works:**
1. Script is written by StoryWriter
2. Script + subject passed to `ImagePromptGenerator`
3. AI reads the story and generates 10 context-specific image prompts
4. Base style (photorealistic, 8k, etc.) automatically appended to all prompts
5. FLUX generates images from these prompts

**Benefits of AI Mode:**
- Images match the actual story being told
- Each video gets unique, contextual visuals
- Natural narrative flow (beginning → middle → end)
- No generic shots - everything is story-specific

### 4. Distribution
Defines default distribution settings:
```yaml
distribution:
  default_platform: "email"
  caption_template: "Check out this {subject}!"
```

## Using Configs

### Command Line
```bash
# Use cars config
python3 main.py --config cars

# Use alien_stories config
python3 main.py --config alien_stories --count 3

# With specific distribution
python3 main.py --config cars --distribute-to tiktok
```

### List Available Configs
```bash
python3 main.py --config nonexistent
# This will error but show available configs
```

## Creating New Configs

1. Copy an existing config file (e.g., `cars.yaml`)
2. Rename it to your new topic (e.g., `scary_stories.yaml`)
3. Update all sections:
   - Change `name` and `description`
   - Rewrite `content_idea` prompts for your topic
   - Rewrite `story_writer` prompts
   - Create new `shot_templates` for your image style
   - Update `subject_key` to match your JSON output
4. Test it:
   ```bash
   python3 main.py --config scary_stories --no-distribute
   ```

## Tips

- **Temperature**: Higher values (1.8-2.0) = more creative, lower (0.7-1.2) = more predictable
- **Image Strategy**:
  - `flux-schnell`: Fast (4-10s per image), good quality
  - `flux-dev`: Slow (15-30s per image), best quality
  - `pexels`: Stock photos from Pexels API
  - `duckduckgo`: Web search (not recommended, heavy rate limits)
- **Shot Templates**: You can have any number of templates (5, 10, 15, etc.)
- **Subject Key**: Must match the JSON key returned by `content_idea`

## Validation

The PromptConfig class validates that:
- All required sections exist (`content_idea`, `story_writer`, `image_generation`)
- Each section has required fields (`role`, `task`, `shot_templates`, etc.)
- If validation fails, you'll get a clear error message

## Examples

### Minimal Config
```yaml
name: "simple"
description: "Minimal example"

content_idea:
  role: "You are a content creator"
  task: "Generate ideas as JSON: {\"subject\": \"...\", \"concept\": \"...\"}"

story_writer:
  role: "You are a script writer"

image_generation:
  shot_templates:
    - name: "shot1"
      description: "First shot"
      template: "{subject}, photorealistic"
```

### Advanced Config
See `cars.yaml` or `alien_stories.yaml` for full examples with:
- Multiple examples
- Detailed instructions
- Custom OpenAI parameters
- 10+ shot templates
- Specific tone and structure guidance
