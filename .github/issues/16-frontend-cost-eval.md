---
title: "Add eval-frontend-cost.sh and hold NES/SNES frontend cost inside the GBA budget"
phase: 2
area: tests
type: test
size: S
depends_on: [14-libretro-env-and-hires]
---

## Why
Success criterion 3: pixel conversion, publish and upload per frame on NES/SNES stay within the GBA budget measured on the same host (docs/PLAN.md Spec, Evaluation criteria "Qualitative", Build step 13).

## Scope
- [ ] `frame_dump --time` mode in `harness/frame_dump.rs`.
- [ ] `evals/eval-frontend-cost.sh`: run `frame_dump --time` on GBA (mgba, gpsp) and NES/SNES test ROMs; mean microseconds per frame for convert + publish + upload from `SLOT_TRACE`; fail if NES or SNES exceeds max(GBA) by more than 5%.
- [ ] Only if the eval fails: a 64K-entry RGB565 LUT in `canvas.rs` that is bit-identical to the per-pixel formula.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. Gate is `evals/eval-frontend-cost.sh` |

No upstream test file is touched. If a LUT is added, the 65,536-input equality test in `canvas.rs` (09-canvas) must still pass.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Measure first; LUT only on a measured overrun |

## Acceptance
- [ ] `evals/eval-frontend-cost.sh` passes for NES and SNES.
- [ ] If a LUT lands: GBA harness compare 0 diffs including gpSP carts, and `bench:compare` within 2%.

## Device check (RG34XXSP)
None, host measurement. Device speed is in the phase device check in 11-phase-2-snes.

## Review notes
- Gotcha 7 (RGB565 slow path): the conversion is shared with gpSP on GBA. Any LUT must be bit-identical or the harness fails on gpSP carts.
- Do not add the LUT speculatively.

## References
- docs/PLAN.md: Spec success 3, Build step 13, Evaluation criteria (Qualitative), AC-to-code coverage (Frontend cost)
