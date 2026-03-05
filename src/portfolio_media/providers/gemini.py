"""Gemini provider for media generation.

Uses Google's Gemini API with Imagen for image generation.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider:
    """Gemini provider - uses Google Imagen for image generation.

    Requires GEMINI_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.name = "gemini"
        self._api_key_param = api_key
        self.api_key = None
        self.client = None
        self._available = None

    def _ensure_initialized(self):
        """Lazy initialization - check env vars at actual use time."""
        if self._available is not None:
            return

        self.api_key = self._api_key_param or os.environ.get("GEMINI_API_KEY")

        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            # Use gemini-2.0-flash for general generation
            # Note: Image generation requires Imagen API, not gemini models
            self.client = genai.GenerativeModel("gemini-2.0-flash")
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
        size: str = "1024x1024"
    ) -> bool:
        """Generate logo using Gemini Imagen.

        Args:
            prompt: Logo description prompt
            output_path: Where to save the image
            size: Image size (256x256, 512x512, 1024x1024)

        Returns:
            True if successful
        """
        if not self.available:
            raise RuntimeError("Gemini provider not available. Install google-generativeai and set GEMINI_API_KEY.")

        try:
            # For image generation, we'd use the Imagen API
            # Currently Gemini 2.0 has limited image gen, so we might need
            # to use a separate Imagen API call
            response = await self._generate_image_async(prompt, size)

            if response and response.startswith("http"):
                # Download from URL
                return await self._download_image(response, output_path)
            elif response:
                # Base64 or binary data
                output_path.write_bytes(response.encode() if isinstance(response, str) else response)
                return True
            return False
        except Exception as e:
            print(f"Gemini image generation failed: {e}")
            return False

    async def _generate_image_async(self, prompt: str, size: str) -> Optional[str]:
        """Generate image asynchronously.

        Note: As of early 2025, Gemini's direct image generation
        may require the separate Imagen API. This is a placeholder
        for that integration.
        """
        # Placeholder for Imagen API integration
        # Would use: https://imagen.googleapis.com/v1/...
        return None

    async def _download_image(self, url: str, output_path: Path) -> bool:
        """Download image from URL."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        output_path.write_bytes(data)
                        return True
            return False
        except ImportError:
            # Fallback to urllib
            import urllib.request
            try:
                urllib.request.urlretrieve(url, str(output_path))
                return True
            except Exception:
                return False

    def generate_diagram_code(self, prompt: str) -> str:
        """Generate Mermaid/PlantUML code using Gemini.

        Gemini is excellent at code generation.
        """
        if not self.available:
            raise RuntimeError("Gemini provider not available")

        response = self.client.generate_content(
            f"Generate a Mermaid diagram code for: {prompt}\n\n"
            f"Output ONLY the Mermaid code block. No explanations."
        )
        return response.text

    def optimize_prompt_for_image_gen(self, description: str) -> str:
        """Use Gemini to optimize a prompt for image generation.

        Gemini is good at prompt engineering.
        """
        if not self.available:
            return description

        response = self.client.generate_content(
            f"Optimize this prompt for AI image generation (DALL-E, Midjourney, etc.):\n\n"
            f"{description}\n\n"
            f"Make it more detailed and specific. Output only the optimized prompt."
        )
        return response.text.strip()

    def check_installation(self) -> dict:
        """Check installation status and return info."""
        self._ensure_initialized()
        return {
            "available": self._available,
            "api_key_set": bool(self.api_key),
            "package_installed": GEMINI_AVAILABLE,
            "install_command": "pip install google-generativeai",
            "env_var": "GEMINI_API_KEY",
        }
