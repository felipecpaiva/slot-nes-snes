---
title: "DEFERRED: Move to Option B variable frame size for true SNES hi-res"
phase: 6
area: video
type: chore
size: L
depends_on: [32-phase-6-deferred]
---

## Why
**Deferred, rejected for v1.** Option B (variable frames up to 512x480) gives full SNES hi-res detail but is a much bigger patch. v1 uses Option A (fixed 360x240 canvas, hi-res blended 2:1) (docs/PLAN.md Approach "Video", Build step 12, Phase 6+).

## Scope
- [ ] If picked up: re-plan the pipeline, upload guard and thumbnails for variable frames, keeping GBA at 240x160.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Deferred |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [ ] A decision recorded as an ADR in docs/adr/.

## Device check (RG34XXSP)
None, deferred.

## Review notes
- Any future work must still pass the GBA harness compare at 0 diffs.

## References
- docs/PLAN.md: Approach (Video: Option A, rejected Option B), Build step 12, Phase 6+ (deferred)
