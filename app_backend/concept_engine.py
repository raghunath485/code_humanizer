from __future__ import annotations

from dataclasses import dataclass


ALL_CONCEPTS = [
    "Functions",
    "Classes",
    "Loops",
    "Conditional Statements",
    "Arrays",
    "Lists",
    "Dictionaries / Maps",
    "Recursion",
    "Exception Handling",
    "File Handling",
    "OOP Principles",
    "Inheritance",
    "Polymorphism",
    "Interfaces",
    "Generics / Templates",
    "Multithreading",
    "Async Programming",
    "Lambda Functions",
    "Functional Programming",
    "Design Patterns",
    "Database Operations",
    "API Calls",
]


@dataclass
class ConceptPlan:
    selected: list[str]
    avoided: list[str]
    directives: list[str]


def build_concept_plan(selected: list[str]) -> ConceptPlan:
    normalized = [concept for concept in selected if concept in ALL_CONCEPTS]
    avoided = [concept for concept in ALL_CONCEPTS if concept not in normalized]
    directives: list[str] = []

    if "Functions" in normalized:
        directives.append("Prefer named helper functions.")
    if "Classes" in normalized or "OOP Principles" in normalized:
        directives.append("Prefer object-oriented structure where the language supports it.")
    if "Loops" in normalized:
        directives.append("Preserve explicit iteration instead of replacing it with recursion.")
    if "Async Programming" in normalized:
        directives.append("Prefer async or await friendly flow when the target language supports it.")
    if "Exception Handling" in normalized:
        directives.append("Wrap failure-prone logic with defensive error handling.")
    if "Design Patterns" in normalized:
        directives.append("Favor clear separation of responsibilities and reusable abstractions.")
    if "API Calls" in normalized:
        directives.append("Keep request and response handling easy to follow.")

    return ConceptPlan(selected=normalized, avoided=avoided, directives=directives)


def apply_mode_guidance(code: str, mode: str, language: str) -> str:
    if not code.strip():
        return code

    if mode == "beginner":
        header = "Simplified for beginners with clearer naming and learning-friendly structure."
    elif mode == "professional":
        header = "Refined toward professional engineering conventions and modular structure."
    elif mode == "production":
        header = "Production-ready emphasis added with reliability, validation, and observability cues."
    else:
        header = "Balanced for intermediate developers with readable structure and moderate abstraction."

    prefix = "#" if language == "python" else "//"
    return f"{prefix} Mode guidance: {header}\n{code}"
