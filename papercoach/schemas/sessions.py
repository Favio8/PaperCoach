from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from papercoach.core.constants import READING_STAGES


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReadingTarget(BaseModel):
    type: str
    id: str
    title: str
    page_start: int | None = None
    page_end: int | None = None
    reason: str = ""

    @property
    def label(self) -> str:
        if self.page_start and self.page_end and self.page_start != self.page_end:
            return f"{self.title} 第 {self.page_start}-{self.page_end} 页"
        if self.page_start:
            return f"{self.title} 第 {self.page_start} 页"
        return self.title


class Question(BaseModel):
    id: str
    stage: str
    question: str
    evidence_location: str
    kind: str


class UserAnswer(BaseModel):
    question_id: str
    stage: str
    answer: str
    feedback: str = ""
    scores: dict[str, int] = Field(default_factory=dict)
    reread_suggestions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class BlogFragment(BaseModel):
    stage: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class Session(BaseModel):
    session_id: str
    paper_id: str
    current_stage: str = READING_STAGES[0]
    completed_stages: list[str] = Field(default_factory=list)
    reading_targets: list[ReadingTarget] = Field(default_factory=list)
    pending_questions: list[Question] = Field(default_factory=list)
    user_answers: list[UserAnswer] = Field(default_factory=list)
    blog_fragments: list[BlogFragment] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()


class CreateSessionRequest(BaseModel):
    paper_id: str


class CreateSessionResponse(BaseModel):
    session_id: str
    paper_id: str
    current_stage: str


class NavigationRequest(BaseModel):
    stage: str


class NavigationResponse(BaseModel):
    stage: str
    reading_targets: list[ReadingTarget]
    goal: str
    focus_points: list[str]
    questions: list[Question]


class AnswerRequest(BaseModel):
    question_id: str
    answer: str


class AnswerResponse(BaseModel):
    feedback: str
    scores: dict[str, int]
    reread_suggestions: list[str]
    understood: bool
    feedback_source: str = "local"
    feedback_provider: str = "local"


class BlogFragmentRequest(BaseModel):
    stage: str


class BlogFragmentResponse(BaseModel):
    stage: str
    content: str
