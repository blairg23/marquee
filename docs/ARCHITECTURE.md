# Architecture

Marquee is a stateless, agent-driven asset generator. The first recipe is event
posters for FFXIV venues; the architecture is recipe-agnostic.

## The pipeline

```
  brief (interactive)
        |
        v
  Director ........ draws constraints, proposes 3 concepts --> you pick
        |
        v
  Designer ..... layout + type + palette --> layout.json
        |
        v
  Renderer ...... background (ComfyUI) + cutouts (rembg) + composite (Pillow)
        |                                                    ^
        v                                                    |
  Critic ........ inspects the PNG --> patch list ---+  (cheap loop)
        |
        v
  MEAT GATE ........... you. approve / redirect / regen (expensive, explicit)
```

Loop economics are the whole design: the Critic-to-Renderer loop edits only
`layout.json` and re-composites (sub-second, no GPU). Background regeneration
requires an explicit `regen` decision from the human gate -- never automatic,
never triggered by the Critic.

### Director: judgment

Reads the brief and venue record, draws a constraint tuple from
`decks/constraints.jsonl` (mandatory, non-negotiable), proposes exactly 3
concepts satisfying the drawn constraints. Emits `runs/<slug>/concepts.jsonl`.
Does not design, does not write prompts, does not pick.

### Designer: judgment

Takes the chosen concept and produces one artifact: `runs/<slug>/layout.json`.
Owns layout, type system, and palette together -- these are not separable.
Also authors the Flux prompt and negative prompt as fields inside
`layout.json`. Everything is coordinates and named tokens, no prose
instructions to a human.

### Renderer: deterministic tool, no LLM

- `art`: submits the prompt from `layout.json` to the ComfyUI HTTP API, polls,
  retrieves the background PNG.
- `cut`: runs rembg (`birefnet-general`) over supplied gpose PNGs.
- `compose`: renders `layout.json` to a PNG with Pillow -- text, glows,
  frames, logo placement, footer, safe margins.

Makes no aesthetic decisions. If `layout.json` is ambiguous, it raises an
error naming the ambiguous field. It never guesses.

### Critic: judgment

Reads the composed PNG plus `layout.json` plus the chosen concept. Checks, in
order: logo integrity, text legibility at thumbnail scale, information
hierarchy, margin/bleed violations, contrast, concept delivery, and drift
toward generic-flyer defaults. Emits `runs/<slug>/critique.jsonl`, one finding
per line, each with a proposed patch against a specific `layout.json` path.
May not praise -- findings or an empty file only.

### Meat Gate: the human

A real stage, not a pause. Presents the current composite, open findings, and
the drawn constraint tuple, then blocks. Four outcomes, each appended to
`runs/<slug>/decisions.jsonl`:

| Decision | Effect |
|---|---|
| `approve` | Run is sealed. Exports fire for every ratio in the brief. |
| `patch` | Selected findings applied, re-compose, back to Critic. Cheap, no GPU. |
| `redirect` | Back to Designer with a note. New `layout.json`, same background. |
| `regen` | Back to Renderer for new background art. The only path that touches the GPU. |

Nothing exports without an `approve` on record. The Meat Gate is the only
stage that may write to `pinned.jsonl`, and only when explicitly asked.

## Statelessness contract

A hard architectural rule, not a preference:

- All run state lives in `runs/<slug>/`. Deleting that folder erases the run
  completely.
- No agent may read any other run's folder -- enforced in the tool layer by a
  file-access helper scoped to the active run's slug.
- The only cross-run memory is `pinned.jsonl` at repo root: append-only,
  written exclusively by explicit `marquee pin "<note>"`, human-readable.
  Nothing writes to it automatically.
- No cached palettes, no "last time" heuristics, no style history, no learned
  preferences.
- Venue records are facts, not taste: logo path, location, brand-locked
  colors, safe margins. Never layouts, concepts, or prompts.

See ADR 0002 for why.

## Data contracts

JSONL for all pipeline I/O. Venue and config files stay plain JSON/TOML
because they are hand-edited config, not pipeline I/O.

- `brief.json` -- per-run intake output (venue, event, lineup, gposes, ratios)
- `runs/<slug>/concepts.jsonl` -- Director output, one concept per line
- `runs/<slug>/layout.json` -- the single source of truth for the composite:
  canvas block, palette block, type block, layers array in z-order, art block
  (Flux prompt/negative/seed/steps/cfg/res). Every visual property is
  addressable by JSON path so the Critic can emit precise patches.
- `runs/<slug>/critique.jsonl` -- Critic findings, each with a patch path
- `runs/<slug>/decisions.jsonl` -- Meat Gate decisions
- `decks/constraints.jsonl` -- one axis per line; the Director draws one value
  per axis to force range instead of relying on "be original"
- `decks/typefaces.jsonl` -- the OFL font stack, organized as a deck (not a
  fixed pairing) so the Designer draws from categories

### Ratios

| Key | Pixels | Use | Flux gen res |
|---|---|---|---|
| `4:5` | 1080x1350 | Instagram feed (default) | 1024x1280 |
| `1:1` | 1080x1080 | IG square, Discord embed | 1024x1024 |
| `9:16` | 1080x1920 | Stories, Reels, TikTok | 832x1472 |
| `16:9` | 1920x1080 | Twitch panel, banner | 1344x768 |
| `3:4` | 1080x1440 | print-ish / general | 960x1280 |

Generate at the Flux res, upscale to target, never stretch.

## See also

- `docs/marquee-brief.md` -- the full project brief (source of truth)
- `docs/ADR/0001-judgment-vs-execution.md`
- `docs/ADR/0002-statelessness-contract.md`
