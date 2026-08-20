"""Pillow composite from layout.json: layers, anchors, scale, opacity, z-order.

M1 (#10). Makes no aesthetic decisions -- ambiguity in layout.json is an
error, never a default. Not implemented yet.
"""

from __future__ import annotations

from pathlib import Path

from marquee.contracts import Layout


def compose(layout: Layout, out_path: Path) -> Path:
    """Render `layout` to a PNG at `out_path`."""
    raise NotImplementedError("renderer is implemented in M1")
