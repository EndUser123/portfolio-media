# Technical Briefing: portfolio-media Package

## Facts

*   **Purpose:** The `portfolio-media` package is designed for automated portfolio asset generation using NotebookLM MCP and AI-Distiller for compression.
*   **Key Components:**
    *   `diagram_generator.py`: Handles Mermaid diagram generation.
    *   `video_generator.py`: Manages video generation via NotebookLM.
    *   `providers/`: Contains implementations for different AI providers, specifically `openrouter` and `notebooklm`.
    *   `__init__.py`: Handles core exports.
*   **Features:**
    *   Generates diagrams with customizable themes.
    *   Generates videos including an "ADHD-friendly focus mode".
    *   Supports multiple providers for AI services.
*   **Dependencies:**
    *   `notebooklm-mcp` (for NotebookLM integration).
    *   `ai-distiller` (for code compression).
    *   `openrouter` (optional AI provider).
*   **Usage:**
    *   Videos are created using the `VideoGenerator` class, specifically the `create_video` method which accepts a `notebook_id` and a `focus` parameter.
    *   Diagrams are created using the `DiagramGenerator` class via the `generate` method, which accepts `structure` and `theme` arguments.

## Limitations

*   **Source Material Scope:** The provided text is a brief package summary (README style) and does not contain detailed API documentation, error handling, or performance metrics.
*   **Dependency Constraints:** The package relies on external libraries (`notebooklm-mcp`, `ai-distiller`), meaning its functionality is tied to the stability and availability of these specific tools.

## Unknowns

*   **Implementation Details:** The specific algorithms used for "compression" by `ai-distiller` or how the "ADHD-friendly focus mode" modifies video content are not detailed in the source text.
*   **Configuration:** Apart from `notebook_id`, `focus`, and `theme`, it is unknown what other configuration options or environment variables are required.

## Conflicts

*   **No explicit conflicts found:** The source text outlines a coherent architecture with distinct modules for diagrams and video, and a provider pattern for AI services. No contradictory information was present in the provided excerpts.
