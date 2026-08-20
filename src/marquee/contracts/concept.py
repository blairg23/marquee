"""Director output contract -- one line per concept in concepts.jsonl."""

from __future__ import annotations

from pydantic import BaseModel


class ConstraintTuple(BaseModel):
    composition: str
    light: str
    material: str
    type_philosophy: str
    color_logic: str


class Concept(BaseModel):
    idea: str
    light_logic: str
    material: str
    type_philosophy: str
    palette_logic: str
    distinguisher: str
    constraint_tuple: ConstraintTuple
