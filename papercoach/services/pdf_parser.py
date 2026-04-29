from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from papercoach.core.ids import stable_id
from papercoach.schemas.papers import Paper, PaperFigure, PaperParagraph, PaperSection, PaperTable

KNOWN_HEADINGS = {
    "abstract",
    "introduction",
    "background",
    "related work",
    "preliminaries",
    "method",
    "methods",
    "methodology",
    "approach",
    "architecture",
    "system",
    "experiments",
    "experiment",
    "evaluation",
    "results",
    "discussion",
    "limitations",
    "conclusion",
    "conclusions",
    "references",
}

NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.{3,100})$")
SPLIT_NUMBER_HEADING_RE = re.compile(r"^([A-Z]|\d+)(?:\.\d+)*\.?$")
FIGURE_RE = re.compile(r"^(fig(?:ure)?\.?\s*\d+)\s*[:.\-]?\s*(.+)$", re.IGNORECASE)
TABLE_RE = re.compile(r"^(table\s*\d+)\s*[:.\-]?\s*(.+)$", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedHeading:
    index: int
    page: int
    title: str
    level: int


class PdfParser:
    """Parse a PDF into PaperCoach's section-oriented document model."""

    def parse(self, path: Path, paper_id: str) -> Paper:
        try:
            import fitz
        except ImportError as exc:  # pragma: no cover - exercised only without dependency
            raise RuntimeError("PyMuPDF is required to parse PDF files.") from exc

        with fitz.open(path) as doc:
            page_texts = [(page.number + 1, page.get_text("text")) for page in doc]

        full_text = "\n".join(text for _, text in page_texts)
        title = extract_title(page_texts)
        authors = extract_authors(page_texts, title)
        abstract = extract_abstract(full_text)
        sections = extract_sections_from_pages(page_texts)
        figures = extract_figures_from_pages(page_texts)
        tables = extract_tables_from_pages(page_texts)
        references = extract_references(full_text)

        if abstract and not any(section.title.lower() == "abstract" for section in sections):
            abstract_section = build_section(
                title="Abstract",
                content=abstract,
                page_start=1,
                page_end=1,
                level=1,
                order=0,
            )
            sections.insert(0, abstract_section)

        return Paper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            figures=figures,
            tables=tables,
            references=references,
            source_file=path,
        )


def extract_title(page_texts: list[tuple[int, str]]) -> str:
    first_page = page_texts[0][1] if page_texts else ""
    lines = clean_lines(first_page)
    for idx, line in enumerate(lines):
        lower = line.lower()
        if lower in KNOWN_HEADINGS or lower.startswith("arxiv:"):
            continue
        if 5 <= len(line) <= 180 and not line.isdigit():
            if idx + 1 < len(lines) and looks_like_subtitle(lines[idx + 1]):
                return f"{line} {lines[idx + 1]}".strip()
            return line
    return "Untitled Paper"


def extract_authors(page_texts: list[tuple[int, str]], title: str) -> list[str]:
    first_page = page_texts[0][1] if page_texts else ""
    lines = clean_lines(first_page)
    abstract_index = next(
        (idx for idx, line in enumerate(lines) if normalize_heading(line) == "abstract"),
        len(lines),
    )
    title_end = 0
    for idx, line in enumerate(lines[:abstract_index]):
        line_words = line.split()
        prefix_words = line_words[: min(3, len(line_words))]
        if line in title or all(word in title for word in prefix_words):
            title_end = idx + 1

    author_lines: list[str] = []
    for line in lines[title_end:abstract_index]:
        lower = line.lower()
        if not line or "http" in lower:
            continue
        if "equal contribution" in lower or "corresponding" in lower or "advising" in lower:
            continue
        if re.match(r"^\d", line):
            continue
        if "," in line or len(author_lines) == 0:
            author_lines.append(line)
        if len(author_lines) >= 2:
            break

    joined = " ".join(author_lines)
    cleaned = re.sub(r"[∗†#]", "", joined)
    cleaned = re.sub(r"\d+", "", cleaned)
    authors = [author.strip() for author in re.split(r",|\band\b", cleaned) if author.strip()]
    return authors[:20]


def looks_like_subtitle(line: str) -> bool:
    normalized = normalize_heading(line)
    if normalized in KNOWN_HEADINGS or "," in line:
        return False
    if len(line) > 100 or len(line) < 4:
        return False
    return line[:1].islower() or line.lower().startswith(("with ", "using ", "for ", "towards "))


def extract_abstract(text: str) -> str:
    lines = clean_lines(text)
    start: int | None = None
    for idx, line in enumerate(lines):
        normalized = normalize_heading(line)
        if normalized == "abstract":
            start = idx + 1
            break
        if line.lower().startswith("abstract "):
            return line.split(" ", 1)[1].strip()

    if start is None:
        return ""

    collected: list[str] = []
    for line in lines[start:]:
        heading = detect_heading(line)
        if heading and heading.title.lower() != "abstract":
            break
        collected.append(line)
    return " ".join(collected).strip()


def extract_sections_from_text(text: str) -> list[PaperSection]:
    return extract_sections_from_pages([(1, text)])


def extract_sections_from_pages(page_texts: list[tuple[int, str]]) -> list[PaperSection]:
    indexed_lines: list[tuple[int, str]] = []
    for page, text in page_texts:
        indexed_lines.extend((page, line) for line in clean_lines(text))

    headings: list[ParsedHeading] = []
    idx = 0
    while idx < len(indexed_lines):
        page, line = indexed_lines[idx]
        heading = detect_heading(line)
        if heading and not is_table_header_line(indexed_lines, idx):
            headings.append(ParsedHeading(idx, page, heading.title, heading.level))
            idx += 1
            continue

        split_heading = detect_split_heading(indexed_lines, idx)
        if split_heading and not is_table_header_line(indexed_lines, idx + 1):
            title_page, _ = indexed_lines[idx + 1]
            headings.append(
                ParsedHeading(idx + 1, title_page, split_heading.title, split_heading.level)
            )
            idx += 2
            continue

        idx += 1

    if not headings:
        full_text = "\n".join(line for _, line in indexed_lines).strip()
        return [
            build_section(
                title="Full Text",
                content=full_text,
                page_start=page_texts[0][0] if page_texts else None,
                page_end=page_texts[-1][0] if page_texts else None,
                level=1,
                order=1,
            )
        ]

    sections: list[PaperSection] = []
    for order, heading in enumerate(headings, start=1):
        next_index = headings[order].index if order < len(headings) else len(indexed_lines)
        body_lines = [line for _, line in indexed_lines[heading.index + 1 : next_index]]
        content = "\n".join(body_lines).strip()
        page_end = indexed_lines[next_index - 1][0] if next_index > heading.index else heading.page
        if is_suspicious_short_section(heading.title, content):
            continue
        if content or heading.title.lower() in {"abstract", "references"}:
            sections.append(
                build_section(
                    title=heading.title,
                    content=content,
                    page_start=heading.page,
                    page_end=page_end,
                    level=heading.level,
                    order=order,
                )
            )
    return sections


def extract_figures_from_pages(page_texts: list[tuple[int, str]]) -> list[PaperFigure]:
    figures: list[PaperFigure] = []
    for page, text in page_texts:
        for line in clean_lines(text):
            match = FIGURE_RE.match(line)
            if not match:
                continue
            caption = f"{match.group(1)} {match.group(2)}".strip()
            figures.append(
                PaperFigure(id=stable_id("fig", f"{page}:{caption}"), caption=caption, page=page)
            )
    return figures


def extract_tables_from_pages(page_texts: list[tuple[int, str]]) -> list[PaperTable]:
    tables: list[PaperTable] = []
    for page, text in page_texts:
        for line in clean_lines(text):
            match = TABLE_RE.match(line)
            if not match:
                continue
            caption = f"{match.group(1)} {match.group(2)}".strip()
            tables.append(
                PaperTable(id=stable_id("table", f"{page}:{caption}"), caption=caption, page=page)
            )
    return tables


def extract_references(text: str) -> list[str]:
    lines = clean_lines(text)
    start = next(
        (idx for idx, line in enumerate(lines) if normalize_heading(line) == "references"),
        None,
    )
    if start is None:
        return []
    refs: list[str] = []
    current: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^\[\d+\]|\d+\.\s+", line) and current:
            refs.append(" ".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        refs.append(" ".join(current).strip())
    return refs[:200]


def build_section(
    title: str,
    content: str,
    page_start: int | None,
    page_end: int | None,
    level: int,
    order: int,
) -> PaperSection:
    paragraphs = split_paragraphs(content)
    section_id = stable_id("sec", f"{order}:{title}:{page_start}:{page_end}")
    return PaperSection(
        id=section_id,
        title=title,
        level=level,
        page_start=page_start,
        page_end=page_end,
        content=content,
        paragraphs=[
            PaperParagraph(
                id=stable_id("para", f"{section_id}:{idx}:{paragraph[:80]}"),
                index=idx,
                text=paragraph,
                page=page_start,
            )
            for idx, paragraph in enumerate(paragraphs, start=1)
        ],
    )


def split_paragraphs(text: str) -> list[str]:
    raw = re.split(r"\n\s*\n|(?<=[.!?。！？])\s+(?=[A-Z\u4e00-\u9fff])", text)
    paragraphs = [re.sub(r"\s+", " ", paragraph).strip() for paragraph in raw]
    return [paragraph for paragraph in paragraphs if paragraph]


def clean_lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]


@dataclass(frozen=True)
class Heading:
    title: str
    level: int


def detect_heading(line: str) -> Heading | None:
    normalized = normalize_heading(line)
    if normalized in KNOWN_HEADINGS:
        return Heading(title=title_case_heading(normalized), level=1)

    numbered = NUMBERED_HEADING_RE.match(line)
    if numbered:
        number, title = numbered.groups()
        cleaned_title = title.strip(" .")
        if looks_like_heading_title(cleaned_title):
            return Heading(title=cleaned_title, level=number.count(".") + 1)
    return None


def detect_split_heading(indexed_lines: list[tuple[int, str]], index: int) -> Heading | None:
    if index + 1 >= len(indexed_lines):
        return None

    page, line = indexed_lines[index]
    next_page, next_line = indexed_lines[index + 1]
    if page != next_page:
        return None

    match = SPLIT_NUMBER_HEADING_RE.match(line.strip())
    if not match:
        return None

    cleaned_title = next_line.strip(" .")
    if not looks_like_split_heading_title(cleaned_title):
        return None

    number = line.strip().rstrip(".")
    level = number.count(".") + 1
    return Heading(title=cleaned_title, level=level)


def is_table_header_line(indexed_lines: list[tuple[int, str]], index: int) -> bool:
    if index < 0 or index >= len(indexed_lines):
        return False

    page, line = indexed_lines[index]
    normalized = normalize_heading(line)
    if normalized not in {"method", "model", "approach", "results"}:
        return False

    previous_same_page = [
        candidate
        for candidate_page, candidate in indexed_lines[max(0, index - 8) : index]
        if candidate_page == page
    ]
    return any(candidate.lower().startswith("table ") for candidate in previous_same_page)


def normalize_heading(line: str) -> str:
    value = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", line.strip())
    value = re.sub(r"[:.\-]+$", "", value)
    return value.lower()


def title_case_heading(value: str) -> str:
    acronyms = {"api", "rag", "llm", "pdf"}
    words = [word.upper() if word in acronyms else word.capitalize() for word in value.split()]
    return " ".join(words)


def looks_like_heading_title(title: str) -> bool:
    if len(title) > 100 or len(title) < 3:
        return False
    if not re.search(r"[A-Za-z\u4e00-\u9fff]", title):
        return False
    if "±" in title:
        return False
    if title.endswith((".", ",")):
        return False
    word_count = len(title.split())
    return word_count <= 12


def looks_like_split_heading_title(title: str) -> bool:
    if not looks_like_heading_title(title):
        return False
    normalized = normalize_heading(title)
    if normalized.startswith("arxiv") or "http" in normalized:
        return False
    if re.match(r"^\[?\d+\]?\s+", title):
        return False
    first = title[:1]
    return first.isupper() or normalized in KNOWN_HEADINGS


def is_suspicious_short_section(title: str, content: str) -> bool:
    if not re.search(r"[A-Za-z\u4e00-\u9fff]", title):
        return True
    return False
