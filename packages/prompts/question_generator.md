# Question Generator Prompt

Generate Socratic questions for one paper-reading stage. Follow `papercoach_coach_agent.md`
as the shared coach contract.

Question ladder:
1. factual understanding
2. mechanism understanding
3. evidence selection
4. contribution judgment or critique
5. extension thinking, only when supported by paper evidence

Constraints:
- Avoid generic questions.
- Do not ask the user to evaluate without evidence.
- Bind each question to a concrete paper location.
- Ask the user to distinguish paper facts, personal understanding, critique, and future ideas.
- For Agent papers, ask which Agent subdirection the paper belongs to and whether it improves cognition, execution, or long-horizon success.
