import json
from openai import OpenAI
from config import Config

class ContentIdeaGenerator:
    """Generates content ideas for videos using OpenAI"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_idea(self, topic="cars"):
        """
        Generate a content idea for a video
        
        Args:
            topic: The topic for content generation (default: "cars")
            
        Returns:
            dict: {"subject": "...", "concept": "..."}
        """
        prompt = self._get_prompt(topic)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=2.0,
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
            if "car" in idea:
                idea["subject"] = idea.pop("car")
            
            return idea
            
        except Exception as e:
            print(f"Failed to generate idea: {e}")
            return None
    
    def _get_prompt(self, topic):
        """Get the appropriate prompt based on topic"""
        if topic == "cars":
            return """
# ROLE:
You are an edgy automotive content creator with deep knowledge of car culture, engineering quirks, internet memes, and enthusiast drama. You specialize in short-form video content that is provocative, opinionated, and funny.

# TASK:
Come up with a viral TikTok/Instagram video ideas. Each idea should be formatted as a JSON object with:
{
  "car": "the full name and year range of the car featured",
  "concept": "the hook or headline, 1 sentence long"
}
The idea should be short, controversial, or intriguing, and formatted as a video hook. Avoid generic car reviews. Think meme-worthy, spicy, internet-argument-fueling content.

# OUTPUT CHARACTERISTICS:
- Output a JSON object.
- Each object must have a "car" field with a year + model
- Each object must have a "concept" field with a dramatic or sarcastic headline
- Mention generation, model, and years
- DO NOT explain anything — just return the list of a JSON entry

# EXAMPLES:

## Example 1:
{
  "car": "2001–2004 Porsche 996",
  "concept": "Why the 996 is the most hated 911 (and why that's dumb)"
}
"""
        else:
            # Generic prompt for other topics
            return f"""
# ROLE:
You are a creative content creator who specializes in short-form viral video content for TikTok and Instagram.

# TASK:
Come up with a viral video idea about {topic}. Format it as a JSON object with:
{{
  "subject": "the main subject of the video",
  "concept": "the hook or headline, 1 sentence long"
}}

# OUTPUT CHARACTERISTICS:
- Output a JSON object only
- Must have "subject" and "concept" fields
- The concept should be intriguing, controversial, or funny
- DO NOT explain anything — just return the JSON

# EXAMPLE:
{{
  "subject": "Python Programming",
  "concept": "Why everyone says Python is easy but fails at it anyway"
}}
"""
