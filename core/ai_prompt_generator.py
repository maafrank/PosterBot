"""
AI Prompt Generator for creating diverse image prompts
"""

class AIPromptGenerator:
    """Generates diverse, cinematic prompts for AI image generation"""

    # Default base style (used if not provided)
    DEFAULT_BASE_STYLE = "professional photography, 8k uhd, dslr, high quality, photorealistic, cinematic lighting, sharp focus"

    @staticmethod
    def generate_prompts(subject_name, count=10, shot_templates=None, base_style=None):
        """
        Generate diverse prompts for a specific subject

        Args:
            subject_name: Name of the subject (e.g., "1994-2001 Acura Integra Type R", "Phoenix Lights UFO")
            count: Number of prompts to generate (default: 10)
            shot_templates: List of template dicts with 'name', 'description', 'template' keys (required)
            base_style: Base style string to append to prompts
                       If None, uses DEFAULT_BASE_STYLE

        Returns:
            list: List of prompt dicts with 'prompt', 'description', 'name' keys
        """
        if shot_templates is None:
            raise ValueError("shot_templates is required. Legacy DEFAULT_CAR_TEMPLATES has been removed.")

        prompts = []

        # Use default base style if not provided
        if base_style is None:
            base_style = AIPromptGenerator.DEFAULT_BASE_STYLE

        # Clean the subject name (remove generation codes, etc.)
        clean_name = AIPromptGenerator._clean_subject_name(subject_name)

        # Generate prompts using templates
        templates_to_use = shot_templates[:count]

        for template_info in templates_to_use:
            template = template_info["template"]
            prompt = template.format(
                subject=clean_name,
                base_style=base_style
            )
            prompts.append({
                "prompt": prompt,
                "description": template_info["description"],
                "name": template_info["name"]
            })

        return prompts

    @staticmethod
    def _clean_subject_name(subject_name):
        """
        Clean subject name while preserving important information
        Examples:
            "1994-2001 Acura Integra Type R (DC2)" -> "1994-2001 Acura Integra Type R"
            "2020 Toyota Supra (A90)" -> "2020 Toyota Supra"
            "Phoenix Lights 1997" -> "Phoenix Lights 1997"
        """
        import re

        # Remove generation codes in parentheses (e.g., "(DC2)", "(A90)")
        cleaned = re.sub(r'\s*\([^)]*\)', '', subject_name)

        # Normalize en-dash to hyphen for year ranges
        cleaned = cleaned.replace('–', '-')

        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()

