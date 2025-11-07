"""
AI Prompt Generator for creating diverse image prompts
"""

class AIPromptGenerator:
    """Generates diverse, cinematic prompts for AI image generation"""

    # Default base style (used if not provided)
    DEFAULT_BASE_STYLE = "professional photography, 8k uhd, dslr, high quality, photorealistic, cinematic lighting, sharp focus"

    # Legacy car shot templates (for backward compatibility)
    DEFAULT_CAR_TEMPLATES = [
        {
            "name": "hero_front",
            "template": "{subject}, front three-quarter view, studio lighting, clean background, {base_style}",
            "description": "Hero front 3/4 angle"
        },
        {
            "name": "side_profile",
            "template": "{subject}, side profile view, clean minimalist background, professional car photography, {base_style}",
            "description": "Side profile"
        },
        {
            "name": "rear_angle",
            "template": "{subject}, rear three-quarter view, dramatic lighting, showing taillights and rear design, {base_style}",
            "description": "Rear 3/4 angle"
        },
        {
            "name": "detail_closeup",
            "template": "{subject}, extreme close-up of headlight and front grille, macro photography, {base_style}",
            "description": "Close-up detail shot"
        },
        {
            "name": "action_motion",
            "template": "{subject}, driving on scenic road, motion blur background, speed and movement, {base_style}",
            "description": "Action shot in motion"
        },
        {
            "name": "lifestyle_context",
            "template": "{subject}, parked in urban city street at sunset, modern architecture background, lifestyle photography, {base_style}",
            "description": "Lifestyle context shot"
        },
        {
            "name": "interior_cabin",
            "template": "{subject} interior, dashboard and steering wheel view, driver's perspective, automotive interior photography, {base_style}",
            "description": "Interior cabin view"
        },
        {
            "name": "aerial_top",
            "template": "{subject}, aerial top-down view, drone photography, geometric composition, {base_style}",
            "description": "Aerial top-down view"
        },
        {
            "name": "low_angle",
            "template": "{subject}, low angle ground level shot, aggressive stance, dramatic sky background, {base_style}",
            "description": "Low angle ground shot"
        },
        {
            "name": "night_scene",
            "template": "{subject}, night scene with city lights, dramatic lighting, reflections on wet pavement, {base_style}",
            "description": "Night scene shot"
        }
    ]

    @staticmethod
    def generate_prompts(subject_name, count=10, shot_templates=None, base_style=None):
        """
        Generate diverse prompts for a specific subject

        Args:
            subject_name: Name of the subject (e.g., "1994-2001 Acura Integra Type R", "Phoenix Lights UFO")
            count: Number of prompts to generate (default: 10)
            shot_templates: List of template dicts with 'name', 'description', 'template' keys
                           If None, uses DEFAULT_CAR_TEMPLATES
            base_style: Base style string to append to prompts
                       If None, uses DEFAULT_BASE_STYLE

        Returns:
            list: List of prompt dicts with 'prompt', 'description', 'name' keys
        """
        prompts = []

        # Use defaults if not provided
        if shot_templates is None:
            shot_templates = AIPromptGenerator.DEFAULT_CAR_TEMPLATES

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

    @staticmethod
    def _clean_car_name(car_name):
        """
        Legacy method for backward compatibility
        Alias for _clean_subject_name
        """
        return AIPromptGenerator._clean_subject_name(car_name)

    @staticmethod
    def _simplify_car_name(car_name):
        """
        Simplify car name for AI understanding (legacy method)
        Examples:
            "1994-2001 Acura Integra Type R (DC2)" -> "Acura Integra Type R"
            "2020 Toyota Supra (A90)" -> "Toyota Supra"
        """
        import re

        # Remove year ranges (e.g., "1994-2001" or "1994–2001")
        simplified = re.sub(r'\d{4}[-–]\d{4}\s*', '', car_name)

        # Remove single years at the start
        simplified = re.sub(r'^\d{4}\s+', '', simplified)

        # Remove generation codes in parentheses (e.g., "(DC2)", "(A90)")
        simplified = re.sub(r'\s*\([^)]*\)', '', simplified)

        # Clean up extra spaces
        simplified = ' '.join(simplified.split())

        return simplified.strip()

    @staticmethod
    def generate_single_prompt(subject_name, shot_type="hero_front", shot_templates=None, base_style=None):
        """
        Generate a single prompt for a specific shot type

        Args:
            subject_name: Name of the subject
            shot_type: Type of shot (matches template names)
            shot_templates: List of template dicts (optional)
            base_style: Base style string (optional)

        Returns:
            str: Generated prompt
        """
        if shot_templates is None:
            shot_templates = AIPromptGenerator.DEFAULT_CAR_TEMPLATES

        if base_style is None:
            base_style = AIPromptGenerator.DEFAULT_BASE_STYLE

        simplified_name = AIPromptGenerator._simplify_car_name(subject_name)

        # Find the template
        template_info = next(
            (t for t in shot_templates if t["name"] == shot_type),
            shot_templates[0]  # Default to first shot
        )

        prompt = template_info["template"].format(
            subject=simplified_name,
            base_style=base_style
        )

        return prompt
