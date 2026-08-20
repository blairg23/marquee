"""Text rendering: variable-font axes, tracking, case, wrapping. M1 (#11).

Requires Pillow built with Raqm for correct shaping. Not implemented yet.
"""

from __future__ import annotations

from marquee.contracts import TypeRole


def render_text(role: TypeRole, text: str) -> object:
    """Render `text` per the given TypeRole spec."""
    raise NotImplementedError("text rendering is implemented in M1")
