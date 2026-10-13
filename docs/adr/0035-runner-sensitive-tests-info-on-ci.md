# 0035. Run runner-sensitive test binaries as information only on CI

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0010](0010-macos-primary-ci.md), `scripts/run-tests.sh`, `.github/workflows/test.yml`

## Context

Shared GitHub runners fail upstream's real-time and GPU pixel tests on the unpatched upstream
tree too: slot `emu` and `audio` (timing), slot-gfx `pipeline` and slot `render_shelf` (the
runner's GPU draws the same frame differently). Our own real-time budget tests (`snes_ff`,
`snes_rewind`) and the retro shader pixel test (`retro_pipeline`) behave the same way there. On
those runners a failure says nothing about the patches.

## Decision

On CI (`CI=true`) these binaries are left out of the gating run and run apart afterwards as
information, with a warning when they fail. Locally they still gate `task check`.

## Consequences

- CI stays green on runner noise; real regressions in those areas are caught by the local
  `task check` that every patch PR runs before review.
- A new runner-sensitive test binary must be added to `ci_timing` in `scripts/run-tests.sh`
  with the CI run that shows the upstream or runner failure.
