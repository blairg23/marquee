# ADR 0001: Separate judgment from execution

## Status

Accepted

## Context

Marquee's pipeline mixes two fundamentally different kinds of work: deciding
what a poster should look like (creative judgment) and actually rendering it
(mechanical execution). Every stage could plausibly be built as one kind of
agent that both decides and renders.

## Decision

Judgment stages (Director, Designer, Critic) are LLM agents that produce
structured, addressable artifacts (`concepts.jsonl`, `layout.json`,
`critique.jsonl`) and make no pixels. Execution stages (Renderer: `art`,
`cut`, `compose`) are deterministic tools with zero creative latitude that
consume those artifacts and produce pixels, and nothing else.

The expensive generative step (background art via ComfyUI) lives entirely in
the execution layer, isolated from the cheap judgment loop. The
Critic-to-Renderer patch loop only ever touches `layout.json` and
re-composites -- sub-second, no GPU. Background regeneration is a separate,
explicit, human-gated action.

If the Renderer ever starts making an aesthetic fallback decision because
`layout.json` is ambiguous, that is a bug: the separation has failed, and the
fix is to raise an error naming the ambiguous field, not to guess.

## Consequences

- M1 (deterministic rendering) is fully buildable and testable before any LLM
  is involved: hand-author a `layout.json`, run `compose`, get a finished
  poster. The LLM layer is optional, not load-bearing.
- The tight iteration loop (Critic finds an issue, Designer or the Meat Gate
  patches `layout.json`, Renderer recomposites) never touches the GPU, which
  keeps the interactive loop cheap and fast.
- Every judgment stage's output is inspectable, diffable, and patchable
  because it is structured data, not prose or an opaque image.
- The cost: judgment stages cannot take a shortcut and directly manipulate
  pixels, even when that would be the "easy" fix for a specific problem. All
  fixes must be expressible as a change to `layout.json`.
