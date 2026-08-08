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


# ── Print statement conversion ───────────────────────────────────────────────

def _convert_print(code: str, source: str, target: str) -> str:
    """Convert print/output statements between languages."""
    result = code

    if source == "python":
        # Python print("...") → target
        def _py_print_replacer(m: re.Match) -> str:
            args = m.group(1)
            if target == "c":
                # Wrap string args in printf format
                clean = args.strip().strip("'\"")
                return f'printf("{clean}\\n")'
            if target == "cpp":
                return f"std::cout << {args} << std::endl"
            if target == "java":
                return f"System.out.println({args})"
            return m.group(0)

        result = re.sub(r"\bprint\s*\((.+?)\)", _py_print_replacer, result)

    elif source == "java":
        def _java_print_replacer(m: re.Match) -> str:
            args = m.group(1)
            if target == "python":
                return f"print({args})"
            if target == "c":
                clean = args.strip().strip("'\"")
                return f'printf("{clean}\\n")'
            if target == "cpp":
                return f"std::cout << {args} << std::endl"
            return m.group(0)

        result = re.sub(r"System\.out\.println\s*\((.+?)\)", _java_print_replacer, result)

    elif source in {"c", "cpp"}:
        # printf("...") or std::cout << ...
        def _c_printf_replacer(m: re.Match) -> str:
            content = m.group(1).strip().strip("'\"").replace("\\n", "")
            if target == "python":
                return f'print("{content}")'
            if target == "java":
                return f'System.out.println("{content}")'
            if target == "cpp":
                return f'std::cout << "{content}" << std::endl'
            return m.group(0)

        result = re.sub(r'\bprintf\s*\("(.+?)"\)', _c_printf_replacer, result)

        def _cout_replacer(m: re.Match) -> str:
            content = m.group(1).strip()
            if target == "python":
                return f"print({content})"
            if target == "java":
                return f"System.out.println({content})"
            if target == "c":
                clean = content.strip("'\"")
                return f'printf("{clean}\\n")'
            return m.group(0)

        result = re.sub(r"std::cout\s*<<\s*(.+?)(?:\s*<<\s*std::endl)?;", _cout_replacer, result)

    return result


# ── Function / method definition conversion ──────────────────────────────────

def _convert_functions(code: str, source: str, target: str) -> str:
    """Convert function definitions between languages."""
    result = code

    if source == "python" and target in {"c", "cpp"}:
        # def func_name(args): → void func_name(args) {
        def _py_to_c_func(m: re.Match) -> str:
            name = m.group(1)
            params = m.group(2)
            return f"void {name}({params}) {{"
        result = re.sub(r"\bdef\s+(\w+)\s*\(([^)]*)\)\s*:", _py_to_c_func, result)

    elif source == "python" and target == "java":
        def _py_to_java_func(m: re.Match) -> str:
            name = m.group(1)
            params = m.group(2)
            return f"public static void {name}({params}) {{"
        result = re.sub(r"\bdef\s+(\w+)\s*\(([^)]*)\)\s*:", _py_to_java_func, result)

    elif source in {"c", "cpp"} and target == "python":
        # void func_name(args) { → def func_name(args):
        def _c_to_py_func(m: re.Match) -> str:
            name = m.group(1)
            params = m.group(2)
            # Strip C type annotations from params
            clean_params = ", ".join(
                p.strip().split()[-1] if p.strip() else "" for p in params.split(",")
            )
            return f"def {name}({clean_params}):"
        result = re.sub(r"\b(?:void|int|float|double|char|bool)\s+(\w+)\s*\(([^)]*)\)\s*\{", _c_to_py_func, result)

    elif source == "java" and target == "python":
        def _java_to_py_func(m: re.Match) -> str:
            name = m.group(1)
            params = m.group(2)
            clean_params = ", ".join(
                p.strip().split()[-1] if p.strip() else "" for p in params.split(",")
            )
            return f"def {name}({clean_params}):"
        result = re.sub(
            r"\b(?:public|private|protected)?\s*(?:static\s+)?(?:void|int|float|double|String|boolean)\s+(\w+)\s*\(([^)]*)\)\s*\{",
            _java_to_py_func,
            result,
        )

    return result


# ── Variable declaration conversion ──────────────────────────────────────────

def _convert_variables(code: str, source: str, target: str) -> str:
    """Convert variable declarations between languages."""
    result = code

    if source == "python" and target in {"c", "cpp", "java"}:
        # x = 10 → int x = 10;  (best-effort type inference)
        def _py_var(m: re.Match) -> str:
            name = m.group(1)
            value = m.group(2).strip()
            inferred = "int" if re.fullmatch(r"-?\d+", value) else \
                       "double" if re.fullmatch(r"-?\d+\.\d+", value) else \
                       "const char*" if target == "c" and (value.startswith('"') or value.startswith("'")) else \
                       "std::string" if target == "cpp" and (value.startswith('"') or value.startswith("'")) else \
                       "String" if target == "java" and (value.startswith('"') or value.startswith("'")) else \
                       "auto" if target == "cpp" else "var"
            suffix = ";" if target in {"c", "cpp", "java"} else ""
            return f"{inferred} {name} = {value}{suffix}"
        result = re.sub(r"^(\w+)\s*=\s*(.+)$", _py_var, result, flags=re.MULTILINE)

    elif source in {"c", "cpp", "java"} and target == "python":
        # int x = 10; → x = 10
        result = re.sub(
            r"\b(?:int|float|double|char|bool|long|short|String|auto|var|const\s+char\*|std::string)\s+(\w+)\s*=\s*(.+?);",
            r"\1 = \2",
            result,
        )

    return result


# ── Syntax: braces, semicolons, indentation ──────────────────────────────────

def _convert_syntax(code: str, source: str, target: str) -> str:
    """Handle braces ↔ indentation and semicolons."""
    result = code

    if source == "python" and target in {"c", "cpp", "java"}:
        # Add semicolons to simple statements (not ending with { or : or })
        lines = result.split("\n")
        converted = []
        for line in lines:
            stripped = line.rstrip()
            if stripped and not stripped.endswith(("{", "}", ":", ";", "*/")) and \
               not stripped.lstrip().startswith(("//", "/*", "#", "}")):
                stripped += ";"
            converted.append(stripped)
        result = "\n".join(converted)

    elif source in {"c", "cpp", "java"} and target == "python":
        # Remove braces and semicolons
        result = result.replace("{", "").replace("}", "")
        result = re.sub(r";\s*$", "", result, flags=re.MULTILINE)
        # Remove #include / import lines for clean Python
        result = re.sub(r"^\s*#include\s+.*$", "", result, flags=re.MULTILINE)

    return result


# ── Wrap in main() if needed ─────────────────────────────────────────────────

def _wrap_main(code: str, source: str, target: str) -> str:
    """Add a main function wrapper and includes/imports when appropriate."""
    has_main = bool(re.search(r"\bmain\s*\(", code))
    has_func = bool(re.search(r"\bdef\b|\bvoid\b|\bint\b.*\(", code))

    # Only wrap simple snippets (no existing functions)
    if has_main or has_func:
        return code

    if target == "c":
        return (
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n\n"
            "int main() {\n"
            + _indent(code, "    ")
            + "\n    return 0;\n}"
        )
    if target == "cpp":
        return (
            "#include <iostream>\n"
            "#include <string>\n\n"
            "int main() {\n"
            + _indent(code, "    ")
            + "\n    return 0;\n}"
        )
    if target == "java":
        return (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            + _indent(code, "        ")
            + "\n    }\n}"
        )

    return code


def _indent(code: str, prefix: str) -> str:
    """Indent every non-empty line with the given prefix."""
    lines = code.strip().split("\n")
    return "\n".join(f"{prefix}{line}" if line.strip() else "" for line in lines)


# ── Comment style conversion ────────────────────────────────────────────────

def _convert_comments(code: str, source: str, target: str) -> str:
    """Convert comment syntax between languages."""
    result = code

    if source == "python" and target in {"c", "cpp", "java"}:
        result = re.sub(r"#\s?(.*)", r"// \1", result)

    elif source in {"c", "cpp", "java"} and target == "python":
        result = re.sub(r"//\s?(.*)", r"# \1", result)

    return result


# ── Loop conversion ─────────────────────────────────────────────────────────

def _convert_loops(code: str, source: str, target: str) -> str:
    """Convert loop syntax between languages."""
    result = code

    if source == "python" and target in {"c", "cpp", "java"}:
        # for i in range(n): → for (int i = 0; i < n; i++) {
        def _py_range(m: re.Match) -> str:
            var = m.group(1)
            limit = m.group(2)
            return f"for (int {var} = 0; {var} < {limit}; {var}++) {{"
        result = re.sub(r"\bfor\s+(\w+)\s+in\s+range\((\w+)\)\s*:", _py_range, result)

    elif source in {"c", "cpp", "java"} and target == "python":
        # for (int i = 0; i < n; i++) { → for i in range(n):
        def _c_for(m: re.Match) -> str:
            var = m.group(1)
            limit = m.group(2)
            return f"for {var} in range({limit}):"
        result = re.sub(r"\bfor\s*\(\s*int\s+(\w+)\s*=\s*0\s*;\s*\w+\s*<\s*(\w+)\s*;\s*\w+\+\+\s*\)\s*\{", _c_for, result)

    return result


# ── Main entry point ─────────────────────────────────────────────────────────

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

    # Run conversion pipeline
    transformed = code.strip()
    transformed = _convert_comments(transformed, resolved_source, target_language)
    transformed = _convert_print(transformed, resolved_source, target_language)
    transformed = _convert_functions(transformed, resolved_source, target_language)
    transformed = _convert_loops(transformed, resolved_source, target_language)
    transformed = _convert_variables(transformed, resolved_source, target_language)
    transformed = _convert_syntax(transformed, resolved_source, target_language)
    transformed = _wrap_main(transformed, resolved_source, target_language)
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
        "converted_code": "\n".join(header_lines) + "\n\n" + transformed,
        "confidence_score": confidence,
        "unsupported_features": warnings,
        "warnings": warnings or ["No major conversion blockers detected in heuristic pass."],
    }

