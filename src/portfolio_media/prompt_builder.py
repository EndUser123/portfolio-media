"""Prompt builder for different LLM providers.

Each provider has specific prompt requirements for optimal image/diagram generation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Provider(Enum):
    """Available LLM providers for media generation."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GLM = "glm"
    PERPLEXITY = "perplexity"
    CODEX = "codex"


class Style(Enum):
    """Visual style options for generated media."""
    MINIMALIST = "minimalist"
    GEOMETRIC = "geometric"
    GRADIENT = "gradient"
    FLAT = "flat"
    TECH = "tech"
    PLAYFUL = "playful"


@dataclass
class LogoPrompt:
    """Logo generation prompt parameters."""
    package_name: str
    description: str
    style: Style = Style.MINIMALIST
    color: Optional[str] = None
    icon_type: str = "simple"

    def build_for_provider(self, provider: Provider) -> str:
        """Build provider-specific prompt."""
        base_prompt = self._build_base()

        if provider == Provider.GEMINI:
            return self._for_gemini(base_prompt)
        elif provider == Provider.OPENROUTER:
            return self._for_openrouter(base_prompt)
        elif provider == Provider.GLM:
            return self._for_glm(base_prompt)
        elif provider == Provider.PERPLEXITY:
            return self._for_perplexity(base_prompt)
        else:
            return base_prompt

    def _build_base(self) -> str:
        """Build base prompt."""
        color_spec = f"Primary color: {self.color}" if self.color else "Professional color palette"
        return f"""Create a modern, {self.style.value} logo for {self.package_name}, a {self.description}.

Requirements:
- Style: {self.style.value}
- {color_spec}
- Simple {self.icon_type} icon, no text or letters
- Clean, scalable design suitable for GitHub avatar
- Professional, tech-oriented aesthetic
- Transparent background preferred
- Works well at small sizes (128x128)"""

    def _for_gemini(self, base: str) -> str:
        """Gemini/Imagen optimized prompt."""
        return f"""Create a {self.style.value} app icon design for {self.package_name}.

{self.description}

Visual specifications:
- {self.style.value} design style
- {f"Primary color: {self.color}" if self.color else "Professional tech colors"}
- Simple symbolic icon
- No text
- Vector-style clean lines
- Transparent background
- Optimized for 512x512px"""

    def _for_openrouter(self, base: str) -> str:
        """OpenRouter (Flux/SDXL) optimized prompt."""
        style_map = {
            Style.MINIMALIST: "minimalist logo design, clean lines, flat design",
            Style.GEOMETRIC: "geometric logo, shapes, symmetry",
            Style.GRADIENT: "gradient logo, modern color blend",
            Style.FLAT: "flat logo, solid colors, simple",
            Style.TECH: "tech logo, circuit patterns, digital",
            Style.PLAYFUL: "playful logo, friendly, colorful",
        }
        style_desc = style_map.get(self.style, "professional logo")
        color_desc = f", {self.color} color scheme" if self.color else ""

        return f"""{style_desc}{color_desc}, logo for {self.package_name} ({self.description}),
simple icon, no text, transparent background, professional, minimalist,
high quality, 512x512"""

    def _for_glm(self, base: str) -> str:
        """GLM optimized prompt."""
        return f"""请设计一个{self.package_name}的logo图标。

产品描述：{self.description}
设计风格：{self.style.value}
{"主色调：" + self.color if self.color else "配色：专业科技感"}

要求：
- 简约图标，无文字
- 适合GitHub头像使用
- 清晰可辨，支持缩放
- 透明背景"""

    def _for_perplexity(self, base: str) -> str:
        """Perplexity optimized prompt."""
        return f"""Design a professional logo for {self.package_name}.

Context: {self.description}
Style: {self.style.value} design
{f"Color: {self.color}" if self.color else ""}

Design brief:
- Simple, memorable icon
- No text or letters
- Scalable vector aesthetic
- GitHub-ready (512x512)
- Transparent background"""


@dataclass
class DiagramPrompt:
    """Architecture diagram prompt parameters."""
    package_name: str
    components: list[str]
    title: str = "Architecture"
    flow_direction: str = "LR"  # LR, TD, BT, RL

    def build_mermaid_prompt(self, provider: Provider = Provider.CLAUDE) -> str:
        """Build prompt for Mermaid diagram generation."""
        components_list = "\n".join(f"  - {c}" for c in self.components)

        if provider == Provider.CLAUDE:
            return f"""Generate a Mermaid architecture diagram for {self.package_name}.

Components to include:
{components_list}

Requirements:
- Flow direction: {self._flow_description()}
- Left-to-right or top-down based on what makes sense
- Use subgraphs for grouping related components
- Color-code by layer (e.g., API, service, data)
- Clear, descriptive labels
- Professional styling

Output ONLY the Mermaid code block wrapped in ```mermaid```."""

        return f"Create Mermaid diagram for {self.package_name} with components: {', '.join(self.components)}"

    def _flow_description(self) -> str:
        """Get human-readable flow description."""
        flows = {
            "LR": "left to right",
            "TD": "top to down",
            "BT": "bottom to top",
            "RL": "right to left",
        }
        return flows.get(self.flow_direction, "left to right")


@dataclass
class ScreenshotPrompt:
    """Screenshot capture prompt parameters."""
    url: str
    selector: Optional[str] = None
    wait_for: Optional[str] = None
    full_page: bool = False
    width: int = 1280
    height: int = 720

    def get_capture_config(self) -> dict:
        """Get Playwright capture configuration."""
        return {
            "viewport": {"width": self.width, "height": self.height},
            "wait_for_selector": self.wait_for,
            "full_page": self.full_page,
            "clip": self._get_clip() if self.selector else None,
        }

    def _get_clip(self) -> dict:
        """Get clip rectangle for element screenshot."""
        # This would be computed at runtime via Playwright's boundingBox()
        return None
