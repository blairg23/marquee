"""Designer: concept to layout.json, including the Flux prompt. M2 (#17).

Owns layout, type, and palette together. Not implemented yet.
"""

from __future__ import annotations

from marquee.agents.base import Agent
from marquee.contracts import Concept, Layout


class Designer(Agent):
    def run(self, *, concept: Concept) -> Layout:  # type: ignore[override]
        raise NotImplementedError("Designer is implemented in M2")
