# Marquee

A stateless, agent-driven asset generator. The first recipe is event posters
for FFXIV venues; the architecture is recipe-agnostic.

See [`docs/marquee-brief.md`](docs/marquee-brief.md) for the full spec and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the pipeline overview.

## Install

```bash
poetry install
poetry run marquee --version
poetry run marquee doctor
```

## Data setup

Everything under `data/` is user-specific (decks, venues) and gitignored.
Each subdirectory ships a `*.example.*` starter file -- copy it to the real
filename and edit it:

```bash
cp data/decks/constraints.example.jsonl data/decks/constraints.jsonl
cp data/decks/typefaces.example.jsonl data/decks/typefaces.jsonl
cp data/venues/venue.example.json data/venues/<your-venue>.json
```

## Status

M0 (skeleton) only. See the repo's issue tracker / project board for the
full roadmap.
