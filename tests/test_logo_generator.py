"""Tests for LogoGenerator module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from portfolio_media.logo_generator import LogoGenerator


class TestLogoGenerator:
    """Test suite for LogoGenerator class."""

    def test_initialization(self):
        """Test LogoGenerator initialization."""
        generator = LogoGenerator()
        assert hasattr(generator, 'providers')
        assert isinstance(generator.providers, dict)

    def test_has_expected_providers(self):
        """Test that LogoGenerator has expected providers."""
        generator = LogoGenerator()
        # Provider names should be present
        assert len(generator.providers) > 0

    def test_generate_is_async(self):
        """Test that generate() is an async method."""
        generator = LogoGenerator()
        assert hasattr(generator, 'generate')
        # Check if it's a coroutine function
        import inspect
        assert inspect.iscoroutinefunction(generator.generate)

    @pytest.mark.asyncio
    async def test_generate_returns_dict(self, tmp_path):
        """Test that generate() returns a dictionary."""
        generator = LogoGenerator()

        # Mock the provider's generate method
        with patch.object(list(generator.providers.values())[0], 'generate_logo') as mock_generate:
            mock_generate.return_value = {"success": True, "path": tmp_path / "test.png"}

            result = await generator.generate(
                package_name="test",
                description="Test package",
                output_path=tmp_path / "output.png"
            )
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_with_minimal_params(self, tmp_path):
        """Test generate() with minimal parameters."""
        generator = LogoGenerator()

        with patch.object(list(generator.providers.values())[0], 'generate_logo') as mock_generate:
            mock_generate.return_value = {"success": True}

            result = await generator.generate(
                package_name="test",
                description="Test",
                output_path=tmp_path / "test.png"
            )
            assert "success" in result or "error" in result

    def test_generate_signature_accepts_style(self):
        """Test that generate() accepts style parameter."""
        import inspect
        generator = LogoGenerator()
        sig = inspect.signature(generator.generate)
        assert 'style' in sig.parameters

    def test_generate_signature_accepts_color(self):
        """Test that generate() accepts color parameter."""
        import inspect
        generator = LogoGenerator()
        sig = inspect.signature(generator.generate)
        assert 'color' in sig.parameters

    def test_generate_signature_accepts_provider(self):
        """Test that generate() accepts provider parameter."""
        import inspect
        generator = LogoGenerator()
        sig = inspect.signature(generator.generate)
        assert 'provider' in sig.parameters


class TestLogoGeneratorIntegration:
    """Integration tests for LogoGenerator."""

    def test_logo_generator_import(self):
        """Test that LogoGenerator can be imported."""
        from portfolio_media import LogoGenerator
        assert LogoGenerator is not None

    def test_logo_generator_instantiation(self):
        """Test that LogoGenerator can be instantiated."""
        from portfolio_media import LogoGenerator
        generator = LogoGenerator()
        assert generator is not None
