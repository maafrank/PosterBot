#!/usr/bin/env python3
"""
PosterBot - Automated Video Content Creation and Distribution

Usage:
    python main.py                      # Create 1 car video and email it
    python main.py --count 5            # Create 5 car videos
    python main.py --topic tech         # Create video about tech
    python main.py --no-distribute      # Create video but don't distribute
"""

import argparse
from core.pipeline import Pipeline

def main():
    parser = argparse.ArgumentParser(description="PosterBot - Automated Video Creation")
    
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
        help="Topic for content generation (default: cars)"
    )
    
    parser.add_argument(
        "--distribute-to",
        type=str,
        default="email",
        choices=["email", "none"],
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
    
    # Create and run pipeline
    print("\n" + "="*60)
    print("POSTERBOT - Video Content Creator")
    print("="*60 + "\n")
    
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
