"""Integration tests for portfolio-media package."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock


class TestPackageImports:
    """Test suite for package-level imports."""

    def test_import_portfolio_media(self):
        """Test that portfolio_media can be imported."""
        import portfolio_media
        assert portfolio_media is not None

    def test_import_assessment(self):
        """Test that Assessment module can be imported."""
        from portfolio_media import AssetAssessment, assess_package
        assert AssetAssessment is not None
        assert assess_package is not None

    def test_import_generators(self):
        """Test that all generators can be imported."""
        from portfolio_media import (
            LogoGenerator,
            DiagramGenerator,
            ScreenshotCapture,
            VideoGenerator
        )
        assert LogoGenerator is not None
        assert DiagramGenerator is not None
        assert ScreenshotCapture is not None
        assert VideoGenerator is not None

    def test_import_providers(self):
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

    def test_import_prompt_builder(self):
        """Test that prompt_builder module can be imported."""
        from portfolio_media.prompt_builder import (
            Provider,
            Style,
            LogoPrompt,
            DiagramPrompt,
            ScreenshotPrompt
        )
        assert Provider is not None
        assert Style is not None
        assert LogoPrompt is not None
        assert DiagramPrompt is not None
        assert ScreenshotPrompt is not None


class TestAssetAssessmentIntegration:
    """Integration tests for AssetAssessment."""

    def test_assess_package_function(self, tmp_path):
        """Test assess_package() convenience function."""
        from portfolio_media import assess_package

        result = assess_package(tmp_path)

        assert isinstance(result, dict)
        assert "package_name" in result
        assert "quality_score" in result
        assert "assets_missing" in result
        assert "recommendations" in result

    def test_assess_package_with_string_path(self, tmp_path):
        """Test assess_package() with string path."""
        from portfolio_media import assess_package

        result = assess_package(str(tmp_path))

        assert isinstance(result, dict)


class TestLogoGeneratorIntegration:
    """Integration tests for LogoGenerator."""

    def test_check_providers_returns_dict(self):
        """Test that check_providers() returns status for all providers."""
        from portfolio_media import LogoGenerator

        generator = LogoGenerator()
        status = generator.check_providers()

        assert isinstance(status, dict)
        # Should have status for each provider
        expected_providers = ["claude", "gemini", "openrouter", "glm", "perplexity"]
        for provider in expected_providers:
            assert provider in status

    def test_generate_variations_returns_list(self, tmp_path):
        """Test that generate_variations() returns list of results."""
        from portfolio_media import LogoGenerator

        generator = LogoGenerator()

        with patch.object(generator, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {"success": True, "output_path": "test.png"}

            import asyncio

            results = asyncio.run(generator.generate_variations(
                package_name="test",
                description="Test package",
                output_dir=tmp_path,
                count=3
            ))

            assert isinstance(results, list)
            assert len(results) == 3


class TestDiagramGeneratorIntegration:
    """Integration tests for DiagramGenerator."""

    @pytest.mark.asyncio
    async def test_generate_from_code(self, tmp_path):
        """Test generate_from_code() method."""
        from portfolio_media import DiagramGenerator

        generator = DiagramGenerator()

        with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
            mock_render.return_value = True

            result = await generator.generate_from_code(
                mermaid_code="flowchart LR\n    A-->B",
                output_path=tmp_path / "test.svg"
            )

            assert isinstance(result, dict)
            assert "success" in result

    @pytest.mark.asyncio
    async def test_analyze_and_diagram(self, tmp_path):
        """Test analyze_and_diagram() method."""
        from portfolio_media import DiagramGenerator

        # Create a simple package structure
        pkg_path = tmp_path / "test_package"
        pkg_path.mkdir()
        (pkg_path / "__init__.py").touch()
        (pkg_path / "module.py").touch()

        generator = DiagramGenerator()

        with patch.object(generator, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {"success": True}

            result = await generator.analyze_and_diagram(
                package_path=pkg_path,
                output_path=tmp_path / "output.svg"
            )

            assert isinstance(result, dict)


class TestVideoGeneratorIntegration:
    """Integration tests for VideoGenerator."""

    def test_check_installation_comprehensive(self):
        """Test that check_installation() returns comprehensive status."""
        from portfolio_media import VideoGenerator

        generator = VideoGenerator()
        status = generator.check_installation()

        # Check all expected keys are present
        expected_keys = [
            "gpu", "cogvideox", "opensora", "openrouter",
            "notebooklm", "ffmpeg", "recommended"
        ]

        for key in expected_keys:
            assert key in status, f"Missing key: {key}"

    def test_recommended_backend_selection(self):
        """Test that appropriate backend is recommended."""
        from portfolio_media import VideoGenerator

        generator = VideoGenerator()
        status = generator.check_installation()

        recommended = status["recommended"]
        assert recommended in ["notebooklm", "cogvideox", "opensora", "openrouter"]


class TestScreenshotCaptureIntegration:
    """Integration tests for ScreenshotCapture."""

    def test_capture_multiple_returns_results(self, tmp_path):
        """Test that capture_multiple() returns results for all URLs."""
        from portfolio_media import ScreenshotCapture

        capture = ScreenshotCapture()

        urls = [
            ("http://example.com", tmp_path / "test1.png"),
            ("http://example.org", tmp_path / "test2.png"),
        ]

        results = capture.capture_multiple(urls)

        assert isinstance(results, list)
        assert len(results) == 2

        for result in results:
            assert isinstance(result, dict)
            assert "success" in result


class TestProvidersIntegration:
    """Integration tests for providers."""

    def test_all_providers_checkable(self):
        """Test that all providers can be checked for availability."""
        from portfolio_media.providers import (
            GeminiProvider,
            OpenRouterProvider,
            GLMProvider,
            PerplexityProvider,
            NotebookLMProvider
        )

        providers = [
            ("gemini", GeminiProvider()),
            ("openrouter", OpenRouterProvider()),
            ("glm", GLMProvider()),
            ("perplexity", PerplexityProvider()),
            ("notebooklm", NotebookLMProvider())
        ]

        for name, provider in providers:
            if hasattr(provider, 'check_installation'):
                status = provider.check_installation()
                assert isinstance(status, dict), f"{name} check_installation should return dict"
                assert "available" in status, f"{name} status should have 'available' key"


class TestPromptBuilderIntegration:
    """Integration tests for prompt_builder."""

    def test_logo_prompt_all_providers(self):
        """Test LogoPrompt with all providers."""
        from portfolio_media.prompt_builder import LogoPrompt, Provider, Style

        prompt = LogoPrompt(
            package_name="testpkg",
            description="A test package",
            style=Style.MINIMALIST,
            color="#3498db"
        )

        providers = [
            Provider.CLAUDE,
            Provider.GEMINI,
            Provider.OPENROUTER,
            Provider.GLM,
            Provider.PERPLEXITY
        ]

        for provider in providers:
            result = prompt.build_for_provider(provider)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "testpkg" in result

    def test_diagram_prompt_flow_directions(self):
        """Test DiagramPrompt with different flow directions."""
        from portfolio_media.prompt_builder import DiagramPrompt

        flow_directions = ["LR", "TD", "BT", "RL"]

        for flow_dir in flow_directions:
            prompt = DiagramPrompt(
                package_name="testpkg",
                components=["A", "B", "C"],
                flow_direction=flow_dir
            )

            description = prompt._flow_description()
            assert isinstance(description, str)
            assert len(description) > 0

    def test_screenshot_prompt_configurations(self):
        """Test ScreenshotPrompt with various configurations."""
        from portfolio_media.prompt_builder import ScreenshotPrompt

        configurations = [
            {"url": "http://example.com"},
            {"url": "http://example.com", "width": 1920, "height": 1080},
            {"url": "http://example.com", "full_page": True},
            {"url": "http://example.com", "wait_for": ".content", "selector": "#main"}
        ]

        for config in configurations:
            prompt = ScreenshotPrompt(**config)
            capture_config = prompt.get_capture_config()

            assert isinstance(capture_config, dict)
            assert "viewport" in capture_config


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""

    def test_assessment_workflow(self, tmp_path):
        """Test complete assessment workflow."""
        from portfolio_media import AssetAssessment

        assessor = AssetAssessment(tmp_path)
        result = assessor.assess()

        assert isinstance(result, dict)
        assert "package_name" in result

        # Can save report
        report_path = tmp_path / "assessment_report.json"
        assessor.save_report(result, report_path)
        assert report_path.exists()

    @pytest.mark.asyncio
    async def test_logo_generation_workflow(self, tmp_path):
        """Test complete logo generation workflow (with mocks)."""
        from portfolio_media import LogoGenerator

        generator = LogoGenerator()

        with patch.object(list(generator.providers.values())[0], 'generate_logo', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = True

            result = await generator.generate(
                package_name="testpkg",
                description="A test package",
                output_path=tmp_path / "logo.png"
            )

            assert isinstance(result, dict)
            assert "success" in result

    @pytest.mark.asyncio
    async def test_diagram_generation_workflow(self, tmp_path):
        """Test complete diagram generation workflow (with mocks)."""
        from portfolio_media import DiagramGenerator

        generator = DiagramGenerator()

        with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
            mock_render.return_value = True

            result = await generator.generate(
                package_name="testpkg",
                components=["A", "B", "C"],
                output_path=tmp_path / "diagram.svg"
            )

            assert isinstance(result, dict)
            # Mermaid code should be saved
            assert (tmp_path / "diagram.mmd").exists()


class TestErrorHandling:
    """Test error handling across the package."""

    def test_assessment_handles_invalid_path(self):
        """Test that assessment handles invalid paths gracefully."""
        from portfolio_media import AssetAssessment, assess_package

        # Should not crash with non-existent path
        result = assess_package("/nonexistent/path/12345")

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_logo_generator_handles_unavailable_provider(self, tmp_path):
        """Test that logo generator handles unavailable providers."""
        from portfolio_media import LogoGenerator

        generator = LogoGenerator()

        # Mock a provider as unavailable
        provider_instance = list(generator.providers.values())[0]
        provider_instance.available = False

        result = await generator.generate(
            package_name="test",
            description="Test",
            output_path=tmp_path / "test.png",
            provider=list(generator.providers.keys())[0]
        )

        # Should return error, not crash
        assert isinstance(result, dict)
        assert "success" in result


class TestConstantsAndEnums:
    """Test constants and enumerations."""

    def test_provider_enum_values(self):
        """Test Provider enum has all expected values."""
        from portfolio_media.prompt_builder import Provider

        expected_values = [
            "claude", "gemini", "openrouter",
            "glm", "perplexity", "codex"
        ]

        for value in expected_values:
            assert hasattr(Provider, value.upper()) or Provider(value).value == value

    def test_style_enum_values(self):
        """Test Style enum has all expected values."""
        from portfolio_media.prompt_builder import Style

        expected_styles = [
            "minimalist", "geometric", "gradient",
            "flat", "tech", "playful"
        ]

        for style in expected_styles:
            assert Style(style).value == style


class TestTypeSafety:
    """Test type safety and type hints."""

    def test_logo_prompt_accepts_string_style(self):
        """Test that LogoPrompt accepts string style parameter."""
        from portfolio_media.prompt_builder import LogoPrompt

        # Should not raise error
        prompt = LogoPrompt(
            package_name="test",
            description="Test",
            style="minimalist"  # String instead of Style enum
        )

        assert prompt.style.value == "minimalist"

    def test_diagram_prompt_accepts_list_of_strings(self):
        """Test that DiagramPrompt accepts list of string components."""
        from portfolio_media.prompt_builder import DiagramPrompt

        # Should not raise error
        prompt = DiagramPrompt(
            package_name="test",
            components=["A", "B", "C"]
        )

        assert len(prompt.components) == 3
