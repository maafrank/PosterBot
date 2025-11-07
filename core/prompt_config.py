"""
PromptConfig - Loads and manages YAML-based prompt configurations
"""

import yaml
import os
from typing import Dict, List, Any, Optional


class PromptConfig:
    """Manages prompt configurations for different content types"""

    def __init__(self, config_path: str):
        """
        Load a prompt configuration from YAML file

        Args:
            config_path: Path to YAML config file
        """
        self.config_path = config_path
        self.data = self._load_config(config_path)
        self._validate_config()

    @staticmethod
    def from_name(config_name: str) -> 'PromptConfig':
        """
        Load a config by name (looks in prompt_configs/ directory)

        Args:
            config_name: Name of config (e.g., "cars", "alien_stories")

        Returns:
            PromptConfig instance
        """
        # Try with .yaml extension first
        config_path = os.path.join("prompt_configs", f"{config_name}.yaml")

        if not os.path.exists(config_path):
            # Try without extension (in case user provided it)
            config_path = os.path.join("prompt_configs", config_name)

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found: {config_name}\n"
                f"Looking in: prompt_configs/{config_name}.yaml"
            )

        return PromptConfig(config_path)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"Empty or invalid YAML config: {config_path}")

        return data

    def _validate_config(self):
        """Validate that required fields are present"""
        required_sections = ['content_idea', 'story_writer', 'image_generation']

        for section in required_sections:
            if section not in self.data:
                raise ValueError(
                    f"Missing required section '{section}' in config: {self.config_path}"
                )

        # Validate content_idea section
        content_idea = self.data['content_idea']
        if 'role' not in content_idea or 'task' not in content_idea:
            raise ValueError("content_idea section must have 'role' and 'task'")

        # Validate story_writer section
        story_writer = self.data['story_writer']
        if 'role' not in story_writer:
            raise ValueError("story_writer section must have 'role'")

        # Validate image_generation section
        image_gen = self.data['image_generation']
        if 'shot_templates' not in image_gen:
            raise ValueError("image_generation section must have 'shot_templates'")

    # === Content Idea Generation ===

    def get_content_idea_prompt(self) -> str:
        """Generate the full prompt for content idea generation"""
        section = self.data['content_idea']

        prompt = f"# ROLE:\n{section['role']}\n\n"
        prompt += f"# TASK:\n{section['task']}\n\n"

        if 'output_characteristics' in section:
            prompt += f"# OUTPUT CHARACTERISTICS:\n{section['output_characteristics']}\n\n"

        if 'examples' in section and section['examples']:
            prompt += "# EXAMPLES:\n\n"
            for i, example in enumerate(section['examples'], 1):
                prompt += f"## Example {i}:\n"
                prompt += str(example) + "\n\n"

        return prompt

    def get_content_idea_model(self) -> str:
        """Get the model to use for content idea generation"""
        return self.data['content_idea'].get('model', 'gpt-4o-mini')

    def get_content_idea_temperature(self) -> float:
        """Get the temperature for content idea generation"""
        return self.data['content_idea'].get('temperature', 2.0)

    def get_subject_key(self) -> str:
        """Get the JSON key that contains the subject/topic"""
        return self.data['content_idea'].get('subject_key', 'subject')

    # === Story Writing ===

    def get_story_writer_prompt(self, concept: str, duration: int = 60) -> str:
        """Generate the full prompt for story writing"""
        section = self.data['story_writer']

        prompt = f"# ROLE:\n{section['role']}\n\n"

        prompt += f"# TASK:\n"
        prompt += f"Write a {duration}-second video script based on the following concept: \"{concept}\".\n\n"

        if 'structure' in section:
            prompt += "Use this structure:\n"
            if isinstance(section['structure'], list):
                for item in section['structure']:
                    prompt += f"- {item}\n"
            else:
                prompt += section['structure']
            prompt += "\n"

        if 'instructions' in section:
            prompt += f"# INSTRUCTIONS:\n{section['instructions']}\n\n"

        if 'output_characteristics' in section:
            prompt += f"# OUTPUT CHARACTERISTICS:\n{section['output_characteristics']}\n\n"

        if 'tone' in section:
            prompt += f"Tone: {section['tone']}\n"

        if 'max_words' in section:
            prompt += f"Max words: {section['max_words']}\n"

        if 'examples' in section and section['examples']:
            prompt += "\n# EXAMPLES:\n"
            for example in section['examples']:
                prompt += f"{example}\n\n"

        return prompt

    def get_story_writer_model(self) -> str:
        """Get the model to use for story writing"""
        return self.data['story_writer'].get('model', 'gpt-4o-mini')

    def get_story_writer_temperature(self) -> float:
        """Get the temperature for story writing"""
        return self.data['story_writer'].get('temperature', 1.9)

    # === Image Generation ===

    def get_image_strategy(self) -> str:
        """Get the image generation strategy (flux-schnell, flux-dev, pexels, etc.)"""
        return self.data['image_generation'].get('strategy', 'flux-schnell')

    def get_image_prompt_mode(self) -> str:
        """
        Get the image prompt generation mode

        Returns:
            'ai_generated' or 'templated' (default)
        """
        return self.data['image_generation'].get('mode', 'templated')

    def get_image_base_style(self) -> str:
        """Get the base style applied to all image prompts"""
        return self.data['image_generation'].get('base_style', 'photorealistic, high quality')

    def get_ai_prompt_instructions(self) -> Optional[str]:
        """
        Get custom AI prompt generation instructions

        Returns:
            Custom instructions string or None to use defaults
        """
        return self.data['image_generation'].get('ai_prompt_instructions', None)

    def get_shot_templates(self) -> List[Dict[str, str]]:
        """
        Get the list of shot templates for image generation (fallback for AI mode)

        Returns:
            List of dicts with keys: name, description, template
        """
        return self.data['image_generation'].get('shot_templates', [])

    def get_shot_count(self) -> int:
        """Get the number of shots/images to generate"""
        # If mode is ai_generated, check for explicit count, otherwise use template count
        if self.get_image_prompt_mode() == 'ai_generated':
            return self.data['image_generation'].get('count', 10)
        else:
            return len(self.get_shot_templates())

    # === Distribution ===

    def get_default_platform(self) -> str:
        """Get the default distribution platform"""
        if 'distribution' in self.data:
            return self.data['distribution'].get('default_platform', 'email')
        return 'email'

    def get_caption_template(self) -> str:
        """Get the template for generating captions"""
        if 'distribution' in self.data:
            return self.data['distribution'].get('caption_template', 'Check out this video!')
        return 'Check out this video!'

    # === General ===

    def get_name(self) -> str:
        """Get the config name"""
        return self.data.get('name', 'unknown')

    def get_description(self) -> str:
        """Get the config description"""
        return self.data.get('description', '')

    def __str__(self) -> str:
        """String representation"""
        return f"PromptConfig(name='{self.get_name()}', shots={self.get_shot_count()})"

    def __repr__(self) -> str:
        return self.__str__()
