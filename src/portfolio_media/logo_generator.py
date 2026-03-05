"""Logo generator using multiple LLM providers.

Supports logo generation via Gemini, OpenRouter, GLM, Perplexity.
"""

import asyncio
from pathlib import Path
from typing import Optional, Literal

from .prompt_builder import LogoPrompt, Provider, Style
from .providers.claude import ClaudeProvider
from .providers.gemini import GeminiProvider
from .providers.openrouter import OpenRouterProvider
from .providers.glm import GLMProvider
from .providers.perplexity import PerplexityProvider


class LogoGenerator:
    """Generate logos using multiple AI providers.

    Usage:
        generator = LogoGenerator()
        await generator.generate(
            package_name="debugRCA",
            description="Root cause analysis toolkit",
            style="minimalist",
            color="#FF6B6B",
            output_path=Path("assets/logo/logo.png")
        )
    """

    def __init__(self):
        self.providers = {
            Provider.CLAUDE: ClaudeProvider(),
            Provider.GEMINI: GeminiProvider(),
            Provider.OPENROUTER: OpenRouterProvider(),
            Provider.GLM: GLMProvider(),
            Provider.PERPLEXITY: PerplexityProvider(),
        }

    async def generate(
        self,
        package_name: str,
        description: str,
        output_path: Path,
        style: str | Style = Style.MINIMALIST,
        color: Optional[str] = None,
        provider: str | Provider = Provider.GEMINI,
        size: str = "1024x1024"
    ) -> dict:
        """Generate a logo for the package.

        Args:
            package_name: Name of the package
            description: Brief description of what it does
            output_path: Where to save the logo
            style: Visual style (minimalist, geometric, gradient, etc.)
            color: Primary color (hex code or color name)
            provider: Which AI provider to use
            size: Image size (256x256, 512x512, 1024x1024)

        Returns:
            Dict with success status and metadata
        """
        # Normalize inputs
        if isinstance(style, str):
            style = Style(style.lower())
        if isinstance(provider, str):
            provider = Provider(provider.lower())

        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build prompt
        logo_prompt = LogoPrompt(
            package_name=package_name,
            description=description,
            style=style,
            color=color
        )
        prompt_text = logo_prompt.build_for_provider(provider)

        # Get provider instance
        provider_instance = self.providers[provider]

        # Check availability
        if hasattr(provider_instance, 'available') and not provider_instance.available:
            return {
                "success": False,
                "error": f"Provider {provider.value} not available",
                "suggestion": provider_instance.check_installation()
            }

        # Generate logo
        try:
            if provider == Provider.CLAUDE:
                # Claude doesn't generate images directly
                # Use Claude to optimize prompt, then delegate
                optimized_prompt = await provider_instance.ask_claude_for_prompt(
                    package_name, description, style.value
                )
                return {
                    "success": False,
                    "note": "Claude optimized the prompt",
                    "optimized_prompt": optimized_prompt,
                    "suggestion": "Use another provider with this prompt"
                }

            success = await provider_instance.generate_logo(
                prompt=prompt_text,
                output_path=output_path,
                size=size
            )

            return {
                "success": success,
                "output_path": str(output_path) if success else None,
                "provider": provider.value,
                "prompt_used": prompt_text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": provider.value
            }

    async def generate_variations(
        self,
        package_name: str,
        description: str,
        output_dir: Path,
        count: int = 3,
        style: str | Style = Style.MINIMALIST,
        color: Optional[str] = None,
        provider: str | Provider = Provider.GEMINI
    ) -> list[dict]:
        """Generate multiple logo variations.

        Args:
            package_name: Name of the package
            description: Brief description
            output_dir: Directory to save logos
            count: Number of variations to generate
            style: Visual style
            color: Primary color
            provider: AI provider to use

        Returns:
            List of result dicts
        """
        results = []
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(count):
            output_path = output_dir / f"logo-variation-{i+1}.png"
            result = await self.generate(
                package_name=package_name,
                description=description,
                output_path=output_path,
                style=style,
                color=color,
                provider=provider
            )
            results.append(result)

        return results

    def check_providers(self) -> dict:
        """Check which providers are available."""
        status = {}
        for provider_name, provider_instance in self.providers.items():
            if hasattr(provider_instance, 'check_installation'):
                status[provider_name.value] = provider_instance.check_installation()
            elif hasattr(provider_instance, 'available'):
                status[provider_name.value] = {"available": provider_instance.available}
            else:
                status[provider_name.value] = {"available": True}
        return status


async def generate_logo_cli(
    package_name: str,
    description: str,
    output_path: str,
    style: str = "minimalist",
    color: Optional[str] = None,
    provider: str = "gemini"
) -> None:
    """CLI entry point for logo generation.

    Usage:
        python -m portfolio_media.logo_generator \\
            --package debugRCA \\
            --description "Root cause analysis toolkit" \\
            --output assets/logo/logo.png \\
            --style minimalist \\
            --color "#FF6B6B" \\
            --provider gemini
    """
    generator = LogoGenerator()
    result = await generator.generate(
        package_name=package_name,
        description=description,
        output_path=Path(output_path),
        style=style,
        color=color,
        provider=provider
    )

    if result["success"]:
        print(f"✓ Logo generated: {result['output_path']}")
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")
        if "suggestion" in result:
            print(f"  Suggestion: {result['suggestion']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate logos using AI")
    parser.add_argument("--package", required=True, help="Package name")
    parser.add_argument("--description", required=True, help="Package description")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--style", default="minimalist", help="Visual style")
    parser.add_argument("--color", help="Primary color (hex or name)")
    parser.add_argument("--provider", default="gemini", help="AI provider")

    args = parser.parse_args()

    asyncio.run(generate_logo_cli(
        package_name=args.package,
        description=args.description,
        output_path=args.output,
        style=args.style,
        color=args.color,
        provider=args.provider
    ))
