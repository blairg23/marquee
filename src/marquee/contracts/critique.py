"""Critic output contract -- one finding per line in critique.jsonl.

The Critic may not praise: findings or an empty file, never a summary.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CritiqueFinding(BaseModel):
    finding: str
    layout_path: str
    proposed_patch: str


class Critique(BaseModel):
    findings: list[CritiqueFinding] = Field(default_factory=list)
