from __future__ import annotations

from pathlib import Path

import pytest

from marquee.config import Config
from marquee.runs import RunAccess, RunIsolationError, new_run, new_slug, slugify


def test_slugify() -> None:
    assert slugify("Club Moon") == "club-moon"
    assert slugify("The Gatsby!!") == "the-gatsby"


def test_new_slug_includes_venue_and_is_unique() -> None:
    a = new_slug("club-moon")
    b = new_slug("club-moon")
    assert a.startswith("club-moon-")
    assert a != b


def test_new_run_creates_directory(tmp_path: Path) -> None:
    config = Config()
    config._config_dir = tmp_path
    run_dir = new_run("club-moon", config=config)
    assert run_dir.exists()
    assert run_dir.is_dir()
    assert run_dir.parent == config.runs_dir


def test_run_access_allows_paths_inside_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "club-moon-abc123"
    run_dir.mkdir(parents=True)
    access = RunAccess(run_dir)
    resolved = access.path("layout.json")
    assert resolved == (run_dir / "layout.json").resolve()


def test_run_access_blocks_escaping_the_run_dir(tmp_path: Path) -> None:
    run_a = tmp_path / "runs" / "run-a"
    run_b = tmp_path / "runs" / "run-b"
    run_a.mkdir(parents=True)
    run_b.mkdir(parents=True)
    (run_b / "layout.json").write_text("{}", encoding="utf-8")

    access = RunAccess(run_a)
    with pytest.raises(RunIsolationError):
        access.path("..", "run-b", "layout.json")


def test_run_access_blocks_absolute_escape(tmp_path: Path) -> None:
    run_a = tmp_path / "runs" / "run-a"
    run_a.mkdir(parents=True)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    access = RunAccess(run_a)
    with pytest.raises(RunIsolationError):
        access.path(str(outside))
