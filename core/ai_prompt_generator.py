"""
AI Prompt Generator for creating diverse car image prompts
"""

class AIPromptGenerator:
    """Generates diverse, cinematic prompts for AI image generation"""

    # Base style that ensures photorealism
    BASE_STYLE = "professional automotive photography, 8k uhd, dslr, high quality, photorealistic, cinematic lighting, sharp focus"

    # 10 different shot types for variety
    SHOT_TEMPLATES = [
        {
            "name": "hero_front",
            "template": "{car_name}, front three-quarter view, studio lighting, clean background, {base_style}",
            "description": "Hero front 3/4 angle"
        },
        {
            "name": "side_profile",
            "template": "{car_name}, side profile view, clean minimalist background, professional car photography, {base_style}",
            "description": "Side profile"
        },
        {
            "name": "rear_angle",
            "template": "{car_name}, rear three-quarter view, dramatic lighting, showing taillights and rear design, {base_style}",
            "description": "Rear 3/4 angle"
        },
        {
            "name": "detail_closeup",
            "template": "{car_name}, extreme close-up of headlight and front grille, macro photography, {base_style}",
            "description": "Close-up detail shot"
        },
        {
            "name": "action_motion",
            "template": "{car_name}, driving on scenic road, motion blur background, speed and movement, {base_style}",
            "description": "Action shot in motion"
        },
        {
            "name": "lifestyle_context",
            "template": "{car_name}, parked in urban city street at sunset, modern architecture background, lifestyle photography, {base_style}",
            "description": "Lifestyle context shot"
        },
        {
            "name": "interior_cabin",
            "template": "{car_name} interior, dashboard and steering wheel view, driver's perspective, automotive interior photography, {base_style}",
            "description": "Interior cabin view"
        },
        {
            "name": "aerial_top",
            "template": "{car_name}, aerial top-down view, drone photography, geometric composition, {base_style}",
            "description": "Aerial top-down view"
        },
        {
            "name": "low_angle",
            "template": "{car_name}, low angle ground level shot, aggressive stance, dramatic sky background, {base_style}",
            "description": "Low angle ground shot"
        },
        {
            "name": "night_scene",
            "template": "{car_name}, night scene with city lights, dramatic lighting, reflections on wet pavement, {base_style}",
            "description": "Night scene shot"
        }
    ]

    @staticmethod
    def generate_prompts(car_name, count=10):
        """
        Generate diverse prompts for a specific car

        Args:
            car_name: Name of the car (e.g., "1994-2001 Acura Integra Type R")
            count: Number of prompts to generate (default: 10)

        Returns:
            list: List of prompt strings
        """
        prompts = []

        # Keep the full car name including years for accurate generation
        # Just remove generation codes in parentheses
        clean_name = AIPromptGenerator._clean_car_name(car_name)

        # Generate prompts using templates
        templates_to_use = AIPromptGenerator.SHOT_TEMPLATES[:count]

        for template_info in templates_to_use:
            template = template_info["template"]
            prompt = template.format(
                car_name=clean_name,
                base_style=AIPromptGenerator.BASE_STYLE
            )
            prompts.append({
                "prompt": prompt,
                "description": template_info["description"],
                "name": template_info["name"]
            })

        return prompts

    @staticmethod
    def _clean_car_name(car_name):
        """
        Clean car name while preserving year information
        Examples:
            "1994-2001 Acura Integra Type R (DC2)" -> "1994-2001 Acura Integra Type R"
            "2020 Toyota Supra (A90)" -> "2020 Toyota Supra"
            "1990–1999 Mazda Miata" -> "1990-1999 Mazda Miata"
        """
        import re

        # Remove generation codes in parentheses (e.g., "(DC2)", "(A90)")
        cleaned = re.sub(r'\s*\([^)]*\)', '', car_name)

        # Normalize en-dash to hyphen for year ranges
        cleaned = cleaned.replace('–', '-')

        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()

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
    def generate_single_prompt(car_name, shot_type="hero_front"):
        """
        Generate a single prompt for a specific shot type

        Args:
            car_name: Name of the car
            shot_type: Type of shot (matches template names)

        Returns:
            str: Generated prompt
        """
        simplified_name = AIPromptGenerator._simplify_car_name(car_name)

        # Find the template
        template_info = next(
            (t for t in AIPromptGenerator.SHOT_TEMPLATES if t["name"] == shot_type),
            AIPromptGenerator.SHOT_TEMPLATES[0]  # Default to hero shot
        )

        prompt = template_info["template"].format(
            car_name=simplified_name,
            base_style=AIPromptGenerator.BASE_STYLE
        )

        return prompt
