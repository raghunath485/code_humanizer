from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


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
    concept_preferences: list[str] = field(default_factory=list)
    refactor_mode: str = "intermediate"


class CodeRequest(BaseModel):
    code: str = Field(default="")
    language_hint: str = Field(default="auto")
    concept_preferences: list[str] = Field(default_factory=list)
    refactor_mode: str = Field(default="intermediate")
    options: dict[str, Any] = Field(default_factory=dict)


class ConversionRequest(BaseModel):
    code: str = Field(default="")
    source_language: str = Field(default="auto")
    target_language: str
    concept_preferences: list[str] = Field(default_factory=list)
    refactor_mode: str = Field(default="professional")


class AssistantRequest(BaseModel):
    code: str = Field(default="")
    language_hint: str = Field(default="auto")
    project_name: str = Field(default="Code Transformation Platform")

