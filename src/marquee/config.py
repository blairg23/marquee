"""Unified config layer: loads, merges, and validates marquee.toml.

Nothing in src/ may hardcode a data or runs path -- every read of those
locations goes through the resolved Config returned here.
"""

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import BaseModel, Field, PrivateAttr

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]

DEFAULT_CONFIG_FILENAME = "marquee.toml"


class PathsConfig(BaseModel):
    data_dir: str = "./data"
    runs_dir: str = "~/.local/state/marquee/runs"


class ComfyUIConfig(BaseModel):
    url: str = "http://127.0.0.1:8188"


class Config(BaseModel):
    """Resolved marquee configuration, with paths made absolute."""

    paths: PathsConfig = Field(default_factory=PathsConfig)
    comfyui: ComfyUIConfig = Field(default_factory=ComfyUIConfig)

    _config_dir: Path = PrivateAttr(default_factory=Path.cwd)

    @property
    def data_dir(self) -> Path:
        return self._resolve(self.paths.data_dir)

    @property
    def runs_dir(self) -> Path:
        return self._resolve(self.paths.runs_dir)

    def _resolve(self, raw: str) -> Path:
        expanded = Path(raw).expanduser()
        if expanded.is_absolute():
            return expanded
        return (self._config_dir / expanded).resolve()


def find_config_file(start: Path | None = None) -> Path | None:
    """Walk up from `start` (default: cwd) looking for marquee.toml."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        config_path = candidate / DEFAULT_CONFIG_FILENAME
        if config_path.exists():
            return config_path
    return None


def load_config(path: Path | None = None) -> Config:
    """Load and validate marquee.toml. Falls back to defaults if not found."""
    config_path = path or find_config_file()
    if config_path is None or not config_path.exists():
        return Config()

    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    config = Config.model_validate(raw)
    config._config_dir = config_path.parent.resolve()
    return config
