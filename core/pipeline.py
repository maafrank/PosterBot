import os
import logging
from datetime import datetime
from config import Config
from core.content_generator import ContentIdeaGenerator
from core.story_writer import StoryWriter
from core.text_to_speech import TextToSpeech
from core.media_collector import MediaCollector
from core.video_composer import VideoComposer
from core.distributor import Distributor

class Pipeline:
    """Orchestrates the entire video creation and distribution workflow"""
    
    def __init__(self):
        # Initialize all components
        self.idea_generator = ContentIdeaGenerator()
        self.story_writer = StoryWriter()
        self.tts = TextToSpeech()
        self.media_collector = MediaCollector()
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
    
    def run(self, iterations=1, topic="cars", distribute_to="email"):
        """
        Run the complete pipeline
        
        Args:
            iterations: Number of videos to create
            topic: Topic for content generation
            distribute_to: Platform to distribute to ("email", "instagram", etc.)
            
        Returns:
            list: Paths to created videos
        """
        # Validate config and create directories
        Config.validate()
        Config.create_directories()
        
        self.logger.info(f"Starting pipeline: {iterations} iterations, topic={topic}")
        
        created_videos = []
        
        for i in range(iterations):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"ITERATION {i+1}/{iterations}")
            self.logger.info(f"{'='*60}\n")
            
            try:
                video_path = self._run_single_iteration(topic, distribute_to, i+1)
                if video_path:
                    created_videos.append(video_path)
                    
            except Exception as e:
                self.logger.error(f"Error in iteration {i+1}: {e}", exc_info=True)
                continue
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Pipeline complete: {len(created_videos)}/{iterations} videos created")
        self.logger.info(f"{'='*60}\n")
        
        return created_videos
    
    def _run_single_iteration(self, topic, distribute_to, iteration_num):
        """Run a single iteration of the pipeline"""
        
        # Step 1: Generate idea
        self.logger.info("Step 1: Generating content idea...")
        idea = self.idea_generator.generate_idea(topic=topic)
        
        if not idea:
            self.logger.error("Failed to generate idea")
            return None
        
        subject = idea.get("subject", "Unknown")
        concept = idea.get("concept", "Unknown")
        
        self.logger.info(f"Subject: {subject}")
        self.logger.info(f"Concept: {concept}")
        
        # Step 2: Write script
        self.logger.info("\nStep 2: Writing script...")
        script = self.story_writer.write_script(concept, topic=topic)
        
        if not script:
            self.logger.error("Failed to write script")
            return None
        
        self.logger.info(f"Script: {script[:100]}...")
        
        # Step 3: Generate audio
        self.logger.info("\nStep 3: Generating audio...")
        durations = self.tts.generate_audio(script)
        
        if not durations:
            self.logger.error("Failed to generate audio")
            return None
        
        self.logger.info(f"Generated {len(durations)} audio segments")
        
        # Step 4: Collect media
        self.logger.info("\nStep 4: Collecting images...")
        image_paths = self.media_collector.collect_media(subject, count=len(durations))
        
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
