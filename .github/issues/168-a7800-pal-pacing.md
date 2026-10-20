---
title: "Pace PAL 7800 games at 50 Hz with a PAL Speed row"
phase: 14
area: video
type: feature
size: S
depends_on: [166-a7800-canvas-screen, 66-pal-pacing]
---

## Why
ProSystem reports exactly 50 fps when the header or its database says PAL (tested). 2 of his dumps are Europe.

## Scope
- [ ] ADR 0071's paced path for A7800; PAL Speed row stored as `a7800`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `pal_pacing.rs` extension | a PAL-headered generated cart is paced at 50 under Native |

## Edge cases
| Case | Expected handling |
|---|---|
| Headerless PAL dump the database misses | Runs as NTSC (core behaviour); noted in the README |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Part of issue 170.

## References
- ADR 0095; docs/research/atari-plan.md
