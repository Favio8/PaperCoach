from fastapi import APIRouter, File, Query, Request, UploadFile
from fastapi.responses import Response

from papercoach.schemas.papers import Paper, PaperUploadResponse, ZoteroImportRequest
from papercoach.services import PaperService

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("", response_model=PaperUploadResponse)
async def upload_paper(request: Request, file: UploadFile = File(...)) -> PaperUploadResponse:
    service: PaperService = request.app.state.paper_service
    paper = service.create_from_upload(filename=file.filename or "paper.pdf", content=await file.read())
    return PaperUploadResponse(paper_id=paper.paper_id, title=paper.title, status="parsed")


@router.post("/import-zotero", response_model=PaperUploadResponse)
def import_zotero_paper(request: Request, payload: ZoteroImportRequest) -> PaperUploadResponse:
    service: PaperService = request.app.state.paper_service
    paper = service.create_from_local_pdf(payload.path)
    return PaperUploadResponse(paper_id=paper.paper_id, title=paper.title, status="parsed")


@router.get("", response_model=list[Paper])
def list_papers(request: Request) -> list[Paper]:
    service: PaperService = request.app.state.paper_service
    return service.list()


@router.get("/{paper_id}/pages/{page_number}/image")
def render_paper_page(
    request: Request,
    paper_id: str,
    page_number: int,
    scale: float = Query(default=1.5, ge=0.5, le=3.0),
) -> Response:
    service: PaperService = request.app.state.paper_service
    content = service.render_page_png(paper_id=paper_id, page_number=page_number, scale=scale)
    return Response(content=content, media_type="image/png")


@router.get("/{paper_id}", response_model=Paper)
def get_paper(request: Request, paper_id: str) -> Paper:
    service: PaperService = request.app.state.paper_service
    return service.get(paper_id)
