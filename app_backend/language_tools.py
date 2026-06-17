from __future__ import annotations

import re


COMMENT_PREFIXES = {
    "python": "#",
    "java": "//",
    "cpp": "//",
    "c": "//",
    "javascript": "//",
    "typescript": "//",
    "generic": "//",
}


LANGUAGE_RULES: list[tuple[str, list[str]]] = [
    ("python", [r"\bdef\b", r"\bimport\b", r":\s*$", r"\bself\b"]),
    ("java", [r"\bpublic\s+class\b", r"\bSystem\.out\.println\b", r"\bnew\s+\w+\("]),
    ("cpp", [r"#include\s*<iostream>", r"\bstd::", r"\bcout\s*<<", r"\bint\s+main\s*\("]),
    ("c", [r"#include\s*<stdio.h>", r"\bprintf\s*\(", r"\bscanf\s*\(", r"\bint\s+main\s*\("]),
    ("javascript", [r"\bconst\b", r"\blet\b", r"=>", r"\bfunction\b"]),
    ("typescript", [r"\binterface\b", r"\btype\s+\w+\s*=", r":\s*(string|number|boolean|Promise<)"]),
]


def detect_language(code: str, language_hint: str = "auto") -> str:
    if language_hint and language_hint != "auto":
        return language_hint

    scores: dict[str, int] = {}
    for language, patterns in LANGUAGE_RULES:
        scores[language] = sum(1 for pattern in patterns if re.search(pattern, code, re.MULTILINE))

    best_language = max(scores, key=scores.get, default="generic")
    return best_language if scores.get(best_language, 0) > 0 else "generic"


def comment_prefix_for(language: str) -> str:
    return COMMENT_PREFIXES.get(language, COMMENT_PREFIXES["generic"])


def file_extension_for(language: str) -> str:
    return {
        "python": "py",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
    }.get(language, "txt")
