"""layout.json contract: the single source of truth for the composite.

See docs/marquee-brief.md 5.4. Every visual property is addressable by JSON
path so the Critic can emit precise patches against it.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CanvasBlock(BaseModel):
    ratio: str
    width: int
    height: int
    safe_margin_pct: float = 5.0


class PaletteToken(BaseModel):
    name: str
    hex: str


class PaletteBlock(BaseModel):
    tokens: list[PaletteToken] = Field(default_factory=list)
    logic: str = ""


class TypeRole(BaseModel):
    role: str
    family: str
    size: float
    tracking: float = 0.0
    case: str = "none"
    palette_token: str = ""
    variable_axes: dict[str, float] = Field(default_factory=dict)


class Layer(BaseModel):
    type: str
    source: str = ""
    anchor: str = "center"
    offset: tuple[float, float] = (0.0, 0.0)
    scale: float = 1.0
    opacity: float = 1.0
    blend: str = "normal"
    effects: list[str] = Field(default_factory=list)


class ArtBlock(BaseModel):
    prompt: str
    negative_prompt: str = ""
    seed: int = 0
    steps: int = 20
    cfg: float = 1.0
    width: int = 1024
    height: int = 1280


class Layout(BaseModel):
    canvas: CanvasBlock
    palette: PaletteBlock = Field(default_factory=PaletteBlock)
    type: list[TypeRole] = Field(default_factory=list)
    layers: list[Layer] = Field(default_factory=list)
    art: ArtBlock
