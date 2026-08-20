"""Director: draws a constraint tuple, proposes 3 concepts. M2 (#16).

Does not design, does not write prompts, does not pick. Not implemented yet.
"""

from __future__ import annotations

from marquee.agents.base import Agent
from marquee.contracts import Brief, Concept, Venue


class Director(Agent):
    def run(self, *, brief: Brief, venue: Venue) -> list[Concept]:  # type: ignore[override]
        raise NotImplementedError("Director is implemented in M2")
