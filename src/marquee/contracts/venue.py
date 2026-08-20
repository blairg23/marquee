"""Venue record contract. Facts, not taste -- see docs/marquee-brief.md 5.1."""

from __future__ import annotations

from pydantic import BaseModel


class Venue(BaseModel):
    id: str
    name: str
    world: str = ""
    datacenter: str = ""
    location: str = ""
    carrd: str = ""
    discord: str = ""
    logo: str = ""
    logo_lock: bool = True
    regular_night: str = ""
    brand_notes: str = ""
    safe_margin_pct: float = 5.0
