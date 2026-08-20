"""ComfyUI HTTP backend: submit workflow, poll, retrieve. M1 (#6, #7).

Marquee never knows ComfyUI's filesystem path -- a URL is the entire
integration surface (docs/marquee-brief.md 2, item 3 and 17). Not
implemented yet.
"""

from __future__ import annotations

from pathlib import Path

from marquee.backends.art_backend import ArtBackend
from marquee.contracts import ArtBlock


class ComfyUIBackend(ArtBackend):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def generate(self, *, art: ArtBlock, out_path: Path) -> Path:
        raise NotImplementedError("ComfyUIBackend is implemented in M1")
