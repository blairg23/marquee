from __future__ import annotations

import json
from pathlib import Path

from marquee.trace import Tracer


def test_emit_writes_one_jsonl_line(tmp_path: Path) -> None:
    trace_path = tmp_path / "runs" / "slug" / "trace.jsonl"
    tracer = Tracer(trace_path)
    tracer.emit(zoom="stage", stage="director", event="started")

    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["zoom"] == "stage"
    assert record["stage"] == "director"
    assert record["event"] == "started"
    assert "ts" in record


def test_emit_appends_multiple_events(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    tracer = Tracer(trace_path)
    tracer.emit(zoom="summary", stage="run", event="start")
    tracer.emit(zoom="call", stage="director", event="llm_call", tokens=123)

    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    second = json.loads(lines[1])
    assert second["tokens"] == 123


def test_emit_creates_parent_dirs(tmp_path: Path) -> None:
    trace_path = tmp_path / "a" / "b" / "trace.jsonl"
    Tracer(trace_path).emit(zoom="summary", stage="run", event="start")
    assert trace_path.exists()
