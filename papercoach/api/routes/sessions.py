from fastapi import APIRouter, Request

from papercoach.schemas.sessions import (
    AnswerRequest,
    AnswerResponse,
    BlogFragmentRequest,
    BlogFragmentResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    NavigationRequest,
    NavigationResponse,
    Session,
)
from papercoach.services import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse)
def create_session(request: Request, payload: CreateSessionRequest) -> CreateSessionResponse:
    service: SessionService = request.app.state.session_service
    session = service.create(payload.paper_id)
    return CreateSessionResponse(
        session_id=session.session_id,
        paper_id=session.paper_id,
        current_stage=session.current_stage,
    )


@router.get("/{session_id}", response_model=Session)
def get_session(request: Request, session_id: str) -> Session:
    service: SessionService = request.app.state.session_service
    return service.get(session_id)


@router.post("/{session_id}/navigation", response_model=NavigationResponse)
def get_navigation(
    request: Request,
    session_id: str,
    payload: NavigationRequest,
) -> NavigationResponse:
    service: SessionService = request.app.state.session_service
    return service.navigation(session_id=session_id, stage=payload.stage)


@router.post("/{session_id}/answers", response_model=AnswerResponse)
def submit_answer(
    request: Request,
    session_id: str,
    payload: AnswerRequest,
) -> AnswerResponse:
    service: SessionService = request.app.state.session_service
    return service.submit_answer(
        session_id=session_id,
        question_id=payload.question_id,
        answer=payload.answer,
    )


@router.post("/{session_id}/blog-fragments", response_model=BlogFragmentResponse)
def build_blog_fragment(
    request: Request,
    session_id: str,
    payload: BlogFragmentRequest,
) -> BlogFragmentResponse:
    service: SessionService = request.app.state.session_service
    return service.blog_fragment(session_id=session_id, stage=payload.stage)
