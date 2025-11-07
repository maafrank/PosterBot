import os
import shutil
import random
from openai import OpenAI
from pydub import AudioSegment
from config import Config

class TextToSpeech:
    """Converts text to speech using OpenAI TTS"""
    
    def __init__(self, api_key=None, voice=None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.voice = voice or Config.DEFAULT_VOICE
    
    def generate_audio(self, text, output_dir=None):
        """
        Convert text to speech and return timing information

        Args:
            text: The text to convert to speech
            output_dir: Directory to save audio files (default: Config.AUDIO_DIR)

        Returns:
            tuple: (durations, sentences) where:
                - durations: list of duration in seconds for each sentence
                - sentences: list of sentence strings
        """
        if output_dir is None:
            output_dir = Config.AUDIO_DIR
        
        # Clean up and recreate audio directory
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Split text into sentences
        sentences = self._split_sentences(text)
        print(f"Processing {len(sentences)} sentences...")
        
        # Select voice
        voice = self._select_voice()
        print(f"Using voice: {voice}")
        
        # Generate audio for each sentence
        audio_segments = []
        durations = []
        
        for i, sentence in enumerate(sentences):
            try:
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence
                )
                
                # Save audio file
                audio_path = os.path.join(output_dir, f"audio_{i}.mp3")
                response.stream_to_file(audio_path)
                
                # Load and get duration
                audio = AudioSegment.from_mp3(audio_path)
                durations.append(audio.duration_seconds)
                audio_segments.append(audio)
                
            except Exception as e:
                print(f"Error generating audio for sentence {i}: {e}")
                continue
        
        # Combine all audio segments
        if audio_segments:
            combined_audio = sum(audio_segments)
            combined_path = os.path.join(Config.OUTPUT_DIR, "combined_output.wav")
            combined_audio.export(combined_path, format="wav")
            print(f"Combined audio saved to: {combined_path}")

        return durations, sentences
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        # Clean and split by period
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        # Remove last sentence if it seems incomplete or very short
        if sentences and len(sentences[-1]) < 10:
            sentences = sentences[:-1]
        return sentences
    
    def _select_voice(self):
        """Select a voice for TTS"""
        if self.voice == "random":
            return random.choice(Config.AVAILABLE_VOICES)
        elif self.voice in Config.AVAILABLE_VOICES:
            return self.voice
        else:
            print(f"Unknown voice '{self.voice}', using random")
            return random.choice(Config.AVAILABLE_VOICES)
