#!/usr/bin/env python3
"""
Test script for FLUX AI image generation
Run this to verify FLUX is working before running the full pipeline
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.media_collector import MediaCollector
from core.ai_prompt_generator import AIPromptGenerator
from config import Config

def test_prompt_generator():
    """Test the AI prompt generator"""
    print("=" * 60)
    print("Testing AI Prompt Generator")
    print("=" * 60)

    test_car = "1994-2001 Acura Integra Type R (DC2)"
    prompts = AIPromptGenerator.generate_prompts(test_car, count=3)

    print(f"\nCar: {test_car}")
    print(f"Generated {len(prompts)} prompts:\n")

    for i, prompt_info in enumerate(prompts, 1):
        print(f"{i}. {prompt_info['description']}")
        print(f"   {prompt_info['prompt'][:100]}...\n")

    print("✓ Prompt generator working correctly\n")

def test_flux_generation():
    """Test FLUX image generation"""
    print("=" * 60)
    print("Testing FLUX Image Generation")
    print("=" * 60)

    # Create directories
    Config.create_directories()

    # Configure for FLUX
    print(f"\nCurrent IMAGE_SOURCE: {Config.IMAGE_SOURCE}")
    print(f"FLUX_MODEL: {Config.FLUX_MODEL}")
    print(f"FLUX_QUANTIZE: {Config.FLUX_QUANTIZE}")
    print(f"Target size: {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}\n")

    # Test with a simple car
    test_car = "2020 Toyota Supra"

    print(f"Testing with: {test_car}")
    print("Generating 2 test images (this may take 30-60 seconds)...\n")

    try:
        collector = MediaCollector(image_source="flux-schnell")
        image_paths = collector.collect_media(test_car, count=2)

        print("\n" + "=" * 60)
        print("✓ SUCCESS! FLUX is working correctly")
        print("=" * 60)
        print(f"\nGenerated {len(image_paths)} images:")
        for path in image_paths:
            print(f"  - {path}")

        print(f"\nImages saved to: {Config.IMAGES_DIR}")
        print("\nYou can now run: python3 main.py --no-distribute")

        return True

    except ImportError as e:
        print("\n" + "=" * 60)
        print("✗ ERROR: mflux not installed")
        print("=" * 60)
        print("\nPlease install mflux:")
        print("  pip install mflux")
        print("\nNote: mflux requires Apple Silicon (M1/M2/M3/M4) Mac")
        return False

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR: FLUX generation failed")
        print("=" * 60)
        print(f"\nError details: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure you have 16GB+ RAM")
        print("  2. Try lowering FLUX_QUANTIZE in .env (e.g., FLUX_QUANTIZE=4)")
        print("  3. Check that you have ~15GB free disk space")
        print("  4. See FLUX_SETUP.md for more help")
        return False

def main():
    """Run all tests"""
    print("\n🧪 PosterBot FLUX Test Suite\n")

    # Test 1: Prompt Generator
    try:
        test_prompt_generator()
    except Exception as e:
        print(f"✗ Prompt generator test failed: {e}\n")
        return

    # Test 2: FLUX Generation
    try:
        success = test_flux_generation()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
