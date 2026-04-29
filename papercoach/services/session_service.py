from __future__ import annotations

from papercoach.agents import AnswerEvaluator, BlogDraftBuilder, QuestionGenerator, ReadingNavigator
from papercoach.core.constants import READING_STAGES
from papercoach.core.ids import new_id
from papercoach.errors import ValidationError
from papercoach.schemas.sessions import (
    AnswerResponse,
    BlogFragment,
    BlogFragmentResponse,
    NavigationResponse,
    Session,
    UserAnswer,
)
from papercoach.services.llm import LLMClient
from papercoach.services.retrieval import LocalRetriever
from papercoach.storage import JsonStore


class SessionService:
    def __init__(
        self,
        store: JsonStore,
        navigator: ReadingNavigator | None = None,
        evaluator: AnswerEvaluator | None = None,
        blog_builder: BlogDraftBuilder | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.store = store
        question_generator = QuestionGenerator()
        self.navigator = navigator or ReadingNavigator(question_generator=question_generator)
        self.evaluator = evaluator or AnswerEvaluator(llm_client=llm_client)
        self.blog_builder = blog_builder or BlogDraftBuilder(llm_client=llm_client)

    def create(self, paper_id: str) -> Session:
        self.store.load_paper(paper_id)
        session = Session(session_id=new_id("session"), paper_id=paper_id)
        self.store.save_session(session)
        return session

    def get(self, session_id: str) -> Session:
        return self.store.load_session(session_id)

    def navigation(self, session_id: str, stage: str) -> NavigationResponse:
        self._validate_stage(stage)
        session = self.store.load_session(session_id)
        paper = self.store.load_paper(session.paper_id)
        retriever = LocalRetriever(paper)
        response = self.navigator.build(stage=stage, retriever=retriever)

        session.current_stage = stage
        session.reading_targets = response.reading_targets
        session.pending_questions = response.questions
        session.touch()
        self.store.save_session(session)
        return response

    def submit_answer(self, session_id: str, question_id: str, answer: str) -> AnswerResponse:
        session = self.store.load_session(session_id)
        question = next(
            (candidate for candidate in session.pending_questions if candidate.id == question_id),
            None,
        )
        if question is None:
            raise ValidationError(
                "Question is not active in this session. Request navigation before submitting answers."
            )

        paper = self.store.load_paper(session.paper_id)
        retriever = LocalRetriever(paper)
        response = self.evaluator.evaluate(question=question, answer=answer, retriever=retriever)

        session.user_answers.append(
            UserAnswer(
                question_id=question_id,
                stage=question.stage,
                answer=answer,
                feedback=response.feedback,
                scores=response.scores,
                reread_suggestions=response.reread_suggestions,
            )
        )
        if response.understood and question.stage not in session.completed_stages:
            session.completed_stages.append(question.stage)
            session.current_stage = next_stage(question.stage)

        session.touch()
        self.store.save_session(session)
        return response

    def blog_fragment(self, session_id: str, stage: str) -> BlogFragmentResponse:
        self._validate_stage(stage)
        session = self.store.load_session(session_id)
        paper = self.store.load_paper(session.paper_id)
        retriever = LocalRetriever(paper)
        response = self.blog_builder.build(stage=stage, session=session, retriever=retriever)

        session.blog_fragments = [
            fragment for fragment in session.blog_fragments if fragment.stage != stage
        ]
        session.blog_fragments.append(BlogFragment(stage=stage, content=response.content))
        session.touch()
        self.store.save_session(session)
        return response

    def _validate_stage(self, stage: str) -> None:
        if stage not in READING_STAGES:
            allowed = ", ".join(READING_STAGES)
            raise ValidationError(f"Unknown reading stage '{stage}'. Allowed stages: {allowed}.")


def next_stage(stage: str) -> str:
    try:
        index = READING_STAGES.index(stage)
    except ValueError:
        return READING_STAGES[0]
    if index + 1 >= len(READING_STAGES):
        return READING_STAGES[-1]
    return READING_STAGES[index + 1]
