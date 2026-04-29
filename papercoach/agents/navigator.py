from __future__ import annotations

from papercoach.agents.question_generator import QuestionGenerator
from papercoach.core.constants import STAGE_GOALS, STAGE_QUERIES
from papercoach.schemas.papers import PaperSection
from papercoach.schemas.sessions import NavigationResponse, ReadingTarget
from papercoach.services.retrieval import LocalRetriever, RetrievalHit


STAGE_SECTION_HINTS: dict[str, list[str]] = {
    "Background": ["Abstract", "Introduction"],
    "Problem": ["Introduction", "Problem", "Motivation"],
    "Key Idea": ["Abstract", "Introduction", "Method"],
    "Architecture": ["Method", "Architecture", "System", "Algorithm"],
    "Method": ["Automatic Curriculum", "Skill Library", "Iterative Prompting Mechanism", "Method"],
    "Experiments": ["Experimental Setup", "Baselines", "Experiments"],
    "Results": ["Evaluation Results", "Ablation Studies", "Results"],
    "Limitations": ["Limitations and Future Work", "Limitations", "Discussion", "Conclusion"],
    "Thoughts": ["Conclusion", "Limitations and Future Work", "Related Work"],
}

MAX_TARGETS_BY_STAGE: dict[str, int] = {
    "Method": 3,
    "Experiments": 2,
    "Results": 2,
}


class ReadingNavigator:
    """Select small evidence areas and produce a reading task."""

    def __init__(self, question_generator: QuestionGenerator | None = None) -> None:
        self.question_generator = question_generator or QuestionGenerator()

    def build(self, stage: str, retriever: LocalRetriever) -> NavigationResponse:
        query = STAGE_QUERIES.get(stage, STAGE_QUERIES["Thoughts"])
        targets = self._targets_from_section_hints(stage, retriever)
        if not targets:
            hits = retriever.search(query, k=8)
            targets = self._targets_from_hits(stage, hits)
        questions = self.question_generator.generate(stage, targets)
        return NavigationResponse(
            stage=stage,
            reading_targets=targets,
            goal=STAGE_GOALS.get(stage, STAGE_GOALS["Thoughts"]),
            focus_points=self._focus_points(stage),
            questions=questions,
        )

    def _targets_from_section_hints(
        self,
        stage: str,
        retriever: LocalRetriever,
    ) -> list[ReadingTarget]:
        sections = [section for section in retriever.paper.sections if is_reader_section(section.title)]
        selected = []
        for hint in STAGE_SECTION_HINTS.get(stage, []):
            found = find_section_by_hint(sections, hint, selected)
            if found is not None:
                selected.append(found)
            if len(selected) >= MAX_TARGETS_BY_STAGE.get(stage, 1):
                break

        return [
            ReadingTarget(
                type="section",
                id=section.id,
                title=section.title,
                page_start=section.page_start,
                page_end=section.page_end,
                reason=self._target_reason(stage),
            )
            for section in selected
        ]

    def _targets_from_hits(self, stage: str, hits: list[RetrievalHit]) -> list[ReadingTarget]:
        targets: list[ReadingTarget] = []
        seen_sections: set[str] = set()
        for hit in hits:
            chunk = hit.chunk
            if chunk.section_id in seen_sections:
                continue
            seen_sections.add(chunk.section_id)
            targets.append(
                ReadingTarget(
                    type="section",
                    id=chunk.section_id,
                    title=chunk.section_title,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    reason=self._target_reason(stage),
                )
            )
            if len(targets) >= 2:
                break
        return targets

    def _focus_points(self, stage: str) -> list[str]:
        focus: dict[str, list[str]] = {
            "Background": ["为什么要做这件事", "过去工作的主要缺口", "论文在 Agent 谱系中的位置"],
            "Problem": ["任务定义和约束", "原方法在哪里失败", "作者真正要提升的 Agent 能力"],
            "Key Idea": ["核心创新点", "和已有工作的关键差异", "新增模块如何解决问题"],
            "Architecture": ["模块边界", "信息流或控制流", "状态如何更新以及谁调用谁"],
            "Method": ["每一步输入输出", "为什么这么设计", "最不可替代的步骤和失败模式"],
            "Experiments": ["benchmark 是否合理", "baseline 和指标是否匹配 claim", "消融是否充分"],
            "Results": ["最强证据", "不充分或反常的结果", "提升相比谁以及代价是什么"],
            "Limitations": ["作者承认的限制", "强模型或工具依赖", "泛化、成本、鲁棒性和安全边界"],
            "Thoughts": ["论文事实和个人评价分离", "研究突破还是工程整合", "后续可以追问的研究方向"],
        }
        return focus.get(stage, focus["Thoughts"])

    def _target_reason(self, stage: str) -> str:
        reasons = {
            "Background": "本阶段先读摘要和引言动机，目标是找出为什么要做这项研究。",
            "Problem": "本阶段需要定位问题定义和已有方法不足，避免只写泛泛的任务描述。",
            "Key Idea": "本阶段优先看贡献段和方法总览，目标是压缩出核心创新。",
            "Architecture": "本阶段需要回到系统图或方法总览，梳理模块、信息流和控制流。",
            "Method": "本阶段需要细读方法步骤，明确每一步输入输出和不可替代性。",
            "Experiments": "本阶段需要检查实验设置、baseline、指标和 claim 是否对齐。",
            "Results": "本阶段需要回到主表、消融或案例，判断哪些证据真正支撑结论。",
            "Limitations": "本阶段需要寻找作者承认的限制和实验没有覆盖的边界。",
            "Thoughts": "本阶段需要回看前面证据，形成自己的评价和后续研究问题。",
        }
        return reasons.get(stage, reasons["Thoughts"])


def normalize_title(value: str) -> str:
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def is_reader_section(title: str) -> bool:
    normalized = normalize_title(title)
    return normalized not in {"references", "acknowledgements", "broader impacts"}


def find_section_by_hint(
    sections: list[PaperSection],
    hint: str,
    selected: list[PaperSection],
) -> PaperSection | None:
    normalized_hint = normalize_title(hint)
    selected_ids = {section.id for section in selected}
    for section in sections:
        if section.id not in selected_ids and normalize_title(section.title) == normalized_hint:
            return section
    for section in sections:
        if section.id not in selected_ids and normalized_hint in normalize_title(section.title):
            return section
    return None
