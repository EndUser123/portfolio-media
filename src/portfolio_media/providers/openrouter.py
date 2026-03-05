"""OpenRouter provider for media generation.

Uses OpenRouter API which provides access to multiple image generation models
including Flux, SDXL, and others.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterProvider:
    """OpenRouter provider - multi-model access via OpenRouter API.

    Requires OPENROUTER_API_KEY environment variable.

    Image models available:
    - flux-pro: High quality image generation
    - flux-pro-1.1-deep-depth: Depth-aware generation
    - sdxl: Stable Diffusion XL
    - Various other models
    """

    def __init__(self, api_key: Optional[str] = None):
        self.name = "openrouter"
        self._api_key_param = api_key  # Store passed key separately
        self.api_key = None  # Will be set lazily
        self.client = None
        self._available = None  # Will be determined lazily

    def _ensure_initialized(self):
        """Lazy initialization - check env vars at actual use time."""
        if self._available is not None:
            return  # Already initialized

        # Get API key from parameter or environment
        self.api_key = self._api_key_param or os.environ.get("OPENROUTER_API_KEY")

        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
            self._available = True
        else:
            self._available = False

    @property
    def available(self) -> bool:
        """Check if provider is available."""
        self._ensure_initialized()
        return self._available

    async def generate_logo(
        self,
        prompt: str,
        output_path: Path,
        model: str = "google/gemini-2.5-flash-image",
        size: str = "1024x1024"
    ) -> bool:
        """Generate logo using OpenRouter image model.

        Args:
            prompt: Logo description prompt
            output_path: Where to save the image
            model: Model to use (flux-pro, sdxl, etc.)
            size: Image size

        Returns:
            True if successful
        """
        if not self.available:
            raise RuntimeError("OpenRouter provider not available. Install openai and set OPENROUTER_API_KEY.")

        try:
            # For image generation, OpenRouter uses a different endpoint
            response = await self._generate_image_async(prompt, model, size)

            if response:
                output_path.write_bytes(response)
                return True
            return False
        except Exception as e:
            print(f"OpenRouter image generation failed: {e}")
            return False

    async def _generate_image_async(
        self,
        prompt: str,
        model: str,
        size: str
    ) -> Optional[bytes]:
        """Generate image via OpenRouter Chat Completions API.

        OpenRouter's image models (like Gemini 2.5 Flash Image) return images
        in the chat completion response's images array.
        """
        try:
            import requests
            import base64
            import json

            # Use chat completions endpoint with image model
            url = "https://openrouter.ai/api/v1/chat/completions"

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/csf/portfolio-media",
                "X-Title": "portfolio-media"
            }

            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            if resp.status_code != 200:
                error_text = resp.text[:500] if resp.text else "No error details"
                print(f"OpenRouter API error: {resp.status_code} - {error_text}")
                return None

            data = resp.json()

            # Check for images in the response
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                images = message.get("images", [])

                if images and len(images) > 0:
                    image_url = images[0].get("image_url", {})
                    url_data = image_url.get("url", "")

                    if url_data.startswith("data:image"):
                        # Base64 encoded image data URL
                        # Format: data:image/png;base64,iVBORw0KGgo...
                        header, encoded = url_data.split(",", 1)
                        return base64.b64decode(encoded)

            return None

        except Exception as e:
            print(f"OpenRouter image generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _download_from_url(self, url: str) -> Optional[bytes]:
        """Download image from URL synchronously."""
        try:
            import requests
            resp = requests.get(url, timeout=30)
            if resp.status == 200:
                return resp.content
            return None
        except Exception as e:
            print(f"Failed to download image: {e}")
            return None

    def optimize_prompt(self, prompt: str, model: str = "flux-pro") -> str:
        """Optimize prompt for specific model.

        Different models prefer different prompt styles.
        """
        model_styles = {
            "flux-pro": "natural language, descriptive",
            "sdxl": "comma-separated keywords, style modifiers",
            "flux-pro-1.1-deep-depth": "detailed scene description",
        }

        style = model_styles.get(model, "natural language")

        if style == "comma-separated keywords":
            # Convert to SDXL style
            words = prompt.split()
            return ", ".join(words[:50])  # SDXL prefers shorter prompts
        else:
            return prompt

    def check_installation(self) -> dict:
        """Check installation status."""
        self._ensure_initialized()
        return {
            "available": self._available,
            "api_key_set": bool(self.api_key),
            "package_installed": OPENAI_AVAILABLE,
            "install_command": "pip install openai",
            "env_var": "OPENROUTER_API_KEY",
            "recommended_models": [
                "google/gemini-2.5-flash-image",
                "google/gemini-3-pro-image-preview",
            ]
        }

    def list_image_models(self) -> list[str]:
        """List available image generation models."""
        return [
            "flux-pro",
            "flux-pro-1.1-deep-depth",
            "flux-realism",
            "sdxl",
            "sdxl-flash",
        ]
