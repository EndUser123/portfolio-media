"""Asset assessor for portfolio-media.

Scans packages to identify missing visual assets and provides recommendations.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class AssetAssessment:
    """Assess package visual assets and identify gaps.

    Scans for:
    - Logo (logo.png, logo.svg)
    - Banner (banner.png)
    - Architecture diagrams (diagrams/*.svg)
    - Screenshots (screenshots/*.png)
    - Demo videos (videos/*.mp4)
    """

    ASSET_STRUCTURE = {
        "logo": {
            "paths": ["assets/logo/logo.png", "assets/logo/logo.svg", "logo.png"],
            "required": True,
            "description": "Package logo for GitHub avatar"
        },
        "banner": {
            "paths": ["assets/banners/banner.png", "assets/banner.png"],
            "required": False,
            "description": "README header banner"
        },
        "diagrams": {
            "paths": ["assets/diagrams/*.svg", "assets/diagrams/*.mmd", "diagrams/"],
            "required": False,
            "description": "Architecture diagrams"
        },
        "screenshots": {
            "paths": ["assets/screenshots/*.png", "screenshots/*.png"],
            "required": False,
            "description": "Documentation screenshots"
        },
        "videos": {
            "paths": ["assets/videos/*.mp4", "videos/*.mp4"],
            "required": False,
            "description": "Demo videos"
        }
    }

    def __init__(self, package_path: Optional[Path] = None):
        self.package_path = (package_path or Path.cwd()).resolve()

    def assess(self, package_path: Optional[Path] = None) -> Dict[str, Any]:
        """Perform full asset assessment.

        Args:
            package_path: Path to package (defaults to cwd)

        Returns:
            Assessment dict with gaps and recommendations
        """
        if package_path:
            self.package_path = package_path.resolve()

        results = {
            "package_path": str(self.package_path),
            "package_name": self.package_path.name,
            "assets_present": {},
            "assets_missing": [],
            "quality_score": 0,
            "recommendations": [],
            "readme_mentions": self._check_readme_mentions()
        }

        # Check each asset type
        for asset_type, config in self.ASSET_STRUCTURE.items():
            found = self._check_asset_type(config["paths"])
            results["assets_present"][asset_type] = found

            if not found and config["required"]:
                results["assets_missing"].append(asset_type)

        # Calculate quality score
        results["quality_score"] = self._calculate_score(results)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _check_asset_type(self, paths: List[str]) -> bool:
        """Check if any of the given paths exist.

        Args:
            paths: List of glob patterns or direct paths

        Returns:
            True if any path exists
        """
        for pattern in paths:
            # Handle glob patterns
            if "*" in pattern:
                matches = list(self.package_path.glob(pattern))
                if matches:
                    return True
            else:
                # Direct path check
                target = self.package_path / pattern
                if target.exists():
                    return True
        return False

    def _check_readme_mentions(self) -> Dict[str, bool]:
        """Check if README mentions visual assets.

        Returns:
            Dict with True/False for each asset mention type
        """
        readme_path = self.package_path / "README.md"
        if not readme_path.exists():
            return {}

        content = readme_path.read_text()

        return {
            "mentions_logo": any(term in content.lower() for term in ["logo", "avatar", "icon"]),
            "mentions_diagram": any(term in content.lower() for term in ["diagram", "architecture"]),
            "mentions_screenshot": any(term in content.lower() for term in ["screenshot", "example", "demo"]),
            "mentions_video": "video" in content.lower() or "youtube" in content.lower()
        }

    def _calculate_score(self, results: Dict[str, Any]) -> int:
        """Calculate asset quality score (0-100).

        Scoring:
        - Logo (required): 40 points
        - Banner: 10 points
        - Diagrams: 20 points
        - Screenshots: 20 points
        - Videos: 10 points
        """
        score = 0

        if results["assets_present"].get("logo"):
            score += 40
        if results["assets_present"].get("banner"):
            score += 10
        if results["assets_present"].get("diagrams"):
            score += 20
        if results["assets_present"].get("screenshots"):
            score += 20
        if results["assets_present"].get("videos"):
            score += 10

        return score

    def _extract_description_from_readme(self) -> str:
        """Extract package description from README.

        Returns:
            Description text or placeholder
        """
        readme_path = self.package_path / "README.md"
        if not readme_path.exists():
            return "A toolkit for developers"

        content = readme_path.read_text()

        # Look for first sentence/paragraph after badges
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            # Skip headers, empty lines, badges, HTML
            if (line and
                not line.startswith("#") and
                not line.startswith("[") and
                not line.startswith("<") and
                not line.startswith("!--") and
                len(line) > 15):  # Must be meaningful
                # Return first meaningful line (up to 200 chars)
                desc = line[:200] + ("..." if len(line) > 200 else "")
                # Clean up common markdown artifacts
                desc = desc.replace("**", "").replace("*", "").replace(">", "").strip()
                return desc

        return "A toolkit for developers"

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate prioritized recommendations.

        Returns:
            List of recommendation dicts with priority, action, command
        """
        recommendations = []
        pkg = results["package_name"]
        description = self._extract_description_from_readme()

        # Logo (highest priority if missing)
        if not results["assets_present"].get("logo"):
            recommendations.append({
                "priority": "HIGH",
                "asset": "logo",
                "action": "Generate package logo",
                "command": f'/portfolio-media logo --package "{pkg}" --description "{description}" --output assets/logo/logo.png'
            })

        # Diagrams
        if not results["assets_present"].get("diagrams"):
            recommendations.append({
                "priority": "MEDIUM",
                "asset": "diagrams",
                "action": "Generate architecture diagram",
                "command": f'/portfolio-media diagram --package "{pkg}" --components "Main,Analyzer,Reporter" --output assets/diagrams/architecture.svg'
            })

        # Screenshots
        if not results["assets_present"].get("screenshots"):
            recommendations.append({
                "priority": "MEDIUM",
                "asset": "screenshots",
                "action": "Capture documentation screenshots",
                "command": '/portfolio-media screenshot --url http://localhost:8000 --output assets/screenshots/home.png'
            })

        # Banner
        if not results["assets_present"].get("banner"):
            recommendations.append({
                "priority": "LOW",
                "asset": "banner",
                "action": "Generate README banner",
                "command": f'/portfolio-media logo --package "{pkg}" --description "{description}" --output assets/banners/banner.png --style gradient'
            })

        return recommendations

    def print_report(self, results: Dict[str, Any]) -> None:
        """Print assessment report to console.

        Args:
            results: Assessment results from assess()
        """
        print(f"\n{'='*60}")
        print(f"Asset Assessment: {results['package_name']}")
        print(f"{'='*60}")
        print(f"Path: {results['package_path']}")
        print(f"\nQuality Score: {results['quality_score']}/100")

        # Assets present
        print("\nAssets Present:")
        for asset_type, present in results["assets_present"].items():
            icon = "✓" if present else "✗"
            req = " (required)" if self.ASSET_STRUCTURE[asset_type]["required"] else ""
            print(f"  {icon} {asset_type.capitalize()}{req}")

        # README mentions
        if results.get("readme_mentions"):
            print("\nREADME Mentions:")
            for mention_type, present in results["readme_mentions"].items():
                icon = "✓" if present else "✗"
                print(f"  {icon} {mention_type.replace('_', ' ').title()}")

        # Recommendations
        if results["recommendations"]:
            print("\nRecommendations:")
            for i, rec in enumerate(results["recommendations"], 1):
                priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
                print(f"\n  {i}. {priority_icon} [{rec['priority']}] {rec['action']}")
                print(f"     Command: {rec['command']}")

        print(f"\n{'='*60}\n")

    def save_report(self, results: Dict[str, Any], output_path: Path) -> None:
        """Save assessment report to JSON.

        Args:
            results: Assessment results
            output_path: Where to save the report
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2))

    def load_report(self, report_path: Path) -> Dict[str, Any]:
        """Load assessment report from JSON.

        Args:
            report_path: Path to report file

        Returns:
            Assessment results dict
        """
        return json.loads(report_path.read_text())


def assess_package(package_path: str = ".") -> Dict[str, Any]:
    """Quick assessment function.

    Args:
        package_path: Path to package

    Returns:
        Assessment results
    """
    assessor = AssetAssessment(Path(package_path))
    return assessor.assess()
