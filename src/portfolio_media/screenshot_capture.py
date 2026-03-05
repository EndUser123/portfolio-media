"""Screenshot capture using Playwright.

Automates browser screenshots for documentation.
"""

import asyncio
from pathlib import Path
from typing import Optional, List

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ScreenshotCapture:
    """Capture screenshots using Playwright.

    Usage:
        capture = ScreenshotCapture()
        capture.capture_url(
            url="http://localhost:8000",
            output_path=Path("assets/screenshots/homepage.png")
        )
    """

    def __init__(self):
        self.available = PLAYWRIGHT_AVAILABLE

    def capture_url(
        self,
        url: str,
        output_path: Path,
        width: int = 1280,
        height: int = 720,
        wait_for: Optional[str] = None,
        full_page: bool = False,
        selector: Optional[str] = None,
        timeout: int = 30000
    ) -> dict:
        """Capture a screenshot of a URL.

        Args:
            url: URL to capture
            output_path: Where to save the screenshot
            width: Viewport width
            height: Viewport height
            wait_for: CSS selector to wait for before capturing
            full_page: Capture full scrollable page
            selector: CSS selector for element screenshot
            timeout: Milliseconds to wait

        Returns:
            Dict with result status
        """
        if not self.available:
            return {
                "success": False,
                "error": "Playwright not installed. Install with: pip install playwright"
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": width, "height": height}
                )

                # Navigate to URL
                page.goto(url, timeout=timeout, wait_until="networkidle")

                # Wait for specific element if requested
                if wait_for:
                    page.wait_for_selector(wait_for, timeout=timeout)

                # Capture screenshot
                screenshot_kwargs = {"path": str(output_path)}

                if selector:
                    # Element screenshot
                    element = page.locator(selector)
                    element.screenshot(**screenshot_kwargs)
                elif full_page:
                    # Full page screenshot
                    screenshot_kwargs["full_page"] = True
                    page.screenshot(**screenshot_kwargs)
                else:
                    # Viewport screenshot
                    page.screenshot(**screenshot_kwargs)

                browser.close()

            return {
                "success": True,
                "output_path": str(output_path),
                "url": url
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def capture_multiple(
        self,
        urls: List[tuple[str, Path]],
        **kwargs
    ) -> List[dict]:
        """Capture multiple screenshots.

        Args:
            urls: List of (url, output_path) tuples
            **kwargs: Additional arguments for capture_url

        Returns:
            List of result dicts
        """
        results = []

        for url, output_path in urls:
            result = self.capture_url(url, Path(output_path), **kwargs)
            results.append(result)

        return results

    def capture_cli_output(
        self,
        command: List[str],
        output_path: Path,
        width: int = 800,
        height: int = 400
    ) -> dict:
        """Capture a terminal command output as screenshot.

        This is a placeholder - would need a different approach
        (e.g., using a terminal emulator that supports screenshots).

        Args:
            command: Command to run
            output_path: Where to save
            width: Terminal width
            height: Terminal height

        Returns:
            Dict with result status
        """
        # TODO: Implement using terminal recorder or ANSI-to-image converter
        return {
            "success": False,
            "error": "Terminal screenshot not yet implemented",
            "suggestion": "Use a terminal recording tool or ANSI-to-image converter"
        }

    def check_installation(self) -> dict:
        """Check Playwright installation status."""
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "installed": False,
                "install_command": "pip install playwright && playwright install chromium"
            }

        # Check if browsers are installed
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                # Try to launch to verify browser installation
                browser = p.chromium.launch(headless=True)
                browser.close()
            return {
                "installed": True,
                "browsers_available": True
            }
        except Exception:
            return {
                "installed": True,
                "browsers_available": False,
                "install_command": "playwright install chromium"
            }


def capture_screenshot_cli(
    url: str,
    output: str,
    width: int = 1280,
    height: int = 720,
    full_page: bool = False
) -> None:
    """CLI entry point for screenshot capture.

    Usage:
        python -m portfolio_media.screenshot_capture \\
            --url http://localhost:8000 \\
            --output assets/screenshots/home.png \\
            --width 1280 \\
            --height 720
    """
    capture = ScreenshotCapture()
    result = capture.capture_url(
        url=url,
        output_path=Path(output),
        width=width,
        height=height,
        full_page=full_page
    )

    if result["success"]:
        print(f"✓ Screenshot saved: {result['output_path']}")
    else:
        print(f"✗ Failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Capture screenshots using Playwright")
    parser.add_argument("--url", required=True, help="URL to capture")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width")
    parser.add_argument("--height", type=int, default=720, help="Viewport height")
    parser.add_argument("--full-page", action="store_true", help="Capture full page")
    parser.add_argument("--wait-for", help="CSS selector to wait for")
    parser.add_argument("--selector", help="CSS selector for element screenshot")

    args = parser.parse_args()

    capture_screenshot_cli(
        url=args.url,
        output=args.output,
        width=args.width,
        height=args.height,
        full_page=args.full_page
    )
