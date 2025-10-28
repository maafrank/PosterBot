import os
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from config import Config

class VideoComposer:
    """Composes video from images and audio"""
    
    def __init__(self, fps=None):
        self.fps = fps or Config.VIDEO_FPS
    
    def create_video(self, image_paths, durations, output_name, audio_path=None):
        """
        Create a video from images and audio
        
        Args:
            image_paths: List of paths to image files
            durations: List of durations (in seconds) for each image
            output_name: Name for the output video file
            audio_path: Path to audio file (default: combined_output.wav in output dir)
            
        Returns:
            str: Path to the created video file
        """
        if audio_path is None:
            audio_path = os.path.join(Config.OUTPUT_DIR, "combined_output.wav")
        
        # Ensure we have matching number of images and durations
        images = image_paths[:len(durations)]
        
        if len(images) != len(durations):
            print(f"Warning: {len(images)} images but {len(durations)} durations")
            # Adjust to use the minimum
            min_len = min(len(images), len(durations))
            images = images[:min_len]
            durations = durations[:min_len]
        
        print(f"Creating video with {len(images)} images...")
        
        # Create video clips from images
        video_clips = []
        for img_path, duration in zip(images, durations):
            clip = ImageClip(img_path).with_duration(duration)
            video_clips.append(clip)
        
        # Position clips sequentially
        current_start = 0
        positioned_clips = []
        for clip, duration in zip(video_clips, durations):
            positioned_clips.append(clip.with_start(current_start))
            current_start += duration
        
        # Create composite video
        video = CompositeVideoClip(positioned_clips)
        
        # Attach audio
        if os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            video = video.with_audio(audio)
        else:
            print(f"Warning: Audio file not found at {audio_path}")
        
        # Generate output path
        output_path = os.path.join(Config.VIDEOS_DIR, f"{output_name}.mp4")
        
        # Write video file
        print(f"Writing video to: {output_path}")
        video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=self.fps,
            ffmpeg_params=["-movflags", "+faststart"]
        )
        
        print(f"✓ Video created: {output_path}")
        return output_path
