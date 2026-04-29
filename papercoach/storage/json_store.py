from __future__ import annotations

from pathlib import Path

from papercoach.config import Settings
from papercoach.errors import NotFoundError
from papercoach.schemas.papers import Paper
from papercoach.schemas.sessions import Session


class JsonStore:
    """Small local JSON store for the MVP.

    It intentionally keeps persistence simple. The model shapes mirror the API
    schemas, so moving to SQLite/PostgreSQL later should be mechanical.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.papers_dir.mkdir(parents=True, exist_ok=True)
        self.settings.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    def paper_path(self, paper_id: str) -> Path:
        return self.settings.papers_dir / f"{paper_id}.json"

    def session_path(self, session_id: str) -> Path:
        return self.settings.sessions_dir / f"{session_id}.json"

    def upload_path(self, paper_id: str, suffix: str = ".pdf") -> Path:
        return self.settings.uploads_dir / f"{paper_id}{suffix}"

    def save_paper(self, paper: Paper) -> None:
        self._write_json(self.paper_path(paper.paper_id), paper.model_dump_json(indent=2))

    def load_paper(self, paper_id: str) -> Paper:
        path = self.paper_path(paper_id)
        if not path.exists():
            raise NotFoundError(f"Paper not found: {paper_id}")
        return Paper.model_validate_json(path.read_text(encoding="utf-8"))

    def list_papers(self) -> list[Paper]:
        return [
            Paper.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.settings.papers_dir.glob("paper_*.json"))
        ]

    def save_session(self, session: Session) -> None:
        self._write_json(self.session_path(session.session_id), session.model_dump_json(indent=2))

    def load_session(self, session_id: str) -> Session:
        path = self.session_path(session_id)
        if not path.exists():
            raise NotFoundError(f"Session not found: {session_id}")
        return Session.model_validate_json(path.read_text(encoding="utf-8"))

    def list_sessions(self) -> list[Session]:
        return [
            Session.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.settings.sessions_dir.glob("session_*.json"))
        ]

    @staticmethod
    def _write_json(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(f"{path.suffix}.tmp")
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
