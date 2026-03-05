---

name: portfolio-media
version: 0.1.0
description: AI-powered visual asset generation for GitHub packages - automated logos, diagrams, and screenshots

# === Taxonomy ===
category: portfolio
domain: media-generation

# === Invocation ===
triggers:
  - "portfolio media"
  - "generate logo"
  - "create diagram"
  - "screenshot"
  - "media asset"
aliases:
  - /portfolio-media

suggest:
  - /portfolio
  - /package

argument-hint: "[command] [options]"

# === Claude Code Config ===
context: fork
agent: general-purpose
user-invocable: true

# === Performance Metadata ===
estimated_tokens: 1000-3000
typical_response_time: 10-60s
context_required: "package name, description, output path"
token_budget_hint: "Available tokens: <5K (Abort), 5-20K (OK), >20K (Good)"

# === Status & Ownership ===
status: experimental
owner: "brsth"
last_reviewed: 2026-02-15
next_review_date: 2026-05-15

# === Dependencies ===
depends_on_skills:
  - /portfolio
  - /llm-gemini
  - /llm-openrouter
  - /llm-qwen
requires_tools:
  - python

---

# /portfolio-media — AI Visual Asset Generator

## Purpose

Automates the creation of professional visual assets (logos, diagrams, screenshots) for GitHub packages using multiple AI providers.

> **Goal**: Every GitHub package gets professional visual assets without manual design work.

## Project Context

### Constitution / Constraints
- **Solo-dev constraints apply** (CLAUDE.md)
- **Provider flexibility**: Support Gemini, OpenRouter, GLM, Perplexity, Claude
- **No OpenAI dependency**: Use existing LLM tools already configured
- **Evidence-first**: Only claim what providers can actually do

### Technical Context
- **Python package**: `pip install portfolio-media`
- **Multi-provider**: Gemini (Imagen), OpenRouter (Flux/SDXL), GLM, Claude (Mermaid)
- **Browser automation**: Playwright for screenshots
- **CLI interface**: Simple commands for each media type

### Architecture Alignment
- Works alongside `/portfolio` for complete package enhancement
- Integrates with `/llm-*` skills for provider access
- Generates assets to `assets/` directory structure

## Your Workflow

**Two-Stage Process:**

### Stage 1: Assess (check what you have)

```bash
/portfolio-media assess
```

Scans the current package for:
- Logos (required)
- Diagrams
- Screenshots
- Videos
- Banners

Outputs:
- Quality score (0-100)
- List of missing assets
- Prioritized recommendations
- Ready-to-run generation commands

### Stage 2: Generate (fill the gaps)

```bash
# Auto-generate based on assessment
/portfolio-media generate

# Or provide specifics manually
/portfolio-media generate \\
    --description "A toolkit for root cause analysis" \\
    --components "Analyzer,Verifier,Reporter" \\
    --url http://localhost:8000 \\
    --provider gemini
```

Generates missing assets automatically.

### Direct Commands (skip assessment)

```bash
/portfolio-media logo --package "X" --description "Y" --output logo.png
/portfolio-media diagram --package "X" --components "A,B,C" --output arch.svg
/portfolio-media screenshot --url http://localhost:8000 --output screen.png
```

## Commands

### Assess (Stage 1)

```bash
/portfolio-media assess
```

Scans current directory for visual assets and produces a report:

```
============================================================
Asset Assessment: debugRCA
============================================================
Path: P:/packages/debugRCA

Quality Score: 20/100

Assets Present:
  ✓ Diagrams (required)
  ✗ Logo (required)
  ✗ Banner
  ✗ Screenshots
  ✗ Videos

README Mentions:
  ✓ Mentions_Diagram
  ✗ Mentions_Logo
  ✓ Mentions_Screenshot
  ✗ Mentions_Video

Recommendations:

  1. 🔴 [HIGH] Generate package logo
     Command: /portfolio-media logo --package "debugRCA" --description "TODO: add description" --output assets/logo/logo.png

  2. 🟡 [MEDIUM] Capture documentation screenshots
     Command: /portfolio-media screenshot --url http://localhost:8000 --output assets/screenshots/home.png

  3. 🟢 [LOW] Generate README banner
     Command: /portfolio-media logo --package "debugRCA" --description "TODO" --output assets/banners/banner.png --style gradient

============================================================
```

**Options:**
- `--path`: Path to package (default: current directory)
- `--output`: Save report to JSON file
- `--quiet`: Only print score, no full report

### Generate (Stage 2)

```bash
# Auto-generate based on assessment
/portfolio-media generate

# With specific parameters
/portfolio-media generate \\
    --description "AI-powered root cause analysis toolkit" \\
    --components "CLI,Analyzer,Hypothesis,Verifier" \\
    --url http://localhost:8000 \\
    --provider gemini
```

Generates missing assets identified during assessment.

**Options:**
- `--path`: Path to package
- `--report`: Path to assessment report (default: auto-discover)
- `--package`: Override detected package name
- `--description`: Package description for logo/banner generation
- `--components`: Comma-separated components for diagram
- `--url`: URL for screenshot capture
- `--provider`: AI provider for generation (default: gemini)
- `--dry-run`: Show what would be generated without doing it

### Logo Generation (Direct)

```bash
/portfolio-media logo --package "debugRCA" \\
    --description "Root cause analysis toolkit" \\
    --output assets/logo/logo.png \\
    --style minimalist \\
    --color "#FF6B6B" \\
    --provider gemini
```

**Options:**
- `--package`: Package name
- `--description`: Brief description (1-2 sentences)
- `--output`: Output file path
- `--style`: minimalist, geometric, gradient, flat, tech, playful
- `--color`: Primary color (hex or name)
- `--provider`: gemini, openrouter, glm
- `--variations`: Generate N variations (requires directory output)

### Diagram Generation

```bash
/portfolio-media diagram --package "debugRCA" \\
    --components "Analyzer,Hypothesis Generator,Verifier" \\
    --output assets/diagrams/architecture.svg \\
    --flow TD
```

**Options:**
- `--package`: Package name
- `--components`: Comma-separated component list
- `--output`: Output file path (.svg for rendered, .mmd for code)
- `--title`: Diagram title (default: "Architecture")
- `--flow`: TD (top-down), LR (left-right), BT, RL
- `--code-only`: Generate Mermaid code only, skip rendering

### Screenshot Capture

```bash
/portfolio-media screenshot \\
    --url http://localhost:8000 \\
    --output assets/screenshots/home.png \\
    --width 1280 \\
    --height 720
```

**Options:**
- `--url`: URL to capture
- `--output`: Output file path
- `--width`: Viewport width (default: 1280)
- `--height`: Viewport height (default: 720)
- `--full-page`: Capture full scrollable page
- `--wait-for`: CSS selector to wait before capturing
- `--selector`: Capture specific element only

### Provider Check

```bash
/portfolio-media check
```

Shows which providers are available and installation instructions for missing ones.

## Provider Matrix

| Provider | Logo | Diagram | Screenshot | Video | Setup |
|----------|------|---------|------------|-------|-------|
| **Gemini** | ✅ Imagen | ✅ | ❌ | ❌ | `GEMINI_API_KEY` |
| **OpenRouter** | ✅ Flux/SDXL | ✅ | ❌ | ✅ Slideshow | `OPENROUTER_API_KEY` |
| **GLM** | ✅ | ✅ | ❌ | ❌ | `GLM_API_KEY` |
| **Claude** | ❌ | ✅ Mermaid | ❌ | ❌ | Built-in |
| **Playwright** | ❌ | ❌ | ✅ | ❌ | `pip install playwright` |
| **CogVideoX** | ❌ | ❌ | ❌ | ✅ Local | `pip install diffusers` + 12GB VRAM |
| **ComfyUI** | ✅ Best | ✅ | ❌ | ✅ Best | Local install (see below) |

## Asset Organization

Generated assets follow this structure:

```
assets/
├── logo/
│   ├── logo.png          # 512x512 primary
│   └── logo-small.png    # 128x128
├── banners/
│   └── banner.png        # 1280x320
├── diagrams/
│   ├── architecture.svg
│   └── architecture.mmd  # Source Mermaid
├── screenshots/
│   ├── homepage.png
│   └── cli-demo.png
└── videos/
    ├── demo.mp4          # Package demo video
    └── tutorial.mp4      # Tutorial walkthrough
```

## Integration with /portfolio

When `/portfolio` detects missing visual assets, it suggests using `/portfolio-media`:

```
/portfolio
→ Detects missing logo
→ Suggestion: Run `/portfolio-media logo --package mypackage ...`
```

## Python API

```python
from portfolio_media import LogoGenerator, DiagramGenerator, VideoGenerator

# Logo
generator = LogoGenerator()
result = await generator.generate(
    package_name="mypackage",
    description="A toolkit for X",
    output_path="assets/logo/logo.png",
    style="minimalist",
    provider="gemini"
)

# Diagram
diagram = DiagramGenerator()
result = await diagram.generate(
    package_name="mypackage",
    components=["API", "Service", "Database"],
    output_path="assets/diagrams/arch.svg"
)

# Video (auto-detects best backend)
video_gen = VideoGenerator()
result = await video_gen.generate(
    package_name="mypackage",
    description="Fast API server with async handlers",
    output_path="assets/videos/demo.mp4",
    duration=4,
    backend="auto"  # or "cogvideox", "opensora", "openrouter"
)

# Check what's available
status = video_gen.check_installation()
print(f"GPU: {status['gpu']['name']} ({status['gpu']['vram_gb']} GB)")
print(f"Recommended: {status['recommended']}")
```

## Validation Rules

- **Before generation**: Check provider availability, fail fast if not configured
- **After generation**: Verify output file exists and is non-zero size
- **Screenshot targets**: Only capture localhost or explicitly specified URLs

### Prohibited Actions

- Do NOT capture screenshots of public URLs without user consent
- Do NOT use providers that aren't configured (check first)
- Do NOT overwrite existing assets without `--force` flag

## Examples

### Generate Logo for Python Package

```bash
/portfolio-media logo \\
    --package debugRCA \\
    --description "AI-powered root cause analysis toolkit for Python" \\
    --output assets/logo/logo.png \\
    --style tech \\
    --color "#00BCD4" \\
    --provider gemini
```

### Create Architecture Diagram

```bash
/portfolio-media diagram \\
    --package debugRCA \\
    --components "CLI,Analyzer,Hypothesis,Verifier,Reporter" \\
    --output assets/diagrams/architecture.svg \\
    --title "debugRCA Architecture" \\
    --flow LR
```

### Capture Documentation Screenshots

```bash
# Homepage
/portfolio-media screenshot \\
    --url http://localhost:8000 \\
    --output assets/screenshots/home.png \\
    --full-page

# Specific element
/portfolio-media screenshot \\
    --url http://localhost:8000/docs \\
    --output assets/screenshots/api.png \\
    --selector "#api-reference"
```

### Generate Multiple Logo Options

```bash
/portfolio-media logo \\
    --package myapp \\
    --description "My application" \\
    --output assets/logo/ \\
    --variations 3 \\
    --style minimalist
```

### Generate Demo Video

```bash
# Auto-detect best backend (CogVideoX for 12GB+ VRAM)
/portfolio-media video \\
    --package myapp \\
    --description "CLI tool for data processing" \\
    --output assets/videos/demo.mp4

# Specific backend
/portfolio-media video \\
    --package myapp \\
    --description "Fast API server" \\
    --output assets/videos/demo.mp4 \\
    --backend cogvideox \\
    --duration 6
```

## Video Generation Options

### Local Video Generation (Recommended for RTX 5070/12GB+)

**ComfyUI** - Best for image/video workflows with local models:

```bash
# Install ComfyUI (Windows portable)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Install CogVideoX wrapper
cd custom_nodes
git clone https://github.com/kijai/ComfyUI-CogVideoXWrapper.git

# Run ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

| Model | VRAM | Resolution | Time | Notes |
|-------|------|------------|------|-------|
| CogVideoX-2B | 8GB | 480p | 4-5 min | Best for quick demos |
| CogVideoX-5B | 12GB | 720p | 8-10 min | Higher quality |
| HunyuanVideo | 12GB | 720p | 8 min | Best img2vid fidelity |
| LTX-2 | 8GB | 720p | 5 min | Real-time capable |

### Cloud Video Generation

**Gemini Veo 3.1** - Native text-to-video with audio:

```bash
export GEMINI_API_KEY="your-key"

portfolio-media video \\
    --package myapp \\
    --description "Animated GitHub repo demo" \\
    --output assets/videos/demo.mp4 \\
    --backend gemini-veo
```

**NotebookLM MCP** - Narrated explainer videos from docs:

```bash
# Requires NotebookLM MCP server
# Feed repo README/docs → get narrated demo video
mcp-call notebooklm generate_video \\
    --sources README.md,docs/ \\
    --style cinematic \\
    --output assets/videos/explainer.mp4
```

## Installation

```bash
# Base package
pip install portfolio-media

# With providers
pip install portfolio-media[gemini]
pip install portfolio-media[openrouter]
pip install portfolio-media[glm]
pip install portfolio-media[all]
```

## Environment Variables

```bash
# Gemini (Google Imagen)
export GEMINI_API_KEY="your-key"

# OpenRouter (Flux, SDXL)
export OPENROUTER_API_KEY="your-key"

# GLM (Zhipu AI)
export GLM_API_KEY="your-key"

# Perplexity (for prompt optimization)
export PERPLEXITY_API_KEY="your-key"
```

## Integration

Works alongside:
- **/portfolio** - Detects gaps and suggests media generation
- **/package** - Creates initial package structure
- **/llm-gemini** - Direct Gemini access
- **/llm-openrouter** - Direct OpenRouter access
- **/llm-qwen** - Direct GLM access

## License

MIT
