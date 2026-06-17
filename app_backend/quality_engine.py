from __future__ import annotations

import math
import re


def score_quality(code: str, complexity: dict[str, object], dead_code: list[str], security_findings: list[dict[str, str]]) -> dict[str, object]:
    line_count = max(len([line for line in code.splitlines() if line.strip()]), 1)
    average_line_length = sum(len(line) for line in code.splitlines() or [""]) / max(len(code.splitlines()), 1)
    comment_density = len(re.findall(r"//|#|/\*", code)) / line_count

    readability = max(35, min(98, int(92 - average_line_length / 2 + comment_density * 18)))
    maintainability = max(30, min(96, int(90 - int(complexity.get("score", 0)) * 3 - len(dead_code) * 5)))
    complexity_score = max(20, min(100, int(100 - int(complexity.get("score", 0)) * 6)))
    security_score = max(15, min(100, 100 - len(security_findings) * 18))
    humanization_score = max(30, min(99, int((readability + maintainability + security_score) / 3)))
    overall = math.floor((readability + maintainability + complexity_score + security_score + humanization_score) / 5)

    return {
        "readability": readability,
        "maintainability": maintainability,
        "complexity": complexity_score,
        "security": security_score,
        "humanization": humanization_score,
        "overall": overall,
    }
