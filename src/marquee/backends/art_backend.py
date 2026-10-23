"""ArtBackend ABC: swapping the diffusion backend touches one adapter. M1 (#6)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from marquee.contracts import ArtBlock


class ArtBackend(ABC):
    @abstractmethod
    def generate(self, *, art: ArtBlock, out_path: Path) -> Path:
        """Generate a background image per `art` and save it to `out_path`."""
        raise NotImplementedError
