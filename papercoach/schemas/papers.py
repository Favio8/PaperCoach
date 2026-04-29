from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PaperParagraph(BaseModel):
    id: str
    index: int
    text: str
    page: int | None = None


class PaperSection(BaseModel):
    id: str
    title: str
    level: int = 1
    page_start: int | None = None
    page_end: int | None = None
    content: str
    paragraphs: list[PaperParagraph] = Field(default_factory=list)


class PaperFigure(BaseModel):
    id: str
    caption: str
    page: int | None = None


class PaperTable(BaseModel):
    id: str
    caption: str
    page: int | None = None


class Paper(BaseModel):
    paper_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    sections: list[PaperSection] = Field(default_factory=list)
    figures: list[PaperFigure] = Field(default_factory=list)
    tables: list[PaperTable] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    source_file: Path | None = None
    created_at: datetime = Field(default_factory=utc_now)


class PaperUploadResponse(BaseModel):
    paper_id: str
    title: str
    status: str = "parsed"


class ZoteroImportRequest(BaseModel):
    path: str
