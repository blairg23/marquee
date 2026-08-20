"""Director output contract -- one line per concept in concepts.jsonl.

Field names match the Director skill's output vocabulary exactly
(.claude/skills/director/SKILL.md) so a concept the skill emits validates
without translation.
"""

from __future__ import annotations

from pydantic import BaseModel


class ConstraintTuple(BaseModel):
    composition: str
    light: str
    material: str
    type_philosophy: str
    color_logic: str


class Concept(BaseModel):
    constraints: ConstraintTuple
    idea: str
    light: str
    material: str
    type_philosophy: str
    color_logic: str
    not_a_flyer: str
