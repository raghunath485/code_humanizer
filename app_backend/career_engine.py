from __future__ import annotations

from app_backend.language_tools import detect_language


def build_career_pack(code: str, language_hint: str, quality: dict[str, object], security: dict[str, object]) -> dict[str, object]:
    language = detect_language(code, language_hint)
    project_summary = (
        f"Designed a multi-language {language.title()} code transformation workflow that improves readability, "
        "surfaces code risks, and generates developer-facing guidance."
    )

    resume_points = [
        "Built a code transformation platform that humanizes and analyzes source code across multiple engineering workflows.",
        "Implemented automated quality scoring, dead-code detection, and security pattern analysis for developer feedback loops.",
        "Designed APIs and UI flows for code refactoring, language conversion, and interview-preparation outputs.",
    ]

    technical_highlights = [
        f"Detected language: {language}",
        f"Overall quality score: {quality.get('overall', 0)}",
        f"Security posture: {security.get('risk_level', 'Low')}",
    ]

    interview_questions = [
        "How would you safely convert logic between strongly typed and dynamically typed languages?",
        "What tradeoffs did you make between heuristic transformation and parser-based refactoring?",
        "How does your platform balance readability, maintainability, and security during refactoring?",
    ]

    interview_answers = [
        "I preserve intent first, then adapt idioms for the target language while returning confidence and warnings when semantics may drift.",
        "Heuristics keep the tool lightweight and fast, but I expose unsupported-feature warnings where a full AST-based pass would be safer.",
        "The pipeline runs quality, dead-code, and security checks after transformation so the user can judge whether the result is production-ready.",
    ]

    complexity_explanation = (
        "Complexity is estimated from branching, loop density, and function count to give a fast signal about how difficult the code may be to maintain."
    )

    return {
        "project_summary": project_summary,
        "resume_bullet_points": resume_points,
        "technical_highlights": technical_highlights,
        "interview_questions": interview_questions,
        "interview_answers": interview_answers,
        "complexity_explanation": complexity_explanation,
    }
