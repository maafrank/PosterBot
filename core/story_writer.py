from openai import OpenAI
from config import Config

class StoryWriter:
    """Writes video scripts from concepts using OpenAI"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
    
    def write_script(self, concept, duration=60, topic="cars"):
        """
        Write a video script based on a concept
        
        Args:
            concept: The concept/hook for the video
            duration: Target duration in seconds (default: 60)
            topic: The topic category (default: "cars")
            
        Returns:
            str: The video script
        """
        prompt = self._get_prompt(concept, duration, topic)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.9,
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
    
    def _get_prompt(self, concept, duration, topic):
        """Get the appropriate prompt based on topic"""
        if topic == "cars":
            return f"""
# ROLE:
You are an edgy automotive content writer who creates viral short-form video scripts for TikTok and Instagram. You combine car knowledge, humor, and controversy to keep car enthusiasts engaged for 60 seconds or less.

# TASK:
Write a {duration}-second video script based on the following concept: "{concept}". Use a direct, opinionated tone. Keep the pacing fast and structured to retain attention:
- Hook (first line should grab attention)
- Drama / conflict / unusual fact
- Breakdown of why it matters
- Punchline, twist, or unexpected takeaway
- Optional call to action ("Would you buy this?" or "Follow for more car drama.")

# Output Characteristics:
- Write it in first-person narrator voice
- Use short sentences and casual tone
- Include subtle humor or sarcasm
- Assume video will be paired with images/video clips of the car
- Max ~250 words (aim for {duration}-second voiceover timing)
- Do NOT add hashtags, emojis, or video editing instructions
- Kind of roast the car but actually hype the car up!

# Examples:
Concept: "Why the Porsche 996 sucks"
Script:
The Porsche 996 is the most hated 911 ever made.
It showed up with headlights that looked like scrambled eggs and an interior that felt cheaper than a 90s Corolla.
But the real kicker? The infamous IMS bearing—a tiny part that can grenade your entire engine.
Suddenly, buying a used 911 came with the same level of anxiety as dating a Hollywood starlet.
Still… it's got a flat-six. Rear-engine. Manual gearbox. And now it's the cheapest way into the 911 club.
So does it suck? Yeah. Do we love it anyway? Also yeah.
Would you risk it?
"""
        else:
            return f"""
# ROLE:
You are a creative content writer who creates viral short-form video scripts for TikTok and Instagram.

# TASK:
Write a {duration}-second video script based on the following concept: "{concept}". 
Use a direct, engaging tone. Keep the pacing fast:
- Hook (grab attention immediately)
- Build tension or curiosity
- Deliver the main point
- Memorable conclusion or call to action

# Output Characteristics:
- Write in first-person narrator voice
- Use short, punchy sentences
- Include humor where appropriate
- Max ~250 words (aim for {duration}-second voiceover timing)
- Do NOT add hashtags, emojis, or editing instructions
"""
