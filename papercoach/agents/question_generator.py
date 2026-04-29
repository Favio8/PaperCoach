from __future__ import annotations

from papercoach.agents.prompts import AGENT_RESEARCH_TOPICS
from papercoach.core.ids import stable_id
from papercoach.schemas.sessions import Question, ReadingTarget


class QuestionGenerator:
    """Generate evidence-bound Socratic questions for a reading stage."""

    def generate(self, stage: str, targets: list[ReadingTarget]) -> list[Question]:
        evidence = targets[0].label if targets else "论文相关章节"
        questions = self._templates(stage, evidence)
        return [
            Question(
                id=stable_id("q", f"{stage}:{idx}:{question}:{evidence}", length=12),
                stage=stage,
                question=question,
                evidence_location=evidence,
                kind=kind,
            )
            for idx, (kind, question) in enumerate(questions, start=1)
        ]

    def _templates(self, stage: str, evidence: str) -> list[tuple[str, str]]:
        agent_topic_hint = " / ".join(AGENT_RESEARCH_TOPICS[:6])
        common = [
            ("fact", f"回到 {evidence}，这一部分直接给出了哪些论文事实？请区分作者原文 claim 和你的理解。"),
            ("mechanism", f"结合 {evidence}，这些事实和论文核心方法或主张之间是什么关系？为什么？"),
            (
                "evidence",
                f"你能从 {evidence} 找到哪一句、哪张图或哪项结果来支持判断？请写出证据位置。",
            ),
        ]
        stage_specific: dict[str, tuple[str, str]] = {
            "Background": (
                "synthesis",
                f"读完 {evidence} 后，你会如何说明这篇论文出现的研究背景，以及它属于 Agent 的哪个子方向？",
            ),
            "Problem": (
                "critique",
                f"根据 {evidence}，作者指出的现有方法不足是什么？它影响的是 Agent 的认知能力、执行能力，还是长程任务成功率？",
            ),
            "Key Idea": (
                "contribution",
                f"从 {evidence} 看，本文的新意是机制变化、任务设定变化，还是系统组织方式变化？可参考方向：{agent_topic_hint}。",
            ),
            "Architecture": (
                "structure",
                f"根据 {evidence}，请描述系统中最关键的两个模块、输入输出，以及它们如何协作。",
            ),
            "Method": (
                "mechanism",
                f"从 {evidence} 看，方法执行流程中哪一步最不可替代？如果移除它，可能会失败在哪里？",
            ),
            "Experiments": (
                "evaluation",
                f"结合 {evidence}，实验设置最主要验证的是论文哪个 claim？baseline、指标和场景是否匹配这个 claim？",
            ),
            "Results": (
                "evidence",
                f"根据 {evidence}，哪个结果最能支撑论文贡献？请说明相比谁、提升了什么指标、代价是什么。",
            ),
            "Limitations": (
                "critique",
                f"从 {evidence} 看，方法局限更可能来自任务设定、模型能力、工具依赖、成本，还是实验设计？",
            ),
            "Thoughts": (
                "extension",
                f"基于 {evidence}，这篇论文改变了你对 Agent 哪个问题的认识？你会提出哪个后续研究方向？",
            ),
        }
        return common + [stage_specific.get(stage, stage_specific["Thoughts"])]
