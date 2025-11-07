import os
import shutil
import random
import time
import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from duckduckgo_search import DDGS
from config import Config
from core.ai_prompt_generator import AIPromptGenerator

class MediaCollector:
    """Collects images/videos for content using various sources"""

    def __init__(self, target_width=None, target_height=None, image_source=None):
        self.target_width = target_width or Config.VIDEO_WIDTH
        self.target_height = target_height or Config.VIDEO_HEIGHT
        self.image_source = image_source or Config.IMAGE_SOURCE
        self.pexels_api_key = Config.PEXELS_API_KEY
        self.flux_model = None  # Lazy load FLUX model when needed
        self.flux_model_name = Config.FLUX_MODEL  # "schnell" or "dev"
        self.flux_quantize = Config.FLUX_QUANTIZE  # Quantization level (4-8 bits)
    
    def collect_media(self, query, count=None, media_type="image", output_dir=None):
        """
        Collect media files based on query
        
        Args:
            query: Search query (e.g., car name)
            count: Number of media files to collect
            media_type: Type of media ("image" or "video")
            output_dir: Directory to save files (default: Config.IMAGES_DIR)
            
        Returns:
            list: Paths to collected media files
        """
        if count is None:
            count = Config.IMAGE_COUNT
        
        if output_dir is None:
            output_dir = Config.IMAGES_DIR
        
        # Clean up and recreate directory
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        if media_type == "image":
            if self.image_source == "flux-schnell" or self.image_source == "flux-dev":
                return self._collect_images_flux(query, count, output_dir)
            elif self.image_source == "pexels":
                return self._collect_images_pexels(query, count, output_dir)
            elif self.image_source == "duckduckgo":
                return self._collect_images_duckduckgo(query, count, output_dir)
            else:
                # Auto-fallback: Try FLUX first, then Pexels, then DuckDuckGo
                print(f"⚠️  Unknown image source '{self.image_source}', trying FLUX first...")
                try:
                    return self._collect_images_flux(query, count, output_dir)
                except Exception as e:
                    print(f"⚠️  FLUX failed: {e}")
                    print("Falling back to Pexels...")
                    try:
                        return self._collect_images_pexels(query, count, output_dir)
                    except Exception as e2:
                        print(f"⚠️  Pexels failed: {e2}")
                        print("Falling back to DuckDuckGo...")
                        return self._collect_images_duckduckgo(query, count, output_dir)
        else:
            raise NotImplementedError("Video collection not yet implemented")
    
    def _collect_images_flux(self, query, count, output_dir):
        """Collect images using FLUX AI model (local generation)"""
        print(f"\n🎨 Generating {count} AI images for: {query}")
        print(f"Using FLUX model: {self.flux_model_name}")

        try:
            # Lazy load FLUX model
            if self.flux_model is None:
                print("Loading FLUX model (this may take a minute on first run)...")
                from mflux.generate import Flux1

                self.flux_model = Flux1.from_name(
                    model_name=self.flux_model_name,
                    quantize=self.flux_quantize
                )
                print("✓ FLUX model loaded successfully")

            # Generate diverse prompts for the car
            prompt_data = AIPromptGenerator.generate_prompts(query, count)

            image_paths = []

            # Determine inference steps based on model
            if self.flux_model_name == "schnell":
                num_steps = 4  # Schnell works best with 2-4 steps
            else:
                num_steps = 20  # Dev works best with 20-25 steps

            from mflux.generate import Config as MfluxConfig

            for i, prompt_info in enumerate(prompt_data):
                prompt_text = prompt_info["prompt"]
                shot_description = prompt_info["description"]

                print(f"\nGenerating image {i+1}/{count}: {shot_description}")
                print(f"Prompt: {prompt_text[:80]}...")

                try:
                    # Generate image
                    start_time = time.time()

                    result = self.flux_model.generate_image(
                        seed=random.randint(0, 1000000),  # Random seed for variety
                        prompt=prompt_text,
                        config=MfluxConfig(
                            num_inference_steps=num_steps,
                            height=self.target_height,
                            width=self.target_width
                        )
                    )

                    generation_time = time.time() - start_time

                    # FLUX returns a GeneratedImage object, get the PIL image
                    if hasattr(result, 'image'):
                        image = result.image
                    else:
                        image = result

                    # Save image
                    image_path = os.path.join(output_dir, f"image_{i}.jpg")

                    # Convert to RGB if needed and save
                    if hasattr(image, 'mode') and image.mode != 'RGB':
                        image = image.convert('RGB')

                    image.save(image_path, quality=95)
                    image_paths.append(image_path)

                    print(f"✓ Generated in {generation_time:.1f}s")

                except Exception as e:
                    print(f"✗ Failed to generate image {i+1}: {e}")
                    # Continue with other images even if one fails
                    continue

            if not image_paths:
                raise RuntimeError("Failed to generate any images with FLUX")

            print(f"\n✓ Successfully generated {len(image_paths)}/{count} images")
            return image_paths

        except ImportError:
            raise RuntimeError(
                "mflux is not installed. Install it with: pip install mflux\n"
                "Note: mflux requires Apple Silicon (M1/M2/M3/M4) Mac"
            )
        except Exception as e:
            raise RuntimeError(f"FLUX image generation failed: {e}")

    def _collect_images_pexels(self, query, count, output_dir):
        """Collect images using Pexels API"""
        # For Pexels, we want to be more specific - always add "car" to the query
        simple_query = self._simplify_query(query)

        # Make sure "car" or "automobile" is in the query
        if "car" not in simple_query.lower() and "automobile" not in simple_query.lower():
            simple_query = f"{simple_query} car"

        print(f"Using Pexels to search for: {simple_query}")

        if not self.pexels_api_key:
            print("⚠️  No Pexels API key found, falling back to DuckDuckGo")
            return self._collect_images_duckduckgo(query, count, output_dir)

        headers = {
            "Authorization": self.pexels_api_key
        }

        image_paths = []

        try:
            # Pexels search endpoint
            url = "https://api.pexels.com/v1/search"
            params = {
                "query": simple_query,
                "per_page": min(count * 3, 80),  # Get extra in case some aren't relevant
                "orientation": "landscape"  # Cars look better in landscape
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            photos = data.get("photos", [])

            print(f"Found {len(photos)} photos on Pexels")

            for photo in photos:
                if len(image_paths) >= count:
                    break

                try:
                    # Use the 'large' size for good quality
                    img_url = photo["src"]["large"]
                    print(f"Downloading: {img_url[:60]}...")

                    # Download image
                    img_response = requests.get(img_url, timeout=10)
                    img_response.raise_for_status()

                    # Process image
                    image = Image.open(BytesIO(img_response.content)).convert("RGB")
                    image = self._resize_and_crop(image, self.target_width, self.target_height)

                    # Convert to OpenCV format and save
                    arr = np.array(image)
                    bgr_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

                    image_path = os.path.join(output_dir, f"image_{len(image_paths)}.jpg")
                    cv2.imwrite(image_path, bgr_img)
                    image_paths.append(image_path)

                    print(f"✓ Saved image {len(image_paths)}/{count}")

                except Exception as e:
                    print(f"✗ Failed to download image: {e}")
                    continue

        except Exception as e:
            print(f"✗ Pexels API error: {e}")
            if not image_paths:
                raise RuntimeError(f"Failed to collect images from Pexels: {e}")

        if not image_paths:
            raise RuntimeError("No valid images were downloaded from Pexels")

        print(f"\n✓ Collected {len(image_paths)} images from Pexels")
        return image_paths

    def _collect_images_duckduckgo(self, query, count, output_dir):
        """Collect images using DuckDuckGo search"""
        # Simplify query - remove special characters and year ranges that cause issues
        simple_query = self._simplify_query(query)

        search_templates = [
            "{query}", "{query} car", "{query} photo",
            "{query} front", "{query} side", "{query} interior"
        ]
        random.shuffle(search_templates)

        image_paths = []
        retry_count = 0
        max_retries = 3

        with DDGS() as ddgs:
            for template in search_templates:
                if len(image_paths) >= count:
                    break

                search_query = template.format(query=simple_query)
                print(f"Searching for: {search_query}")

                try:
                    # Try to get more results per query to reduce number of queries
                    results = ddgs.images(search_query, max_results=15)

                    for result in results:
                        if len(image_paths) >= count:
                            break

                        try:
                            img_url = result["image"]
                            print(f"Downloading: {img_url[:60]}...")

                            # Download image
                            headers = {"User-Agent": "Mozilla/5.0"}
                            response = requests.get(img_url, headers=headers, timeout=5)

                            # Process image
                            image = Image.open(BytesIO(response.content)).convert("RGB")
                            image = self._resize_and_crop(image, self.target_width, self.target_height)

                            # Convert to OpenCV format and save
                            arr = np.array(image)
                            bgr_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

                            image_path = os.path.join(output_dir, f"image_{len(image_paths)}.jpg")
                            cv2.imwrite(image_path, bgr_img)
                            image_paths.append(image_path)

                            print(f"✓ Saved image {len(image_paths)}/{count}")

                        except Exception as e:
                            print(f"✗ Failed: {e}")
                            continue

                    # Longer delay between searches to avoid rate limits
                    time.sleep(3)
                    retry_count = 0  # Reset retry count on success

                except Exception as e:
                    print(f"Search error: {e}")
                    retry_count += 1

                    if retry_count >= max_retries:
                        print(f"Max retries ({max_retries}) reached, stopping image collection")
                        break

                    # Exponential backoff
                    wait_time = 5 * (2 ** retry_count)
                    print(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

        if not image_paths:
            raise RuntimeError("No valid images were downloaded. DuckDuckGo may be rate-limiting. Try again later.")

        print(f"\nCollected {len(image_paths)} images")
        return image_paths

    def _simplify_query(self, query):
        """Simplify search query while keeping brand/model info"""
        import re

        # Remove content in parentheses (like generation codes)
        simplified = re.sub(r'\([^)]*\)', '', query)

        # Remove special unicode characters like em-dash
        simplified = simplified.replace('–', ' ').replace('—', ' ')

        # Keep year range but make it cleaner (e.g., "1994-2001" becomes "1994 2001")
        # This helps Pexels understand we want that era
        simplified = re.sub(r'(\d{4})[-–](\d{4})', r'\1 \2', simplified)

        # Clean up extra spaces
        simplified = ' '.join(simplified.split())

        return simplified.strip()
    
    def _resize_and_crop(self, image, target_width, target_height):
        """Resize and crop image to target dimensions"""
        # Calculate aspect ratios
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
        # Resize image
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(img_ratio * new_height)
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)
        
        image = image.resize((new_width, new_height), resample=Image.LANCZOS)
        
        # Crop the center
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return image.crop((left, top, right, bottom))
