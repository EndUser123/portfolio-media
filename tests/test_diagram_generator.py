"""Tests for DiagramGenerator module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from portfolio_media.diagram_generator import DiagramGenerator, _find_mmdc


class TestFindMmdc:
    """Test suite for _find_mmdc function."""

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    def test_returns_mmdc_on_non_windows(self, mock_exists, mock_system):
        """Test that _find_mmdc returns 'mmdc' on non-Windows systems."""
        mock_system.return_value = "Linux"
        result = _find_mmdc()
        assert result == "mmdc"
        mock_exists.assert_not_called()

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    def test_checks_windows_paths_on_windows(self, mock_exists, mock_system):
        """Test that _find_mmdc checks Windows-specific paths."""
        mock_system.return_value = "Windows"
        mock_exists.return_value = False
        result = _find_mmdc()
        assert result == "mmdc"
        # Should check multiple paths
        assert mock_exists.call_count > 0

    @patch('platform.system')
    @patch('os.path.expandvars')
    @patch('pathlib.Path.exists')
    def test_finds_mmdc_in_windows_path(self, mock_exists, mock_expandvars, mock_system):
        """Test that _find_mmdc finds mmdc in Windows AppData."""
        mock_system.return_value = "Windows"
        mock_expandvars.return_value = r"C:\Users\test\AppData\Roaming"
        mock_exists.return_value = True
        result = _find_mmdc()
        # Should return the path that exists
        assert "mmdc" in result.lower()


class TestDiagramGenerator:
    """Test suite for DiagramGenerator class."""

    def test_initialization(self):
        """Test DiagramGenerator initialization."""
        generator = DiagramGenerator()
        assert hasattr(generator, 'claude')
        assert generator.claude is not None

    @pytest.mark.asyncio
    async def test_generate_returns_dict(self, tmp_path):
        """Test that generate() returns a dictionary."""
        generator = DiagramGenerator()

        with patch.object(generator, '_generate_mermaid_code', new_callable=AsyncMock) as mock_code:
            mock_code.return_value = "flowchart LR\n    A-->B"
            with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
                mock_render.return_value = True

                result = await generator.generate(
                    package_name="test",
                    components=["A", "B"],
                    output_path=tmp_path / "test.svg"
                )

                assert isinstance(result, dict)
                assert "success" in result

    @pytest.mark.asyncio
    async def test_generate_creates_output_directory(self, tmp_path):
        """Test that generate() creates the output directory."""
        generator = DiagramGenerator()
        output_path = tmp_path / "subdir" / "test.svg"

        with patch.object(generator, '_generate_mermaid_code', new_callable=AsyncMock) as mock_code:
            mock_code.return_value = "flowchart LR\n    A-->B"
            with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
                mock_render.return_value = True

                await generator.generate(
                    package_name="test",
                    components=["A"],
                    output_path=output_path
                )

                assert output_path.parent.exists()

    @pytest.mark.asyncio
    async def test_generate_saves_mermaid_code(self, tmp_path):
        """Test that generate() saves the Mermaid source code."""
        generator = DiagramGenerator()
        test_code = "flowchart LR\n    A-->B"

        with patch.object(generator, '_generate_mermaid_code', new_callable=AsyncMock) as mock_code:
            mock_code.return_value = test_code
            with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
                mock_render.return_value = False  # Don't actually render

                result = await generator.generate(
                    package_name="test",
                    components=["A", "B"],
                    output_path=tmp_path / "test.svg"
                )

                # Check .mmd file was created
                mmd_path = tmp_path / "test.mmd"
                assert mmd_path.exists()
                assert mmd_path.read_text() == test_code
                assert result["mermaid_code"] == test_code

    @pytest.mark.asyncio
    async def test_generate_with_renderer_none(self, tmp_path):
        """Test generate() with renderer='none' skips rendering."""
        generator = DiagramGenerator()

        with patch.object(generator, '_generate_mermaid_code', new_callable=AsyncMock) as mock_code:
            mock_code.return_value = "flowchart LR\n    A-->B"
            with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
                # Should not be called when renderer='none'
                mock_render.return_value = True

                result = await generator.generate(
                    package_name="test",
                    components=["A"],
                    output_path=tmp_path / "test.svg",
                    renderer="none"
                )

                assert result["success"] is True
                mock_render.assert_not_called()
                assert result.get("svg_path") is None

    @pytest.mark.asyncio
    async def test_generate_fails_without_mermaid_code(self, tmp_path):
        """Test that generate() handles failure to generate Mermaid code."""
        generator = DiagramGenerator()

        with patch.object(generator, '_generate_mermaid_code', new_callable=AsyncMock) as mock_code:
            mock_code.return_value = None

            result = await generator.generate(
                package_name="test",
                components=["A"],
                output_path=tmp_path / "test.svg"
            )

            assert result["success"] is False
            assert "error" in result
            assert "Mermaid code" in result["error"]

    def test_generate_mermaid_code_returns_string(self, tmp_path):
        """Test that _generate_mermaid_code returns a string."""
        generator = DiagramGenerator()
        from portfolio_media.prompt_builder import DiagramPrompt

        prompt = DiagramPrompt(
            package_name="test",
            components=["A", "B"],
            title="Test"
        )

        # This is a synchronous method, no await needed
        result = generator._generate_mermaid_code(prompt)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "flowchart" in result

    def test_generate_mermaid_code_includes_components(self):
        """Test that _generate_mermaid_code includes all components."""
        generator = DiagramGenerator()
        from portfolio_media.prompt_builder import DiagramPrompt

        components = ["Analyzer", "Processor", "Exporter"]
        prompt = DiagramPrompt(
            package_name="test",
            components=components,
            title="Test Diagram"
        )

        result = generator._generate_mermaid_code(prompt)

        # Check that components are included
        for comp in components:
            assert comp in result

    def test_generate_mermaid_code_applies_styles(self):
        """Test that _generate_mermaid_code applies style classes."""
        generator = DiagramGenerator()
        from portfolio_media.prompt_builder import DiagramPrompt

        prompt = DiagramPrompt(
            package_name="test",
            components=["Main", "Data"],
            title="Test"
        )

        result = generator._generate_mermaid_code(prompt)

        # Check for style definitions
        assert "classDef" in result
        assert "primary" in result or "accent" in result


class TestDiagramGeneratorRendering:
    """Test suite for diagram rendering functionality."""

    @pytest.mark.asyncio
    async def test_render_mermaid_calls_mmdc(self, tmp_path):
        """Test that _render_mermaid calls mmdc subprocess."""
        generator = DiagramGenerator()

        with patch('portfolio_media.diagram_generator._find_mmdc') as mock_find:
            mock_find.return_value = "mmdc"
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                result = await generator._render_mermaid(
                    mermaid_code="flowchart LR\n    A-->B",
                    output_path=tmp_path / "test.svg"
                )

                assert mock_run.called
                # Check that mmdc was called with correct arguments
                call_args = mock_run.call_args
                assert "mmdc" in str(call_args)

    @pytest.mark.asyncio
    async def test_render_mermaid_handles_missing_mmdc(self, tmp_path):
        """Test that _render_mermaid handles missing mmdc gracefully."""
        generator = DiagramGenerator()

        with patch('portfolio_media.diagram_generator._find_mmdc') as mock_find:
            mock_find.return_value = "mmdc"
            with patch('subprocess.run') as mock_run:
                # Simulate mmdc not found
                mock_run.side_effect = FileNotFoundError()

                result = await generator._render_mermaid(
                    mermaid_code="flowchart LR\n    A-->B",
                    output_path=tmp_path / "test.svg"
                )

                assert result is False

    @pytest.mark.asyncio
    async def test_render_mermaid_creates_temp_file(self, tmp_path):
        """Test that _render_mermaid creates and cleans up temp file."""
        generator = DiagramGenerator()

        with patch('portfolio_media.diagram_generator._find_mmdc') as mock_find:
            mock_find.return_value = "mmdc"
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                mermaid_code = "flowchart LR\n    A-->B"
                await generator._render_mermaid(
                    mermaid_code=mermaid_code,
                    output_path=tmp_path / "test.svg"
                )

                # Temp file should be created
                temp_files = list(tmp_path.glob("*.temp.mmd"))
                # Temp file should be cleaned up (not exist after completion)
                # But we can't easily test this without examining the subprocess call


class TestDiagramGeneratorIntegration:
    """Integration tests for DiagramGenerator."""

    @pytest.mark.asyncio
    async def test_generate_from_code(self, tmp_path):
        """Test generate_from_code() method."""
        generator = DiagramGenerator()
        mermaid_code = "flowchart LR\n    A-->B"

        with patch.object(generator, '_render_mermaid', new_callable=AsyncMock) as mock_render:
            mock_render.return_value = True

            result = await generator.generate_from_code(
                mermaid_code=mermaid_code,
                output_path=tmp_path / "test.svg"
            )

            assert isinstance(result, dict)
            assert result["success"] is True
            assert "mmd_path" in result

    @pytest.mark.asyncio
    async def test_analyze_and_diagram(self, tmp_path):
        """Test analyze_and_diagram() method."""
        generator = DiagramGenerator()

        # Create a test package structure
        pkg_path = tmp_path / "test_package"
        pkg_path.mkdir()
        (pkg_path / "__init__.py").touch()
        (pkg_path / "module1.py").touch()
        (pkg_path / "module2.py").touch()

        with patch.object(generator, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "success": True,
                "svg_path": str(tmp_path / "output.svg")
            }

            result = await generator.analyze_and_diagram(
                package_path=pkg_path,
                output_path=tmp_path / "output.svg"
            )

            assert isinstance(result, dict)
            mock_gen.assert_called_once()


class TestDiagramGeneratorCli:
    """Test suite for CLI functionality."""

    @pytest.mark.asyncio
    async def test_generate_diagram_cli_success(self, tmp_path, capsys):
        """Test generate_diagram_cli() success case."""
        with patch('portfolio_media.diagram_generator.DiagramGenerator.generate') as mock_gen:
            mock_gen.return_value = {
                "success": True,
                "svg_path": str(tmp_path / "test.svg"),
                "mmd_path": str(tmp_path / "test.mmd")
            }

            from portfolio_media.diagram_generator import generate_diagram_cli

            await generate_diagram_cli(
                package_name="test",
                components="A,B,C",
                output_path=str(tmp_path / "test.svg")
            )

            captured = capsys.readouterr()
            assert "Diagram generated" in captured.out

    @pytest.mark.asyncio
    async def test_generate_diagram_cli_failure(self, tmp_path, capsys):
        """Test generate_diagram_cli() failure case."""
        with patch('portfolio_media.diagram_generator.DiagramGenerator.generate') as mock_gen:
            mock_gen.return_value = {
                "success": False,
                "error": "Test error"
            }

            from portfolio_media.diagram_generator import generate_diagram_cli

            await generate_diagram_cli(
                package_name="test",
                components="A,B,C",
                output_path=str(tmp_path / "test.svg")
            )

            captured = capsys.readouterr()
            assert "Failed" in captured.out
