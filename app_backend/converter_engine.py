from __future__ import annotations

import re

from app_backend.concept_engine import ConceptPlan, apply_mode_guidance
from app_backend.language_tools import comment_prefix_for, detect_language


SUPPORTED_LANGUAGES = {"c", "cpp", "java", "python"}


def _extract_comments(code: str) -> list[str]:
    return re.findall(r"//.*?$|#.*?$|/\*.*?\*/", code, re.MULTILINE | re.DOTALL)


def _unsupported_features(code: str, source_language: str, target_language: str) -> list[str]:
    warnings: list[str] = []

    if re.search(r"\btemplate\s*<", code) and target_language not in {"cpp", "java"}:
        warnings.append("Template-heavy logic may require manual adaptation.")
    if re.search(r"\bmalloc\b|\bfree\b", code) and target_language == "python":
        warnings.append("Manual memory management was detected and cannot be represented directly in Python.")
    if re.search(r"\bThread\b|\bpthread_", code) and target_language in {"c", "cpp"}:
        warnings.append("Threading primitives may require library-specific rewrites.")
    if re.search(r"\btry\b|\bcatch\b", code) and target_language == "c":
        warnings.append("Exception handling does not map directly into C.")
    if source_language == target_language:
        warnings.append("Source and target languages are the same, so conversion behaves like a readability refactor.")

    return warnings


def _convert_signature(code: str, source_language: str, target_language: str) -> str:
    stripped = code.strip()
    if not stripped:
        return ""

    if target_language == "python":
        return re.sub(r"\b(public|private|protected|static|final)\b", "", stripped)
    if target_language == "java":
        return re.sub(r"\bdef\s+(\w+)\(", r"public static void \1(", stripped)
    if target_language == "c":
        return stripped.replace("System.out.println", "printf").replace("cout <<", "printf(")
    if target_language == "cpp":
        return stripped.replace("printf(", "std::cout << ").replace("System.out.println", "std::cout <<")

    return stripped


def convert_code(
    code: str,
    source_language: str,
    target_language: str,
    concept_plan: ConceptPlan,
    refactor_mode: str,
) -> dict[str, object]:
    resolved_source = detect_language(code, source_language)
    warnings = _unsupported_features(code, resolved_source, target_language)
    comments = _extract_comments(code)
    transformed = _convert_signature(code, resolved_source, target_language)
    transformed = apply_mode_guidance(transformed, refactor_mode, target_language)

    prefix = comment_prefix_for(target_language)
    header_lines = [
        f"{prefix} Converted from {resolved_source} to {target_language}.",
        f"{prefix} Conversion guidance: preserve functionality and adapt idioms carefully.",
    ]

    if concept_plan.directives:
        header_lines.append(f"{prefix} Concept plan: {' | '.join(concept_plan.directives)}")

    if comments:
        header_lines.append(f"{prefix} Preserved comment hints: {' '.join(comment.strip() for comment in comments[:2])}")

    confidence = max(35, 92 - len(warnings) * 12 - abs(len(code.splitlines()) - len(transformed.splitlines())))

    return {
        "source_language": resolved_source,
        "target_language": target_language,
        "converted_code": "\n".join(header_lines) + "\n" + transformed,
        "confidence_score": confidence,
        "unsupported_features": warnings,
        "warnings": warnings or ["No major conversion blockers detected in heuristic pass."],
    }
