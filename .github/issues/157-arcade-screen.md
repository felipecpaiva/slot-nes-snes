---
title: "Give each arcade board its own Screen section, and stand vertical games upright"
phase: 16
area: video
type: feature
size: M
depends_on: [156-arcade-options]
---

## Why
Every system has its own Screen section. Vertical CPS games ask the frontend for a quarter turn, which slot refused.

## Scope
- [x] Neo Geo: Shader, Picture. CPS1 and CPS2: Shader, Picture, Vertical Games (Upright, Turned) in `Config/arcade.txt`.
- [x] Quarter turns answered for the arcade cores only; slot turns the frame into a 3:4 picture on a 576x384 canvas.
- [x] Turned: FBNeo's vertical mode on, the D-pad turned for a handheld held right edge up.

## Tests
| ID | File | Asserts |
|---|---|---|
| S1 | `arcade_screen.rs` | sections, rows, persistence, upright canvas with the real core, turned frame, horizontal sets untouched, the turned pad |
| S2 | `canvas.rs (in-source)` | quarter turns answered only when asked for; the turned frame lands upright at 3:4 in the middle |

## Edge cases
| Case | Expected handling |
|---|---|
| A quarter turn asked by another core | still refused |
| Turned on a horizontal game | nothing changes |

## Acceptance
- [x] S1 and S2 pass; upstream sites (g) and (h) take their tokens.

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
