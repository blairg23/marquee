# Kickoff

Paste this into Claude Code, launched from the repo root.

---

```
Read marquee-brief.md in full before doing anything else.

1. Read RepoScaffold's own docs and CLI help. Use its real commands, do not invent flags.
   Create or register this repo with RepoScaffold under the name "marquee".
2. Generate the backlog from the Roadmap section, one ticket per line item, grouped by
   milestone. 32 tickets, M0 through M5.
3. Write /docs/ARCHITECTURE.md from Sections 3, 4 and 5. Write ADRs for:
   - the judgment vs execution split
   - the statelessness contract
   - standalone-always and why there is no CueQueue code here
   - deterministic rendering before the agent layer
4. Scaffold the repo layout in Section 6. Empty modules with docstrings and signatures
   are fine at this stage.
5. Implement M0 only. Stop and check in before starting M1.

The skill files in .claude/skills/, the decks in decks/, and the venue records in $MARQUEE_HOME/venues/
are already written. Do not regenerate them. Wire the code to read them.

Do not start on the agent layer. M1 is deterministic rendering and it comes first.
Do not import CueQueue or any other ET component. This repo stands alone.
```

---

## After M0 lands

Do not go straight to M2 just because the agents are the interesting part. M1 first:
ComfyUI backend, rembg, fonts, the Pillow compositor.

**M1 exit criteria:** you can hand-author a `layout.json` and run `marquee compose` and get a
finished poster with zero LLM involvement. Until that works, the agent layer has nothing
solid to stand on.
