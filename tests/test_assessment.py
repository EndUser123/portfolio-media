"""Tests for AssetAssessment module."""

from pathlib import Path

from portfolio_media.assessment import AssetAssessment, assess_package


class TestAssetAssessment:
    """Test suite for AssetAssessment class."""

    def test_initialization(self, tmp_path):
        """Test AssetAssessment initialization."""
        assessment = AssetAssessment(tmp_path)
        assert assessment.package_path == tmp_path

    def test_initialization_defaults_to_cwd(self):
        """Test that initialization defaults to current directory."""
        assessment = AssetAssessment()
        assert assessment.package_path == Path.cwd()

    def test_assess_returns_dict(self, tmp_path):
        """Test that assess() returns a dictionary."""
        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert isinstance(result, dict)

    def test_assess_includes_missing_assets(self, tmp_path):
        """Test that assess() identifies missing assets."""
        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert "assets_missing" in result
        assert isinstance(result["assets_missing"], list)

    def test_assess_includes_recommendations(self, tmp_path):
        """Test that assess() provides recommendations."""
        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_detects_missing_logo(self, tmp_path):
        """Test detection of missing logo asset."""
        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert "logo" in result["assets_missing"]

    def test_detects_existing_logo(self, tmp_path):
        """Test detection of existing logo asset."""
        # Create logo directory and file
        logo_dir = tmp_path / "assets" / "logo"
        logo_dir.mkdir(parents=True)
        (logo_dir / "logo.png").touch()

        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert "logo" not in result["assets_missing"]

    def test_assess_score_calculation(self, tmp_path):
        """Test that assess() calculates a completion score."""
        assessment = AssetAssessment(tmp_path)
        result = assessment.assess()
        assert "quality_score" in result
        assert 0 <= result["quality_score"] <= 100

    def test_asset_structure_constant(self):
        """Test that ASSET_STRUCTURE is properly defined."""
        assert hasattr(AssetAssessment, 'ASSET_STRUCTURE')
        assert isinstance(AssetAssessment.ASSET_STRUCTURE, dict)
        assert "logo" in AssetAssessment.ASSET_STRUCTURE
        assert "diagrams" in AssetAssessment.ASSET_STRUCTURE
        assert "screenshots" in AssetAssessment.ASSET_STRUCTURE


class TestAssessPackage:
    """Test suite for assess_package function."""

    def test_assess_package_function_exists(self):
        """Test that assess_package function exists."""
        assert callable(assess_package)

    def test_assess_package_returns_dict(self, tmp_path):
        """Test that assess_package() returns a dictionary."""
        result = assess_package(tmp_path)
        assert isinstance(result, dict)

    def test_assess_package_with_string_path(self, tmp_path):
        """Test assess_package() with string path."""
        result = assess_package(str(tmp_path))
        assert isinstance(result, dict)
