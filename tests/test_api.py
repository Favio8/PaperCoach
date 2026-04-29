import fitz
from fastapi.testclient import TestClient

from papercoach.app import create_app
from papercoach.config import Settings
from papercoach.schemas.papers import Paper, PaperParagraph, PaperSection


def test_session_api_flow_without_pdf_upload(tmp_path) -> None:
    app = create_app(Settings(data_dir=tmp_path, llm_provider="local"))
    app.state.store.save_paper(
        Paper(
            paper_id="paper_test",
            title="Test Paper",
            sections=[
                PaperSection(
                    id="sec_intro",
                    title="Introduction",
                    page_start=1,
                    page_end=1,
                    content="Existing methods lack active reading guidance and feedback.",
                    paragraphs=[
                        PaperParagraph(
                            id="para_intro",
                            index=1,
                            text="Existing methods lack active reading guidance and feedback.",
                            page=1,
                        )
                    ],
                )
            ],
        )
    )
    client = TestClient(app)

    create_response = client.post("/api/sessions", json={"paper_id": "paper_test"})
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    nav_response = client.post(f"/api/sessions/{session_id}/navigation", json={"stage": "Problem"})
    assert nav_response.status_code == 200
    question_id = nav_response.json()["questions"][0]["id"]

    answer_response = client.post(
        f"/api/sessions/{session_id}/answers",
        json={
            "question_id": question_id,
            "answer": "Introduction 第 1 页 states that existing methods lack active guidance "
            "and feedback, therefore the problem is not only summarization but learning support.",
        },
    )
    assert answer_response.status_code == 200
    assert "scores" in answer_response.json()
    assert answer_response.json()["feedback_source"] == "local"

    blog_response = client.post(
        f"/api/sessions/{session_id}/blog-fragments",
        json={"stage": "Problem"},
    )
    assert blog_response.status_code == 200
    assert "## Problem" in blog_response.json()["content"]


def test_web_index_is_served(tmp_path) -> None:
    client = TestClient(create_app(Settings(data_dir=tmp_path, llm_provider="local")))

    response = client.get("/")

    assert response.status_code == 200
    assert "PaperCoach" in response.text
    assert "AI 阅读教练" in response.text


def test_static_frontend_assets_are_served(tmp_path) -> None:
    client = TestClient(create_app(Settings(data_dir=tmp_path, llm_provider="local")))

    script_response = client.get("/static/app.js")
    style_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "exportNotes" in script_response.text
    assert "submitAnswer" in script_response.text
    assert "importFromZoteroPath" in script_response.text
    assert style_response.status_code == 200
    assert ".settings-modal" in style_response.text


def test_import_zotero_pdf_from_local_path(tmp_path) -> None:
    pdf_path = tmp_path / "zotero-paper.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Zotero Test Paper\nAbstract\nThis paper is imported from Zotero for testing.",
    )
    doc.save(pdf_path)
    doc.close()

    client = TestClient(create_app(Settings(data_dir=tmp_path, llm_provider="local")))

    response = client.post("/api/papers/import-zotero", json={"path": str(pdf_path)})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "parsed"
    imported = client.get(f"/api/papers/{payload['paper_id']}").json()
    assert imported["source_file"].endswith(".pdf")
    assert "uploads" in imported["source_file"]

    image_response = client.get(f"/api/papers/{payload['paper_id']}/pages/1/image")
    assert image_response.status_code == 200
    assert image_response.headers["content-type"] == "image/png"
    assert image_response.content.startswith(b"\x89PNG")
