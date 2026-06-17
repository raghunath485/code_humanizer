from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from app_backend.concept_engine import ConceptPlan, apply_mode_guidance, build_concept_plan
from app_backend.language_tools import comment_prefix_for, detect_language
from app_backend.schemas import HumanizeOptions
from app_backend.quality_engine import score_quality
from app_backend.security_engine import analyze_security


SHORTHAND_MAP = {
    "acct": "account",
    "ai": "artificialIntelligence",
    "addr": "address",
    "amt": "amount",
    "api": "api",
    "bot": "assistant",
    "calc": "calculate",
    "chat": "chat",
    "conv": "conversation",
    "convo": "conversation",
    "ctx": "context",
    "dta": "data",
    "emb": "embedding",
    "hist": "history",
    "hndl": "handle",
    "intent": "intent",
    "kb": "knowledgeBase",
    "llm": "languageModel",
    "mem": "memory",
    "msg": "message",
    "nxt": "next",
    "resp": "response",
    "sess": "session",
    "svc": "service",
    "sys": "system",
    "usr": "user",
    "vec": "vector",
}

CHATBOT_SIGNAL_PATTERNS = {
    "message handling": r"\bmessage\b|\bmessages\b|\bmsg\b|\bchat\b|\bconversation\b|\bconvo\b",
    "prompt construction": r"\bprompt\b|\bsystem\b|\bassistant\b|\buser_prompt\b|\bsys_prompt\b",
    "model invocation": r"\bllm\b|\bopenai\b|\banthropic\b|\bgenerate\b|\bgen_resp\b|\bgenResp\b|\bcompletion\b",
    "memory or session state": r"\bmemory\b|\bhistory\b|\bhist\b|\bsession\b|\bsess\b|\bcontext\b|\bctx\b",
    "retrieval flow": r"\brag\b|\bretriev\w*\b|\bembedding\b|\bvector\b|\bknowledge\b",
    "intent routing": r"\bintent\b|\bclassif\w*\b|\broute\b|\bhandler\b|\bhndl\b",
}


@dataclass
class InsightCard:
    title: str
    body: str


def calculate_complexity(code: str) -> dict[str, object]:
    conditionals = len(re.findall(r"\bif\b|\belse\b|\bswitch\b", code))
    loops = len(re.findall(r"\bfor\b|\bwhile\b", code))
    functions = len(re.findall(r"\bdef\b|\bfunction\b|=>", code))
    score = conditionals + loops * 2 + functions

    return {
        "score": score,
        "level": "Low" if score < 5 else "Medium" if score < 12 else "High",
        "conditionals": conditionals,
        "loops": loops,
        "functions": functions,
    }


def detect_dead_code(code: str) -> list[str]:
    findings: list[str] = []

    if re.search(r"if\s*\(\s*false\s*\)", code, re.IGNORECASE):
        findings.append("Found condition that will never execute.")
    if re.search(r"return\s+.*\n\s+return", code):
        findings.append("Multiple sequential returns detected.")

    for variable in re.findall(r"(?:const|let|var)\s+(\w+)\s*=", code):
        if len(re.findall(rf"\b{variable}\b", code)) == 1:
            findings.append(f"Possible unused variable: {variable}")

    return findings


def detect_chatbot_signals(code: str) -> list[str]:
    return [
        label
        for label, pattern in CHATBOT_SIGNAL_PATTERNS.items()
        if re.search(pattern, code, re.IGNORECASE)
    ]


def split_identifier(identifier: str) -> list[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", identifier)
    expanded = re.sub(r"[_-]+", " ", expanded).strip()
    return [part for part in expanded.split() if part]


def match_identifier_style(identifier: str) -> str:
    if "_" in identifier:
        return "snake"
    if re.fullmatch(r"[A-Z0-9_]+", identifier):
        return "constant"
    if re.match(r"^[A-Z]", identifier):
        return "pascal"
    return "camel"


def to_style(words: list[str], style: str) -> str:
    if not words:
        return ""

    if style == "snake":
        return "_".join(word.lower() for word in words)
    if style == "constant":
        return "_".join(word.upper() for word in words)
    if style == "pascal":
        return "".join(word[:1].upper() + word[1:].lower() for word in words)

    first, *rest = words
    return "".join([first.lower(), *[word[:1].upper() + word[1:].lower() for word in rest]])


def expand_identifier(identifier: str) -> str:
    words = split_identifier(identifier)
    expanded_words = [SHORTHAND_MAP.get(word.lower(), word) for word in words]
    return to_style(expanded_words, match_identifier_style(identifier))


def collect_rename_map(code: str) -> dict[str, str]:
    rename_map: dict[str, str] = {}
    declaration_pattern = re.compile(r"\b(?:const|let|var|function|class|def)\s+([A-Za-z_][A-Za-z0-9_]*)")
    parameter_pattern = re.compile(r"\(([^(){}]*)\)\s*=>|\b(?:function|def)\b[^(]*\(([^()]*)\)")

    for match in declaration_pattern.finditer(code):
        original = match.group(1)
        expanded = expand_identifier(original)
        if original != expanded:
            rename_map[original] = expanded

    for match in parameter_pattern.finditer(code):
        raw_params = match.group(1) or match.group(2) or ""
        for param in raw_params.split(","):
            candidate = param.strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", candidate):
                expanded = expand_identifier(candidate)
                if candidate != expanded:
                    rename_map[candidate] = expanded

    return rename_map


def replace_outside_strings(code: str, rename_map: dict[str, str]) -> str:
    updated = code
    for original, expanded in rename_map.items():
        updated = re.sub(rf"(?<!\.)\b{re.escape(original)}\b", expanded, updated)
    return updated


def rename_identifiers(code: str) -> str:
    rename_map = collect_rename_map(code)
    return replace_outside_strings(code, rename_map) if rename_map else code


def add_docstrings(code: str, language: str) -> str:
    if language != "python":
        return code

    pattern = re.compile(r"def\s+(\w+)\((.*?)\):")

    def replacer(match: re.Match[str]) -> str:
        name = match.group(1)
        params = match.group(2)
        return (
            f"def {name}({params}):\n"
            f"    \"\"\"\n"
            f"    Humanized function: {name}\n"
            f"    Parameters: {params or 'None'}\n"
            f"    \"\"\""
        )

    return pattern.sub(replacer, code)


def normalize_spacing(code: str, language: str) -> str:
    lines = [re.sub(r"\s+$", "", line.replace("\t", "  ")) for line in code.replace("\r\n", "\n").split("\n")]
    if language == "python":
        return "\n".join(re.sub(r"\s+", " ", line).replace(" ,", ",").replace(" .", ".") if line.strip() else "" for line in lines)

    return "\n".join(re.sub(r"\s+", " ", line).replace(" ,", ",").replace(" .", ".") if line.strip() else "" for line in lines)


def build_summary_comment(code: str, language: str, chatbot_signals: list[str]) -> str:
    line_count = len([line for line in code.splitlines() if line.strip()])
    prefix = comment_prefix_for(language)
    parts = [f"Humanized summary: this {language} snippet spans {line_count} active lines."]
    if chatbot_signals:
        parts.append(f"Detected chatbot-oriented areas: {', '.join(chatbot_signals)}.")
    return f"{prefix} {' '.join(parts)}"


def summarize_code(code: str, language: str, chatbot_signals: list[str], concept_plan: ConceptPlan) -> list[InsightCard]:
    loops = len(re.findall(r"\bfor\b|\bwhile\b|\bmap\b|\bfilter\b|\breduce\b", code))
    returns = len(re.findall(r"\breturn\b", code))
    cards = [
        InsightCard("Detected language", f"The platform classified this snippet as {language}."),
        InsightCard("Control flow", f"The snippet contains {loops} loop-style operations and {returns} return statements."),
        InsightCard(
            "Concept plan",
            f"Selected concepts: {', '.join(concept_plan.selected) if concept_plan.selected else 'None specified'}.",
        ),
    ]

    if chatbot_signals:
        cards.append(
            InsightCard(
                "Human-readable walkthrough",
                "The snippet appears to orchestrate message, prompt, or stateful chatbot logic and was renamed to make those roles easier to follow.",
            )
        )

    return cards


def humanize(code: str, options: HumanizeOptions | None = None) -> dict[str, object]:
    settings = options or HumanizeOptions()
    result = code.strip()
    if not result:
        return {"code": "", "insights": []}

    language = detect_language(result, settings.language_hint)
    concept_plan = build_concept_plan(settings.concept_preferences)
    chatbot_signals = detect_chatbot_signals(result)

    if settings.rename_identifiers:
        result = rename_identifiers(result)
    if settings.add_docstrings:
        result = add_docstrings(result, language)
    if settings.normalize_spacing:
        result = normalize_spacing(result, language)

    result = apply_mode_guidance(result, settings.refactor_mode, language)

    if settings.add_summary_comment:
        result = f"{build_summary_comment(result, language, chatbot_signals)}\n{result}"

    complexity = calculate_complexity(result) if settings.explain_complexity else {}
    dead_code = detect_dead_code(result) if settings.detect_dead_code else []
    security = analyze_security(result)
    quality = score_quality(result, complexity, dead_code, security["findings"])

    insights = [asdict(card) for card in summarize_code(result, language, chatbot_signals, concept_plan)]
    if complexity:
        insights.append({"title": "Complexity", "body": f"Score: {complexity['score']}, Level: {complexity['level']}"})
    if dead_code:
        insights.append({"title": "Dead Code Findings", "body": "\n".join(dead_code)})

    return {
        "code": result,
        "insights": insights,
        "language": language,
        "chatbot_signals": chatbot_signals,
        "profile": settings.target_profile,
        "complexity": complexity,
        "dead_code": dead_code,
        "concept_plan": {
            "selected": concept_plan.selected,
            "avoided": concept_plan.avoided[:8],
            "directives": concept_plan.directives,
        },
        "quality": quality,
        "security": security,
        "mode": settings.refactor_mode,
    }
