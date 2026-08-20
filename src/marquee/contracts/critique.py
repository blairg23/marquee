"""Critic output contract -- one finding per line in critique.jsonl.

The Critic may not praise: findings or an empty file, never a summary.
Field names match the Critic skill's output vocabulary exactly
(.claude/skills/critic/SKILL.md) so a finding the skill emits validates
without translation.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["blocker", "major", "minor"]


class CritiqueFinding(BaseModel):
    severity: Severity
    check: str
    observed: str
    path: str
    patch: Any


class Critique(BaseModel):
    findings: list[CritiqueFinding] = Field(default_factory=list)
