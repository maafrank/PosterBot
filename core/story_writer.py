from openai import OpenAI
from config import Config

class StoryWriter:
    """Writes video scripts from concepts using OpenAI"""

    def __init__(self, api_key=None, prompt_config=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.prompt_config = prompt_config

        if not prompt_config:
            raise ValueError("StoryWriter requires a PromptConfig object. Legacy topic-based mode has been removed.")

    def write_script(self, concept, duration=60, prompt_config=None):
        """
        Write a video script based on a concept

        Args:
            concept: The concept/hook for the video
            duration: Target duration in seconds (default: 60)
            prompt_config: PromptConfig object (overrides instance config if provided)

        Returns:
            str: The video script
        """
        # Use provided config or instance config
        config = prompt_config or self.prompt_config

        if not config:
            raise ValueError("PromptConfig is required. Legacy topic-based mode has been removed.")

        # Use PromptConfig
        prompt = config.get_story_writer_prompt(concept, duration)
        model = config.get_story_writer_model()
        temperature = config.get_story_writer_temperature()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1000,
                top_p=0.90,
                frequency_penalty=1.2,
                n=1
            )

            story = response.choices[0].message.content
            return story

        except Exception as e:
            print(f"Failed to write script: {e}")
            return None
