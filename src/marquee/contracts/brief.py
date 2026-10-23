"""Per-run brief contract -- see docs/marquee-brief.md 5.2."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LineupEntry(BaseModel):
    name: str
    twitch: str = ""
    set: str = ""
    wordmark: str = ""


class EventInfo(BaseModel):
    title: str = ""
    date: str = ""
    doors: str = ""
    theme: str = ""


class Brief(BaseModel):
    venue: str
    event: EventInfo = Field(default_factory=EventInfo)
    lineup: list[LineupEntry] = Field(default_factory=list)
    gposes: list[str] = Field(default_factory=list)
    ratios: list[str] = Field(default_factory=lambda: ["4:5"])
    fonts: list[str] = Field(default_factory=list)
    notes: str = ""
