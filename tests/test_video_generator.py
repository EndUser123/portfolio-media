"""Tests for VideoGenerator module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from portfolio_media.video_generator import VideoGenerator


class TestVideoGenerator:
    """Test suite for VideoGenerator class."""

    def test_initialization(self):
        """Test VideoGenerator initialization."""
        generator = VideoGenerator()
        assert hasattr(generator, 'gpu_available')
        assert hasattr(generator, 'vram_gb')
        assert isinstance(generator.gpu_available, bool)
        assert isinstance(generator.vram_gb, (int, float))

    @patch('subprocess.run')
    def test_check_gpu(self, mock_run):
        """Test GPU detection."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="GeForce RTX 3080\n"
        )
        generator = VideoGenerator()
        assert generator.gpu_available is True

    @patch('subprocess.run')
    def test_check_gpu_no_nvidia_smi(self, mock_run):
        """Test GPU detection when nvidia-smi is not available."""
        mock_run.side_effect = FileNotFoundError()
        generator = VideoGenerator()
        assert generator.gpu_available is False

    @patch('subprocess.run')
    def test_get_vram(self, mock_run):
        """Test VRAM detection."""
        # First call for GPU check, second for VRAM
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="GeForce RTX 3080\n"),
            MagicMock(returncode=0, stdout="10240\n")
        ]
        generator = VideoGenerator()
        assert generator.vram_gb > 0
        # VRAM should be around 10GB (10240 MB / 1024)
        assert 9 < generator.vram_gb < 11

    def test_check_installation_returns_dict(self):
        """Test that check_installation() returns a dictionary."""
        generator = VideoGenerator()
        result = generator.check_installation()

        assert isinstance(result, dict)
        assert "gpu" in result
        assert "cogvideox" in result
        assert "opensora" in result
        assert "openrouter" in result
        assert "notebooklm" in result
        assert "ffmpeg" in result
        assert "recommended" in result

    def test_check_installation_gpu_info(self):
        """Test that check_installation() includes GPU info."""
        generator = VideoGenerator()
        result = generator.check_installation()

        gpu_info = result["gpu"]
        assert "available" in gpu_info
        assert "vram_gb" in gpu_info

    def test_check_installation_recommended_backend(self):
        """Test that check_installation() recommends appropriate backend."""
        generator = VideoGenerator()
        result = generator.check_installation()

        assert "recommended" in result
        assert result["recommended"] in ["notebooklm", "cogvideox", "opensora", "openrouter"]


class TestVideoGeneratorProviders:
    """Test suite for video generation providers."""

    @patch('shutil.which')
    def test_check_notebooklm_with_cli(self, mock_which):
        """Test NotebookLM detection when CLI is available."""
        mock_which.return_value = "/usr/bin/nlm"

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            generator = VideoGenerator()
            result = generator.check_installation()

            notebooklm_info = result["notebooklm"]
            assert notebooklm_info["available"] is True

    @patch('shutil.which')
    def test_check_notebooklm_without_cli(self, mock_which):
        """Test NotebookLM detection when CLI is not available."""
        mock_which.return_value = None

        generator = VideoGenerator()
        result = generator.check_installation()

        notebooklm_info = result["notebooklm"]
        assert notebooklm_info["available"] is False
        assert "install_command" in notebooklm_info

    def test_check_openrouter(self):
        """Test OpenRouter API key detection."""
        generator = VideoGenerator()
        result = generator.check_installation()

        openrouter_info = result["openrouter"]
        assert "available" in openrouter_info
        assert "env_var" in openrouter_info

    @patch('shutil.which')
    def test_check_ffmpeg_available(self, mock_which):
        """Test ffmpeg detection when available."""
        mock_which.return_value = "/usr/bin/ffmpeg"

        generator = VideoGenerator()
        result = generator.check_installation()

        ffmpeg_info = result["ffmpeg"]
        assert ffmpeg_info["installed"] is True

    @patch('shutil.which')
    def test_check_ffmpeg_not_available(self, mock_which):
        """Test ffmpeg detection when not available."""
        mock_which.return_value = None

        generator = VideoGenerator()
        result = generator.check_installation()

        ffmpeg_info = result["ffmpeg"]
        assert ffmpeg_info["installed"] is False
        assert "install_command" in ffmpeg_info


class TestVideoGeneratorGenerate:
    """Test suite for video generation."""

    @pytest.mark.asyncio
    async def test_generate_returns_dict(self, tmp_path):
        """Test that generate() returns a dictionary."""
        generator = VideoGenerator()

        with patch.object(generator, 'check_installation') as mock_check:
            mock_check.return_value = {"recommended": "openrouter"}
            with patch.object(generator, '_generate_openrouter', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = {"success": True, "output_path": str(tmp_path / "test.mp4")}

                result = await generator.generate(
                    package_name="test",
                    description="Test package",
                    output_path=tmp_path / "test.mp4"
                )

                assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_with_auto_backend(self, tmp_path):
        """Test that generate() with backend='auto' selects appropriate backend."""
        generator = VideoGenerator()

        with patch.object(generator, 'check_installation') as mock_check:
            mock_check.return_value = {"recommended": "notebooklm"}
            with patch.object(generator, '_generate_notebooklm', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = {"success": True, "output_path": str(tmp_path / "test.mp4")}

                await generator.generate(
                    package_name="test",
                    description="Test package",
                    output_path=tmp_path / "test.mp4",
                    backend="auto"
                )

                # Should call the recommended backend
                mock_gen.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_custom_prompt(self, tmp_path):
        """Test that generate() uses custom prompt when provided."""
        generator = VideoGenerator()
        custom_prompt = "A custom video prompt"

        with patch.object(generator, 'check_installation') as mock_check:
            mock_check.return_value = {"recommended": "openrouter"}
            with patch.object(generator, '_generate_openrouter', new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = {"success": True}

                await generator.generate(
                    package_name="test",
                    description="Test package",
                    output_path=tmp_path / "test.mp4",
                    prompt=custom_prompt
                )

                # Check that custom prompt was used
                call_args = mock_gen.call_args
                assert call_args[0][0] == custom_prompt

    @pytest.mark.asyncio
    async def test_generate_unknown_backend(self, tmp_path):
        """Test that generate() handles unknown backend gracefully."""
        generator = VideoGenerator()

        result = await generator.generate(
            package_name="test",
            description="Test package",
            output_path=tmp_path / "test.mp4",
            backend="unknown_backend"
        )

        assert result["success"] is False
        assert "error" in result
        assert "unknown" in result["error"].lower()

    def test_generate_prompt_generation(self):
        """Test _generate_prompt() creates appropriate prompt."""
        generator = VideoGenerator()

        prompt = generator._generate_prompt(
            package_name="testpkg",
            description="A testing toolkit"
        )

        assert isinstance(prompt, str)
        assert "testpkg" in prompt
        assert "testing toolkit" in prompt


class TestVideoGeneratorBackends:
    """Test suite for specific backends."""

    @pytest.mark.asyncio
    async def test_generate_cogvideox_without_gpu(self, tmp_path):
        """Test _generate_cogvideox() fails gracefully without GPU."""
        generator = VideoGenerator()
        generator.gpu_available = False

        result = await generator._generate_cogvideox(
            prompt="Test prompt",
            output_path=tmp_path / "test.mp4"
        )

        assert result["success"] is False
        assert "GPU" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_cogvideox_missing_dependencies(self, tmp_path):
        """Test _generate_cogvideox() handles missing dependencies."""
        generator = VideoGenerator()
        generator.gpu_available = True

        # Will fail due to missing torch/diffusers
        result = await generator._generate_cogvideox(
            prompt="Test prompt",
            output_path=tmp_path / "test.mp4"
        )

        # Should handle ImportError gracefully
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_generate_opensora_without_gpu(self, tmp_path):
        """Test _generate_opensora() fails gracefully without GPU."""
        generator = VideoGenerator()
        generator.gpu_available = False

        result = await generator._generate_opensora(
            prompt="Test prompt",
            output_path=tmp_path / "test.mp4"
        )

        assert result["success"] is False
        assert "GPU" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_openrouter_no_api_key(self, tmp_path):
        """Test _generate_openrouter() handles missing API key."""
        generator = VideoGenerator()

        with patch.dict('os.environ', {}, clear=False):
            # Remove OPENROUTER_API_KEY if it exists
            os.environ.pop('OPENROUTER_API_KEY', None)

            result = await generator._generate_openrouter(
                prompt="Test prompt",
                output_path=tmp_path / "test.mp4"
            )

            assert result["success"] is False
            assert "API key" in result.get("error", "")

    @pytest.mark.asyncio
    async def test_generate_notebooklm_unavailable(self, tmp_path):
        """Test _generate_notebooklm() handles unavailable provider."""
        generator = VideoGenerator()

        with patch('portfolio_media.video_generator.NotebookLMProvider') as mock_provider:
            mock_instance = MagicMock()
            mock_instance.available = False
            mock_provider.return_value = mock_instance

            result = await generator._generate_notebooklm(
                package_name="test",
                description="Test package",
                readme_path=None,
                output_path=tmp_path / "test.mp4"
            )

            assert result["success"] is False
            assert "not available" in result["error"].lower()


class TestVideoGeneratorCli:
    """Test suite for CLI functionality."""

    @pytest.mark.asyncio
    async def test_generate_demo_video(self, tmp_path):
        """Test generate_demo_video() convenience function."""
        with patch('portfolio_media.video_generator.VideoGenerator.generate') as mock_gen:
            mock_gen.return_value = {
                "success": True,
                "output_path": str(tmp_path / "demo.mp4")
            }

            from portfolio_media.video_generator import generate_demo_video

            result = await generate_demo_video(
                package_name="test",
                description="Test package",
                output_path=str(tmp_path / "demo.mp4")
            )

            assert result["success"] is True
            mock_gen.assert_called_once()


class TestVideoGeneratorIntegration:
    """Integration tests for VideoGenerator."""

    def test_video_generator_import(self):
        """Test that VideoGenerator can be imported."""
        from portfolio_media import VideoGenerator
        assert VideoGenerator is not None

    def test_video_generator_instantiation(self):
        """Test that VideoGenerator can be instantiated."""
        from portfolio_media import VideoGenerator
        generator = VideoGenerator()
        assert generator is not None

    def test_get_gpu_name(self):
        """Test _get_gpu_name() method."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="GeForce RTX 3080\n"
            )

            generator = VideoGenerator()
            name = generator._get_gpu_name()

            assert name == "GeForce RTX 3080"

    def test_get_gpu_name_no_gpu(self):
        """Test _get_gpu_name() when no GPU is available."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()

            generator = VideoGenerator()
            name = generator._get_gpu_name()

            assert name is None

    def test_get_ffmpeg_cmd(self):
        """Test _get_ffmpeg_cmd() returns command when available."""
        generator = VideoGenerator()

        with patch('shutil.which') as mock_which:
            mock_which.return_value = "/usr/bin/ffmpeg"

            cmd = generator._get_ffmpeg_cmd()
            assert cmd is not None
            assert "ffmpeg" in cmd

    def test_get_ffmpeg_cmd_not_available(self):
        """Test _get_ffmpeg_cmd() returns None when ffmpeg not available."""
        generator = VideoGenerator()

        with patch('shutil.which') as mock_which:
            mock_which.return_value = None

            cmd = generator._get_ffmpeg_cmd()
            assert cmd is None
