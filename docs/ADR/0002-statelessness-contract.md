# ADR 0002: Statelessness contract

## Status

Accepted

## Context

LLMs and diffusion models have attractor states. A stateless director asked
for "cosmic club poster" fifty times tends to converge on the same handful of
choices -- purple, circles, neon -- every time. The naive fix, giving the tool
memory of past runs ("don't repeat what you did last time"), does not
actually solve this: forgetting does not produce range on its own, and a tool
that references its own history is one step from developing a house style,
which directly contradicts the goal of every poster being genuinely
different.

## Decision

Marquee's runs are fully isolated and stateless:

- All run state lives in `runs/<slug>/`. Deleting that folder erases the run
  completely, with nothing left behind anywhere else.
- No agent may read any other run's folder. This is enforced in the tool
  layer, not just by convention: the file-access helper takes the active
  run's slug and refuses paths outside it, and a test asserts this directly.
- The only cross-run memory is `pinned.jsonl`, and it is deliberately narrow:
  append-only, human-readable, written exclusively by an explicit
  `marquee pin "<note>"` call from the Meat Gate. No stage writes to it
  automatically, ever.
- No cached palettes, no "last time" heuristics, no learned preferences.

Range comes from a different mechanism entirely: forced constraint draws from
`decks/constraints.jsonl` (see the Director's role) and font draws from
`decks/typefaces.jsonl`. Forgetting doesn't produce variety; forced draws do.

## Consequences

- Every run is independently reproducible from its own folder and fully
  disposable -- there is no hidden state anywhere else that would make a
  deleted run's absence incomplete.
- The tool cannot develop an implicit house style over time, which is the
  entire point: Marquee is explicitly not a template engine.
- This is the exact inverse of Signet's contract, and that is intentional,
  not an oversight -- see Signet's own ADR on why a brand identity tool must
  do the opposite. Do not import Signet's registry pattern into this repo.
- The isolation guard is a real architectural boundary, not just documentation:
  it must be enforced in code and covered by a test, not merely a convention
  future stages are expected to honor.
