from papercoach.services.pdf_parser import extract_abstract, extract_sections_from_text


def test_extract_abstract_and_sections_from_text() -> None:
    text = """
    A Useful Agent Paper
    Abstract
    This paper studies agent reading workflows and evidence-bound feedback.
    1 Introduction
    Existing summarizers are passive and do not check user understanding.
    2 Method
    We propose staged navigation, questions, evaluation, and blog fragments.
    3 Results
    Users cite more evidence after using the system.
    """

    abstract = extract_abstract(text)
    sections = extract_sections_from_text(text)

    assert "agent reading workflows" in abstract
    assert [section.title for section in sections] == ["Abstract", "Introduction", "Method", "Results"]
    assert "staged navigation" in sections[2].content


def test_split_numbered_headings_and_table_headers() -> None:
    text = """
    1
    Introduction
    This section motivates the agent problem.
    2
    Method
    The method has three modules.
    2.1
    Automatic Curriculum
    The curriculum proposes tasks.
    Table 1: Main results.
    Method
    Score
    VOYAGER
    99
    3.3
    Evaluation Results
    VOYAGER improves long-horizon task completion.
    """

    sections = extract_sections_from_text(text)

    assert [section.title for section in sections] == [
        "Introduction",
        "Method",
        "Automatic Curriculum",
        "Evaluation Results",
    ]
