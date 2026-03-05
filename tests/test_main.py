"""Tests for portfolio_media module."""

import pytest
from pathlib import Path


def test_import():
    """Test that the main module can be imported."""
    pytest.importorskip("portfolio_media")


def test_package_structure():
    """Test that package structure is correct."""
    # Test that key directories exist
    assert Path("src").exists() or Path(module_name).exists()


def test_readme_exists():
    """Test that README.md exists."""
    assert Path("README.md").exists()


def test_pyproject_exists():
    """Test that pyproject.toml exists."""
    assert Path("pyproject.toml").exists()


def test_license_exists():
    """Test that LICENSE file exists."""
    license_files = list(Path(".").glob("LICENSE*"))
    assert len(license_files) > 0, "No LICENSE file found"


def test_gitignore_exists():
    """Test that .gitignore exists."""
    assert Path(".gitignore").exists()


def test_docs_directory_exists():
    """Test that docs/ directory exists."""
    assert Path("docs").exists()


def test_security_policy_exists():
    """Test that SECURITY.md exists."""
    assert Path("SECURITY.md").exists()


def test_contributing_guide_exists():
    """Test that CONTRIBUTING.md exists."""
    assert Path("CONTRIBUTING.md").exists()


def test_precommit_config_exists():
    """Test that .pre-commit-config.yaml exists."""
    assert Path(".pre-commit-config.yaml").exists()


def test_pytest_config_exists():
    """Test that pytest.ini exists."""
    assert Path("pytest.ini").exists()


def test_dependabot_config_exists():
    """Test that Dependabot config exists."""
    assert Path(".github/dependabot.yml").exists()


def test_basic_functionality():
    """Basic functionality test."""
    # TODO: Add actual functionality tests
    assert True


class TestPortfoliomediaPackage:
    """Test suite for package structure."""

    def test_package_metadata(self):
        """Test that package has proper metadata."""
        import tomli
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)

        assert "project" in pyproject
        assert "name" in pyproject["project"]
        assert "version" in pyproject["project"]

    def test_package_urls(self):
        """Test that project URLs are defined."""
        import tomli
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)

        assert "project" in pyproject
        assert "urls" in pyproject["project"] or "repository" in pyproject["project"]
