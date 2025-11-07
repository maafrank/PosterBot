import json
from openai import OpenAI
from config import Config

class ContentIdeaGenerator:
    """Generates content ideas for videos using OpenAI"""

    def __init__(self, api_key=None, prompt_config=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.prompt_config = prompt_config

        if not prompt_config:
            raise ValueError("ContentIdeaGenerator requires a PromptConfig object. Legacy topic-based mode has been removed.")

    def generate_idea(self, prompt_config=None):
        """
        Generate a content idea for a video

        Args:
            prompt_config: PromptConfig object (overrides instance config if provided)

        Returns:
            dict: {"subject": "...", "concept": "..."}
        """
        # Use provided config or instance config
        config = prompt_config or self.prompt_config

        if not config:
            raise ValueError("PromptConfig is required. Legacy topic-based mode has been removed.")

        # Use PromptConfig
        prompt = config.get_content_idea_prompt()
        model = config.get_content_idea_model()
        temperature = config.get_content_idea_temperature()
        subject_key = config.get_subject_key()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=1.0,
                presence_penalty=0.5,
                n=1,
                response_format={"type": "json_object"}
            )

            # Parse the JSON output
            idea = json.loads(response.choices[0].message.content)

            # Normalize the keys to match our expected format
            # The config tells us which key contains the subject
            if subject_key in idea and subject_key != "subject":
                idea["subject"] = idea.pop(subject_key)

            return idea

        except Exception as e:
            print(f"Failed to generate idea: {e}")
            return None
