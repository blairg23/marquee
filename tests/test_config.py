from __future__ import annotations

from pathlib import Path

from marquee.config import Config, find_config_file, load_config


def test_default_config_has_expected_paths() -> None:
    config = Config()
    assert config.paths.data_dir == "./data"
    assert config.paths.runs_dir == "~/.local/state/marquee/runs"


def test_load_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    config = load_config(tmp_path / "nonexistent.toml")
    assert config.paths.data_dir == "./data"


def test_load_config_reads_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "marquee.toml"
    config_path.write_text(
        '[paths]\ndata_dir = "./mydata"\nruns_dir = "./myruns"\n', encoding="utf-8"
    )
    config = load_config(config_path)
    assert config.paths.data_dir == "./mydata"
    assert config.data_dir == (tmp_path / "mydata").resolve()


def test_data_dir_resolves_relative_to_config_file(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    config_path = nested / "marquee.toml"
    config_path.write_text('[paths]\ndata_dir = "./data"\n', encoding="utf-8")
    config = load_config(config_path)
    assert config.data_dir == (nested / "data").resolve()


def test_find_config_file_walks_up(tmp_path: Path) -> None:
    (tmp_path / "marquee.toml").write_text("", encoding="utf-8")
    child = tmp_path / "a" / "b"
    child.mkdir(parents=True)
    found = find_config_file(child)
    assert found == tmp_path / "marquee.toml"


def test_find_config_file_returns_none_when_absent(tmp_path: Path) -> None:
    assert find_config_file(tmp_path) is None


def test_load_config_reads_comfyui_url(tmp_path: Path) -> None:
    config_path = tmp_path / "marquee.toml"
    config_path.write_text(
        '[art.comfyui]\nurl = "http://example.invalid:9000"\n', encoding="utf-8"
    )
    config = load_config(config_path)
    assert config.art.comfyui.url == "http://example.invalid:9000"
