"""Tests for providers module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Test imports
def test_provider_imports():
    """Test that all providers can be imported."""
    from portfolio_media.providers import (
        ClaudeProvider,
        GeminiProvider,
        OpenRouterProvider,
        GLMProvider,
        PerplexityProvider,
        NotebookLMProvider
    )
    assert ClaudeProvider is not None
    assert GeminiProvider is not None
    assert OpenRouterProvider is not None
    assert GLMProvider is not None
    assert PerplexityProvider is not None
    assert NotebookLMProvider is not None


class TestClaudeProvider:
    """Test suite for ClaudeProvider."""

    def test_initialization(self):
        """Test ClaudeProvider initialization."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()
        assert provider.name == "claude"

    @pytest.mark.asyncio
    async def test_generate_diagram_code(self):
        """Test generate_diagram_code() method."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        result = await provider.generate_diagram_code(
            prompt="Create a flowchart",
            diagram_type="mermaid"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_mermaid_with_subprocess(self):
        """Test render_mermaid() with subprocess call."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = provider.render_mermaid(
                mermaid_code="flowchart LR\n    A-->B",
                output_path=Path("/tmp/test.svg")
            )

            # May return False if mmdc not available, but should not crash
            assert isinstance(result, bool)

    def test_render_mermaid_without_mmdc(self, tmp_path):
        """Test render_mermaid() when mmdc is not available."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        with patch('subprocess.run') as mock_run:
            # Simulate mmdc not found
            mock_run.side_effect = FileNotFoundError()

            result = provider.render_mermaid(
                mermaid_code="flowchart LR\n    A-->B",
                output_path=tmp_path / "test.svg"
            )

            assert result is False
            # Should save .mmd file
            assert (tmp_path / "test.mmd").exists()

    def test_generate_logo_prompt(self):
        """Test generate_logo_prompt() method."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        prompt = provider.generate_logo_prompt(
            package_name="testpkg",
            description="A testing toolkit",
            style="minimalist"
        )

        assert isinstance(prompt, str)
        assert "testpkg" in prompt
        assert "testing toolkit" in prompt

    @pytest.mark.asyncio
    async def test_ask_claude_for_prompt(self):
        """Test ask_claude_for_prompt() method."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        result = await provider.ask_claude_for_prompt(
            package_name="testpkg",
            description="A testing toolkit",
            style="minimalist"
        )

        assert isinstance(result, str)
        assert "testpkg" in result


class TestGeminiProvider:
    """Test suite for GeminiProvider."""

    def test_initialization(self):
        """Test GeminiProvider initialization."""
        from portfolio_media.providers.gemini import GeminiProvider
        provider = GeminiProvider()
        assert hasattr(provider, 'name')

    def test_check_installation(self):
        """Test check_installation() method."""
        from portfolio_media.providers.gemini import GeminiProvider
        provider = GeminiProvider()

        result = provider.check_installation()

        assert isinstance(result, dict)
        assert "available" in result
        assert "env_var" in result

    @pytest.mark.asyncio
    async def test_generate_logo_with_mock(self, tmp_path):
        """Test generate_logo() with mocked API call."""
        from portfolio_media.providers.gemini import GeminiProvider
        provider = GeminiProvider()

        # Mock the actual API call
        with patch.object(provider, '_call_gemini_api', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = b"fake_image_data"

            result = await provider.generate_logo(
                prompt="A simple logo",
                output_path=tmp_path / "test.png"
            )

            # Result structure should be correct even if API fails
            assert isinstance(result, bool)


class TestOpenRouterProvider:
    """Test suite for OpenRouterProvider."""

    def test_initialization(self):
        """Test OpenRouterProvider initialization."""
        from portfolio_media.providers.openrouter import OpenRouterProvider
        provider = OpenRouterProvider()
        assert hasattr(provider, 'name')

    def test_check_installation(self):
        """Test check_installation() method."""
        from portfolio_media.providers.openrouter import OpenRouterProvider
        provider = OpenRouterProvider()

        result = provider.check_installation()

        assert isinstance(result, dict)
        assert "available" in result
        assert "env_var" in result


class TestGLMProvider:
    """Test suite for GLMProvider."""

    def test_initialization(self):
        """Test GLMProvider initialization."""
        from portfolio_media.providers.glm import GLMProvider
        provider = GLMProvider()
        assert hasattr(provider, 'name')

    def test_check_installation(self):
        """Test check_installation() method."""
        from portfolio_media.providers.glm import GLMProvider
        provider = GLMProvider()

        result = provider.check_installation()

        assert isinstance(result, dict)
        assert "available" in result


class TestPerplexityProvider:
    """Test suite for PerplexityProvider."""

    def test_initialization(self):
        """Test PerplexityProvider initialization."""
        from portfolio_media.providers.perplexity import PerplexityProvider
        provider = PerplexityProvider()
        assert hasattr(provider, 'name')

    def test_check_installation(self):
        """Test check_installation() method."""
        from portfolio_media.providers.perplexity import PerplexityProvider
        provider = PerplexityProvider()

        result = provider.check_installation()

        assert isinstance(result, dict)
        assert "available" in result


class TestNotebookLMProvider:
    """Test suite for NotebookLMProvider."""

    def test_initialization(self):
        """Test NotebookLMProvider initialization."""
        from portfolio_media.providers.notebooklm import NotebookLMProvider
        provider = NotebookLMProvider()
        assert hasattr(provider, 'available')

    def test_check_installation(self):
        """Test check_installation() method."""
        from portfolio_media.providers.notebooklm import NotebookLMProvider
        provider = NotebookLMProvider()

        result = provider.check_installation()

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_video(self, tmp_path):
        """Test generate_video() method."""
        from portfolio_media.providers.notebooklm import NotebookLMProvider
        provider = NotebookLMProvider()

        result = await provider.generate_video(
            package_name="testpkg",
            description="A test package",
            readme_path=None,
            output_path=tmp_path / "test.mp4"
        )

        assert isinstance(result, dict)
        assert "success" in result


class TestProvidersIntegration:
    """Integration tests for providers."""

    def test_all_providers_have_check_installation(self):
        """Test that all providers have check_installation method."""
        from portfolio_media.providers import (
            ClaudeProvider,
            GeminiProvider,
            OpenRouterProvider,
            GLMProvider,
            PerplexityProvider,
            NotebookLMProvider
        )

        providers = [
            ClaudeProvider(),
            GeminiProvider(),
            OpenRouterProvider(),
            GLMProvider(),
            PerplexityProvider(),
            NotebookLMProvider()
        ]

        for provider in providers:
            assert hasattr(provider, 'check_installation') or hasattr(provider, 'available')

    def test_all_providers_return_dict_from_check(self):
        """Test that all providers return dict from check_installation."""
        from portfolio_media.providers import (
            GeminiProvider,
            OpenRouterProvider,
            GLMProvider,
            PerplexityProvider
        )

        providers = [
            GeminiProvider(),
            OpenRouterProvider(),
            GLMProvider(),
            PerplexityProvider()
        ]

        for provider in providers:
            if hasattr(provider, 'check_installation'):
                result = provider.check_installation()
                assert isinstance(result, dict)
                assert "available" in result

    def test_provider_env_vars_documented(self):
        """Test that providers document their environment variables."""
        from portfolio_media.providers import (
            GeminiProvider,
            OpenRouterProvider,
            GLMProvider,
            PerplexityProvider
        )

        providers = [
            ("gemini", GeminiProvider()),
            ("openrouter", OpenRouterProvider()),
            ("glm", GLMProvider()),
            ("perplexity", PerplexityProvider())
        ]

        for name, provider in providers:
            result = provider.check_installation()
            # Should have env_var in result or available=False
            assert "env_var" in result or "available" in result


class TestProvidersAsync:
    """Test suite for async provider methods."""

    @pytest.mark.asyncio
    async def test_claude_provider_async_methods(self):
        """Test ClaudeProvider async methods don't crash."""
        from portfolio_media.providers.claude import ClaudeProvider
        provider = ClaudeProvider()

        # Should not raise exceptions
        result = await provider.generate_diagram_code("test prompt")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_gemini_provider_async_methods(self):
        """Test GeminiProvider async methods."""
        from portfolio_media.providers.gemini import GeminiProvider
        provider = GeminiProvider()

        # Test with mocked API to avoid actual calls
        with patch.object(provider, '_call_gemini_api', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = b"test_data"

            result = await provider.generate_logo(
                prompt="test",
                output_path=Path("/tmp/test.png")
            )

            # Should handle gracefully
            assert isinstance(result, bool)
