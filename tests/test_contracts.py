from __future__ import annotations

from marquee.contracts import (
    ArtBlock,
    Brief,
    Concept,
    Critique,
    CritiqueFinding,
    Layout,
    Venue,
)
from marquee.contracts.concept import ConstraintTuple
from marquee.contracts.layout import CanvasBlock


def test_venue_defaults() -> None:
    venue = Venue(id="club-moon", name="Club Moon")
    assert venue.logo_lock is True
    assert venue.safe_margin_pct == 5.0


def test_brief_requires_venue() -> None:
    brief = Brief(venue="club-moon")
    assert brief.ratios == ["4:5"]
    assert brief.lineup == []


def test_concept_round_trip() -> None:
    concept = Concept(
        idea="neon crescent over a wet street",
        light_logic="single hard source",
        material="chrome",
        type_philosophy="type as structure",
        palette_logic="monochrome + one accent",
        distinguisher="the crescent doubles as the headline underline",
        constraint_tuple=ConstraintTuple(
            composition="diagonal cascade",
            light="single hard source",
            material="chrome",
            type_philosophy="type as structure",
            color_logic="monochrome + one accent",
        ),
    )
    assert concept.model_dump()["constraint_tuple"]["material"] == "chrome"


def test_layout_requires_canvas_and_art() -> None:
    layout = Layout(
        canvas=CanvasBlock(ratio="4:5", width=1080, height=1350),
        art=ArtBlock(prompt="neon crescent over a wet street"),
    )
    assert layout.canvas.width == 1080
    assert layout.type == []
    assert layout.layers == []


def test_critique_may_be_empty() -> None:
    critique = Critique()
    assert critique.findings == []


def test_critique_finding_shape() -> None:
    finding = CritiqueFinding(
        finding="logo has been recolored",
        layout_path="layers[2].opacity",
        proposed_patch="set opacity to 1.0",
    )
    assert finding.layout_path == "layers[2].opacity"
