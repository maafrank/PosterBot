import os
import shutil
import logging
from datetime import datetime
from config import Config
from core.content_generator import ContentIdeaGenerator
from core.story_writer import StoryWriter
from core.text_to_speech import TextToSpeech
from core.media_collector import MediaCollector
from core.video_composer import VideoComposer
from core.distributor import Distributor
from core.prompt_config import PromptConfig

class Pipeline:
    """Orchestrates the entire video creation and distribution workflow"""

    def __init__(self, prompt_config):
        """
        Initialize the pipeline

        Args:
            prompt_config: PromptConfig object (required)
        """
        if not prompt_config:
            raise ValueError("Pipeline requires a PromptConfig object. Legacy topic-based mode has been removed.")

        self.prompt_config = prompt_config

        # Initialize all components with config
        self.idea_generator = ContentIdeaGenerator(prompt_config=prompt_config)
        self.story_writer = StoryWriter(prompt_config=prompt_config)
        self.tts = TextToSpeech()
        self.media_collector = MediaCollector(prompt_config=prompt_config)
        self.video_composer = VideoComposer()
        self.distributor = Distributor()

        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        
        log_file = os.path.join(Config.LOGS_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)

    def _cleanup_temp_files(self):
        """Clean up temporary audio and image files after video creation"""
        try:
            # Clean audio directory
            if os.path.exists(Config.AUDIO_DIR):
                for file in os.listdir(Config.AUDIO_DIR):
                    file_path = os.path.join(Config.AUDIO_DIR, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.logger.info("✓ Cleaned up audio files")

            # Clean images directory
            if os.path.exists(Config.IMAGES_DIR):
                for file in os.listdir(Config.IMAGES_DIR):
                    file_path = os.path.join(Config.IMAGES_DIR, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.logger.info("✓ Cleaned up image files")

            # Clean combined audio output file
            combined_audio = os.path.join(Config.OUTPUT_DIR, "combined_output.wav")
            if os.path.exists(combined_audio):
                os.remove(combined_audio)

        except Exception as e:
            self.logger.warning(f"⚠️  Error cleaning up temp files: {e}")

    def run(self, iterations=1, distribute_to="email", prompt_config=None):
        """
        Run the complete pipeline

        Args:
            iterations: Number of videos to create
            distribute_to: Platform to distribute to ("email", "instagram", etc.)
            prompt_config: PromptConfig object (overrides instance config if provided)

        Returns:
            list: Paths to created videos
        """
        # Validate config and create directories
        Config.validate()
        Config.create_directories()

        # Use provided config or instance config
        config = prompt_config or self.prompt_config

        config_name = config.get_name()
        self.logger.info(f"Starting pipeline: {iterations} iterations, config={config_name}")

        created_videos = []

        for i in range(iterations):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"ITERATION {i+1}/{iterations}")
            self.logger.info(f"{'='*60}\n")

            try:
                video_path = self._run_single_iteration(distribute_to, i+1, config)
                if video_path:
                    created_videos.append(video_path)

            except Exception as e:
                self.logger.error(f"Error in iteration {i+1}: {e}", exc_info=True)
                continue

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Pipeline complete: {len(created_videos)}/{iterations} videos created")
        self.logger.info(f"{'='*60}\n")

        return created_videos
    
    def _run_single_iteration(self, distribute_to, iteration_num, prompt_config=None):
        """Run a single iteration of the pipeline"""

        # Use provided config or instance config
        config = prompt_config or self.prompt_config

        # Step 1: Generate idea
        self.logger.info("Step 1: Generating content idea...")
        idea = self.idea_generator.generate_idea(prompt_config=config)

        if not idea:
            self.logger.error("Failed to generate idea")
            return None

        subject = idea.get("subject", "Unknown")
        concept = idea.get("concept", "Unknown")

        self.logger.info(f"Subject: {subject}")
        self.logger.info(f"Concept: {concept}")

        # Step 2: Write script
        self.logger.info("\nStep 2: Writing script...")
        script = self.story_writer.write_script(concept, prompt_config=config)

        if not script:
            self.logger.error("Failed to write script")
            return None

        self.logger.info(f"Script:\n{script}")
        
        # Step 3: Generate audio
        self.logger.info("\nStep 3: Generating audio...")
        durations, sentences = self.tts.generate_audio(script)

        if not durations:
            self.logger.error("Failed to generate audio")
            return None

        self.logger.info(f"Generated {len(durations)} audio segments")

        # Step 4: Collect media
        self.logger.info("\nStep 4: Collecting images...")
        image_paths = self.media_collector.collect_media(
            subject,
            count=len(durations),
            script=script,  # Pass script for AI-generated image prompts
            sentences=sentences  # Pass sentences for 1:1 image-sentence mapping
        )
        
        if not image_paths:
            self.logger.error("Failed to collect images")
            return None
        
        self.logger.info(f"Collected {len(image_paths)} images")
        
        # Step 5: Create video
        self.logger.info("\nStep 5: Creating video...")
        # Create a safe filename from the subject
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in subject)
        safe_name = safe_name[:50]  # Limit length
        output_name = f"{iteration_num:03d}_{safe_name}"
        
        video_path = self.video_composer.create_video(
            image_paths, 
            durations, 
            output_name
        )
        
        if not video_path:
            self.logger.error("Failed to create video")
            return None

        # Clean up temporary files after video creation
        self._cleanup_temp_files()

        # Step 6: Distribute
        self.logger.info(f"\nStep 6: Distributing to {distribute_to}...")
        
        metadata = {
            "subject": f"PosterBot Video: {concept}",
            "body": f"Video about: {subject}\n\nConcept: {concept}\n\nGenerated by PosterBot"
        }
        
        success = self.distributor.distribute(
            video_path, 
            platform=distribute_to,
            metadata=metadata
        )
        
        if success:
            self.logger.info("✓ Distribution successful")
        else:
            self.logger.warning("✗ Distribution failed")
        
        return video_path
