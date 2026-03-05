"""Tests for CLI module."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from portfolio_media.cli import main, _get_env_var, _ensure_env_vars


class TestEnvVarHelpers:
    """Test suite for environment variable helper functions."""

    def test_get_env_var_with_value(self):
        """Test _get_env_var() when environment variable is set."""
        # Set a test environment variable
        os.environ['TEST_VAR_KEY'] = 'test_value'

        result = _get_env_var('TEST_VAR_KEY')
        assert result == 'test_value'

        # Clean up
        del os.environ['TEST_VAR_KEY']

    def test_get_env_var_without_value(self):
        """Test _get_env_var() when environment variable is not set."""
        result = _get_env_var('NONEXISTENT_VAR_12345')
        assert result is None

    def test_ensure_env_vars_does_not_crash(self):
        """Test that _ensure_env_vars() runs without crashing."""
        # Should not raise any exceptions
        _ensure_env_vars()


class TestMainCli:
    """Test suite for main CLI entry point."""

    def test_main_without_args(self, capsys):
        """Test main() without arguments shows help."""
        with patch('sys.argv', ['portfolio-media']):
            result = main()
            # Should show help and return non-zero
            assert result != 0

    def test_main_with_help(self, capsys):
        """Test main() --help shows help text."""
        with patch('sys.argv', ['portfolio-media', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # --help causes SystemExit(0)
            assert exc_info.value.code == 0


class TestLogoCommand:
    """Test suite for logo command."""

    @patch('portfolio_media.cli.LogoGenerator')
    @patch('portfolio_media.cli.asyncio.run')
    def test_run_logo_command_success(self, mock_run, mock_generator, capsys):
        """Test run_logo_command() success case."""
        # Mock successful generation
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate = AsyncMock(return_value={
            "success": True,
            "output_path": "test.png"
        })
        mock_generator.return_value = mock_gen_instance
        mock_run.return_value = 0

        from portfolio_media.cli import run_logo_command

        args = Mock(
            package="testpkg",
            description="A test package",
            output="test.png",
            style="minimalist",
            color=None,
            provider="gemini",
            variations=None
        )

        result = run_logo_command(args)

        captured = capsys.readouterr()
        # Should indicate success
        assert result == 0

    @patch('portfolio_media.cli.LogoGenerator')
    @patch('portfolio_media.cli.asyncio.run')
    def test_run_logo_command_failure(self, mock_run, mock_generator, capsys):
        """Test run_logo_command() failure case."""
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate = AsyncMock(return_value={
            "success": False,
            "error": "Test error"
        })
        mock_generator.return_value = mock_gen_instance
        mock_run.return_value = 1

        from portfolio_media.cli import run_logo_command

        args = Mock(
            package="testpkg",
            description="A test package",
            output="test.png",
            style="minimalist",
            color=None,
            provider="gemini",
            variations=None
        )

        result = run_logo_command(args)

        # Should return non-zero on failure
        assert result == 1


class TestDiagramCommand:
    """Test suite for diagram command."""

    @patch('portfolio_media.cli.DiagramGenerator')
    @patch('portfolio_media.cli.asyncio.run')
    def test_run_diagram_command_success(self, mock_run, mock_generator, capsys):
        """Test run_diagram_command() success case."""
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate = AsyncMock(return_value={
            "success": True,
            "svg_path": "test.svg",
            "mmd_path": "test.mmd"
        })
        mock_generator.return_value = mock_gen_instance
        mock_run.return_value = 0

        from portfolio_media.cli import run_diagram_command

        args = Mock(
            package="testpkg",
            components="A,B,C",
            output="test.svg",
            title="Architecture",
            flow="TD",
            code_only=False
        )

        result = run_diagram_command(args)

        assert result == 0

    @patch('portfolio_media.cli.DiagramGenerator')
    @patch('portfolio_media.cli.asyncio.run')
    def test_run_diagram_command_with_code_only(self, mock_run, mock_generator):
        """Test run_diagram_command() with --code-only."""
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate = AsyncMock(return_value={
            "success": True,
            "mmd_path": "test.mmd"
        })
        mock_generator.return_value = mock_gen_instance
        mock_run.return_value = 0

        from portfolio_media.cli import run_diagram_command

        args = Mock(
            package="testpkg",
            components="A,B,C",
            output="test.svg",
            title="Architecture",
            flow="TD",
            code_only=True
        )

        result = run_diagram_command(args)

        assert result == 0


class TestScreenshotCommand:
    """Test suite for screenshot command."""

    @patch('portfolio_media.cli.ScreenshotCapture')
    def test_run_screenshot_command_success(self, mock_capture, capsys):
        """Test run_screenshot_command() success case."""
        mock_capture_instance = MagicMock()
        mock_capture_instance.capture_url.return_value = {
            "success": True,
            "output_path": "test.png"
        }
        mock_capture.return_value = mock_capture_instance

        from portfolio_media.cli import run_screenshot_command

        args = Mock(
            url="http://example.com",
            output="test.png",
            width=1280,
            height=720,
            wait_for=None,
            full_page=False,
            selector=None
        )

        result = run_screenshot_command(args)

        assert result == 0

    @patch('portfolio_media.cli.ScreenshotCapture')
    def test_run_screenshot_command_failure(self, mock_capture, capsys):
        """Test run_screenshot_command() failure case."""
        mock_capture_instance = MagicMock()
        mock_capture_instance.capture_url.return_value = {
            "success": False,
            "error": "Browser error"
        }
        mock_capture.return_value = mock_capture_instance

        from portfolio_media.cli import run_screenshot_command

        args = Mock(
            url="http://example.com",
            output="test.png",
            width=1280,
            height=720,
            wait_for=None,
            full_page=False,
            selector=None
        )

        result = run_screenshot_command(args)

        assert result == 1


class TestVideoCommand:
    """Test suite for video command."""

    @patch('portfolio_media.cli.VideoGenerator')
    @patch('portfolio_media.cli.asyncio.run')
    def test_run_video_command_success(self, mock_run, mock_generator, capsys):
        """Test run_video_command() success case."""
        mock_gen_instance = MagicMock()
        mock_gen_instance.check_installation.return_value = {
            "gpu": {"available": False},
            "recommended": "openrouter"
        }
        mock_gen_instance.generate = AsyncMock(return_value={
            "success": True,
            "output_path": "test.mp4"
        })
        mock_generator.return_value = mock_gen_instance
        mock_run.return_value = 0

        from portfolio_media.cli import run_video_command

        args = Mock(
            package="testpkg",
            description="A test package",
            output="test.mp4",
            duration=4,
            backend="auto",
            prompt=None
        )

        result = run_video_command(args)

        assert result == 0


class TestCheckCommand:
    """Test suite for check command."""

    @patch('portfolio_media.cli.LogoGenerator')
    @patch('portfolio_media.cli.ScreenshotCapture')
    @patch('portfolio_media.cli.VideoGenerator')
    def test_run_check_command(self, mock_video, mock_screenshot, mock_logo, capsys):
        """Test run_check_command() displays status."""
        mock_logo_instance = MagicMock()
        mock_logo_instance.check_providers.return_value = {
            "gemini": {"available": True},
            "openrouter": {"available": False}
        }
        mock_logo.return_value = mock_logo_instance

        mock_screenshot_instance = MagicMock()
        mock_screenshot_instance.check_installation.return_value = {
            "installed": False,
            "install_command": "pip install playwright"
        }
        mock_screenshot.return_value = mock_screenshot_instance

        mock_video_instance = MagicMock()
        mock_video_instance.check_installation.return_value = {
            "gpu": {"available": False},
            "recommended": "openrouter",
            "cogvideox": {"available": False},
            "opensora": {"available": False},
            "openrouter": {"available": False}
        }
        mock_video.return_value = mock_video_instance

        from portfolio_media.cli import run_check_command

        result = run_check_command()

        captured = capsys.readouterr()
        assert "Provider Status" in captured.out
        assert result == 0


class TestAssessCommand:
    """Test suite for assess command."""

    @patch('portfolio_media.cli.AssetAssessment')
    def test_run_assess_command(self, mock_assessment, tmp_path, capsys):
        """Test run_assess_command() generates assessment."""
        mock_assessment_instance = MagicMock()
        mock_assessment_instance.assess.return_value = {
            "package_name": "testpkg",
            "quality_score": 50,
            "assets_missing": ["logo", "diagrams"],
            "recommendations": []
        }
        mock_assessment.return_value = mock_assessment_instance

        from portfolio_media.cli import run_assess_command

        args = Mock(
            path=str(tmp_path),
            output=None,
            quiet=False
        )

        result = run_assess_command(args)

        # Should print report
        assert result == 1  # Missing required assets

    @patch('portfolio_media.cli.AssetAssessment')
    def test_run_assess_command_quiet(self, mock_assessment, tmp_path, capsys):
        """Test run_assess_command() with --quiet flag."""
        mock_assessment_instance = MagicMock()
        mock_assessment_instance.assess.return_value = {
            "package_name": "testpkg",
            "quality_score": 100,
            "assets_missing": [],
            "recommendations": []
        }
        mock_assessment.return_value = mock_assessment_instance

        from portfolio_media.cli import run_assess_command

        args = Mock(
            path=str(tmp_path),
            output=None,
            quiet=True
        )

        result = run_assess_command(args)

        captured = capsys.readouterr()
        # Should only print score
        assert "100" in captured.out
        assert result == 0


class TestGenerateCommand:
    """Test suite for generate command."""

    @patch('portfolio_media.cli.AssetAssessment')
    @patch('portfolio_media.cli.execute_generation')
    def test_run_generate_command_dry_run(self, mock_execute, mock_assessment, tmp_path, capsys):
        """Test run_generate_command() with --dry-run."""
        mock_assessment_instance = MagicMock()
        mock_assessment_instance.assess.return_value = {
            "package_name": "testpkg",
            "quality_score": 50,
            "assets_missing": ["logo"],
            "recommendations": [
                {"asset": "logo", "priority": "high", "action": "Generate logo", "command": "test"}
            ]
        }
        mock_assessment.return_value = mock_assessment_instance

        from portfolio_media.cli import run_generate_command

        args = Mock(
            path=str(tmp_path),
            report=None,
            package="testpkg",
            description="A test package",
            components="A,B,C",
            url="http://example.com",
            provider="gemini",
            dry_run=True
        )

        result = run_generate_command(args)

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        # execute_generation should not be called in dry-run mode
        mock_execute.assert_not_called()


class TestExtractDescription:
    """Test suite for extract_description_from_readme()."""

    def test_extract_from_readme(self, tmp_path):
        """Test extracting description from README."""
        readme_content = """# Test Package

This is a testing toolkit for developers.

## Installation

Run `pip install test-package`
"""
        readme_path = tmp_path / "README.md"
        readme_path.write_text(readme_content)

        from portfolio_media.cli import extract_description_from_readme

        result = extract_description_from_readme(tmp_path)

        assert result is not None
        assert "testing toolkit" in result.lower()

    def test_extract_from_missing_readme(self, tmp_path):
        """Test extracting description when README doesn't exist."""
        from portfolio_media.cli import extract_description_from_readme

        result = extract_description_from_readme(tmp_path)

        assert result is None

    def test_extract_skips_headers(self, tmp_path):
        """Test that extract_description skips headers."""
        readme_content = """# Test Package

[![Build Status](badge.svg)]

This is the actual description.

## Features
"""
        readme_path = tmp_path / "README.md"
        readme_path.write_text(readme_content)

        from portfolio_media.cli import extract_description_from_readme

        result = extract_description_from_readme(tmp_path)

        assert result is not None
        # Should skip the header and badge
        assert "actual description" in result.lower()


class TestCliIntegration:
    """Integration tests for CLI."""

    def test_cli_imports(self):
        """Test that CLI module can be imported."""
        from portfolio_media.cli import (
            main,
            run_logo_command,
            run_diagram_command,
            run_screenshot_command,
            run_video_command,
            run_check_command,
            run_assess_command,
            run_generate_command
        )
        assert main is not None
        assert run_logo_command is not None
        assert run_diagram_command is not None
        assert run_screenshot_command is not None
        assert run_video_command is not None
        assert run_check_command is not None
        assert run_assess_command is not None
        assert run_generate_command is not None

    def test_cli_argparse_setup(self):
        """Test that CLI argument parser is set up correctly."""
        from portfolio_media.cli import main
        import argparse

        # Main function should create parser without crashing
        # We can't easily test the full parser, but we can check it exists
        assert callable(main)
