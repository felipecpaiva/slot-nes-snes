---
title: "Pace PAL 2600 games at 49.92 Hz with a PAL Speed row"
phase: 14
area: video
type: feature
size: S
depends_on: [158-a2600-canvas-screen, 66-pal-pacing]
---

## Why
Stella reports 49.92 fps for a 312-line game (tested); 30 of his dumps are Europe. NTSC at 59.92 is inside ADR 0071's window and needs nothing.

## Scope
- [ ] ADR 0071's paced path for A2600; PAL Speed row (Native default) stored as `a2600` in `Config/pal_speed.txt`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `pal_pacing.rs` extension | a 312-line generated cart is paced at its own fps under Native, at 60 under Panel |

## Edge cases
| Case | Expected handling |
|---|---|
| A game switches line count at runtime | `SET_SYSTEM_AV_INFO` path of patch 0006 |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Part of issue 162: a PAL dump runs at the right speed and pitch.

## References
- ADR 0095; docs/research/atari-plan.md
