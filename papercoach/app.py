from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from papercoach.api.routes import health, papers, sessions
from papercoach.config import Settings
from papercoach.errors import NotFoundError, ValidationError
from papercoach.services import PaperService, SessionService, build_llm_client
from papercoach.storage import JsonStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = JsonStore(settings)
    web_dir = Path(__file__).parent / "web"

    app = FastAPI(
        title="PaperCoach API",
        version="0.1.0",
        description="A Socratic Python agent for guided research paper understanding.",
    )
    app.state.settings = settings
    app.state.store = store
    app.state.paper_service = PaperService(store)
    app.state.llm_client = build_llm_client(settings)
    app.state.session_service = SessionService(store, llm_client=app.state.llm_client)

    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ValidationError, validation_handler)

    if web_dir.exists():
        app.mount("/static", StaticFiles(directory=web_dir), name="static")

        @app.get("/", response_class=HTMLResponse, include_in_schema=False)
        def web_app() -> HTMLResponse:
            return HTMLResponse((web_dir / "index.html").read_text(encoding="utf-8"))

    app.include_router(health.router)
    app.include_router(papers.router, prefix="/api")
    app.include_router(sessions.router, prefix="/api")
    return app


async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
