from __future__ import annotations

from papercoach.agents.prompts import BLOG_DRAFT_BUILDER_SYSTEM_PROMPT
from papercoach.core.constants import STAGE_GOALS, STAGE_QUERIES
from papercoach.schemas.sessions import BlogFragmentResponse, Session
from papercoach.services.llm import LLMClient, LLMError
from papercoach.services.retrieval import LocalRetriever


class BlogDraftBuilder:
    """Build a stage-level blog fragment from paper evidence and user answers."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client

    def build(self, stage: str, session: Session, retriever: LocalRetriever) -> BlogFragmentResponse:
        hits = retriever.search(STAGE_QUERIES.get(stage, stage), k=3)
        answers = [answer for answer in session.user_answers if answer.stage == stage]

        facts = "\n".join(
            f"- {hit.chunk.location}: {compact(hit.chunk.text, 180)}" for hit in hits[:3]
        )
        if not facts:
            facts = "- 暂未检索到足够的论文事实，请先完成该阶段阅读导航。"

        understanding = "\n".join(f"- {answer.answer.strip()}" for answer in answers if answer.answer.strip())
        if not understanding:
            understanding = "- 这里等待补充你的阶段性理解。"

        feedback_notes = "\n".join(
            f"- Q `{answer.question_id}`: accuracy={answer.scores.get('accuracy', '-')}, "
            f"depth={answer.scores.get('depth', '-')}, evidence={answer.scores.get('evidence', '-')}"
            for answer in answers
        )
        if not feedback_notes:
            feedback_notes = "- 尚无回答评分。"

        llm_content = self._llm_fragment(stage, facts, understanding, feedback_notes)
        if llm_content is not None:
            return BlogFragmentResponse(stage=stage, content=llm_content)

        content = (
            f"## {stage}\n\n"
            "### 论文事实\n"
            f"{facts}\n\n"
            "### 我的理解\n"
            f"{understanding}\n\n"
            "### 我的评价\n"
            "- 这里等待基于实验结果、局限性或 Agent 研究脉络补充你的判断。\n\n"
            "### Agent 反馈摘要\n"
            f"{feedback_notes}\n\n"
            "### 值得继续追问的问题\n"
            f"- {STAGE_GOALS.get(stage, STAGE_GOALS['Thoughts'])}\n"
        )
        return BlogFragmentResponse(stage=stage, content=content)

    def _llm_fragment(
        self,
        stage: str,
        facts: str,
        understanding: str,
        feedback_notes: str,
    ) -> str | None:
        if self.llm_client is None:
            return None
        system = BLOG_DRAFT_BUILDER_SYSTEM_PROMPT
        user = (
            f"阅读阶段：{stage}\n\n"
            f"论文事实：\n{facts}\n\n"
            f"用户理解：\n{understanding}\n\n"
            f"反馈摘要：\n{feedback_notes}\n\n"
            "请生成 Markdown，结构固定为：\n"
            f"## {stage}\n"
            "### 论文事实\n"
            "### 我的理解\n"
            "### 我的评价\n"
            "### Agent 反馈摘要\n"
            "### 值得继续追问的问题\n"
            "\n要求：不要生成完整博客，不要包含 Implementation / 简单复现模块。"
        )
        try:
            return self.llm_client.complete(system=system, user=user, temperature=0.25)
        except LLMError:
            return None


def compact(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."
