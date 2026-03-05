"""CLI entry point for portfolio-media."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Load environment variables from .env files
try:
    from dotenv import load_dotenv
    # Try to load .env from current directory up to root
    cwd = Path.cwd()
    load_dotenv(cwd / ".env")
    load_dotenv(cwd.parent / ".env")
    load_dotenv(cwd.parent.parent / ".env")
    load_dotenv(cwd.parent.parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# Map PowerShell-style env var names to standard names
# This allows the CLI to work with both PowerShell profile vars and .env files
_ENV_VAR_MAP = {
    "GeminiKey": "GEMINI_API_KEY",
    "OpenRouterKey": "OPENROUTER_API_KEY",
    "PerplexityKey": "PERPLEXITY_API_KEY",
    "MistralKey": "MISTRAL_API_KEY",
    "GroqKey": "GROQ_API_KEY",
    "GROQ_API_KEY": "GROQ_API_KEY",
}


def _get_env_var(name: str) -> Optional[str]:
    """Get environment variable with PowerShell var name fallback."""
    # First try standard name
    value = os.environ.get(name)
    if value:
        return value

    # Try PowerShell-style names
    for pwsh_var, standard_var in _ENV_VAR_MAP.items():
        if standard_var == name:
            pwsh_value = os.environ.get(pwsh_var)
            if pwsh_value:
                # Set the standard name so subsequent calls work
                os.environ[name] = pwsh_value
                return pwsh_value

    return None


def _ensure_env_vars():
    """Ensure all API keys are available under standard names."""
    _get_env_var("GEMINI_API_KEY")
    _get_env_var("OPENROUTER_API_KEY")
    _get_env_var("PERPLEXITY_API_KEY")
    _get_env_var("MISTRAL_API_KEY")
    _get_env_var("GROQ_API_KEY")


# Call at import time to normalize env vars
_ensure_env_vars()

from .logo_generator import LogoGenerator
from .diagram_generator import DiagramGenerator
from .screenshot_capture import ScreenshotCapture
from .video_generator import VideoGenerator
from .assessment import AssetAssessment, assess_package


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="portfolio-media - AI visual asset generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a logo
  portfolio-media logo --package myapp --description "My app" --output logo.png

  # Generate a diagram
  portfolio-media diagram --package myapp --components "A,B,C" --output arch.svg

  # Capture screenshot
  portfolio-media screenshot --url http://localhost:8000 --output screen.png

  # Generate demo video
  portfolio-media video --package myapp --description "My app" --output demo.mp4

  # Check provider availability
  portfolio-media check
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Logo command
    logo_parser = subparsers.add_parser("logo", help="Generate a logo")
    logo_parser.add_argument("--package", required=True, help="Package name")
    logo_parser.add_argument("--description", required=True, help="Package description")
    logo_parser.add_argument("--output", required=True, help="Output path")
    logo_parser.add_argument("--style", default="minimalist", help="Visual style")
    logo_parser.add_argument("--color", help="Primary color (hex or name)")
    logo_parser.add_argument("--provider", default="gemini", help="AI provider")
    logo_parser.add_argument("--variations", type=int, help="Generate N variations")

    # Diagram command
    diagram_parser = subparsers.add_parser("diagram", help="Generate architecture diagram")
    diagram_parser.add_argument("--package", required=True, help="Package name")
    diagram_parser.add_argument("--components", required=True, help="Comma-separated components")
    diagram_parser.add_argument("--output", required=True, help="Output path")
    diagram_parser.add_argument("--title", default="Architecture", help="Diagram title")
    diagram_parser.add_argument("--flow", default="TD", help="Flow direction (TD, LR, BT, RL)")
    diagram_parser.add_argument("--code-only", action="store_true", help="Generate code only (no render)")

    # Screenshot command
    screenshot_parser = subparsers.add_parser("screenshot", help="Capture screenshot")
    screenshot_parser.add_argument("--url", required=True, help="URL to capture")
    screenshot_parser.add_argument("--output", required=True, help="Output path")
    screenshot_parser.add_argument("--width", type=int, default=1280, help="Viewport width")
    screenshot_parser.add_argument("--height", type=int, default=720, help="Viewport height")
    screenshot_parser.add_argument("--full-page", action="store_true", help="Capture full page")
    screenshot_parser.add_argument("--wait-for", help="CSS selector to wait for")
    screenshot_parser.add_argument("--selector", help="CSS selector for element screenshot")

    # Video command
    video_parser = subparsers.add_parser("video", help="Generate demo video")
    video_parser.add_argument("--package", required=True, help="Package name")
    video_parser.add_argument("--description", required=True, help="Package description")
    video_parser.add_argument("--output", required=True, help="Output path")
    video_parser.add_argument("--duration", type=int, default=4, help="Video duration in seconds")
    video_parser.add_argument("--backend", default="auto", help="Video backend (auto, cogvideox, opensora, openrouter)")
    video_parser.add_argument("--prompt", help="Custom video prompt (auto-generated if not provided)")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check provider availability")

    # Assess command (Stage 1: Assessment)
    assess_parser = subparsers.add_parser("assess", help="Assess package assets and identify gaps")
    assess_parser.add_argument("--path", default=".", help="Path to package (default: current directory)")
    assess_parser.add_argument("--output", help="Save report to JSON file")
    assess_parser.add_argument("--quiet", action="store_true", help="Only print score, no full report")

    # Generate command (Stage 2: Auto-generate based on assessment)
    generate_parser = subparsers.add_parser("generate", help="Auto-generate assets based on assessment")
    generate_parser.add_argument("--path", default=".", help="Path to package")
    generate_parser.add_argument("--report", help="Path to assessment report (default: auto-discover)")
    generate_parser.add_argument("--package", help="Package name (overrides detection)")
    generate_parser.add_argument("--description", help="Package description for logo generation")
    generate_parser.add_argument("--components", help="Comma-separated components for diagram")
    generate_parser.add_argument("--url", help="URL for screenshot capture")
    generate_parser.add_argument("--provider", default="gemini", help="AI provider for generation")
    generate_parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "logo":
        return run_logo_command(args)
    elif args.command == "diagram":
        return run_diagram_command(args)
    elif args.command == "screenshot":
        return run_screenshot_command(args)
    elif args.command == "video":
        return run_video_command(args)
    elif args.command == "check":
        return run_check_command()
    elif args.command == "assess":
        return run_assess_command(args)
    elif args.command == "generate":
        return run_generate_command(args)

    return 0


def run_logo_command(args):
    """Run logo generation command."""
    generator = LogoGenerator()

    async def generate():
        if args.variations:
            output_dir = Path(args.output).parent
            results = await generator.generate_variations(
                package_name=args.package,
                description=args.description,
                output_dir=output_dir,
                count=args.variations,
                style=args.style,
                color=args.color,
                provider=args.provider
            )

            success_count = sum(1 for r in results if r.get("success"))
            print(f"Generated {success_count}/{args.variations} logo variations")

            return all(r.get("success") for r in results)
        else:
            result = await generator.generate(
                package_name=args.package,
                description=args.description,
                output_path=Path(args.output),
                style=args.style,
                color=args.color,
                provider=args.provider
            )

            if result["success"]:
                print(f"✓ Logo generated: {result['output_path']}")
                return 0
            else:
                print(f"✗ Failed: {result.get('error', 'Unknown error')}")
                if "suggestion" in result:
                    print(f"  Suggestion: {result['suggestion']}")
                return 1

    return asyncio.run(generate())


def run_diagram_command(args):
    """Run diagram generation command."""
    generator = DiagramGenerator()

    components = [c.strip() for c in args.components.split(",")]

    async def generate():
        renderer = "none" if args.code_only else "auto"

        result = await generator.generate(
            package_name=args.package,
            components=components,
            output_path=Path(args.output),
            title=args.title,
            flow_direction=args.flow,
            renderer=renderer
        )

        if result["success"]:
            print(f"✓ Diagram generated: {result.get('svg_path', result['mmd_path'])}")
            return 0
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            return 1

    return asyncio.run(generate())


def run_screenshot_command(args):
    """Run screenshot capture command."""
    capture = ScreenshotCapture()

    result = capture.capture_url(
        url=args.url,
        output_path=Path(args.output),
        width=args.width,
        height=args.height,
        wait_for=args.wait_for,
        full_page=args.full_page,
        selector=args.selector
    )

    if result["success"]:
        print(f"✓ Screenshot saved: {result['output_path']}")
        return 0
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")
        return 1


def run_video_command(args):
    """Run video generation command."""
    generator = VideoGenerator()

    async def generate():
        # Show detected GPU info
        status = generator.check_installation()
        if status["gpu"]["available"]:
            print(f"GPU detected: {status['gpu']['name']} ({status['gpu']['vram_gb']:.1f} GB VRAM)")
            print(f"Recommended backend: {status['recommended']}")
        else:
            print("No GPU detected - using OpenRouter backend")

        result = await generator.generate(
            package_name=args.package,
            description=args.description,
            output_path=Path(args.output),
            duration=args.duration,
            backend=args.backend,
            prompt=args.prompt
        )

        if result["success"]:
            print(f"✓ Video generated: {result['output_path']}")
            if "frames" in result:
                print(f"  Frames: {result['frames']}")
            if "backend" in result:
                print(f"  Backend: {result['backend']}")
            return 0
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            if "suggestion" in result:
                print(f"  Suggestion: {result['suggestion']}")
            return 1

    return asyncio.run(generate())


def run_check_command():
    """Check provider availability."""
    generator = LogoGenerator()
    status = generator.check_providers()

    print("Provider Status:")
    print("-" * 50)

    for provider, info in status.items():
        available = info.get("available", False)
        status_icon = "✓" if available else "✗"
        print(f"{status_icon} {provider.upper():12} {'Available' if available else 'Not Available'}")

        if not available and "install_command" in info:
            print(f"  Install: {info['install_command']}")
        if "env_var" in info:
            print(f"  Env var: {info['env_var']}")

    print("-" * 50)

    # Check Playwright
    capture = ScreenshotCapture()
    playwright_status = capture.check_installation()
    print(f"{'✓' if playwright_status.get('installed') else '✗'} PLAYWRIGHT   {'Installed' if playwright_status.get('installed') else 'Not Installed'}")

    if not playwright_status.get("installed"):
        print(f"  Install: {playwright_status.get('install_command')}")

    # Check Video Generation
    print("\nVideo Generation Status:")
    print("-" * 50)

    video_gen = VideoGenerator()
    video_status = video_gen.check_installation()

    gpu = video_status["gpu"]
    if gpu["available"]:
        print(f"{'✓'} GPU          {gpu['name']} ({gpu['vram_gb']:.1f} GB VRAM)")
        print(f"  Recommended: {video_status['recommended']}")
    else:
        print(f"{'✗'} GPU          Not available")

    for backend in ["cogvideox", "opensora", "openrouter"]:
        info = video_status[backend]
        available = info.get("available") or info.get("installed") or info.get("model_installed", False)
        status_icon = "✓" if available else "✗"
        name = backend.upper()
        print(f"{status_icon} {name:12} {'Available' if available else 'Not Available'}")

        if not available:
            if "install_command" in info:
                print(f"  Install: {info['install_command']}")
            if "env_var" in info:
                print(f"  Env var: {info['env_var']}")

    print("-" * 50)

    return 0


def run_assess_command(args):
    """Run asset assessment command (Stage 1)."""
    assessor = AssetAssessment(Path(args.path))
    results = assessor.assess()

    # Save report if requested
    if args.output:
        assessor.save_report(results, Path(args.output))
        print(f"Report saved to: {args.output}")

    # Print report (unless quiet mode)
    if not args.quiet:
        assessor.print_report(results)
    else:
        # Quiet mode: just print score
        print(f"{results['quality_score']}")
        # Also print missing count as exit code logic
        missing = len(results["assets_missing"])
        if missing > 0:
            print(f"Missing: {missing} required asset(s)", file=sys.stderr)

    # Return exit code based on whether required assets are missing
    return 1 if results["assets_missing"] else 0


def run_generate_command(args):
    """Run auto-generate command (Stage 2)."""
    package_path = Path(args.path)

    # Load or create assessment report
    if args.report:
        assessor = AssetAssessment(package_path)
        assessment = assessor.load_report(Path(args.report))
    else:
        assessor = AssetAssessment(package_path)
        assessment = assessor.assess()

    print(f"\n{'='*60}")
    print(f"Auto-Generate: {assessment['package_name']}")
    print(f"{'='*60}")

    # Get package info
    package_name = args.package or assessment["package_name"]
    description = args.description or extract_description_from_readme(package_path)

    if args.dry_run:
        print("\n[DRY RUN - Would generate the following:]\n")

    # Generate based on recommendations
    generated = []
    skipped = []

    for rec in assessment["recommendations"]:
        asset_type = rec["asset"]
        priority = rec["priority"]

        print(f"\n[{priority}] {rec['action']}")

        if args.dry_run:
            print(f"  Command: {rec['command']}")
            generated.append(asset_type)
            continue

        # Skip if specific parameters missing
        if asset_type == "logo" and not description:
            print("  ⚠ Skipped: No description provided. Use --description")
            skipped.append(asset_type)
            continue

        if asset_type == "diagram" and not args.components:
            print("  ⚠ Skipped: No components provided. Use --components")
            skipped.append(asset_type)
            continue

        if asset_type == "screenshots" and not args.url:
            print("  ⚠ Skipped: No URL provided. Use --url")
            skipped.append(asset_type)
            continue

        # Execute generation
        success = execute_generation(
            asset_type=asset_type,
            package_name=package_name,
            description=description,
            components=args.components,
            url=args.url,
            provider=args.provider
        )

        if success:
            print(f"  ✓ Generated")
            generated.append(asset_type)
        else:
            print(f"  ✗ Failed")
            skipped.append(asset_type)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {len(generated)} generated, {len(skipped)} skipped")

    if not args.dry_run and generated:
        print("\nNext steps:")
        print("  1. Review generated assets in assets/")
        print("  2. Integrate into README.md")
        print("  3. Run /portfolio to update package metadata")

    return 0 if len(skipped) == 0 else 1


def execute_generation(
    asset_type: str,
    package_name: str,
    description: Optional[str],
    components: Optional[str],
    url: Optional[str],
    provider: str
) -> bool:
    """Execute a specific generation task.

    Returns:
        True if successful
    """
    try:
        if asset_type == "logo":
            return asyncio.run(generate_logo_sync(
                package_name=package_name,
                description=description or "A toolkit",
                provider=provider
            ))

        elif asset_type == "diagrams":
            if not components:
                return False
            comp_list = [c.strip() for c in components.split(",")]
            return asyncio.run(generate_diagram_sync(
                package_name=package_name,
                components=comp_list
            ))

        elif asset_type == "screenshots":
            if not url:
                return False
            return generate_screenshot_sync(url=url)

        elif asset_type == "banner":
            # Banner is just a wide logo
            return asyncio.run(generate_logo_sync(
                package_name=package_name,
                description=description or "A toolkit",
                provider=provider,
                output_path="assets/banners/banner.png"
            ))

        elif asset_type == "videos":
            return asyncio.run(generate_video_sync(
                package_name=package_name,
                description=description or "A toolkit"
            ))

        return False

    except Exception as e:
        print(f"  Error: {e}")
        return False


async def generate_logo_sync(
    package_name: str,
    description: str,
    provider: str,
    output_path: str = "assets/logo/logo.png"
) -> bool:
    """Async wrapper for logo generation."""
    generator = LogoGenerator()
    result = await generator.generate(
        package_name=package_name,
        description=description,
        output_path=Path(output_path),
        provider=provider
    )
    return result.get("success", False)


async def generate_diagram_sync(
    package_name: str,
    components: list[str]
) -> bool:
    """Async wrapper for diagram generation."""
    diagram = DiagramGenerator()
    result = await diagram.generate(
        package_name=package_name,
        components=components,
        output_path=Path("assets/diagrams/architecture.svg")
    )
    return result.get("success", False)


def generate_screenshot_sync(url: str) -> bool:
    """Sync wrapper for screenshot capture."""
    capture = ScreenshotCapture()
    result = capture.capture_url(
        url=url,
        output_path=Path("assets/screenshots/home.png")
    )
    return result.get("success", False)


async def generate_video_sync(
    package_name: str,
    description: str
) -> bool:
    """Async wrapper for video generation."""
    generator = VideoGenerator()
    result = await generator.generate(
        package_name=package_name,
        description=description,
        output_path=Path("assets/videos/demo.mp4")
    )
    return result.get("success", False)


def extract_description_from_readme(package_path: Path) -> Optional[str]:
    """Extract package description from README.

    Args:
        package_path: Path to package

    Returns:
        Description text or None
    """
    readme_path = package_path / "README.md"
    if not readme_path.exists():
        return None

    content = readme_path.read_text()

    # Look for first sentence/paragraph
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        # Skip headers, empty lines, badges
        if line and not line.startswith("#") and not line.startswith("["):
            # Return first meaningful line (up to 200 chars)
            return line[:200] + ("..." if len(line) > 200 else "")

    return None


if __name__ == "__main__":
    sys.exit(main())
