"""Claude Code provider for media generation.

Uses Claude Code's built-in vision capabilities for diagram generation
and prompt construction for other media types.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class ClaudeProvider:
    """Claude Code provider - generates Mermaid/PlantUML diagrams.

    Claude doesn't generate images directly but excels at:
    - Mermaid diagram code
    - PlantUML diagram code
    - Architecture descriptions
    """

    def __init__(self):
        self.name = "claude"

    async def generate_diagram_code(
        self,
        prompt: str,
        diagram_type: str = "mermaid"
    ) -> str:
        """Generate diagram code using Claude.

        Args:
            prompt: Description of the diagram to create
            diagram_type: mermaid, plantuml, dot, etc.

        Returns:
            Diagram code as string
        """
        # This would be called via /llm-codex or direct Claude invocation
        # For now, return the prompt for manual execution
        return f"""# Run this with Claude:
/llm-codex "{prompt} --format {diagram_type}"
"""

    def render_mermaid(
        self,
        mermaid_code: str,
        output_path: Path,
        background: str = "transparent"
    ) -> bool:
        """Render Mermaid code to SVG using mermaid-cli.

        Args:
            mermaid_code: Mermaid diagram code
            output_path: Output file path
            background: Background color (transparent, white, etc.)

        Returns:
            True if successful
        """
        # Check if mmdc (mermaid-cli) is available
        try:
            result = subprocess.run(
                ["mmdc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            mmdc_available = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            mmdc_available = False

        if not mmdc_available:
            # Fallback: write mermaid code for manual rendering
            output_path.with_suffix(".mmd").write_text(mermaid_code)
            return False

        # Write temp mermaid file
        temp_mmd = output_path.with_suffix(".mmd")
        temp_mmd.write_text(mermaid_code)

        # Render with mmdc
        try:
            subprocess.run([
                "mmdc",
                "-i", str(temp_mmd),
                "-o", str(output_path),
                "-b", background,
                "-s", "2"  # scale
            ], check=True, capture_output=True, timeout=30)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return False

    def generate_logo_prompt(self, package_name: str, description: str, style: str) -> str:
        """Generate optimized logo prompt for another provider.

        Claude is good at constructing prompts for image generators.
        """
        return f"""Create a logo for {package_name} - {description}.

Style: {style}
Requirements:
- Simple, iconic design
- No text
- Scalable
- Professional

Use this prompt with your image generation provider."""

    async def ask_claude_for_prompt(
        self,
        package_name: str,
        description: str,
        style: str
    ) -> str:
        """Ask Claude to generate an optimized prompt for image generation.

        This leverages Claude's strength in prompt engineering.
        """
        # Would integrate with /llm-codex or direct Claude API
        prompt = f"""Generate an optimized image generation prompt for a logo.

Package: {package_name}
Description: {description}
Style: {style}

Generate a detailed prompt that will work well with:
- DALL-E 3
- Midjourney
- Stable Diffusion
- Google Imagen

Output only the prompt text, no explanations."""
        return prompt
