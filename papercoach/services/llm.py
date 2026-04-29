from __future__ import annotations

from dataclasses import dataclass

from papercoach.config import Settings


class LLMError(RuntimeError):
    """Raised when a configured LLM provider cannot complete a request."""


@dataclass(frozen=True)
class LLMClient:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: float = 45.0

    def complete(self, system: str, user: str, temperature: float = 0.2) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency is declared for runtime
            raise LLMError("The openai package is required for remote LLM providers.") from exc

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        )
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
            )
        except Exception as exc:  # pragma: no cover - depends on remote provider behavior
            raise LLMError(f"{self.provider} request failed: {exc}") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMError(f"{self.provider} returned an empty response.")
        return content.strip()


def build_llm_client(settings: Settings) -> LLMClient | None:
    provider = settings.llm_provider.lower().strip()
    if provider == "local":
        return None
    if provider == "deepseek":
        if not settings.deepseek_api_key:
            return None
        return LLMClient(
            provider="deepseek",
            model=settings.deepseek_model,
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    if provider == "openai":
        if not settings.openai_api_key:
            return None
        return LLMClient(
            provider="openai",
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    return None
