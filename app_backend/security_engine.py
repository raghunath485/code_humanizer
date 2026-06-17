from __future__ import annotations

import re


SECURITY_RULES = [
    ("eval() usage", r"\beval\s*\(", "High", "Avoid evaluating runtime strings directly."),
    ("exec() usage", r"\bexec\s*\(", "High", "Execute explicit logic paths instead of dynamic code strings."),
    ("SQL injection risk", r"(SELECT|INSERT|UPDATE|DELETE).*(\+|%s|\{)", "High", "Use parameterized queries."),
    ("Hardcoded credentials", r"(password|secret|token|api_key)\s*[:=]\s*['\"][^'\"]+['\"]", "High", "Move secrets into environment variables or a vault."),
    ("Unsafe file operation", r"\bopen\s*\([^,]+,\s*['\"]w", "Medium", "Validate file paths and write targets before modifying files."),
    ("Unsafe deserialization", r"\bpickle\.loads\b|\byaml\.load\b", "High", "Use safe loaders or structured serialization formats."),
    ("XSS risk", r"innerHTML\s*=|dangerouslySetInnerHTML", "Medium", "Sanitize untrusted content before rendering."),
    ("Command injection risk", r"\bos\.system\b|\bsubprocess\.(Popen|run)\b", "High", "Whitelist commands and avoid string-built shell invocations."),
]


def analyze_security(code: str) -> dict[str, object]:
    findings: list[dict[str, str]] = []

    for title, pattern, risk, fix in SECURITY_RULES:
        if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
            findings.append(
                {
                    "title": title,
                    "risk": risk,
                    "explanation": f"The snippet contains a pattern associated with {title.lower()}.",
                    "recommended_fix": fix,
                }
            )

    highest_risk = "Low"
    if any(finding["risk"] == "High" for finding in findings):
        highest_risk = "High"
    elif any(finding["risk"] == "Medium" for finding in findings):
        highest_risk = "Medium"

    return {
        "risk_level": highest_risk,
        "findings": findings,
    }
