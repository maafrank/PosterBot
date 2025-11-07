#!/usr/bin/env python3
"""
PosterBot - Automated Video Content Creation and Distribution

Usage:
    python main.py                              # Create 1 car video and email it (default)
    python main.py --config cars --count 5      # Create 5 car videos
    python main.py --config alien_stories       # Create alien encounter video
    python main.py --distribute-to tiktok       # Post to TikTok
    python main.py --no-distribute              # Create video but don't distribute

Legacy (still supported):
    python main.py --topic cars                 # Old style (use --config instead)
"""

import argparse
import sys
from core.pipeline import Pipeline
from core.prompt_config import PromptConfig

def main():
    parser = argparse.ArgumentParser(
        description="PosterBot - Automated Video Creation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Prompt configuration to use (e.g., 'cars', 'alien_stories'). Config files in prompt_configs/ directory."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of videos to create (default: 1)"
    )

    parser.add_argument(
        "--topic",
        type=str,
        default="cars",
        help="[LEGACY] Topic for content generation (default: cars). Use --config instead."
    )

    parser.add_argument(
        "--distribute-to",
        type=str,
        default="email",
        choices=["email", "tiktok", "instagram", "youtube", "none"],
        help="Platform to distribute to (default: email)"
    )

    parser.add_argument(
        "--no-distribute",
        action="store_true",
        help="Create videos but don't distribute them"
    )

    args = parser.parse_args()

    # Override distribution if --no-distribute is set
    distribute_to = "none" if args.no_distribute else args.distribute_to

    # Load prompt config if specified
    prompt_config = None
    if args.config:
        try:
            print(f"Loading config: {args.config}")
            prompt_config = PromptConfig.from_name(args.config)
            print(f"✓ Loaded config: {prompt_config.get_name()} - {prompt_config.get_description()}")
            print(f"  Image strategy: {prompt_config.get_image_strategy()}")
            print(f"  Shot templates: {prompt_config.get_shot_count()}")
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            print("\nAvailable configs in prompt_configs/:")
            import os
            if os.path.exists("prompt_configs"):
                for f in os.listdir("prompt_configs"):
                    if f.endswith(".yaml"):
                        print(f"  - {f.replace('.yaml', '')}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error loading config: {e}")
            sys.exit(1)

    # Create and run pipeline
    print("\n" + "="*60)
    print("POSTERBOT - Video Content Creator")
    print("="*60 + "\n")

    if prompt_config:
        pipeline = Pipeline(prompt_config=prompt_config)
        videos = pipeline.run(
            iterations=args.count,
            distribute_to=distribute_to,
            prompt_config=prompt_config
        )
    else:
        # Legacy mode
        print(f"⚠️  Running in legacy mode with topic='{args.topic}'")
        print("   Consider using --config instead (e.g., --config cars)\n")
        pipeline = Pipeline()
        videos = pipeline.run(
            iterations=args.count,
            topic=args.topic,
            distribute_to=distribute_to
        )

    print(f"\n✓ Created {len(videos)} video(s)")
    for i, video in enumerate(videos, 1):
        print(f"  {i}. {video}")

    print("\nDone!\n")

if __name__ == "__main__":
    main()
