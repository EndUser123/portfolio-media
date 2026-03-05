"""
Basic usage example for portfolio-media media generation.

Demonstrates logo generation for a Python package.
"""

from portfolio_media.models import PackageType

from portfolio_media import LogoGenerator, MediaConfig

# Configure generation
config = MediaConfig(
    package_name="my-awesome-package",
    package_type=PackageType.PYTHON,
    style="modern",
    color_scheme="blue"
)

# Generate logo
generator = LogoGenerator()
result = generator.generate_logo(
    config=config,
    output_path="assets/logos/my-awesome-package-logo.png"
)

print(f"Logo generated: {result.output_path}")
print(f"Dimensions: {result.width}x{result.height}")
print(f"Format: {result.format}")
print(f"Size: {result.size_bytes} bytes")
