from __future__ import annotations

import re
from dataclasses import asdict, dataclass


SHORTHAND_MAP = {
    "acct": "account",
    "ai": "artificialIntelligence",
    "addr": "address",
    "amt": "amount",
    "api": "api",
    "bot": "assistant",
    "btn": "button",
    "cfg": "config",
    "calc": "calculate",
    "chat": "chat",
    "conv": "conversation",
    "convo": "conversation",
    "ctx": "context",
    "cnt": "count",
    "dta": "data",
    "emb": "embedding",
    "hist": "history",
    "hndl": "handle",
    "img": "image",
    "idx": "index",
    "intent": "intent",
    "itm": "item",
    "kb": "knowledgeBase",
    "llm": "languageModel",
    "mem": "memory",
    "msg": "message",
    "nm": "name",
    "num": "number",
    "obj": "object",
    "opt": "option",
    "nxt": "next",
    "prompt": "prompt",
    "rag": "retrievalAugmentedGeneration",
    "resp": "response",
    "req": "request",
    "res": "result",
    "retrvr": "retriever",
    "sess": "session",
    "svc": "service",
    "sys": "system",
    "tmp": "temporary",
    "usr": "user",
    "vec": "vector",
}

COMMENT_PREFIXES = {
    "python": "#",
    "ruby": "#",
    "shell": "#",
    "javascript": "//",
    "typescript": "//",
    "java": "//",
    "csharp": "//",
    "go": "//",
    "rust": "//",
    "kotlin": "//",
    "swift": "//",
    "php": "//",
    "cpp": "//",
    "c": "//",
    "generic": "//",
}

CHATBOT_SIGNAL_PATTERNS = {
    "message handling": r"\bmessage\b|\bmessages\b|\bmsg\b|\bchat\b|\bconversation\b|\bconvo\b",
    "prompt construction": r"\bprompt\b|\bsystem\b|\bassistant\b|\buser_prompt\b|\bsys_prompt\b",
    "model invocation": r"\bllm\b|\bopenai\b|\banthropic\b|\bgenerate\b|\bgen_resp\b|\bgenResp\b|\bcompletion\b|\bchatcompletion\b",
    "memory or session state": r"\bmemory\b|\bhistory\b|\bhist\b|\bsession\b|\bsess\b|\bcontext\b|\bctx\b",
    "retrieval flow": r"\brag\b|\bretriev\w*\b|\bretrvr\b|\bembedding\b|\bemb\b|\bvector\b|\bvec\b|\bknowledge\b",
    "intent routing": r"\bintent\b|\bclassif\w*\b|\broute\b|\bhandler\b|\bhndl\b",
}

LANGUAGE_RULES = [
    ("python", [r"\bdef\b", r"\bimport\b", r":\s*$", r"\bself\b"]),
    ("javascript", [r"\bconst\b", r"\blet\b", r"=>", r"\bfunction\b"]),
    ("typescript", [r"\binterface\b", r"\btype\s+\w+\s*=", r":\s*(string|number|boolean|Promise<)"]),
    ("java", [r"\bpublic\s+class\b", r"\bSystem\.out\.println\b", r"\bnew\s+\w+\("]),
    ("csharp", [r"\bnamespace\b", r"\busing\s+System\b", r"\basync\s+Task\b"]),
    ("go", [r"\bfunc\b", r"\bpackage\s+\w+", r"\bfmt\."]),
    ("rust", [r"\bfn\b", r"\blet\s+mut\b", r"\bimpl\b"]),
    ("php", [r"<\?php", r"\$\w+", r"\bfunction\b"]),
    ("ruby", [r"\bend\b", r"\bdef\b", r"\bputs\b"]),
    ("cpp", [r"#include\s*<", r"\bstd::", r"\bint\s+main\s*\("]),
]


def calculate_complexity(code: str) -> dict:
    conditionals = len(re.findall(r"\bif\b|\belse\b|\bswitch\b", code))
    loops = len(re.findall(r"\bfor\b|\bwhile\b", code))
    functions = len(re.findall(r"\bdef\b|\bfunction\b|=>", code))

    score = conditionals + loops * 2 + functions

    if score < 5:
        level = "Low"
    elif score < 12:
        level = "Medium"
    else:
        level = "High"

    return {
        "score": score,
        "level": level,
        "conditionals": conditionals,
        "loops": loops,
        "functions": functions,
    }


def detect_dead_code(code: str) -> list[str]:
    findings = []

    if re.search(r"if\s*\(\s*false\s*\)", code):
        findings.append("Found condition that will never execute.")

    if re.search(r"return\s+.*\n\s+return", code):
        findings.append("Multiple sequential returns detected.")

    unused_vars = re.findall(r"(?:const|let|var)\s+(\w+)\s*=", code)

    for variable in unused_vars:
        occurrences = len(re.findall(rf"\b{variable}\b", code))

        if occurrences == 1:
            findings.append(f"Possible unused variable: {variable}")

    return findings


def add_docstrings(code: str, language: str) -> str:
    if language == "python":
        pattern = re.compile(r"def\s+(\w+)\((.*?)\):")

        def replacer(match):
            name = match.group(1)
            params = match.group(2)

            return f'''def {name}({params}):
    """
    Humanized function: {name}
    Parameters: {params or "None"}
    """'''

        return pattern.sub(replacer, code)

    return code


@dataclass
class HumanizeOptions:
    add_summary_comment: bool = True
    rename_identifiers: bool = True
    normalize_spacing: bool = True
    language_hint: str = "auto"
    target_profile: str = "developer_friendly"
    add_docstrings: bool = True
    explain_complexity: bool = True
    detect_dead_code: bool = True


@dataclass
class InsightCard:
    title: str
    body: str


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


def detect_chatbot_signals(code: str) -> list[str]:
    signals = [
        label
        for label, pattern in CHATBOT_SIGNAL_PATTERNS.items()
        if re.search(pattern, code, re.IGNORECASE)
    ]
    return signals


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

    def expand_join_word(word: str) -> list[str]:
        return split_identifier(word) if re.search(r"[A-Z]", word[1:]) else [word]

    def to_pascal_word(word: str) -> str:
        if any(character.isupper() for character in word[1:]):
            return word[:1].upper() + word[1:]
        return word[:1].upper() + word[1:].lower()

    def to_camel_word(word: str) -> str:
        if any(character.isupper() for character in word[1:]):
            return word[:1].lower() + word[1:]
        return word.lower()

    if style == "snake":
        flattened = [part.lower() for word in words for part in expand_join_word(word)]
        return "_".join(flattened)
    if style == "constant":
        flattened = [part.upper() for word in words for part in expand_join_word(word)]
        return "_".join(flattened)
    if style == "pascal":
        return "".join(to_pascal_word(word) for word in words)

    first, *rest = words
    transformed = [to_camel_word(first)]
    transformed.extend(to_pascal_word(word) for word in rest)
    return "".join(transformed)


def expand_identifier(identifier: str) -> str:
    words = split_identifier(identifier)
    expanded_words = [SHORTHAND_MAP.get(word.lower(), word) for word in words]
    return to_style(expanded_words, match_identifier_style(identifier))


def collect_rename_map(code: str) -> dict[str, str]:
    rename_map: dict[str, str] = {}

    declaration_patterns = [
        re.compile(r"\b(?:const|let|var|function|class|def)\s+([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\b(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?[A-Za-z_<>\[\],?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", re.MULTILINE),
    ]
    parameter_pattern = re.compile(
        r"\(([^(){}]*)\)\s*=>|\b(?:function|def)\b[^(]*\(([^()]*)\)"
    )

    for pattern in declaration_patterns:
        for match in pattern.finditer(code):
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
    segments: list[str] = []
    index = 0
    quote: str | None = None

    def replace_segment(segment: str) -> str:
        updated = segment
        for original, expanded in rename_map.items():
            updated = re.sub(rf"(?<!\.)\b{re.escape(original)}\b", expanded, updated)
        return updated

    while index < len(code):
        char = code[index]
        next_char = code[index + 1] if index + 1 < len(code) else ""

        if quote is None and char == "/" and next_char == "/":
            line_end = code.find("\n", index)
            if line_end == -1:
                segments.append(code[index:])
                break
            segments.append(code[index:line_end])
            index = line_end
            continue

        if quote is None and char == "/" and next_char == "*":
            comment_end = code.find("*/", index + 2)
            end = len(code) if comment_end == -1 else comment_end + 2
            segments.append(code[index:end])
            index = end
            continue

        if quote is not None:
            segments.append(char)
            if char == "\\" and index + 1 < len(code):
                segments.append(code[index + 1])
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            segments.append(char)
            index += 1
            continue

        start = index
        while index < len(code):
            current = code[index]
            upcoming = code[index + 1] if index + 1 < len(code) else ""
            if current in {"'", '"', "`"} or (current == "/" and upcoming in {"/", "*"}):
                break
            index += 1
        segments.append(replace_segment(code[start:index]))

    return "".join(segments)


def rename_identifiers(code: str) -> str:
    rename_map = collect_rename_map(code)
    if not rename_map:
        return code
    return replace_outside_strings(code, rename_map)


def normalize_spacing(code: str, language: str = "generic") -> str:
    lines = [
        re.sub(r"\s+$", "", line.replace("\t", "  "))
        for line in code.replace("\r\n", "\n").split("\n")
    ]

    if language == "python":
        formatted_lines: list[str] = []

        for line in lines:
            if not line.strip():
                formatted_lines.append("")
                continue

            leading_whitespace = len(line) - len(line.lstrip(" "))
            indent = " " * leading_whitespace
            trimmed = line.strip()
            trimmed = re.sub(r"\s*(===|!==|==|!=|<=|>=|\|\||&&|\+=|-=|\*=|/=|%=)\s*", r" \1 ", trimmed)
            trimmed = re.sub(r"\s*([=+\-*/<>%,])\s*", r" \1 ", trimmed)
            trimmed = re.sub(r",\s*", ", ", trimmed)
            trimmed = re.sub(r":\s*$", ":", trimmed)
            trimmed = re.sub(r"\(\s+", "(", trimmed)
            trimmed = re.sub(r"\s+\)", ")", trimmed)
            trimmed = re.sub(r"\s+", " ", trimmed)
            trimmed = trimmed.replace(" ,", ",").replace(" .", ".")
            formatted_lines.append(f"{indent}{trimmed}")

        return "\n".join(formatted_lines)

    depth = 0
    formatted_lines: list[str] = []

    multi_char_pattern = re.compile(r"\s*(===|!==|==|!=|<=|>=|\|\||&&|=>|\+=|-=|\*=|/=|%=)\s*")
    single_char_pattern = re.compile(r"\s*([=+\-*/<>%,])\s*")

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            formatted_lines.append("")
            continue

        if re.match(r"^[)\]}]", trimmed):
            depth = max(depth - 1, 0)

        protected: list[str] = []

        def preserve_operator(match: re.Match[str]) -> str:
            marker = f"__OP_{len(protected)}__"
            protected.append(f" {match.group(1)} ")
            return marker

        formatted = multi_char_pattern.sub(preserve_operator, trimmed)
        formatted = single_char_pattern.sub(r" \1 ", formatted)
        formatted = re.sub(r",\s*", ", ", formatted)
        formatted = re.sub(r";\s*", "; ", formatted)
        formatted = re.sub(r"\(\s+", "(", formatted)
        formatted = re.sub(r"\s+\)", ")", formatted)
        formatted = re.sub(r"\{\s+", "{ ", formatted)
        formatted = re.sub(r"\s+\}", " }", formatted)
        formatted = re.sub(r"\s+", " ", formatted)
        formatted = formatted.replace(" ,", ",").replace(" .", ".").replace("? .", "?.")
        formatted = re.sub(r";\s*$", ";", formatted)
        formatted = re.sub(
            r"__OP_(\d+)__",
            lambda match: protected[int(match.group(1))],
            formatted,
        )

        formatted_lines.append(f"{'  ' * depth}{formatted}")
        open_count = len(re.findall(r"[{\[(]", trimmed))
        close_count = len(re.findall(r"[}\])]", trimmed))
        depth = max(depth + open_count - close_count, 0)

    return "\n".join(formatted_lines)


def summarize_code(code: str, language: str, chatbot_signals: list[str]) -> list[InsightCard]:
    functions = re.findall(
        r"\b(function\s+[A-Za-z_][A-Za-z0-9_]*|def\s+[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\s*=\s*\()",
        code,
    )
    conditionals = len(re.findall(r"\bif\b|\?\s", code))
    loops = len(re.findall(r"\bfor\b|\bwhile\b|\bmap\b|\bfilter\b|\breduce\b", code))
    returns = len(re.findall(r"\breturn\b", code))
    async_work = bool(re.search(r"\basync\b|\bawait\b|\bfetch\b|\bPromise\b", code))

    cards = [
        InsightCard(
            title="Detected language",
            body=(
                f"This looks most like {language.title()} code, so the humanizer keeps its comment style and naming conventions aligned with that ecosystem."
                if language != "generic"
                else "The snippet does not clearly match one language, so the humanizer applies language-neutral formatting and naming rules."
            ),
        ),
        InsightCard(
            title="Structure",
            body=(
                f"This snippet appears to define {len(functions)} reusable "
                f"{'function' if len(functions) == 1 else 'functions'}, so the main behavior is wrapped in callable logic."
                if functions
                else "This snippet is mostly inline logic, so the main behavior runs directly from top to bottom."
            ),
        ),
        InsightCard(
            title="Control flow",
            body=(
                f"I found {conditionals} conditional checks and {loops} iteration-style operations, "
                "which suggests the code mixes decision-making with data processing."
            ),
        ),
        InsightCard(
            title="Outputs",
            body=(
                f"It returns a value {returns} time{'' if returns == 1 else 's'}, so the code is focused on "
                "producing data rather than only causing side effects."
                if returns
                else "There is no explicit return value here, so the snippet likely exists to trigger side effects or update state."
            ),
        ),
    ]

    cards.append(
        InsightCard(
            title="Chatbot signals",
            body=(
                "I detected chatbot-oriented patterns such as "
                + ", ".join(chatbot_signals)
                + ", so the rewrite leans toward clearer conversation, prompt, and state-management naming."
                if chatbot_signals
                else "I did not find strong chatbot-specific markers, so the rewrite stays conservative and focuses on readability."
            ),
        )
    )

    if async_work:
        cards.append(
            InsightCard(
                title="Async behavior",
                body="There are signs of async work, which means the code probably waits on network calls, timers, or other promise-based tasks.",
            )
        )

    return cards


def build_summary_comment(code: str, language: str, chatbot_signals: list[str]) -> str:
    line_count = len([line for line in code.split("\n") if line.strip()])
    prefix = comment_prefix_for(language)
    parts = [
        f"Humanized summary: this {language if language != 'generic' else 'multi-language'} snippet spans {line_count} active line{'' if line_count == 1 else 's'}."
    ]

    if re.search(r"\bmap\b|\bfilter\b|\breduce\b", code):
        parts.append("It transforms or filters a collection.")

    if re.search(r"\bfind\b|\bget\b|\bfetch\b", code):
        parts.append("It includes lookup-style behavior.")

    if chatbot_signals:
        parts.append("It appears to implement part of an NLP chatbot flow.")
        parts.append(f"Detected areas: {', '.join(chatbot_signals)}.")

    return f"{prefix} " + " ".join(parts)


def humanize(code: str, options: HumanizeOptions | None = None) -> dict[str, object]:
    settings = options or HumanizeOptions()
    result = code.strip()

    if not result:
        return {"code": "", "insights": []}

    language = detect_language(result, settings.language_hint)
    original_code = result
    chatbot_signals = detect_chatbot_signals(original_code)

    if settings.rename_identifiers:
        result = rename_identifiers(result)
        chatbot_signals = detect_chatbot_signals(f"{original_code}\n{result}")

    if settings.add_docstrings:
        result = add_docstrings(result, language)

    if settings.normalize_spacing:
        result = normalize_spacing(result, language)

    if settings.add_summary_comment:
        result = f"{build_summary_comment(result, language, chatbot_signals)}\n{result}"

    complexity = calculate_complexity(result) if settings.explain_complexity else {}
    dead_code = detect_dead_code(result) if settings.detect_dead_code else []

    if settings.add_docstrings:
        result = add_docstrings(result, language)

    insights = [asdict(card) for card in summarize_code(result, language, chatbot_signals)]

    if settings.explain_complexity:
        insights.append({"title": "Complexity", "body": f"Score: {complexity['score']}, Level: {complexity['level']}"})

    if settings.detect_dead_code and dead_code:
        insights.append({"title": "Dead Code Findings", "body": "\n".join(dead_code)})

    return {
        "code": result,
        "insights": insights,
        "language": language,
        "chatbot_signals": chatbot_signals,
        "profile": settings.target_profile,
        "complexity": complexity,
        "dead_code": dead_code,
    }

