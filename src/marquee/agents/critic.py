"""Critic: inspects the composed PNG, emits critique.jsonl. M2 (#18).

May not praise -- findings or an empty file only. Not implemented yet.
"""

from __future__ import annotations

from pathlib import Path

from marquee.agents.base import Agent
from marquee.contracts import Concept, Critique, Layout


class Critic(Agent):
    def run(  # type: ignore[override]
        self, *, png_path: Path, layout: Layout, concept: Concept
    ) -> Critique:
        raise NotImplementedError("Critic is implemented in M2")
