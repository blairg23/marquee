"""Observability: zoom-tagged JSONL event emitter.

Every stage emits structured events to runs/<slug>/trace.jsonl with a `zoom`
field (summary | stage | call) so a dashboard can collapse or expand a run.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Literal

Zoom = Literal["summary", "stage", "call"]


class Tracer:
    """Appends zoom-tagged events to a single run's trace.jsonl."""

    def __init__(self, trace_path: Path):
        self._trace_path = trace_path
        self._trace_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, *, zoom: Zoom, stage: str, event: str, **fields: object) -> None:
        record = {
            "ts": time.time(),
            "zoom": zoom,
            "stage": stage,
            "event": event,
            **fields,
        }
        with self._trace_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
