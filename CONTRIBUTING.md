# Contributing to MetaGPT-Pro

We welcome contributions to MetaGPT-Pro! To ensure a high-quality, maintainable, and robust enterprise-grade system, please follow these guidelines.

## Code of Conduct

*   **Be Respectful**: Treat all contributors and users with respect and consideration.
*   **Constructive Feedback**: Provide and accept feedback gracefully. Focus on the code, not the person.
*   **Inclusivity**: We are committed to providing a friendly, safe, and welcoming environment for all.

## Development Workflow

1.  **Fork & Clone**: Fork the repository and clone it locally.
2.  **Branching**: Create a new branch for your feature or bugfix (e.g., `feature/api-endpoints`, `fix/rate-limit`).
3.  **Coding Standards**:
    *   **Style**: We follow PEP 8 for Python. Use meaningful variable and function names.
    *   **Type Hinting**: All new code MUST have type hints.
    *   **Docstrings**: All public modules, classes, and functions MUST have Google-style docstrings.
    *   **Imports**: Organize imports: Standard library -> Third-party -> Local application.
4.  **Testing**:
    *   Add unit tests for all new logic.
    *   Ensure existing tests pass (`pytest`).
    *   For API changes, add integration tests in `tests/api/`.
5.  **Documentation**: Update `docs/` if you change behavior or add features.
6.  **Pull Request**: Submit a PR with a clear description of changes. Link relevant issues.

## API Development Guidelines

*   **Framework**: We use FastAPI.
*   **Schema**: use Pydantic models for all Request/Response bodies (in `metagpt/api/schemas.py`).
*   **Versioning**: All paths must start with `/v1/`.
*   **Error Handling**: Use `3000` series for logic errors, `400` for default client errors, `500` for server errors. Return JSON with `detail`.

## Architecture Principles

*   **Non-Invasive**: API layer (`metagpt/api`) should NOT modify core logic (`metagpt/roles`, `metagpt/team`) unless absolutely necessary.
*   **Orchestrator Pattern**: Use `GlobalOrchestrator` to manage state. Do not instantiate `Team` globally elsewhere.
*   **Thread Safety**: Be mindful of `asyncio` loops and shared states.

## Reporting Bugs

Please use the GitHub Issue Tracker. Include:
*   Version of MetaGPT-Pro.
*   Steps to reproduce.
*   Expected vs. Actual behavior.
*   Logs/Screenshots.

Happy Coding!
