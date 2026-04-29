from __future__ import annotations

from pathlib import Path
import shutil

from papercoach.core.ids import new_id
from papercoach.errors import ValidationError
from papercoach.schemas.papers import Paper
from papercoach.services.pdf_parser import PdfParser
from papercoach.storage import JsonStore


class PaperService:
    def __init__(self, store: JsonStore, parser: PdfParser | None = None) -> None:
        self.store = store
        self.parser = parser or PdfParser()

    def create_from_upload(self, filename: str, content: bytes) -> Paper:
        suffix = Path(filename or "paper.pdf").suffix.lower()
        if suffix != ".pdf":
            raise ValidationError("Only PDF uploads are supported in the MVP.")
        if not content:
            raise ValidationError("Uploaded PDF is empty.")

        paper_id = new_id("paper")
        upload_path = self.store.upload_path(paper_id, suffix=".pdf")
        upload_path.write_bytes(content)

        paper = self.parser.parse(upload_path, paper_id=paper_id)
        self.store.save_paper(paper)
        return paper

    def create_from_local_pdf(self, source_path: str | Path) -> Paper:
        source = Path(source_path).expanduser()
        if not source.exists():
            raise ValidationError(f"PDF file does not exist: {source}")
        if source.suffix.lower() != ".pdf":
            raise ValidationError("Only PDF files can be imported from Zotero.")

        paper_id = new_id("paper")
        upload_path = self.store.upload_path(paper_id, suffix=".pdf")
        shutil.copy2(source, upload_path)

        paper = self.parser.parse(upload_path, paper_id=paper_id)
        self.store.save_paper(paper)
        return paper

    def get(self, paper_id: str) -> Paper:
        return self.store.load_paper(paper_id)

    def list(self) -> list[Paper]:
        return self.store.list_papers()

    def render_page_png(self, paper_id: str, page_number: int, scale: float = 2.0) -> bytes:
        paper = self.store.load_paper(paper_id)
        if paper.source_file is None:
            raise ValidationError("This paper has no source PDF file.")

        source = Path(paper.source_file)
        if not source.exists():
            raise ValidationError(f"Source PDF file does not exist: {source}")
        if page_number < 1:
            raise ValidationError("Page number must be greater than or equal to 1.")

        try:
            import fitz
        except ImportError as exc:  # pragma: no cover - dependency is declared for runtime
            raise RuntimeError("PyMuPDF is required to render PDF pages.") from exc

        with fitz.open(source) as doc:
            if page_number > doc.page_count:
                raise ValidationError(f"Page number exceeds PDF page count: {doc.page_count}.")
            page = doc[page_number - 1]
            matrix = fitz.Matrix(scale, scale)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            return pixmap.tobytes("png")
