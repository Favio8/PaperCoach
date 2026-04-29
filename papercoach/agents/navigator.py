from __future__ import annotations

from papercoach.agents.question_generator import QuestionGenerator
from papercoach.core.constants import (
    STAGE_MODULES,
    STAGE_QUERIES,
    STAGE_READING_GUIDES,
)
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
            goal=self._stage_goal(stage),
            focus_points=self._focus_points(stage),
            questions=questions,
        )

    def _targets_from_section_hints(
        self,
        stage: str,
        retriever: LocalRetriever,
    ) -> list[ReadingTarget]:
        sections = [
            section for section in retriever.paper.sections if is_reader_section(section.title)
        ]
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
        guide = STAGE_READING_GUIDES.get(stage, STAGE_READING_GUIDES["Thoughts"])
        focus = guide["focus"]
        return list(focus) if isinstance(focus, tuple) else [str(focus)]

    def _target_reason(self, stage: str) -> str:
        guide = STAGE_READING_GUIDES.get(stage, STAGE_READING_GUIDES["Thoughts"])
        reads = guide["read"]
        read_text = "；".join(reads[:2]) if isinstance(reads, tuple) else str(reads)
        return f"建议先读：{read_text}。阅读目标：{guide['goal']}"

    def _stage_goal(self, stage: str) -> str:
        modules = " + ".join(STAGE_MODULES.get(stage, (stage,)))
        guide = STAGE_READING_GUIDES.get(stage, STAGE_READING_GUIDES["Thoughts"])
        return f"当前模块：{modules}。阅读目标：{guide['goal']}"


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
