"""Run folder lifecycle and the cross-run isolation guard.

See docs/marquee-brief.md Section 4 (statelessness contract) and ADR 0002.
No agent may read any other run's folder -- this module is where that rule
is actually enforced, not just documented.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from marquee.config import Config

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    return _SLUG_RE.sub("-", value.lower()).strip("-")


def new_slug(venue: str) -> str:
    return f"{slugify(venue)}-{uuid.uuid4().hex[:8]}"


def new_run(venue: str, *, config: Config) -> Path:
    """Create runs/<slug>/ for a fresh run and return its path."""
    slug = new_slug(venue)
    run_dir = config.runs_dir / slug
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


class RunIsolationError(PermissionError):
    """Raised when code tries to access a path outside the active run."""


class RunAccess:
    """Scopes all file access to a single run's folder.

    Every stage that touches run state should go through an instance of
    this class rather than building paths directly, so the isolation
    guarantee is structural rather than a convention agents can forget.
    """

    def __init__(self, run_dir: Path):
        self._run_dir = run_dir.resolve()

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def path(self, *parts: str) -> Path:
        """Resolve a path within this run, refusing anything outside it."""
        candidate = (self._run_dir / Path(*parts)).resolve()
        try:
            candidate.relative_to(self._run_dir)
        except ValueError as exc:
            raise RunIsolationError(
                f"{candidate} is outside run folder {self._run_dir}"
            ) from exc
        return candidate
