# Marquee: Project Brief

> Drop this whole file into Claude Code at the root of a new working directory.
> Ask it to register/generate the repo with RepoScaffold, then generate the backlog
> from the Roadmap section. Do not invent RepoScaffold flags. Read RepoScaffold's
> own docs/CLI help first and use the real ones.

---

## 0. Names

Two layers, per ET convention: plain names outward, mythology inward.

### Naming discipline (binding)

**Internal names appear ONLY in planning docs under `/docs`.** They must never appear in
`/src`, in CLI commands, in config keys, in trace stage ids, in skill names, in file names,
or in anything a user or another tool sees.

| Surface | Uses |
|---|---|
| `/docs` planning docs | mythology names, freely. That is what they are for. |
| CLI | `marquee <verb>`. Always. |
| `/src` modules | role names: `director.py`, `designer.py`, `critic.py` |
| trace stage ids | `director`, `designer`, `renderer`, `critic`, `gate` |
| `.claude/skills/` | role names: `director/`, `designer/`, `critic/` |

The mythology is a thinking tool and a naming convention for humans. It is not an API.

**Outside name: Marquee.** The lit sign outside a venue announcing who is playing
tonight. This is what the repo, the docs, and any public face are called.

**Inside name: Ptah** (planning docs only; the CLI is `marquee`). Ptah is the Egyptian craftsman-creator who
brings things into existence by conceiving them in the heart and speaking them with the
tongue, which is exactly what this does: a brief in words becomes a finished visual
artifact. Sits beside Thoth and Enki in the ET naming system. Four letters, unambiguous
on a command line.

If you want a different outside name, it is a one-line swap. Nothing below depends on it.

Internal role names follow the same mythology map:

| Stage | Name | Why |
|---|---|---|
| Director | **Sia** | Egyptian personification of perception and creative conception. Has the idea. |
| Designer | **Seshat** | Goddess of measurement, drafting, and architectural layout. Owns the plan. |
| Renderer | **Khnum** | The potter god who shapes forms on his wheel. Pure execution, no opinions. |
| Critic | **Ma'at** | Weighs a thing against the standard. Returns truth, not encouragement. |
| Human gate | **Meat Gate** | You. Final authority. Nothing ships without a carbon-based sign-off. |

The Meat Gate is deliberately off the mythology system. Dev-facing internals in ET use the
Deadpool easter-egg naming (Billy, Wade, Weasel), and the human gate is dev-facing.
Stage id `meat_gate`, command `marquee gate`.

Rejected outside names: `PosterCreator` (contradicts the general-purpose goal on day one),
`AssetGenerator` (a category, not a product, and this is a directed studio with a critic
in the loop, not a generator), `Fabricator` (good factory fit, but "fabricated" invites the
obvious AI-art joke), `Foundry` (real design-world resonance, hopelessly crowded in dev
tooling).

---

## 1. What Marquee is

A **stateless, agent-driven asset generator**. The first recipe is event posters for
in-game FFXIV venues. The architecture is recipe-agnostic; Twitch banners, mix cover art,
and Discord announcement images are later recipes against the same skeleton.

**The core bet:** separate *judgment* from *execution*. Judgment stages are LLM agents.
Execution stages are deterministic tools with zero creative latitude. The expensive
generative step (background art) is isolated so the tight iteration loop never touches it.

**The core constraint:** every output must be a genuinely different piece of art. Marquee is
explicitly *not* a template engine. Design decisions that would make it one are rejected
in Section 7.

---

## 2. Standalone always, ET-compatible by construction

**Marquee is a standalone tool. Always.** It never takes a build-time dependency on any
other ET component. It ships, installs, and runs on its own with no ET ecosystem present.

ET integration is *composition*, not integration: because every operation is reachable via
CLI flags or a config/template file, other ET tools wrap Marquee from the outside. In
particular there is **no CueQueue adapter and no CueQueue code anywhere in this repo**.
CueQueue, if used, queues `marquee art --run <slug>` as a job like it would any other binary.
That is the entire integration surface. If you find yourself importing CueQueue, stop.

The same rule holds for the agent layer: an LLM provider is behind an interface, and after
M1 the tool produces finished posters with no LLM in the loop at all.

It still must meet the 8 ET component criteria, because those are what make it composable:

1. **Unified install/run/idempotency**, Poetry. `poetry install && poetry run marquee`.
   Re-running any stage on the same run folder is idempotent.
2. **CLI or GUI**, CLI is the primary and complete interface. A local web preview panel
   is optional and additive; the CLI must never depend on it.
3. **OS- and LLM-agnostic**, no shell-outs to OS-specific binaries; all paths via
   `pathlib`. The agent layer talks to a provider interface, not to a vendor SDK directly.
   Same for the image backend: `ComfyUIBackend` is one implementation of `ArtBackend`.
4. **Observability**, every stage emits structured events to `runs/<slug>/trace.jsonl`
   with a `zoom` field (`summary` | `stage` | `call`) so the ET dashboard can collapse
   or expand the run.
5. **Unified config layer**, `marquee.toml` at repo root for tool config, `$MARQUEE_HOME/venues/*.json`
   for venue facts, `decks/*.jsonl` for constraint decks. Different config, different
   outcome, no code changes.
6. **Standards policed by RepoScaffold**, repo registered with RepoScaffold; CI, lint,
   license, AGENTS.md, and CLAUDE.md all managed from there.
7. **Documented**, `/docs` is the single source of truth. A human or an agent should be
   able to stand this up from `/docs/QUICKSTART.md` alone.
8. **Not framework-locked**, Ptah takes input, reads config, emits output. Swapping
   ComfyUI for another backend, or Pillow for Skia, touches one adapter module.

**I/O format: JSONL everywhere.** Single-shot stages emit one line. Streaming stages emit
many. Venue and config files stay as plain JSON/TOML because they are hand-edited config,
not pipeline I/O.

---

## 3. The pipeline

```
  brief (interactive)
        |
        v
  [Sia] Director ........ draws constraints, proposes 3 concepts --> you pick
        |
        v
  [Seshat] Designer ..... layout + type + palette --> layout.json
        |
        v
  [Khnum] Renderer ...... background (ComfyUI) + cutouts (rembg) + composite (Pillow)
        |                                                    ^
        v                                                    |
  [Ma'at] Critic ........ inspects the PNG --> patch list ---+  (cheap loop)
        |
        v
  [MEAT GATE] ........... you. approve / redirect / regen (expensive, explicit)
```

**Loop economics are the whole design.** The Ma'at to Khnum loop edits only `layout.json`
and re-composites. Sub-second, no GPU. Background regeneration requires an explicit
`marquee art --regen` from you. Never automatic, never triggered by the Critic.

### 3.1 Sia (Director): judgment

- Reads the brief and the venue record.
- **Draws a constraint tuple** from `decks/constraints.jsonl` before inventing anything.
  This is mandatory and non-negotiable (see Section 7).
- Proposes exactly 3 concepts that satisfy the drawn constraints. Each concept states:
  the visual idea in one sentence, the light logic, the material, the type philosophy,
  the palette logic, and what specifically makes it unlike a generic club flyer.
- Emits `runs/<slug>/concepts.jsonl`, one concept per line.
- Does not design. Does not write prompts. Does not pick.

### 3.2 Seshat (Designer): judgment

- Takes the chosen concept and produces one artifact: `runs/<slug>/layout.json`.
- Owns layout, type system, and palette **together**. These are not separable; splitting
  type into its own agent produces posters whose type fights their layout.
- Also authors the Flux prompt for the background and the negative prompt, as fields
  inside `layout.json`.
- Everything is coordinates and named tokens. No prose instructions to a human.

### 3.3 Khnum (Renderer): deterministic tool, no LLM

- `art`: POSTs the prompt from `layout.json` to the ComfyUI HTTP API, polls, retrieves
  the background PNG into `runs/<slug>/art/`.
- `cut`: runs rembg (`birefnet-general`) over supplied gpose PNGs into `runs/<slug>/cut/`.
- `compose`: renders `layout.json` to `runs/<slug>/out/<ratio>.png` with Pillow.
  Text, glows, frames, logo placement, footer, safe margins.
- **Hard rule:** Khnum makes no aesthetic decisions. If `layout.json` is ambiguous, Khnum
  raises an error naming the ambiguous field. It never guesses.

### 3.4 Ma'at (Critic): judgment

- Reads the composed PNG plus `layout.json` plus the chosen concept.
- Checks, in order: logo integrity (Club Moon's crescent C/M must be pixel-identical to
  source, never redrawn or restyled), text legibility at thumbnail scale, information
  hierarchy, margin and bleed violations, contrast, whether the render actually delivers
  the concept, and whether the result has drifted toward generic-flyer defaults.
- Emits `runs/<slug>/critique.jsonl`, one finding per line, each with a proposed patch
  against a specific `layout.json` path.
- **Ma'at may not praise.** Findings or an empty file. No summary paragraph.

### 3.5 Meat Gate: the human

`marquee gate <run>` is a real stage, not a pause. It presents the current composite, the open
findings from `critique.jsonl`, and the constraint tuple Sia drew, then blocks on you.

Four outcomes, each appended to `runs/<slug>/decisions.jsonl`:

| Decision | Effect |
|---|---|
| `approve` | Run is sealed. Exports fire for every ratio in the brief. |
| `patch` | Selected Ma'at findings applied, re-compose, back to Ma'at. Cheap, no GPU. |
| `redirect` | Back to Seshat with your note. New `layout.json`, same background. |
| `regen` | Back to Khnum for new background art. **The only path that touches the GPU.** |

Two rules that make the gate load-bearing rather than ceremonial:

- **Nothing exports without an `approve` decision on record.** No auto-ship, no
  "critic found nothing so we shipped it."
- **The Meat Gate is the only stage that may write to `pinned.jsonl`,** and only when you
  explicitly ask. Every other stage is forbidden from touching cross-run memory. This is
  where the "only remembers what I ask it to remember" rule is actually enforced.

---

## 4. Statelessness contract

This is a hard architectural rule, not a preference.

- All run state lives in `runs/<slug>/`. Deleting that folder erases the run completely.
- **No agent may read any other run's folder.** Enforce this in the tool layer: the file
  access helper takes the active run slug and refuses paths outside it. A test asserts this.
- The only cross-run memory is `pinned.jsonl` at repo root. It is append-only, written
  **exclusively** by explicit `marquee pin "<note>"`, and human-readable. Nothing writes to it
  automatically.
- No cached palettes, no "last time" heuristics, no style history, no learned preferences.
- Venue records in `$MARQUEE_HOME/venues/*.json` are **facts, not taste**: logo path, location string,
  carrd URL, Discord URL, DJ wordmark paths, safe margins, brand-locked colors. Never
  layouts, never concepts, never prompts.

---

## 5. Data contracts

### 5.1 `$MARQUEE_HOME/venues/club-moon.json` (config, hand-edited)

```json
{
  "id": "club-moon",
  "name": "Club Moon",
  "world": "Dynamis",
  "datacenter": "Marilith",
  "location": "Goblet, Ward 3, Plot 35",
  "carrd": "club-moon.carrd.co",
  "discord": "",
  "logo": "assets/club-moon/logo.png",
  "logo_lock": true,
  "regular_night": "Thursday",
  "brand_notes": "cosmic / moon-phase. Logo is a crescent C with M lettering.",
  "safe_margin_pct": 5.0
}
```

`logo_lock: true` means the logo is placed as-is. Never regenerated, never recolored,
never traced, never restyled. Ma'at checks this.

### 5.2 `brief.json` (per run, produced by the interactive intake)

```json
{
  "venue": "club-moon",
  "event": { "title": "", "date": "", "doors": "", "theme": "" },
  "lineup": [
    { "name": "dj_me0wy", "twitch": "dj_me0wy", "set": "8-9pm", "wordmark": "assets/wordmarks/me0wy.png" }
  ],
  "gposes": ["inbox/pose-01.png"],
  "ratios": ["4:5"],
  "fonts": [],
  "notes": ""
}
```

### 5.3 Ratios

| Key | Pixels | Use | Flux gen res |
|---|---|---|---|
| `4:5` | 1080x1350 | Instagram feed (default) | 1024x1280 |
| `1:1` | 1080x1080 | IG square, Discord embed | 1024x1024 |
| `9:16` | 1080x1920 | Stories, Reels, TikTok | 832x1472 |
| `16:9` | 1920x1080 | Twitch panel, banner | 1344x768 |
| `3:4` | 1080x1440 | print-ish / general | 960x1280 |

Generate at the Flux res, upscale to target, never stretch.

### 5.4 `layout.json`

The single source of truth for the composite. Contains: canvas block (ratio, px, safe
margins), palette block (named tokens with hex, plus a stated color logic), type block
(roles like `headline` / `lineup` / `meta` / `footer`, each with family, size, tracking,
case, and a palette token reference), layers array in z-order (each with type, source,
anchor, offset, scale, opacity, blend, and effects), and an `art` block holding the Flux
prompt, negative prompt, seed, steps, cfg, and gen res.

Every visual property is addressable by JSON path so Ma'at can emit precise patches.

### 5.5 `decks/constraints.jsonl`

One axis per line. Sia draws one value from each axis.

```jsonl
{"axis":"composition","values":["strict grid","orbital","stratified bands","collage","single dominant object","diagonal cascade","radial symmetry","negative-space void"]}
{"axis":"light","values":["single hard source","bioluminescent","backlit silhouette","no discernible source","reflected/bounced only","overexposed bloom","candlelit warm"]}
{"axis":"material","values":["letterpress","chrome","watercolor","CRT scanline","stone relief","risograph","oil impasto","cyanotype","torn paper"]}
{"axis":"type_philosophy","values":["type dominates","type hidden in the scene","type as structure","type minimal/absent","type as data readout","type hand-lettered"]}
{"axis":"color_logic","values":["monochrome + one accent","complementary clash","analogous drift","desaturated with neon punctuation","duotone","full-spectrum prism"]}
```

**Why this exists:** LLMs and Flux both have attractor states. Ask a stateless director for
"cosmic club poster" fifty times and you get purple, circles, and neon fifty times.
Forgetting does not produce range. Forced constraint draws do. Extend the decks over time;
never let Sia bypass them.

### 5.6 `decks/typefaces.jsonl`: the font stack

**All fonts are SIL OFL.** Nothing else enters the repo. OFL permits bundling,
redistribution, and embedding, which keeps Marquee installable by anyone with no license
audit. `marquee fonts sync` fetches the stack into `assets/fonts/` from Google Fonts' Git
repo; the list is data, not code.

Fonts are a **deck, not a pairing**. Seshat draws from categories rather than defaulting to
one house style, for the same reason Sia draws constraints. A fixed pairing is a template
by another name.

```jsonl
{"class":"display_signage","fonts":["Bungee","Bungee Inline","Bungee Shade","Big Shoulders Display","Archivo Black","League Gothic"]}
{"class":"display_novelty","fonts":["Monoton","Syne","Unbounded","Rubik Glitch","Bowlby One","Silkscreen"]}
{"class":"geometric_tech","fonts":["Orbitron","Chakra Petch","Michroma","Audiowide","Space Grotesk"]}
{"class":"serif_display","fonts":["Fraunces","Cinzel","Playfair Display","Bodoni Moda","Instrument Serif"]}
{"class":"grotesque_body","fonts":["Inter","Archivo","IBM Plex Sans","Public Sans","Manrope"]}
{"class":"mono_data","fonts":["IBM Plex Mono","JetBrains Mono","Space Mono","DM Mono"]}
{"class":"script_hand","fonts":["Caveat","Yellowtail","Grechen Fuemen","Sacramento"]}
```

Two implementation notes that matter more than they look:

- **Build Pillow with Raqm.** Without it you get no proper kerning, no ligatures, and no
  complex shaping, and poster type looks subtly wrong in a way that is hard to diagnose.
  `marquee doctor` must check for Raqm support and fail loudly if it is missing.
- **Prefer variable fonts.** Fraunces alone has weight, optical size, softness, and a
  "wonk" axis. Exposing axes to Seshat as continuous parameters gives it a far larger
  design space than a list of static weights, which directly serves the no-sameness rule.
  Store axis values in `layout.json` under each type role.

---

## 6. Repo layout

```
marquee/
  pyproject.toml            # poetry
  marquee.toml                 # tool config: backends, endpoints, defaults
  CLAUDE.md                 # generated/managed by RepoScaffold
  AGENTS.md                 # generated/managed by RepoScaffold
  pinned.jsonl              # the ONLY cross-run memory. append-only, human-written.
  docs/                     # single source of truth
    QUICKSTART.md
    ARCHITECTURE.md
    RECIPES.md
    ADR/
  src/marquee/
    cli.py                  # typer/click entrypoint
    config.py               # unified config layer
    trace.py                # observability, zoom-tagged JSONL events
    runs.py                 # run folder lifecycle + the isolation guard
    contracts/              # pydantic models: brief, layout, concept, critique
    agents/
      base.py               # provider-agnostic agent interface
      director.py
      designer.py
      critic.py
    backends/
      art_backend.py        # ABC
      comfyui.py
      cutout.py             # rembg adapter
    compose/
      renderer.py           # Pillow composite from layout.json
      text.py
      effects.py
  recipes/
    poster.md
    twitch-banner.md
    mix-cover.md
  $MARQUEE_HOME/venues/
    club-moon.json
    the-gatsby.json
    edge-of-the-abyss.json
    silver-helix.json
  decks/
    constraints.jsonl
    typefaces.jsonl         # OFL-only font stack, drawn from per run
  assets/                   # logos, wordmarks, fonts. gitignored if large.
    fonts/                  # populated by `marquee fonts sync`. gitignored.
  inbox/                    # drop gposes here
  runs/                     # gitignored. disposable.
  .claude/skills/
    director/SKILL.md
    designer/SKILL.md
    critic/SKILL.md
    marquee-intake/SKILL.md
  tests/
```

---

## 7. Non-goals and invariants

Reject any proposal that violates these, including your own later proposals.

1. **No master template.** There is no base layout that events are recolored into.
   Concept and layout are invented per run.
2. **No style memory.** Ptah must not learn preferences, cache palettes, or reference
   prior runs. Range comes from constraint draws, not from history.
3. **Khnum has no opinions.** If the renderer starts making aesthetic fallbacks, the
   separation has failed. Ambiguity is an error, not a default.
4. **No AI-generated text on the poster.** All type is composited by Pillow from real
   fonts. Diffusion models cannot spell.
5. **No AI-generated characters.** Character imagery is always the user's own gpose
   screenshots, background-removed. Never synthesized.
6. **Logos are never regenerated.** `logo_lock` venues get pixel-exact placement.
7. **Background regen is explicit.** The critic loop never triggers GPU work.
8. **Ma'at does not compliment.** Findings only.

---

## 8. Roadmap

Ticket-sized. Feed to RepoScaffold as the initial backlog.

### M0: Skeleton
- `#1` Poetry project, typer CLI shell, `marquee --version`, `marquee doctor`
- `#2` Config layer: `marquee.toml` load/merge/validate
- `#3` Pydantic contracts for brief / venue / concept / layout / critique
- `#4` Run lifecycle: `marquee new <venue>` creates `runs/<slug>/`, plus the cross-run
  isolation guard and a test proving an agent cannot read a sibling run
- `#5` `trace.py` zoom-tagged JSONL event emitter

### M1: Render before intelligence
Build the deterministic half first. It is testable without an LLM and de-risks everything.
- `#6` ComfyUI backend: submit workflow, poll, retrieve. Behind the `ArtBackend` ABC
- `#7` Flux fp8 txt2img workflow template, parameterized by prompt/seed/res
- `#8` rembg cutout adapter with `birefnet-general`
- `#9` Font stack: `decks/typefaces.jsonl`, `marquee fonts sync`, OFL license manifest,
  and a test asserting every bundled font is OFL
- `#10` Pillow compositor: layers, anchors, scale, opacity, z-order. `marquee doctor` fails
  loudly if Pillow lacks Raqm support
- `#11` Text rendering: variable-font axis support, tracking, case, wrapping,
  glow/outline/shadow effects
- `#12` Ratio system and safe-margin enforcement, all five ratios
- `#13` `marquee compose <run>` renders a hand-written `layout.json` end to end
- **M1 exit criteria:** you can hand-author `layout.json` and get a finished poster.
  The LLM layer is now optional, not load-bearing.

### M2: Judgment
- `#14` Provider-agnostic agent base (no vendor SDK in business logic)
- `#15` `decks/constraints.jsonl` plus the draw mechanism
- `#16` Sia: constraint draw, 3 concepts, `concepts.jsonl`, `marquee direct`
- `#17` Seshat: concept to `layout.json` including type draw from `typefaces.jsonl`,
  `marquee design`
- `#18` Ma'at: PNG inspection to `critique.jsonl` with JSON-path patches, `marquee critique`
- `#19` `marquee patch` applies selected critique patches to `layout.json`
- `#20` `marquee loop` runs critique to patch to compose until clean or max iterations
- `#21` Meat Gate: `marquee gate <run>`, the four decisions, `decisions.jsonl`, and a test
  asserting no export path exists without an `approve` on record

### M3: Intake and venues
- `#22` Interactive intake: conversational brief refinement to `brief.json`
- `#23` Venue records for all four venues
- `#24` `marquee pin` and the `pinned.jsonl` contract, writable only from the Meat Gate
- `#25` The Claude Code skill files in `.claude/skills/`

### M4: Ship the poster
- `#26` End-to-end run for a real Club Moon Thursday, all deliverables
- `#27` Multi-ratio export in one pass, gated on `approve`
- `#28` `docs/QUICKSTART.md` verified by standing the repo up from scratch on a clean box

### M5: Generalize
- `#29` Recipe abstraction: `recipes/*.md` define required inputs, canvases, critic checks
- `#30` `recipes/twitch-banner.md`
- `#31` `recipes/mix-cover.md`
- `#32` Optional local preview panel (additive, CLI stays complete without it)

---

## 9. Kickoff prompt for Claude Code

```
Read marquee-brief.md in full.

1. Read RepoScaffold's own docs and CLI help. Use its real commands, do not invent flags.
   Create or register this repo with RepoScaffold under the name "marquee".
2. Generate the backlog from the Roadmap section, one ticket per line item, grouped by
   milestone.
3. Write /docs/ARCHITECTURE.md from Sections 3, 4, and 5. Write an ADR for the
   judgment-vs-execution split and an ADR for the statelessness contract.
4. Scaffold the repo layout in Section 6. Empty modules with docstrings and signatures
   are fine at this stage.
5. Implement M0 only. Stop and check in before starting M1.

Do not start on the agent layer. M1 is deterministic rendering and it comes first.
Do not import CueQueue or any other ET component. This repo stands alone.
```

---

## 10. Settled decisions

Recorded so they do not get relitigated mid-build.

| Question | Decision |
|---|---|
| Outside name | Marquee |
| Inside name / CLI | Ptah / `marquee` |
| ET integration | Standalone always. Composition from outside via CLI, never a dependency |
| CueQueue | Not in this repo. It wraps `marquee` as a job if you want it to |
| Art backend | ComfyUI over direct HTTP, behind `ArtBackend` |
| Fonts | SIL OFL only, fetched by `marquee fonts sync`, drawn as a deck not a fixed pairing |
| Build order | Deterministic rendering (M1) before any agent work (M2) |
| Default ratio | 4:5, 1080x1350 |

---

## 11. Scope boundary: Marquee does not do branding

Logos, wordmarks, and brand identity are a **separate tool**, planned as `Signet`
(inside name: `Ren`, the Egyptian concept of the name, the part of the soul that must be
spoken and preserved for a thing to exist). Do not build it here. Do not let it leak into
this repo.

The boundary is not arbitrary. Three hard differences:

1. **Opposite memory policy.** Marquee must be unique every run. A brand identity must be
   *identical* every run, forever. The statelessness contract in Section 4 is correct for
   Marquee and actively wrong for branding.
2. **Opposite output format.** Brand marks are vector, authored as SVG. Marquee is raster,
   composited with Pillow. Almost no shared code.
3. **Opposite critic.** Ma'at judges a poster at feed scale. A brand critic judges a mark
   at 16px favicon size, in single-color, and reversed on dark.

**The handoff contract.** Signet is *upstream* of Marquee, not a sibling. Signet produces
the brand kit; Marquee consumes it as venue facts. Concretely, Signet emits a venue record
matching the schema in Section 5.1, plus the logo and wordmark files it references:

```
signet export club-moon --to-venue > $MARQUEE_HOME/venues/club-moon.json
```

Marquee never generates, redraws, restyles, or recolors a mark. It places what Signet
(or a human) produced. That is what `logo_lock` in Section 5.1 already enforces, and it is
why the invariant exists.

**Known hard problem for whoever builds Signet later:** diffusion models are bad at logos.
They produce mushy, artifact-ridden, unreproducible raster output that cannot be scaled or
color-separated. The realistic pipeline is an agent authoring SVG paths directly for
geometric marks, with diffusion used only for moodboarding, plus `vtracer`/`potrace` when
something must come back from raster. Do not promise a one-shot logo generator.

### M3 additions: the interview layer

- `#33` `<cli> init`: create the home dir, seed defaults, first-run questions
- `#34` Config resolution: shipped defaults, user overrides, CLI flags. `decks show`
  prints the merged view with provenance per value
- `#35` `venue new` / `client new` interview skill, writes a validated record
- `#36` `venue edit <id>`: re-interview named fields only
- `#37` `decks extend`: propose-only, with redundancy checking against existing axis values
- `#38` Gate approval required before any proposed deck value is written

---

## Data layer

`data/` sits beside `src/`, and its location comes from config. Nothing in `src/` ever
hardcodes a path.

```
Marquee/
  src/marquee/
  data/
    decks/      constraints.jsonl, typefaces.jsonl   COMMITTED
    venues/     your records                          not committed
    assets/     logos, wordmarks                      not committed
  marquee.toml
```

```toml
[paths]
data_dir = "./data"
runs_dir = "~/.local/state/marquee/runs"
```

**Why the config indirection matters.** `data_dir` defaults to `./data` for a dev checkout,
but it is just a value. Point it at a shared drive, a synced folder, or a per-machine
location and nothing in the code changes. That is also what keeps this working when the
package is installed rather than run from a checkout, and it is the reason `data/` is a
sibling of `src/` rather than living inside the package.

**What is committed and what is not.** `data/decks/` is committed: those are the shipped
defaults that make a fresh install work, and they define tool behavior. Everything else
under `data/` is user data. Marquee for a water balloon fight at a park ships with working
decks and none of your venues.

**Durability.** Uncommitted does not mean unprotected. Whatever syncs this folder versions
those files. The only real hazard is `git clean -x`, which deletes ignored files. Plain
`git clean -fd` respects `.gitignore` and leaves them alone.

### User data is generated, not hand-authored

Hand-editing stays possible. It is not the expected path.

```
<cli> init              first run. creates data_dir, seeds decks, asks a few questions
<cli> venue new         interviews you, writes a venue record
<cli> venue edit <id>   re-asks only the fields you name
<cli> decks extend      proposes new axis values for your kind of events
```

The park organizer answers "Riverside Park", "no website", "no logo" and has a working venue
record without ever seeing JSON. You answer with a Goblet plot number. Same interview, same
schema, different outcome.

Each interview is a separate single-purpose skill.

**One hard rule on `decks extend`.** The deck is the entire anti-sameness mechanism, and an
LLM asked to invent creative axes produces clustered, overlapping values. "Art deco" and
"1920s glamour" as two entries silently halves your real variety. So it may only propose,
never append; every proposal is checked for redundancy against existing values on that axis;
and you approve each one at the gate. A tool that helpfully extends its own deck will
helpfully destroy the thing that makes it work.
