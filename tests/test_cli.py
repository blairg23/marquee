from __future__ import annotations

from typer.testing import CliRunner

from marquee import __version__
from marquee.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_new_creates_run_dir(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "marquee.toml"
    config_path.write_text(
        f'[paths]\ndata_dir = "./data"\nruns_dir = "{tmp_path.as_posix()}/runs"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "club-moon"])
    assert result.exit_code == 0
    assert "club-moon-" in result.stdout
