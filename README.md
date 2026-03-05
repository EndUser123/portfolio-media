# portfolio-media

> AI-powered visual asset generation for GitHub repositories

[![Build Status](https://img.shields.io/github/actions/status/EndUser123/portfolio-media?branch=main)](https://github.com/EndUser123/portfolio-media/actions)  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 📺 Assets & Media

Visual asset examples and explainer videos are available in the [assets/](./assets/) directory:

- **Architecture Diagram**: See [assets/diagrams/architecture.md](./assets/diagrams/architecture.md) for system design overview
- **Explainer Video**: Watch the [assets/videos/portfolio-media_explainer_pbs.mp4](./assets/videos/portfolio-media_explainer_pbs.mp4) for PBS-structured explainer (2:15)
- **Example Gallery**: See [assets/examples/](./assets/examples/) for sample outputs from all providers

Note: Media assets are generated using NotebookLM and Claude Code's built-in diagramming tools.

## Overview

`portfolio-media` automates the creation of professional visual assets for your GitHub repositories:

- **Logos** - Generate package logos using Gemini, OpenRouter, or GLM
- **Diagrams** - Create Mermaid architecture diagrams
- **Screenshots** - Automated browser screenshots with Playwright

## Installation

```bash
# Basic installation
pip install portfolio-media

# With specific provider
pip install portfolio-media[gemini]   # Google Imagen
pip install portfolio-media[openrouter] # Flux/SDXL models
pip install portfolio-media[glm]     # Zhipu AI

# All providers
pip install portfolio-media[all]
```

## Quick Start

### Generate a Logo

```bash
portfolio-media-logo \
  --package debugRCA \
  --description "Root cause analysis toolkit" \
  --output assets/logo/logo.png \
  --style minimalist \
  --color "#FF6B6B" \
  --provider gemini
```

### Generate an Architecture Diagram

```bash
portfolio-media-diagram \
  --package debugRCA \
  --components "Analyzer,Verifier,Hypothesis Generator" \
  --output assets/diagrams/architecture.svg \
  --flow TD
```

### Capture a Screenshot

```bash
portfolio-media-screenshot \
  --url http://localhost:8000 \
  --output assets/screenshots/home.png \
  --width 1280 \
  --height 720
```

## Python API

```python
from portfolio_media import LogoGenerator, DiagramGenerator

# Generate a logo
generator = LogoGenerator()
result = await generator.generate(
  package_name="mypackage",
  description="A toolkit for doing X",
  output_path="assets/logo/logo.png",
  style="minimalist",
  color="#3B82F6",
  provider="gemini"
)

# Generate a diagram
diagram = DiagramGenerator()
result = await diagram.generate(
  package_name="mypackage",
  components=["API", "Service", "Database"],
  output_path="assets/diagrams/arch.svg"
)
```

## Provider Configuration

| Provider | Image Gen | Diagram | Notes |
|----------|-----------|---------|-------|
| **Gemini** | ✅ Imagen | ✅ | Best overall, free tier available |
| **OpenRouter** | ✅ Flux/SDXL | ✅ | Multiple models, pay-per-use |
| **GLM** | ✅ | ✅ | Zhipu AI, Chinese-optimized |
| **Claude** | ❌ | ✅ Mermaid | Best for diagram code generation |
| **Perplexity** | ❌ | ❌ | Use for prompt optimization |

### Environment Variables

```bash
# Gemini (Google Imagen)
export GEMINI_API_KEY="your-key"

# OpenRouter
export OPENROUTER_API_KEY="your-key"

# GLM (Zhipu AI)
export GLM_API_KEY="your-key"

# Perplexity
export PERPLEXITY_API_KEY="your-key"
```

## Asset Organization

Generated assets follow this structure:

```
assets/
├── logo/
│  ├── logo.png     # 512x512 primary
│  └── logo-small.png  # 128x128
├── banners/
│  └── banner.png    # 1280x320
├── diagrams/
│  ├── architecture.svg
│  └── architecture.mmd # Source Mermaid
└── screenshots/
  ├── homepage.png
  └── cli-demo.png
```

## Integration with /portfolio

This package integrates seamlessly with the `/portfolio` skill:

```bash
# Run /portfolio to detect gaps
/portfolio

# /portfolio will auto-suggest using /portfolio-media
# for missing visual assets
```

## License

MIT

## Repository

https://github.com/EndUser123/portfolio-media
