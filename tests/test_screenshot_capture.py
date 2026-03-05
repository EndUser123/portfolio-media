"""Tests for ScreenshotCapture module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from portfolio_media.screenshot_capture import ScreenshotCapture, PLAYWRIGHT_AVAILABLE


class TestScreenshotCapture:
    """Test suite for ScreenshotCapture class."""

    def test_initialization(self):
        """Test ScreenshotCapture initialization."""
        capture = ScreenshotCapture()
        assert hasattr(capture, 'available')
        assert capture.available == PLAYWRIGHT_AVAILABLE

    def test_capture_url_returns_dict(self, tmp_path):
        """Test that capture_url() returns a dictionary."""
        capture = ScreenshotCapture()

        if not PLAYWRIGHT_AVAILABLE:
            # Should return error dict when Playwright not available
            result = capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png"
            )
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "error" in result

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_creates_directory(self, mock_playwright, tmp_path):
        """Test that capture_url() creates output directory."""
        # Mock successful capture
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        capture = ScreenshotCapture()
        output_path = tmp_path / "subdir" / "test.png"

        # Only run if Playwright is available
        if PLAYWRIGHT_AVAILABLE:
            result = capture.capture_url(
                url="http://example.com",
                output_path=output_path
            )
            assert output_path.parent.exists()

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_sets_viewport(self, mock_playwright, tmp_path):
        """Test that capture_url() sets correct viewport dimensions."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png",
                width=1920,
                height=1080
            )

            # Check that new_page was called with viewport
            mock_browser.new_page.assert_called()
            call_kwargs = mock_browser.new_page.call_args[1]
            assert call_kwargs["viewport"]["width"] == 1920
            assert call_kwargs["viewport"]["height"] == 1080

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_navigates_to_url(self, mock_playwright, tmp_path):
        """Test that capture_url() navigates to the specified URL."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            test_url = "http://example.com"
            capture.capture_url(
                url=test_url,
                output_path=tmp_path / "test.png"
            )

            # Check that goto was called with the URL
            mock_page.goto.assert_called()
            call_args = mock_page.goto.call_args
            assert test_url in str(call_args)

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_handles_wait_for_selector(self, mock_playwright, tmp_path):
        """Test that capture_url() waits for selector when specified."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png",
                wait_for=".loaded-content"
            )

            # Check that wait_for_selector was called
            mock_page.wait_for_selector.assert_called_with(".loaded-content", timeout=30000)

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_full_page_screenshot(self, mock_playwright, tmp_path):
        """Test that capture_url() captures full page when requested."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png",
                full_page=True
            )

            # Check that screenshot was called with full_page=True
            mock_page.screenshot.assert_called()
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("full_page") is True

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_element_screenshot(self, mock_playwright, tmp_path):
        """Test that capture_url() captures element when selector provided."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_element = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.locator.return_value = mock_element

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png",
                selector="#main-content"
            )

            # Check that element screenshot was taken
            mock_page.locator.assert_called_with("#main-content")
            mock_element.screenshot.assert_called()

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_capture_url_handles_exceptions(self, mock_playwright, tmp_path):
        """Test that capture_url() handles exceptions gracefully."""
        mock_playwright.side_effect = Exception("Browser error")

        capture = ScreenshotCapture()

        if PLAYWRIGHT_AVAILABLE:
            result = capture.capture_url(
                url="http://example.com",
                output_path=tmp_path / "test.png"
            )

            assert result["success"] is False
            assert "error" in result


class TestScreenshotCaptureMultiple:
    """Test suite for multiple screenshot capture."""

    def test_capture_multiple_returns_list(self, tmp_path):
        """Test that capture_multiple() returns a list of results."""
        capture = ScreenshotCapture()

        urls = [
            ("http://example.com", tmp_path / "test1.png"),
            ("http://example.org", tmp_path / "test2.png"),
        ]

        results = capture.capture_multiple(urls)

        assert isinstance(results, list)
        assert len(results) == len(urls)

    def test_capture_multiple_all_return_dicts(self, tmp_path):
        """Test that all results from capture_multiple() are dicts."""
        capture = ScreenshotCapture()

        urls = [
            ("http://example.com", tmp_path / "test1.png"),
        ]

        results = capture.capture_multiple(urls)

        for result in results:
            assert isinstance(result, dict)
            assert "success" in result


class TestScreenshotCaptureCliOutput:
    """Test suite for CLI output capture."""

    def test_capture_cli_output_returns_dict(self, tmp_path):
        """Test that capture_cli_output() returns a dictionary."""
        capture = ScreenshotCapture()

        result = capture.capture_cli_output(
            command=["echo", "test"],
            output_path=tmp_path / "test.png"
        )

        assert isinstance(result, dict)
        assert "success" in result

    def test_capture_cli_output_not_implemented(self, tmp_path):
        """Test that capture_cli_output() indicates not implemented."""
        capture = ScreenshotCapture()

        result = capture.capture_cli_output(
            command=["echo", "test"],
            output_path=tmp_path / "test.png"
        )

        # Terminal screenshot is not yet implemented
        assert result["success"] is False
        assert "not yet implemented" in result.get("error", "")


class TestScreenshotCaptureInstallation:
    """Test suite for installation checking."""

    def test_check_installation_returns_dict(self):
        """Test that check_installation() returns a dictionary."""
        capture = ScreenshotCapture()
        result = capture.check_installation()

        assert isinstance(result, dict)
        assert "installed" in result

    @patch('portfolio_media.screenshot_capture.sync_playwright')
    def test_check_installation_detects_playwright(self, mock_playwright):
        """Test that check_installation() detects Playwright availability."""
        mock_pw_instance = MagicMock()
        mock_browser = MagicMock()

        mock_playwright.return_value.__enter__.return_value = mock_pw_instance
        mock_pw_instance.chromium.launch.return_value = mock_browser

        capture = ScreenshotCapture()
        result = capture.check_installation()

        assert isinstance(result, dict)
        if PLAYWRIGHT_AVAILABLE:
            # Should attempt to launch browser
            assert "installed" in result

    def test_check_installation_when_unavailable(self):
        """Test check_installation() when Playwright is not available."""
        # This test validates behavior when PLAYWRIGHT_AVAILABLE is False
        capture = ScreenshotCapture()

        if not PLAYWRIGHT_AVAILABLE:
            result = capture.check_installation()
            assert result["installed"] is False
            assert "install_command" in result


class TestScreenshotCaptureCli:
    """Test suite for CLI functionality."""

    @patch('portfolio_media.screenshot_capture.ScreenshotCapture.capture_url')
    def test_capture_screenshot_cli_success(self, mock_capture, tmp_path, capsys):
        """Test capture_screenshot_cli() success case."""
        mock_capture.return_value = {
            "success": True,
            "output_path": str(tmp_path / "test.png"),
            "url": "http://example.com"
        }

        from portfolio_media.screenshot_capture import capture_screenshot_cli

        capture_screenshot_cli(
            url="http://example.com",
            output=str(tmp_path / "test.png")
        )

        captured = capsys.readouterr()
        assert "Screenshot saved" in captured.out

    @patch('portfolio_media.screenshot_capture.ScreenshotCapture.capture_url')
    def test_capture_screenshot_cli_failure(self, mock_capture, tmp_path, capsys):
        """Test capture_screenshot_cli() failure case."""
        mock_capture.return_value = {
            "success": False,
            "error": "Test error",
            "url": "http://example.com"
        }

        from portfolio_media.screenshot_capture import capture_screenshot_cli

        capture_screenshot_cli(
            url="http://example.com",
            output=str(tmp_path / "test.png")
        )

        captured = capsys.readouterr()
        assert "Failed" in captured.out

    @patch('portfolio_media.screenshot_capture.ScreenshotCapture.capture_url')
    def test_capture_screenshot_cli_passes_dimensions(self, mock_capture, tmp_path):
        """Test that capture_screenshot_cli() passes width and height."""
        mock_capture.return_value = {
            "success": True,
            "output_path": str(tmp_path / "test.png")
        }

        from portfolio_media.screenshot_capture import capture_screenshot_cli

        capture_screenshot_cli(
            url="http://example.com",
            output=str(tmp_path / "test.png"),
            width=1920,
            height=1080
        )

        # Check that capture_url was called with correct dimensions
        mock_capture.assert_called_once()
        call_kwargs = mock_capture.call_args[1]
        assert call_kwargs["width"] == 1920
        assert call_kwargs["height"] == 1080

    @patch('portfolio_media.screenshot_capture.ScreenshotCapture.capture_url')
    def test_capture_screenshot_cli_full_page(self, mock_capture, tmp_path):
        """Test that capture_screenshot_cli() passes full_page parameter."""
        mock_capture.return_value = {
            "success": True,
            "output_path": str(tmp_path / "test.png")
        }

        from portfolio_media.screenshot_capture import capture_screenshot_cli

        capture_screenshot_cli(
            url="http://example.com",
            output=str(tmp_path / "test.png"),
            full_page=True
        )

        # Check that full_page was passed
        mock_capture.assert_called_once()
        call_kwargs = mock_capture.call_args[1]
        assert call_kwargs["full_page"] is True


class TestScreenshotCaptureIntegration:
    """Integration tests for ScreenshotCapture."""

    def test_screenshot_capture_import(self):
        """Test that ScreenshotCapture can be imported."""
        from portfolio_media import ScreenshotCapture
        assert ScreenshotCapture is not None

    def test_screenshot_capture_instantiation(self):
        """Test that ScreenshotCapture can be instantiated."""
        from portfolio_media import ScreenshotCapture
        capture = ScreenshotCapture()
        assert capture is not None
