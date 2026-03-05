"""Diagram generator using Claude + mermaid-cli.

Generates Mermaid architecture diagrams and renders them to SVG.
"""

import asyncio
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

from .prompt_builder import DiagramPrompt, Provider
from .providers.claude import ClaudeProvider


def _find_mmdc() -> Optional[str]:
    """Find the mmdc executable, handling Windows npm install locations."""
    # On Windows, npm installs to AppData/Roaming/npm
    if platform.system() == "Windows":
        # Check common npm locations
        npm_paths = [
            Path(os.path.expandvars(r"%APPDATA%\npm\mmdc.cmd")),
            Path(os.path.expanduser(r"~/AppData/Roaming/npm/mmdc.cmd")),
            Path("C:/Users/brsth/AppData/Roaming/npm/mmdc.cmd"),
        ]
        for p in npm_paths:
            if p.exists():
                return str(p)
    # Fall back to PATH search
    return "mmdc"


class DiagramGenerator:
    """Generate architecture diagrams using Claude + mermaid-cli.

    Usage:
        generator = DiagramGenerator()
        await generator.generate(
            package_name="debugRCA",
            components=["Analyzer", "Hypothesis Generator", "Verifier"],
            output_path=Path("assets/diagrams/architecture.svg")
        )
    """

    def __init__(self):
        self.claude = ClaudeProvider()

    async def generate(
        self,
        package_name: str,
        components: list[str],
        output_path: Path,
        title: str = "Architecture",
        flow_direction: str = "TD",
        renderer: str = "auto"
    ) -> dict:
        """Generate and render an architecture diagram.

        Args:
            package_name: Name of the package
            components: List of component names/roles
            output_path: Where to save the diagram
            title: Diagram title
            flow_direction: TD (top-down), LR (left-right), etc.
            renderer: auto, mmdc, or none (code only)

        Returns:
            Dict with success status and paths
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build diagram prompt
        diagram_prompt = DiagramPrompt(
            package_name=package_name,
            components=components,
            title=title,
            flow_direction=flow_direction
        )

        # Generate Mermaid code via Claude
        mermaid_code = await self._generate_mermaid_code(diagram_prompt)

        if not mermaid_code:
            return {
                "success": False,
                "error": "Failed to generate Mermaid code"
            }

        # Save raw Mermaid code
        mmd_path = output_path.with_suffix(".mmd")
        mmd_path.write_text(mermaid_code)

        # Render to SVG if requested
        if renderer == "none":
            return {
                "success": True,
                "mermaid_code": mermaid_code,
                "mmd_path": str(mmd_path)
            }

        svg_path = output_path
        rendered = await self._render_mermaid(mermaid_code, svg_path)

        return {
            "success": rendered,
            "mermaid_code": mermaid_code,
            "mmd_path": str(mmd_path),
            "svg_path": str(svg_path) if rendered else None,
            "renderer": renderer
        }

    async def _generate_mermaid_code(self, prompt: DiagramPrompt) -> Optional[str]:
        """Generate high-quality Mermaid diagram code.

        Creates visually appealing architecture diagrams with proper styling.
        """
        components = prompt.components

        # Modern color scheme - cohesive blues and accent colors
        colors = {
            "primary": "#2563eb",      # Vibrant blue
            "primary_light": "#dbeafe", # Light blue
            "accent": "#06b6d4",       # Cyan
            "accent_light": "#cffafe",  # Light cyan
            "success": "#10b981",      # Green
            "success_light": "#d1fae5", # Light green
            "warning": "#f59e0b",      # Amber
            "warning_light": "#fef3c7", # Light amber
            "dark": "#1e293b",         # Slate dark
            "text": "#334155",         # Slate text
        }

        # Start with flowchart using LR (left-to-right) for better readability
        direction = "LR" if prompt.flow_direction == "TD" else prompt.flow_direction
        mermaid_lines = [
            f"flowchart {direction}",
            "",
            f'    %% {prompt.package_name} - {prompt.title}',
            "",
        ]

        # Define styles first (more modern, clean look)
        mermaid_lines.extend([
            "    %% Modern color scheme",
            f"    classDef primary fill:{colors['primary_light']},stroke:{colors['primary']},stroke-width:2px,color:{colors['dark']},rx:8px",
            f"    classDef accent fill:{colors['accent_light']},stroke:{colors['accent']},stroke-width:2px,color:{colors['dark']},rx:8px",
            f"    classDef success fill:{colors['success_light']},stroke:{colors['success']},stroke-width:2px,color:{colors['dark']},rx:8px",
            f"    classDef warning fill:{colors['warning_light']},stroke:{colors['warning']},stroke-width:2px,color:{colors['dark']},rx:8px",
            f"    classDef container fill:#f8fafc,stroke:#94a3b8,stroke-width:1px,color:{colors['dark']},stroke-dasharray: 5 5",
            "",
        ])

        # Add main container/subgraph
        safe_name = prompt.package_name.replace("-", "_").replace(".", "_")
        mermaid_lines.extend([
            f'    subgraph {safe_name}["{prompt.title}"]',
            f"        direction {direction}",
            "",
        ])

        # Create nodes with better naming
        for i, comp in enumerate(components):
            # Determine node style based on component type keywords
            comp_lower = comp.lower()
            if any(k in comp_lower for k in ["main", "core", "center", "hub"]):
                style_class = ":::primary"
            elif any(k in comp_lower for k in ["api", "client", "input", "user"]):
                style_class = ":::accent"
            elif any(k in comp_lower for k in ["reporter", "output", "export", "save"]):
                style_class = ":::success"
            elif any(k in comp_lower for k in ["data", "store", "db", "cache"]):
                style_class = ":::warning"
            else:
                # Rotate through styles for visual variety
                style_classes = [":::primary", ":::accent", ":::success", ":::warning"]
                style_class = style_classes[i % len(style_classes)]

            # Use descriptive IDs
            node_id = f"{comp.lower().replace(' ', '_').replace('-', '_')[:20]}"
            mermaid_lines.append(f'        {node_id}["{comp}"]{style_class}')

        mermaid_lines.extend([
            "",
            "    end",
            "",
        ])

        # Create meaningful connections (not just linear)
        # First component connects to all others as entry point
        if len(components) > 2:
            mermaid_lines.extend([
                "    %% Data flow connections",
                f"        {components[0].lower().replace(' ', '_')[:20]} --> {components[1].lower().replace(' ', '_')[:20]}",
            ])

            # Middle components interconnect
            for i in range(1, len(components) - 1):
                curr = components[i].lower().replace(' ', '_')[:20]
                next_comp = components[i + 1].lower().replace(' ', '_')[:20]
                mermaid_lines.append(f"        {curr} --> {next_comp}")

            # Add bidirectional flows for related components (adds visual interest)
            if len(components) >= 3:
                first = components[0].lower().replace(' ', '_')[:20]
                last = components[-1].lower().replace(' ', '_')[:20]
                mermaid_lines.extend([
                    "",
                    "    %% Feedback loop",
                    f"        {last} -.->|feedback| {first}",
                ])

        mermaid_lines.extend([
            "",
            "    %% Link styling",
            "    linkStyle default stroke:#64748b,stroke-width:2px",
            "    linkStyle 1 stroke:#2563eb,stroke-width:3px",  # Highlight main flow
        ])

        return "\n".join(mermaid_lines)

    async def _render_mermaid(self, mermaid_code: str, output_path: Path) -> bool:
        """Render Mermaid code to SVG using mermaid-cli."""
        mmdc_cmd = _find_mmdc()

        # Verify mmdc works
        try:
            result = subprocess.run([mmdc_cmd, "--version"], capture_output=True, timeout=5, shell=True)
            if result.returncode != 0:
                print("⚠ mermaid-cli (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli")
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            print("⚠ mermaid-cli (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli")
            return False

        # Write temp file
        temp_mmd = output_path.with_suffix(".temp.mmd")
        temp_mmd.write_text(mermaid_code)

        # Render
        try:
            result = subprocess.run([
                mmdc_cmd,
                "-i", str(temp_mmd),
                "-o", str(output_path),
                "-b", "transparent",
                "-s", "2"
            ], check=True, capture_output=True, timeout=30, shell=True)

            # Clean up temp file
            temp_mmd.unlink()
            return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"⚠ Rendering failed: {e}")
            return False

    async def generate_from_code(
        self,
        mermaid_code: str,
        output_path: Path
    ) -> dict:
        """Render existing Mermaid code to SVG.

        Args:
            mermaid_code: Existing Mermaid diagram code
            output_path: Where to save the SVG

        Returns:
            Dict with result status
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save source code
        mmd_path = output_path.with_suffix(".mmd")
        mmd_path.write_text(mermaid_code)

        # Render
        rendered = await self._render_mermaid(mermaid_code, output_path)

        return {
            "success": rendered,
            "mmd_path": str(mmd_path),
            "svg_path": str(output_path) if rendered else None
        }

    async def analyze_and_diagram(
        self,
        package_path: Path,
        output_path: Path,
        max_depth: int = 2
    ) -> dict:
        """Analyze a package and generate its architecture diagram.

        Args:
            package_path: Path to the package directory
            output_path: Where to save the diagram
            max_depth: How deep to analyze the structure

        Returns:
            Dict with result status
        """
        # This would use Claude to analyze the code structure
        # and generate an appropriate diagram

        package_name = package_path.name

        # Find Python modules
        py_files = list(package_path.rglob("*.py"))
        modules = [f.stem for f in py_files if f.stem != "__init__"]

        # Find main components (simplified)
        components = list(set(modules))[:10]  # Limit to 10 for readability

        return await self.generate(
            package_name=package_name,
            components=components,
            output_path=output_path
        )


async def generate_diagram_cli(
    package_name: str,
    components: str,
    output_path: str,
    title: str = "Architecture",
    flow: str = "TD"
) -> None:
    """CLI entry point for diagram generation.

    Usage:
        python -m portfolio_media.diagram_generator \\
            --package debugRCA \\
            --components "Analyzer,Verifier,Hypothesis" \\
            --output assets/diagrams/arch.svg \\
            --flow TD
    """
    generator = DiagramGenerator()
    component_list = [c.strip() for c in components.split(",")]

    result = await generator.generate(
        package_name=package_name,
        components=component_list,
        output_path=Path(output_path),
        title=title,
        flow_direction=flow
    )

    if result["success"]:
        print(f"✓ Diagram generated: {result.get('svg_path')}")
        print(f"  Mermaid code: {result['mmd_path']}")
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate architecture diagrams")
    parser.add_argument("--package", required=True, help="Package name")
    parser.add_argument("--components", required=True, help="Comma-separated component list")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--title", default="Architecture", help="Diagram title")
    parser.add_argument("--flow", default="TD", help="Flow direction (TD, LR, BT, RL)")

    args = parser.parse_args()

    asyncio.run(generate_diagram_cli(
        package_name=args.package,
        components=args.components,
        output_path=args.output,
        title=args.title,
        flow=args.flow
    ))
