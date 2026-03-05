"""Video Generator - Creates demo videos using local AI models or cloud APIs.

Supports:
- CogVideoX-5B (local, requires 8GB+ VRAM)
- Open-Sora 1.2 (local, requires 8-16GB VRAM)
- OpenRouter image-to-video API (cloud)
- NotebookLM Video Overviews (explainer videos from documentation)
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
import os
import shutil


class VideoGenerator:
    """Generate demo videos for GitHub packages."""

    def __init__(self):
        self.gpu_available = self._check_gpu()
        self.vram_gb = self._get_vram()

    def _check_gpu(self) -> bool:
        """Check if NVIDIA GPU is available."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _get_vram(self) -> float:
        """Get available VRAM in GB."""
        if not self.gpu_available:
            return 0

        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                mb = int(result.stdout.strip().split()[0])
                return mb / 1024
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
            pass
        return 0

    def check_installation(self) -> Dict[str, Any]:
        """Check what video generation tools are available."""
        status = {
            "gpu": {
                "available": self.gpu_available,
                "vram_gb": self.vram_gb,
                "name": self._get_gpu_name() if self.gpu_available else None
            },
            "cogvideox": self._check_cogvideox(),
            "opensora": self._check_opensora(),
            "openrouter": self._check_openrouter(),
            "notebooklm": self._check_notebooklm(),
            "ffmpeg": self._check_ffmpeg(),
        }

        # Recommend backend based on hardware
        if self._check_notebooklm().get("available"):
            status["recommended"] = "notebooklm"
        elif self.vram_gb >= 10:  # CogVideoX-5B needs ~10GB
            status["recommended"] = "cogvideox"
        elif self.vram_gb >= 6:  # CogVideoX-2B and Open-Sora need ~6GB
            status["recommended"] = "opensora"
        else:
            status["recommended"] = "openrouter"

        return status

    def _get_gpu_name(self) -> Optional[str]:
        """Get GPU name."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    def _check_cogvideox(self) -> Dict[str, Any]:
        """Check if CogVideoX is available."""
        # Check for diffusers installation
        try:
            import diffusers
            has_diffusers = True
        except ImportError:
            has_diffusers = False

        # Check for CogVideoX model cache or install script
        install_path = Path.home() / ".cache" / "huggingface" / "hub" / "models--THUDM--cogvideox-5b"
        has_model = install_path.exists()

        return {
            "available": has_diffusers,
            "model_installed": has_model,
            "install_command": "pip install diffusers transformers accelerate",
            "model_download": "huggingface-cli download THUDM/cogvideox-5b --local-dir ~/.cache/huggingface/hub/models--THUDM--cogvideox-5b"
        }

    def _check_opensora(self) -> Dict[str, Any]:
        """Check if Open-Sora is available."""
        install_path = Path.home() / "open-sora"
        pip_installed = False

        try:
            import opensora
            pip_installed = True
        except ImportError:
            pass

        return {
            "available": install_path.exists() or pip_installed,
            "install_command": "pip install opensora",
            "github": "https://github.com/hpcaitech/Open-Sora"
        }

    def _check_openrouter(self) -> Dict[str, Any]:
        """Check if OpenRouter API key is available."""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        return {
            "available": bool(api_key),
            "env_var": "OPENROUTER_API_KEY",
            "models": [
                "lumaai/photon-1.0-7b",
                "stabilityai/stable-video-diffusion"
            ]
        }

    def _check_notebooklm(self) -> Dict[str, Any]:
        """Check if NotebookLM (nlm CLI) is available."""
        if shutil.which("nlm"):
            # Check authentication
            try:
                result = subprocess.run(
                    ["nlm", "login", "--check"],
                    capture_output=True,
                    timeout=10,
                    shell=True
                )
                authenticated = result.returncode == 0
                return {
                    "available": True,
                    "authenticated": authenticated,
                    "install_command": "uv tool install notebooklm-mcp-cli"
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return {
                    "available": True,
                    "authenticated": False,
                    "install_command": "uv tool install notebooklm-mcp-cli"
                }

        return {
            "available": False,
            "install_command": "uv tool install notebooklm-mcp-cli"
        }

    def _check_ffmpeg(self) -> Dict[str, Any]:
        """Check if ffmpeg is available."""
        # Check PATH first
        if shutil.which("ffmpeg"):
            return {"installed": True, "path": "ffmpeg"}

        # Check common Windows locations
        common_paths = [
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/Program Files/Vowen/resources/app.asar.unpacked/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe"),
        ]
        for p in common_paths:
            if p.exists():
                return {"installed": True, "path": str(p)}

        return {
            "installed": False,
            "install_command": "winget install ffmpeg"
        }

    def _get_ffmpeg_cmd(self) -> Optional[str]:
        """Get the ffmpeg command to use."""
        check = self._check_ffmpeg()
        if check.get("installed"):
            return check.get("path", "ffmpeg")
        return None

    async def generate(
        self,
        package_name: str,
        description: str,
        output_path: Path,
        duration: int = 4,
        backend: str = "auto",
        prompt: Optional[str] = None,
        readme_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Generate a demo video for the package.

        Args:
            package_name: Name of the package
            description: Brief description
            output_path: Where to save the video
            duration: Video duration in seconds (for backends that support it)
            backend: "auto", "cogvideox", "opensora", "openrouter", "notebooklm"
            prompt: Custom prompt (auto-generated if not provided)
            readme_path: Path to README for NotebookLM backend

        Returns:
            Dict with success status and output path or error
        """
        # Auto-select backend
        if backend == "auto":
            status = self.check_installation()
            backend = status["recommended"]

        # Generate prompt if not provided
        if not prompt:
            prompt = self._generate_prompt(package_name, description)

        # Route to appropriate backend
        if backend == "notebooklm":
            return await self._generate_notebooklm(
                package_name=package_name,
                description=description,
                readme_path=readme_path,
                output_path=output_path
            )
        elif backend == "cogvideox":
            return await self._generate_cogvideox(prompt, output_path, duration)
        elif backend == "opensora":
            return await self._generate_opensora(prompt, output_path, duration)
        elif backend == "openrouter":
            return await self._generate_openrouter(prompt, output_path)
        else:
            return {
                "success": False,
                "error": f"Unknown backend: {backend}",
                "suggestion": f"Install {backend} or use 'openrouter' for cloud generation"
            }

    def _generate_prompt(self, package_name: str, description: str) -> str:
        """Generate a video prompt from package info."""
        return f"""A professional demo video for {package_name}, {description}.

The video shows:
- Clean terminal/command line interface
- Smooth typing animation of commands
- Professional color scheme with good contrast
- Technical aesthetics, minimalist design
- 1080p resolution, cinematic lighting

Style: Tech tutorial, professional software demonstration, clean UI."""

    async def _generate_cogvideox(
        self,
        prompt: str,
        output_path: Path,
        duration: int = 4
    ) -> Dict[str, Any]:
        """Generate video using local CogVideoX."""
        try:
            import torch
            from diffusers import CogVideoXPipeline
            from diffusers.utils import export_to_video

            # Check GPU
            if not self.gpu_available:
                return {
                    "success": False,
                    "error": "GPU required for CogVideoX",
                    "suggestion": "Use OpenRouter backend or install NVIDIA GPU"
                }

            # Check torch CUDA availability
            if not torch.cuda.is_available():
                return {
                    "success": False,
                    "error": "PyTorch CUDA not available",
                    "suggestion": "Install PyTorch with CUDA support: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118"
                }

            print(f"Loading CogVideoX-5B model (first run downloads ~10GB)...")
            print(f"VRAM available: {self.vram_gb:.1f} GB")

            # Load model with optimizations for 12GB VRAM
            pipe = CogVideoXPipeline.from_pretrained(
                "THUDM/cogvideox-5b",
                torch_dtype=torch.float16,
                use_safetensors=True
            )

            # Enable memory optimizations
            pipe.enable_model_cpu_offload()

            # Generate
            output_path.parent.mkdir(parents=True, exist_ok=True)

            num_frames = min(49, 49 * (duration // 4))  # Cap at 49 frames for VRAM
            print(f"Generating {num_frames} frames ({duration}s target)...")

            video = pipe(
                prompt=prompt,
                num_videos_per_prompt=1,
                num_inference_steps=50,
                num_frames=num_frames,
                guidance_scale=6.0,
                generator=torch.Generator("cuda").manual_seed(42)
            ).frames[0]

            # Save video
            export_to_video(video, str(output_path))

            return {
                "success": True,
                "output_path": str(output_path),
                "backend": "cogvideox",
                "frames": num_frames
            }

        except ImportError as e:
            return {
                "success": False,
                "error": f"Missing dependencies: {e}",
                "suggestion": "pip install diffusers transformers accelerate imageio-ffmpeg torch"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_opensora(
        self,
        prompt: str,
        output_path: Path,
        duration: int = 4
    ) -> Dict[str, Any]:
        """Generate video using local Open-Sora."""
        try:
            # Open-Sora uses its own CLI or Python API
            # This is a simplified wrapper
            import torch

            if not self.gpu_available:
                return {
                    "success": False,
                    "error": "GPU required for Open-Sora",
                    "suggestion": "Use OpenRouter backend"
                }

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Use Open-Sora's script if available
            opensora_path = Path.home() / "open-sora"
            if opensora_path.exists():
                script = opensora_path / "scripts" / "inference.py"
                if script.exists():
                    result = subprocess.run(
                        [
                            "python", str(script),
                            "--prompt", prompt,
                            "--num_frames", str(16 * duration),  # Open-Sora: 16 frames/sec
                            "--output", str(output_path)
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )

                    if result.returncode == 0:
                        return {
                            "success": True,
                            "output_path": str(output_path),
                            "backend": "opensora"
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.stderr or "Unknown error"
                        }

            return {
                "success": False,
                "error": "Open-Sora not found",
                "suggestion": "cd ~ && git clone https://github.com/hpcaitech/Open-Sora"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_openrouter(
        self,
        prompt: str,
        output_path: Path
    ) -> Dict[str, Any]:
        """Generate video using OpenRouter API.

        Currently OpenRouter doesn't have native video models,
        but we can use image generation and convert to slideshow video.
        """
        try:
            import requests

            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "error": "OPENROUTER_API_KEY not set",
                    "suggestion": "export OPENROUTER_API_KEY='your-key'"
                }

            # For now, generate 4 images and create a slideshow video
            # This is a fallback until OpenRouter adds true video models
            from .logo_generator import LogoGenerator

            logo_gen = LogoGenerator()

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate 4 keyframe images
            temp_dir = output_path.parent / ".temp_frames"
            temp_dir.mkdir(exist_ok=True)

            keyframes = [
                f"{prompt} - frame 1: title screen with '{prompt.split()[0]}'",
                f"{prompt} - frame 2: feature demonstration",
                f"{prompt} - frame 3: code example or interface",
                f"{prompt} - frame 4: call to action with clean design"
            ]

            for i, frame_prompt in enumerate(keyframes):
                frame_path = temp_dir / f"frame_{i:03d}.png"
                result = await logo_gen.generate(
                    package_name="frame",  # Placeholder
                    description=frame_prompt,
                    output_path=frame_path,
                    provider="openrouter"
                )
                if not result.get("success"):
                    raise Exception(f"Failed to generate frame {i}: {result.get('error')}")

            # Use ffmpeg to create slideshow
            ffmpeg_cmd = self._get_ffmpeg_cmd()
            if ffmpeg_cmd:
                subprocess.run([
                    ffmpeg_cmd, "-framerate", "1", "-i",
                    str(temp_dir / "frame_%03d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-t", "4", str(output_path)
                ], check=True, capture_output=True, shell=True)

                # Cleanup temp frames
                shutil.rmtree(temp_dir, ignore_errors=True)

                return {
                    "success": True,
                    "output_path": str(output_path),
                    "backend": "openrouter-slideshow",
                    "frames": 4
                }
            else:
                return {
                    "success": False,
                    "error": "ffmpeg required for video assembly",
                    "suggestion": "winget install ffmpeg"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_notebooklm(
        self,
        package_name: str,
        description: str,
        readme_path: Optional[Path],
        output_path: Path
    ) -> Dict[str, Any]:
        """Generate video using NotebookLM Video Overview.

        Creates an explainer video from package documentation.
        """
        from .providers.notebooklm import NotebookLMProvider

        provider = NotebookLMProvider()

        if not provider.available:
            return {
                "success": False,
                "error": "NotebookLM (nlm CLI) not available",
                "suggestion": "Install with: uv tool install notebooklm-mcp-cli && nlm login"
            }

        return await provider.generate_video(
            package_name=package_name,
            description=description,
            readme_path=readme_path,
            output_path=output_path
        )


async def generate_demo_video(
    package_name: str,
    description: str,
    output_path: str = "assets/videos/demo.mp4",
    duration: int = 4,
    backend: str = "auto"
) -> Dict[str, Any]:
    """Convenience function to generate a demo video.

    Args:
        package_name: Name of the package
        description: Brief description
        output_path: Where to save the video
        duration: Video duration in seconds
        backend: "auto", "cogvideox", "opensora", "openrouter"

    Returns:
        Dict with success status and output path
    """
    generator = VideoGenerator()
    return await generator.generate(
        package_name=package_name,
        description=description,
        output_path=Path(output_path),
        duration=duration,
        backend=backend
    )
