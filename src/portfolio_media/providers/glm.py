"""GLM provider for media generation.

Uses Zhipu AI's GLM models which have image generation capabilities.
"""

import os
from pathlib import Path
from typing import Optional


class GLMProvider:
    """GLM provider - uses Zhipu AI for image generation.

    Requires GLM_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.name = "glm"
        self.api_key = api_key or os.environ.get("GLM_API_KEY")

        try:
            import zhipuai
            self._available = True
        except ImportError:
            self._available = False

    @property
    def available(self) -> bool:
        """Check if provider is available."""
        return self._available and bool(self.api_key)

    async def generate_logo(
        self,
        prompt: str,
        output_path: Path
    ) -> bool:
        """Generate logo using GLM.

        Args:
            prompt: Logo description
            output_path: Where to save

        Returns:
            True if successful
        """
        if not self.available:
            raise RuntimeError("GLM provider not available")

        try:
            # GLM-4V has image generation capabilities
            result = await self._call_glm_image_api(prompt)

            if result:
                output_path.write_bytes(result)
                return True
            return False
        except Exception as e:
            print(f"GLM image generation failed: {e}")
            return False

    async def _call_glm_image_api(self, prompt: str) -> Optional[bytes]:
        """Call GLM image generation API."""
        # Placeholder for GLM image API integration
        return None

    def optimize_prompt_chinese(self, prompt: str) -> str:
        """Optimize prompt for GLM (works well with Chinese prompts).

        GLM is developed by Zhipu AI (Chinese company) and often
        performs better with Chinese prompts.
        """
        # Could translate or enhance prompt for GLM
        return prompt

    def check_installation(self) -> dict:
        """Check installation status."""
        return {
            "available": self.available,
            "api_key_set": bool(self.api_key),
            "install_command": "pip install zhipuai",
            "env_var": "GLM_API_KEY",
        }
