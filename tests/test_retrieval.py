from papercoach.schemas.papers import Paper, PaperParagraph, PaperSection
from papercoach.services.retrieval import LocalRetriever


def test_local_retriever_returns_relevant_section() -> None:
    paper = Paper(
        paper_id="paper_test",
        title="Test Paper",
        sections=[
            PaperSection(
                id="sec_intro",
                title="Introduction",
                content="The problem is that existing summarizers are passive.",
                paragraphs=[
                    PaperParagraph(
                        id="para_intro",
                        index=1,
                        text="The problem is that existing summarizers are passive.",
                        page=1,
                    )
                ],
            ),
            PaperSection(
                id="sec_method",
                title="Method",
                content="The method uses staged navigation and answer feedback.",
                paragraphs=[
                    PaperParagraph(
                        id="para_method",
                        index=1,
                        text="The method uses staged navigation and answer feedback.",
                        page=2,
                    )
                ],
            ),
        ],
    )

    hits = LocalRetriever(paper).search("staged navigation feedback", k=1)

    assert hits[0].chunk.section_title == "Method"
