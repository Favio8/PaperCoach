from __future__ import annotations

import re

from papercoach.agents.prompts import ANSWER_EVALUATOR_SYSTEM_PROMPT
from papercoach.schemas.sessions import AnswerResponse, Question
from papercoach.services.llm import LLMClient, LLMError
from papercoach.services.retrieval import LocalRetriever, RetrievalHit, tokenize


class AnswerEvaluator:
    """Evaluate a user answer against retrieved paper evidence."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client

    def evaluate(
        self,
        question: Question,
        answer: str,
        retriever: LocalRetriever,
    ) -> AnswerResponse:
        answer = answer.strip()
        hits = retriever.search(f"{question.question} {answer}", k=3)
        context = "\n".join(hit.chunk.text for hit in hits)
        scores = self._scores(question, answer, context)
        reread_suggestions = [hit.chunk.location for hit in hits]
        feedback = self._llm_feedback(question, answer, scores, reread_suggestions, hits, context)
        feedback_source = "llm" if feedback is not None else "local"
        feedback_provider = (
            self.llm_client.provider if feedback is not None and self.llm_client else "local"
        )
        if feedback is None:
            feedback = self._feedback(question, answer, scores, reread_suggestions, hits)
        understood = self._understood(scores)
        return AnswerResponse(
            feedback=feedback,
            scores=scores,
            reread_suggestions=reread_suggestions,
            understood=understood,
            feedback_source=feedback_source,
            feedback_provider=feedback_provider,
        )

    def _scores(self, question: Question, answer: str, context: str) -> dict[str, int]:
        if not answer:
            return {"accuracy": 1, "completeness": 1, "depth": 1, "evidence": 1, "expression": 1}

        answer_tokens = set(tokenize(answer))
        context_tokens = set(tokenize(context))
        overlap = len(answer_tokens & context_tokens) / max(len(answer_tokens), 1)

        accuracy = threshold_score(overlap, [(0.25, 5), (0.16, 4), (0.08, 3), (0.03, 2)])
        completeness = length_score(len(answer))
        evidence = evidence_score(question, answer)
        depth = depth_score(answer)
        expression = expression_score(answer)
        if evidence >= 4 and len(answer) >= 80:
            # Most papers are English while the user writes notes in Chinese. A strong evidence
            # citation should prevent pure token overlap from making an otherwise grounded
            # Chinese answer look completely inaccurate.
            accuracy = max(accuracy, 3)
        if evidence >= 4 and depth >= 3:
            accuracy = max(accuracy, 4)
        return {
            "accuracy": accuracy,
            "completeness": completeness,
            "depth": depth,
            "evidence": evidence,
            "expression": expression,
        }

    def _feedback(
        self,
        question: Question,
        answer: str,
        scores: dict[str, int],
        reread_suggestions: list[str],
        hits: list[RetrievalHit],
    ) -> str:
        if not answer:
            return (
                "【1. 你回答中的亮点】\n"
                "- 你还没有提交回答，因此现在最重要的是先回到原文建立证据。\n\n"
                "【2. 需要修正的地方】\n"
                f"- 当前问题还没有被回答：{question.question}\n\n"
                "【3. 建议回读的位置】\n"
                f"- {question.evidence_location}：先找出能直接支撑回答的原文表述。\n\n"
                "【4. 可以继续挖深的问题】\n"
                "- 这一位置里，哪一句最能说明作者的核心判断？\n\n"
                "【5. 博客可用版本】\n"
                "- 暂无。请先用自己的话完成一版回答，再按"
                "“论文事实 / 我的理解 / 我的评价”整理成博客片段。\n\n"
                "【6. 下一步阅读导航】\n"
                f"- 建议先读：{question.evidence_location}\n"
                "- 阅读目标：找到能回答当前问题的原文证据。\n"
                "- 重点关注：作者的 claim、方法关系、实验依据或限制条件。\n"
                "- 读完后回来回答：请用 3 到 5 句话回答当前问题，并写出证据位置。\n"
            )

        highlight = "你已经尝试用自己的话回应问题，这是后续纠偏的基础。"
        if scores["evidence"] >= 4:
            highlight = "你的回答已经包含了较明确的论文位置或证据意识。"
        elif scores["depth"] >= 4:
            highlight = "你的回答不仅复述现象，也开始解释原因或机制。"

        fixes: list[str] = []
        if scores["accuracy"] <= 2:
            fixes.append("回答和可检索到的论文文本重合较少，需要回到原文确认关键术语和 claim。")
        if scores["completeness"] <= 2:
            fixes.append("回答偏短，建议补充作者的原始表述、方法关系或实验依据。")
        if scores["evidence"] <= 2:
            fixes.append("缺少明确证据位置，建议写出 section、figure、table 或页码。")
        if not fixes:
            fixes.append("当前回答可以继续推进，但建议再补一个更具体的原文证据。")
        score_feedback = [
            f"准确性：{score_label(scores['accuracy'])}",
            f"完整性：{score_label(scores['completeness'])}",
            f"深度：{score_label(scores['depth'])}",
            f"表达质量：{score_label(scores['expression'])}",
            f"证据使用：{score_label(scores['evidence'])}",
        ]

        evidence_preview = ""
        if hits:
            text = re.sub(r"\s+", " ", hits[0].chunk.text).strip()
            evidence_preview = text[:260]

        suggestions = "\n".join(
            f"- {location}：核对你的判断是否有原文证据支撑。"
            for location in reread_suggestions[:3]
        )
        fixes_md = "\n".join(f"- {item}" for item in fixes)
        score_md = "\n".join(f"- {item}" for item in score_feedback)
        blog_version = blog_ready_answer(answer, question, scores)
        next_target = reread_suggestions[0] if reread_suggestions else question.evidence_location
        return (
            "【1. 你回答中的亮点】\n"
            f"- {highlight}\n\n"
            "【2. 需要修正的地方】\n"
            f"{score_md}\n"
            f"{fixes_md}\n\n"
            "【3. 建议回读的位置】\n"
            f"{suggestions}\n\n"
            "【4. 可以继续挖深的问题】\n"
            f"- 如果只能保留一个证据来回答“{question.question}”，你会选哪一句或哪张图表？\n\n"
            "【5. 博客可用版本】\n"
            f"{blog_version}\n\n"
            "【6. 下一步阅读导航】\n"
            f"- 建议先读：{next_target}\n"
            "- 阅读目标：把当前回答中的判断补上最直接的论文证据。\n"
            "- 重点关注：作者原始 claim、关键模块、指标或限制条件，避免只写抽象评价。\n"
            "- 读完后回来回答：请补充一个 section、figure、table 或页码级证据。\n\n"
            "【相关原文线索】\n"
            f"- {evidence_preview}"
        )

    def _llm_feedback(
        self,
        question: Question,
        answer: str,
        scores: dict[str, int],
        reread_suggestions: list[str],
        hits: list[RetrievalHit],
        context: str,
    ) -> str | None:
        if self.llm_client is None or not answer:
            return None
        evidence_locations = ", ".join(reread_suggestions[:3])
        system = ANSWER_EVALUATOR_SYSTEM_PROMPT
        user = (
            f"问题：{question.question}\n"
            f"证据位置：{evidence_locations}\n"
            f"本地评分：{scores}\n\n"
            f"论文证据：\n{context[:3500]}\n\n"
            f"用户回答：\n{answer}\n\n"
            "请按以下结构输出：\n"
            "【1. 你回答中的亮点】\n"
            "【2. 需要修正的地方】必须分别评价准确性、完整性、深度、表达质量和证据使用。\n"
            "【3. 建议回读的位置】\n"
            "【4. 可以继续挖深的问题】\n"
            "【5. 博客可用版本】要区分论文事实、我的理解、我的评价，且只写当前模块。\n"
            "【6. 下一步阅读导航】\n"
        )
        try:
            return self.llm_client.complete(system=system, user=user, temperature=0.2)
        except LLMError:
            return None

    def _understood(self, scores: dict[str, int]) -> bool:
        weighted = (
            scores["accuracy"] * 0.35
            + scores["completeness"] * 0.2
            + scores["depth"] * 0.2
            + scores["evidence"] * 0.15
            + scores["expression"] * 0.1
        )
        return weighted >= 3.5


def threshold_score(value: float, thresholds: list[tuple[float, int]]) -> int:
    for threshold, score in thresholds:
        if value >= threshold:
            return score
    return 1


def length_score(length: int) -> int:
    if length >= 500:
        return 5
    if length >= 260:
        return 4
    if length >= 120:
        return 3
    if length >= 40:
        return 2
    return 1


def evidence_score(question: Question, answer: str) -> int:
    answer_lower = answer.lower()
    if question.evidence_location.lower() in answer_lower:
        return 5
    if re.search(r"(section|figure|fig\.|table|page|第\s*\d+|图\s*\d+|表\s*\d+)", answer_lower):
        return 4
    location_terms = set(tokenize(question.evidence_location))
    answer_terms = set(tokenize(answer))
    if location_terms and len(location_terms & answer_terms) >= 2:
        return 3
    return 2 if len(answer) >= 80 else 1


def depth_score(answer: str) -> int:
    markers = [
        "because",
        "therefore",
        "mechanism",
        "trade-off",
        "limitation",
        "因为",
        "因此",
        "所以",
        "机制",
        "原因",
        "局限",
        "权衡",
    ]
    marker_hits = sum(1 for marker in markers if marker in answer.lower())
    if marker_hits >= 2 and len(answer) >= 180:
        return 5
    if marker_hits >= 1 and len(answer) >= 120:
        return 4
    if len(answer) >= 120:
        return 3
    if marker_hits >= 1:
        return 2
    return 1


def expression_score(answer: str) -> int:
    sentence_count = len(re.findall(r"[.!?。！？]", answer))
    if sentence_count >= 4 and len(answer) >= 180:
        return 5
    if sentence_count >= 2 and len(answer) >= 100:
        return 4
    if len(answer) >= 80:
        return 3
    if answer:
        return 2
    return 1


def score_label(score: int) -> str:
    labels = {
        5: "很好，可以推进，但仍建议保留证据位置。",
        4: "基本到位，补一处更精确证据会更稳。",
        3: "有基础，但还需要补全关键链路。",
        2: "偏弱，需要回到原文重新核对。",
        1: "暂不充分，需要先建立原文证据。",
    }
    return labels.get(score, labels[1])


def blog_ready_answer(answer: str, question: Question, scores: dict[str, int]) -> str:
    normalized = " ".join(answer.split())
    if scores["evidence"] <= 2:
        return (
            f"- 当前回答还不适合直接放进博客。建议保留你的核心判断，但补上来自"
            f" {question.evidence_location} 的明确证据后再成稿。"
        )
    if len(normalized) > 260:
        normalized = f"{normalized[:260].rstrip()}..."
    return (
        "- 论文事实：当前回答已引用了原文证据位置。\n"
        f"- 我的理解：{normalized}\n"
        "- 我的评价：这部分还可以继续补充“为什么该证据足以支持判断”和“可能的代价或边界”。"
    )
