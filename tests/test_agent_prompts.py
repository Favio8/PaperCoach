from papercoach.agents.evaluator import AnswerEvaluator
from papercoach.agents.prompts import COACH_SYSTEM_PROMPT
from papercoach.schemas.sessions import Question


def test_coach_prompt_excludes_implementation_module() -> None:
    assert "Implementation" in COACH_SYSTEM_PROMPT
    assert "不要包含" in COACH_SYSTEM_PROMPT
    assert "【本轮阅读导航】" in COACH_SYSTEM_PROMPT
    assert "【5. 博客可用版本】" in COACH_SYSTEM_PROMPT


def test_fallback_feedback_uses_required_coach_sections() -> None:
    question = Question(
        id="q_test",
        stage="Problem",
        question="作者指出的核心问题是什么？",
        evidence_location="Introduction 第 2 页",
        kind="critique",
    )
    feedback = AnswerEvaluator()._feedback(
        question=question,
        answer="Introduction 第 2 页说明，已有方法缺少持续学习能力，因此无法长期积累技能。",
        scores={"accuracy": 4, "completeness": 3, "depth": 3, "evidence": 5, "expression": 3},
        reread_suggestions=["Introduction 第 2 页"],
        hits=[],
    )

    assert "【1. 你回答中的亮点】" in feedback
    assert "【2. 需要修正的地方】" in feedback
    assert "【3. 建议回读的位置】" in feedback
    assert "【4. 可以继续挖深的问题】" in feedback
    assert "【5. 博客可用版本】" in feedback
    assert "【6. 下一步阅读导航】" in feedback

