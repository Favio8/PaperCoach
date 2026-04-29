from papercoach.config import Settings
from papercoach.schemas.papers import Paper, PaperParagraph, PaperSection
from papercoach.services.session_service import SessionService
from papercoach.storage import JsonStore


def test_session_navigation_answer_and_blog_fragment(tmp_path) -> None:
    store = JsonStore(Settings(data_dir=tmp_path))
    paper = Paper(
        paper_id="paper_test",
        title="Test Paper",
        abstract="This paper proposes guided paper reading.",
        sections=[
            PaperSection(
                id="sec_problem",
                title="Introduction",
                page_start=1,
                page_end=1,
                content="Existing PDF QA tools summarize papers passively and miss evidence.",
                paragraphs=[
                    PaperParagraph(
                        id="para_problem",
                        index=1,
                        text="Existing PDF QA tools summarize papers passively and miss evidence.",
                        page=1,
                    )
                ],
            ),
            PaperSection(
                id="sec_method",
                title="Method",
                page_start=2,
                page_end=2,
                content="PaperCoach uses staged navigation, Socratic questions, and feedback.",
                paragraphs=[
                    PaperParagraph(
                        id="para_method",
                        index=1,
                        text="PaperCoach uses staged navigation, Socratic questions, and feedback.",
                        page=2,
                    )
                ],
            ),
        ],
    )
    store.save_paper(paper)

    service = SessionService(store)
    session = service.create("paper_test")
    navigation = service.navigation(session.session_id, "Problem")
    question = navigation.questions[0]
    answer = service.submit_answer(
        session.session_id,
        question.id,
        "In Introduction 第 1 页, the main problem is that PDF QA tools summarize passively "
        "and miss evidence, so users cannot verify their understanding.",
    )
    fragment = service.blog_fragment(session.session_id, "Problem")

    assert navigation.stage == "Problem"
    assert navigation.reading_targets[0].title == "Introduction"
    assert "当前模块：论文要解决的问题（Problem）" in navigation.goal
    assert any("作者要提升的是认知能力" in point for point in navigation.focus_points)
    assert question.evidence_location
    assert answer.scores["expression"] >= 2
    assert answer.feedback_source == "local"
    assert "## Problem" in fragment.content
