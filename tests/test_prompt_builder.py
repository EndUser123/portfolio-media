"""Tests for prompt_builder module."""

import pytest
from portfolio_media.prompt_builder import (
    Provider,
    Style,
    LogoPrompt,
    DiagramPrompt,
    ScreenshotPrompt
)


class TestProvider:
    """Test suite for Provider enum."""

    def test_provider_values(self):
        """Test that Provider enum has expected values."""
        assert Provider.CLAUDE.value == "claude"
        assert Provider.GEMINI.value == "gemini"
        assert Provider.OPENROUTER.value == "openrouter"
        assert Provider.GLM.value == "glm"
        assert Provider.PERPLEXITY.value == "perplexity"
        assert Provider.CODEX.value == "codex"

    def test_provider_from_string(self):
        """Test creating Provider from string value."""
        provider = Provider("gemini")
        assert provider == Provider.GEMINI

    def test_provider_invalid_string(self):
        """Test that invalid string raises error."""
        with pytest.raises(ValueError):
            Provider("invalid_provider")


class TestStyle:
    """Test suite for Style enum."""

    def test_style_values(self):
        """Test that Style enum has expected values."""
        assert Style.MINIMALIST.value == "minimalist"
        assert Style.GEOMETRIC.value == "geometric"
        assert Style.GRADIENT.value == "gradient"
        assert Style.FLAT.value == "flat"
        assert Style.TECH.value == "tech"
        assert Style.PLAYFUL.value == "playful"

    def test_style_from_string(self):
        """Test creating Style from string value."""
        style = Style("geometric")
        assert style == Style.GEOMETRIC


class TestLogoPrompt:
    """Test suite for LogoPrompt dataclass."""

    def test_initialization(self):
        """Test LogoPrompt initialization."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        assert prompt.package_name == "testpkg"
        assert prompt.description == "A test package"
        assert prompt.style == Style.MINIMALIST
        assert prompt.color is None
        assert prompt.icon_type == "simple"

    def test_initialization_with_style(self):
        """Test LogoPrompt with custom style."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            style=Style.GEOMETRIC
        )
        assert prompt.style == Style.GEOMETRIC

    def test_initialization_with_color(self):
        """Test LogoPrompt with custom color."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            color="#FF6B6B"
        )
        assert prompt.color == "#FF6B6B"

    def test_build_base_prompt(self):
        """Test that _build_base() creates a prompt string."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        base = prompt._build_base()

        assert isinstance(base, str)
        assert "testpkg" in base
        assert "A test package" in base
        assert "minimalist" in base

    def test_build_base_prompt_with_color(self):
        """Test that _build_base() includes color when specified."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            color="#FF6B6B"
        )
        base = prompt._build_base()

        assert "#FF6B6B" in base

    def test_build_for_provider_gemini(self):
        """Test build_for_provider() with Gemini."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        gemini_prompt = prompt.build_for_provider(Provider.GEMINI)

        assert "testpkg" in gemini_prompt
        assert "A test package" in gemini_prompt
        assert "512x512" in gemini_prompt

    def test_build_for_provider_openrouter(self):
        """Test build_for_provider() with OpenRouter."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            style=Style.GEOMETRIC
        )
        or_prompt = prompt.build_for_provider(Provider.OPENROUTER)

        assert "testpkg" in or_prompt
        assert "geometric" in or_prompt.lower()

    def test_build_for_provider_glm(self):
        """Test build_for_provider() with GLM (Chinese)."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        glm_prompt = prompt.build_for_provider(Provider.GLM)

        assert "testpkg" in glm_prompt
        # Should contain Chinese characters
        assert any(ord(c) > 127 for c in glm_prompt)

    def test_build_for_provider_perplexity(self):
        """Test build_for_provider() with Perplexity."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            style=Style.TECH
        )
        perplexity_prompt = prompt.build_for_provider(Provider.PERPLEXITY)

        assert "testpkg" in perplexity_prompt
        assert "tech" in perplexity_prompt.lower()

    def test_build_for_provider_default(self):
        """Test build_for_provider() with unknown provider uses base."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        # Use CODEX which doesn't have a specific implementation
        default_prompt = prompt.build_for_provider(Provider.CODEX)

        assert "testpkg" in default_prompt
        assert "A test package" in default_prompt

    def test_for_gemini_includes_transparent_background(self):
        """Test that Gemini prompt includes transparent background."""
        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package"
        )
        gemini_prompt = prompt._for_gemini("base prompt")

        assert "transparent" in gemini_prompt.lower()

    def test_for_openrouter_style_mapping(self):
        """Test that OpenRouter maps styles correctly."""
        style_map = {
            Style.MINIMALIST: "minimalist",
            Style.GEOMETRIC: "geometric",
            Style.GRADIENT: "gradient",
            Style.FLAT: "flat",
            Style.TECH: "tech",
            Style.PLAYFUL: "playful",
        }

        for style, expected_keyword in style_map.items():
            prompt = LogoPrompt(
                package_name="testpkg",
                description="A test package",
                style=style
            )
            or_prompt = prompt._for_openrouter("base")
            assert expected_keyword in or_prompt.lower()


class TestDiagramPrompt:
    """Test suite for DiagramPrompt dataclass."""

    def test_initialization(self):
        """Test DiagramPrompt initialization."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["A", "B", "C"]
        )
        assert prompt.package_name == "testpkg"
        assert prompt.components == ["A", "B", "C"]
        assert prompt.title == "Architecture"
        assert prompt.flow_direction == "LR"

    def test_initialization_with_custom_params(self):
        """Test DiagramPrompt with custom parameters."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["X", "Y", "Z"],
            title="Custom Diagram",
            flow_direction="TD"
        )
        assert prompt.title == "Custom Diagram"
        assert prompt.flow_direction == "TD"

    def test_build_mermaid_prompt_claude(self):
        """Test build_mermaid_prompt() with Claude provider."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["Analyzer", "Processor", "Exporter"]
        )
        mermaid_prompt = prompt.build_mermaid_prompt(Provider.CLAUDE)

        assert "testpkg" in mermaid_prompt
        assert "Analyzer" in mermaid_prompt
        assert "Processor" in mermaid_prompt
        assert "Exporter" in mermaid_prompt

    def test_build_mermaid_prompt_includes_flow_direction(self):
        """Test that build_mermaid_prompt() includes flow direction."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["A", "B"],
            flow_direction="TD"
        )
        mermaid_prompt = prompt.build_mermaid_prompt(Provider.CLAUDE)

        assert "top to down" in mermaid_prompt.lower()

    def test_flow_description(self):
        """Test _flow_description() method."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["A", "B"]
        )

        assert prompt._flow_description() == "left to right"

        prompt.flow_direction = "TD"
        assert prompt._flow_description() == "top to down"

        prompt.flow_direction = "BT"
        assert prompt._flow_description() == "bottom to top"

        prompt.flow_direction = "RL"
        assert prompt._flow_description() == "right to left"

    def test_build_mermaid_prompt_default_provider(self):
        """Test build_mermaid_prompt() with default provider."""
        prompt = DiagramPrompt(
            package_name="testpkg",
            components=["A", "B"]
        )
        mermaid_prompt = prompt.build_mermaid_prompt()

        assert "testpkg" in mermaid_prompt
        assert "A" in mermaid_prompt


class TestScreenshotPrompt:
    """Test suite for ScreenshotPrompt dataclass."""

    def test_initialization(self):
        """Test ScreenshotPrompt initialization."""
        prompt = ScreenshotPrompt(
            url="http://example.com"
        )
        assert prompt.url == "http://example.com"
        assert prompt.selector is None
        assert prompt.wait_for is None
        assert prompt.full_page is False
        assert prompt.width == 1280
        assert prompt.height == 720

    def test_initialization_with_custom_params(self):
        """Test ScreenshotPrompt with custom parameters."""
        prompt = ScreenshotPrompt(
            url="http://example.com",
            selector="#main",
            wait_for=".loaded",
            full_page=True,
            width=1920,
            height=1080
        )
        assert prompt.selector == "#main"
        assert prompt.wait_for == ".loaded"
        assert prompt.full_page is True
        assert prompt.width == 1920
        assert prompt.height == 1080

    def test_get_capture_config(self):
        """Test that get_capture_config() returns correct config."""
        prompt = ScreenshotPrompt(
            url="http://example.com",
            width=1920,
            height=1080
        )
        config = prompt.get_capture_config()

        assert isinstance(config, dict)
        assert config["viewport"]["width"] == 1920
        assert config["viewport"]["height"] == 1080
        assert config["wait_for_selector"] is None
        assert config["full_page"] is False

    def test_get_capture_config_with_wait_for(self):
        """Test get_capture_config() with wait_for selector."""
        prompt = ScreenshotPrompt(
            url="http://example.com",
            wait_for=".content-loaded"
        )
        config = prompt.get_capture_config()

        assert config["wait_for_selector"] == ".content-loaded"

    def test_get_capture_config_full_page(self):
        """Test get_capture_config() with full_page=True."""
        prompt = ScreenshotPrompt(
            url="http://example.com",
            full_page=True
        )
        config = prompt.get_capture_config()

        assert config["full_page"] is True

    def test_get_clip_returns_none(self):
        """Test that _get_clip() returns None (placeholder)."""
        prompt = ScreenshotPrompt(
            url="http://example.com",
            selector="#main"
        )
        clip = prompt._get_clip()

        # Currently returns None as it's computed at runtime
        assert clip is None


class TestPromptBuilderIntegration:
    """Integration tests for prompt_builder module."""

    def test_logo_prompt_workflow(self):
        """Test complete LogoPrompt workflow."""
        prompt = LogoPrompt(
            package_name="mypackage",
            description="A testing toolkit",
            style=Style.MINIMALIST,
            color="#3498db"
        )

        # Build for different providers
        providers_to_test = [
            Provider.GEMINI,
            Provider.OPENROUTER,
            Provider.GLM,
            Provider.PERPLEXITY
        ]

        for provider in providers_to_test:
            result = prompt.build_for_provider(provider)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "mypackage" in result

    def test_diagram_prompt_workflow(self):
        """Test complete DiagramPrompt workflow."""
        prompt = DiagramPrompt(
            package_name="myapp",
            components=["API", "Service", "Database"],
            title="System Architecture",
            flow_direction="TD"
        )

        mermaid_prompt = prompt.build_mermaid_prompt(Provider.CLAUDE)

        assert "myapp" in mermaid_prompt
        assert "API" in mermaid_prompt
        assert "Service" in mermaid_prompt
        assert "Database" in mermaid_prompt

    def test_screenshot_prompt_workflow(self):
        """Test complete ScreenshotPrompt workflow."""
        prompt = ScreenshotPrompt(
            url="http://localhost:8000",
            width=1920,
            height=1080,
            full_page=True
        )

        config = prompt.get_capture_config()

        assert config["viewport"]["width"] == 1920
        assert config["viewport"]["height"] == 1080
        assert config["full_page"] is True
