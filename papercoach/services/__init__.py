"""Service exports with lazy loading to avoid agent/service import cycles."""

from typing import Any

__all__ = ["LLMClient", "LocalRetriever", "PaperService", "SessionService", "build_llm_client"]


def __getattr__(name: str) -> Any:
    if name in {"LLMClient", "build_llm_client"}:
        from papercoach.services.llm import LLMClient, build_llm_client

        return {"LLMClient": LLMClient, "build_llm_client": build_llm_client}[name]
    if name == "LocalRetriever":
        from papercoach.services.retrieval import LocalRetriever

        return LocalRetriever
    if name == "PaperService":
        from papercoach.services.paper_service import PaperService

        return PaperService
    if name == "SessionService":
        from papercoach.services.session_service import SessionService

        return SessionService
    raise AttributeError(f"module 'papercoach.services' has no attribute {name!r}")

