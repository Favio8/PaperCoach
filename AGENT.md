# PaperCoach Coding Agent Guide

## Mission

Build PaperCoach as a Python-first MVP that validates the core learning loop:

PDF upload -> paper structure extraction -> staged reading guidance -> user answer feedback -> blog fragment generation.

## Implementation Rules

- Prefer clear, testable Python modules over framework-heavy abstractions.
- Keep the first implementation local-first: local filesystem storage, SQLite-ready data shapes, and deterministic fallbacks.
- Do not block core flows on external LLM or embedding services. External providers should be optional.
- Preserve evidence locations wherever possible: section title, page range, paragraph id, figure/table id.
- Agent outputs must guide the user instead of replacing the user's thinking.
- Avoid broad refactors unrelated to the current MVP.
- Keep API contracts explicit with Pydantic schemas.
- Add tests around parsers, state transitions, and deterministic agent behavior.

## Technical Choices

- Language: Python.
- API framework: FastAPI.
- PDF parser: PyMuPDF.
- Retrieval: local TF-IDF fallback for MVP; vector provider can be added later.
- Storage: local JSON files for MVP to reduce setup friction.
- LLM: optional OpenAI-compatible provider; deterministic rule-based fallback by default.

## Quality Bar

- Every endpoint should return structured errors or typed responses.
- All persisted objects must have stable ids.
- No hidden global state except app-level service initialization.
- Prompts live in `packages/prompts` and are versionable.
- Keep tests runnable without API keys, network access, or sample PDFs.

## Deferred Until After MVP

- Multi-paper comparison.
- Long-term user modeling.
- Team permissions.
- Fine-grained figure/table visual understanding.
- Full knowledge graph generation.
