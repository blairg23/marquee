# Read this first

This is a starter kit, not a repo. Unzip it into an empty folder and point Claude Code at
it. It contains the spec, the hand-written data files, and the agent skills. It contains no
code, because the code is what Claude Code is going to write.

## What is in here

```
marquee-brief.md              the spec. everything is in here.
KICKOFF.md                    the prompt to paste into Claude Code
.claude/skills/               four agent skills, already written
  marquee-intake/SKILL.md          collects the brief, designs nothing
  director/SKILL.md         draws constraints, proposes 3 concepts
  designer/SKILL.md      concept -> layout.json, owns type and palette
  critic/SKILL.md          inspects the render, emits patches, never praises
decks/
  constraints.jsonl           the anti-sameness deck. Sia must draw from it.
  typefaces.jsonl             OFL-only font stack, drawn as a deck not a fixed pairing
$MARQUEE_HOME/venues/
  club-moon.json              filled in. Discord URL still TODO.
  the-gatsby.json             skeleton, fill in when you get to it
  edge-of-the-abyss.json      skeleton
  silver-helix.json           skeleton
docs/                         empty. Claude Code writes ARCHITECTURE.md and the ADRs here.
```

## Before the first real run

1. **Fill in `$MARQUEE_HOME/venues/club-moon.json`.** The Discord URL is `TODO`. Verify the plot and
   world too, since I wrote those from memory of what you told me.
2. **Drop the logos in.** `assets/club-moon/logo.png` and the DJ wordmarks. Marquee will
   never generate these, so if the file is not there the run fails at compose.
3. **Install ComfyUI and Flux.** This is on the critical path for M1 and nothing in the
   render pipeline can be tested without it.
4. **Check Pillow has Raqm.** Without it there is no kerning and no ligature support, and
   poster type looks subtly wrong in a way that is genuinely hard to diagnose later.

## The one rule that keeps this from becoming a template engine

Sia draws from `decks/constraints.jsonl` before it thinks about the event, and it cannot
negotiate the draw. Everything else in the design follows from that tuple. If you ever find
yourself letting the director "pick something that fits Club Moon better," you have
rebuilt the thing you were trying to avoid.
