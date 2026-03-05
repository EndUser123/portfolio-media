"""Portfolio Media Generator - AI-powered visual asset generation for GitHub packages.

Generates logos, diagrams, screenshots, and demo videos using multiple LLM providers.
"""

__version__ = "0.1.0"

from .logo_generator import LogoGenerator
from .diagram_generator import DiagramGenerator
from .screenshot_capture import ScreenshotCapture
from .video_generator import VideoGenerator
from .assessment import AssetAssessment, assess_package

__all__ = [
    "LogoGenerator",
    "DiagramGenerator",
    "ScreenshotCapture",
    "VideoGenerator",
    "AssetAssessment",
    "assess_package",
]
