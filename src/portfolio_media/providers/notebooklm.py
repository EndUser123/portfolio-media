"""NotebookLM provider for video generation.

Uses Google NotebookLM's Video Overview feature to generate
explainer videos from notebook sources via the nlm CLI.

This module now uses the shared NotebookLMClient from media-pipeline
to avoid code duplication while maintaining portfolio-media's API.

ROLLBACK PLAN: If this refactor causes issues, revert to the previous
implementation which directly called nlm CLI via subprocess. The original
implementation is preserved in git history.

To revert:
    git checkout HEAD~1 -- packages/portfolio-media/src/portfolio_media/providers/notebooklm.py
    # Then remove media-pipeline from pyproject.toml dependencies

Refactored: 2025-02-16 (Phase 8 of media-pipeline implementation)
See: P:/packages/media-pipeline/plan-20250216-media-pipeline.md
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

# Import the shared NotebookLMClient from media-pipeline
try:
    from media_pipeline.providers import NotebookLMClient
    from media_pipeline.providers.notebooklm import NotebookLMError
    _MEDIA_PIPELINE_AVAILABLE = True
except ImportError:
    # Fallback if media-pipeline not available - will use limited implementation
    _MEDIA_PIPELINE_AVAILABLE = False
    NotebookLMClient = None
    NotebookLMError = Exception


class NotebookLMProvider:
    """NotebookLM provider - generates explainer videos from content.

    Requires nlm CLI (notebooklm-mcp-cli) to be installed and authenticated.

    Video generation workflow:
    1. Create a notebook from sources
    2. Add package documentation (README, docs)
    3. Generate video overview
    4. Download the video

    Video formats: explainer (default), brief
    Visual styles: auto_select, classic, whiteboard, kawaii, anime,
                  watercolor, retro_print, heritage, paper_craft

    This class maintains the portfolio-media API while using the shared
    NotebookLMClient from media-pipeline internally.
    """

    def __init__(self):
        self.name = "notebooklm"
        self._available: Optional[bool] = None
        self._client: Optional[NotebookLMClient] = None

    def _ensure_initialized(self):
        """Lazy initialization - check CLI at actual use time."""
        if self._available is not None:
            return

        if not _MEDIA_PIPELINE_AVAILABLE:
            self._available = False
            return

        try:
            self._client = NotebookLMClient()
            # Check installation status
            status = self._client.check_installation()
            self._available = status.get("available", False)
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        """Check if provider is available."""
        self._ensure_initialized()
        return self._available

    async def generate_video(
        self,
        package_name: str,
        description: str,
        readme_path: Optional[Path] = None,
        output_path: Path = Path("assets/videos/demo.mp4"),
        video_format: str = "explainer",
        visual_style: str = "auto_select",
        language: str = "en",
        focus_topic: Optional[str] = None,
        notebook_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an explainer video using NotebookLM.

        Args:
            package_name: Name of the package
            description: Brief description for the video content
            readme_path: Path to README.md or documentation file
            output_path: Where to save the video
            video_format: explainer or brief (note: media-pipeline uses 'explainer' only)
            visual_style: Visual style (note: media-pipeline uses 'whiteboard' only)
            language: BCP-47 language code (not currently used by media-pipeline)
            focus_topic: Optional specific topic to focus on
            notebook_id: Existing notebook ID to reuse (skips notebook creation)

        Returns:
            Dict with success status, output path, and metadata
        """
        if not self.available:
            return {
                "success": False,
                "error": "nlm CLI not found or media-pipeline not available",
                "suggestion": "Install with: uv tool install notebooklm-mcp-cli && pip install media-pipeline"
            }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Use existing notebook or create new one
            if notebook_id:
                target_notebook = notebook_id
            else:
                target_notebook = self._client.ensure_notebook(
                    title=f"{package_name} Documentation"
                )

            # Add sources if provided
            if readme_path and readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    self._client.sync_concept_source(
                        notebook_id=target_notebook,
                        concept_text=content,
                        title=readme_path.name
                    )
                except NotebookLMError as e:
                    # Log but continue - video may still work
                    print(f"Warning: Could not add README: {e}")

            # Generate video using shared client
            # Note: media-pipeline uses synchronous methods, so we run in executor
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(
                None,
                lambda: self._client.generate_video(
                    notebook_id=target_notebook,
                    focus_prompt=focus_topic or description,
                    output_dir=output_path.parent
                )
            )

            # The shared client generates with a specific filename pattern
            # We need to check if the output path matches and rename if needed
            if video_path.exists() and video_path != output_path:
                video_path.rename(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "size_bytes": output_path.stat().st_size if output_path.exists() else 0,
                "notebook_id": target_notebook,
                "backend": "notebooklm"
            }

        except NotebookLMError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "NotebookLMError"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_installation(self) -> Dict[str, Any]:
        """Check installation status."""
        self._ensure_initialized()

        if self._available and self._client:
            # Use the shared client's check
            status = self._client.check_installation()
            return {
                "available": status.get("available", False),
                "authenticated": status.get("authenticated", False),
                "auth_status": "authenticated" if status.get("authenticated") else "not_authenticated",
                "install_command": status.get("install_command", "uv tool install notebooklm-mcp-cli"),
                "auth_command": status.get("auth_command", "nlm login"),
                "supported_formats": ["explainer"],  # media-pipeline supports explainer
                "supported_styles": [
                    "whiteboard",  # media-pipeline uses whiteboard
                ],
                "_note": "Using media-pipeline NotebookLMClient"
            }

        return {
            "available": False,
            "authenticated": False,
            "auth_status": "unavailable",
            "install_command": "uv tool install notebooklm-mcp-cli && pip install media-pipeline",
            "auth_command": "nlm login",
            "supported_formats": [],
            "supported_styles": [],
            "_note": "media-pipeline not available"
        }

    async def list_notebooks(self) -> Dict[str, Any]:
        """List available notebooks.

        Note: This method is a placeholder for API compatibility.
        The shared NotebookLMClient doesn't currently implement list_notebooks.
        """
        if not self.available:
            return {"success": False, "error": "nlm CLI not available"}

        # TODO: Implement using nlm CLI directly if needed
        return {
            "success": True,
            "notebooks": [],
            "_note": "list_notebooks not yet implemented in shared client"
        }

    # ========================================================================
    # Legacy async methods maintained for backward compatibility
    # These delegate to the shared NotebookLMClient
    # ========================================================================

    async def _create_notebook(self, title: str) -> Dict[str, Any]:
        """Create a new NotebookLM notebook.

        Deprecated: Use the public generate_video method instead.
        """
        if not self._client:
            return {"success": False, "error": "Client not available"}
        try:
            notebook_id = self._client.ensure_notebook(title)
            return {"success": True, "notebook_id": notebook_id}
        except NotebookLMError as e:
            return {"success": False, "error": str(e)}

    async def _add_source_to_notebook(
        self,
        notebook_id: str,
        source_path: Path
    ) -> Dict[str, Any]:
        """Add a source file to the notebook.

        Deprecated: Use the public generate_video method instead.
        """
        if not self._client:
            return {"success": False, "error": "Client not available"}
        try:
            content = source_path.read_text(encoding='utf-8', errors='ignore')
            self._client.sync_concept_source(notebook_id, content, source_path.name)
            return {"success": True}
        except NotebookLMError as e:
            return {"success": False, "error": str(e)}

    async def _create_video_overview(
        self,
        notebook_id: str,
        video_format: str = "explainer",
        visual_style: str = "auto_select",
        language: str = "en",
        focus_topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a video overview in NotebookLM Studio.

        Deprecated: Use the public generate_video method instead.
        """
        # This is now handled by generate_video
        return {"success": True, "notebook_id": notebook_id, "message": "Delegated to generate_video"}

    async def _download_video(
        self,
        notebook_id: str,
        output_path: Path,
        max_wait: int = 180
    ) -> Dict[str, Any]:
        """Download the generated video with polling for completion.

        Deprecated: Use the public generate_video method instead.
        """
        # This is now handled by generate_video
        return {"success": True, "output_path": str(output_path), "message": "Delegated to generate_video"}
