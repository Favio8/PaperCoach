from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from papercoach.schemas.papers import Paper, PaperSection


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    text: str
    section_id: str
    section_title: str
    page_start: int | None
    page_end: int | None
    paragraph_id: str | None = None

    @property
    def location(self) -> str:
        if self.page_start and self.page_end and self.page_start != self.page_end:
            return f"{self.section_title} 第 {self.page_start}-{self.page_end} 页"
        if self.page_start:
            return f"{self.section_title} 第 {self.page_start} 页"
        return self.section_title


@dataclass(frozen=True)
class RetrievalHit:
    chunk: DocumentChunk
    score: float


class LocalRetriever:
    """Small TF-IDF style retriever that requires no external service."""

    def __init__(self, paper: Paper) -> None:
        self.paper = paper
        self.chunks = build_chunks(paper)
        self.doc_tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self.doc_freq = build_doc_freq(self.doc_tokens)
        self.total_docs = max(len(self.doc_tokens), 1)

    def search(self, query: str, k: int = 5) -> list[RetrievalHit]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return [RetrievalHit(chunk=chunk, score=0.0) for chunk in self.chunks[:k]]

        query_counts = Counter(query_tokens)
        scored: list[RetrievalHit] = []
        for chunk, tokens in zip(self.chunks, self.doc_tokens, strict=False):
            score = self._score(query_counts, Counter(tokens))
            if score > 0:
                scored.append(RetrievalHit(chunk=chunk, score=score))
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[:k] if scored else [RetrievalHit(chunk=chunk, score=0.0) for chunk in self.chunks[:k]]

    def _score(self, query_counts: Counter[str], doc_counts: Counter[str]) -> float:
        score = 0.0
        doc_len = sum(doc_counts.values()) or 1
        for token, query_count in query_counts.items():
            if token not in doc_counts:
                continue
            idf = math.log((self.total_docs + 1) / (self.doc_freq.get(token, 0) + 1)) + 1.0
            tf = doc_counts[token] / doc_len
            score += query_count * tf * idf
        return score


def build_chunks(paper: Paper) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for section in paper.sections:
        if section.paragraphs:
            chunks.extend(chunk_from_paragraphs(section))
        elif section.content.strip():
            chunks.append(
                DocumentChunk(
                    id=section.id,
                    text=section.content,
                    section_id=section.id,
                    section_title=section.title,
                    page_start=section.page_start,
                    page_end=section.page_end,
                )
            )
    return chunks


def chunk_from_paragraphs(section: PaperSection) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for paragraph in section.paragraphs:
        chunks.append(
            DocumentChunk(
                id=paragraph.id,
                text=paragraph.text,
                section_id=section.id,
                section_title=section.title,
                page_start=paragraph.page or section.page_start,
                page_end=paragraph.page or section.page_end,
                paragraph_id=paragraph.id,
            )
        )
    return chunks


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def build_doc_freq(token_lists: list[list[str]]) -> dict[str, int]:
    doc_freq: dict[str, int] = {}
    for tokens in token_lists:
        for token in set(tokens):
            doc_freq[token] = doc_freq.get(token, 0) + 1
    return doc_freq
