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
- [x] `frame_dump --time` mode in `harness/frame_dump.rs`. Deviation: the timing is a separate example, `evals/frontend_cost.rs`, copied into `build/slot/crates/slot/examples/` by the eval. `frame_dump.rs` is also built in the upstream tree, and the timing needs patched-only calls (`LibretroCore::set_canvas`, `Core::canvas`); editing it would also make `control.ok` stale.
- [x] `evals/eval-frontend-cost.sh` (`task eval:frontend-cost`): run `frame_dump --time` on GBA (mgba, gpsp) and NES/SNES test ROMs; mean microseconds per frame for convert + publish + upload from `SLOT_TRACE`; fail if NES or SNES exceeds max(GBA) by more than 5%.
- [x] Not needed (the eval passes). Only if the eval fails: a 64K-entry RGB565 LUT in `canvas.rs` that is bit-identical to the per-pixel formula.

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
- [x] `evals/eval-frontend-cost.sh` passes for NES and SNES. Min of 3 interleaved passes, 5 repeats of 600 frames each, us/frame (convert + publish + upload): mgba 47.5, gpsp 47.2, fceumm 43.9 (92.4% of max GBA), snes9x 44.0 (92.6%). `SLOT_TRACE` has no per-frame timing, so the example times the same calls itself: convert is `run_frame` at the real canvas minus the same frames at a 1x1 canvas (difference of the minimums), publish is slot's `Frames` calls, upload is `Compositor::upload_game` (CPU side, no `glFinish`, same for GBA). The SNES test ROM is a generated 256-wide LoROM (`harness/make_assets.py snes`), so the 512-wide hi-res halving path is not timed; pass `SNES_ROM=` to time a hi-res game.
- [x] No LUT landed. If a LUT lands: GBA harness compare 0 diffs including gpSP carts, and `bench:compare` within 2%.

## Device check (RG34XXSP)
None, host measurement. Device speed is in the phase device check in 11-phase-2-snes.

## Review notes
- Gotcha 7 (RGB565 slow path): the conversion is shared with gpSP on GBA. Any LUT must be bit-identical or the harness fails on gpSP carts.
- Do not add the LUT speculatively.

## References
- docs/PLAN.md: Spec success 3, Build step 13, Evaluation criteria (Qualitative), AC-to-code coverage (Frontend cost)
