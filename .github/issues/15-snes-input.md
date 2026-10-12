---
title: "Patch 0007: Pass SNES X/Y/L/R to the game, add SELECT+X picture mode and guard SELECT+Y"
phase: 2
area: input
type: feature
size: M
depends_on: [14-libretro-env-and-hires]
---

## Why
Upstream always strips X/Y for turbo and uses L1/R1 for picture mode. SNES needs X, Y, L and R as game buttons, so picture mode moves to a new SELECT+X chord on SNES only (docs/PLAN.md Phase 2 deliverables, Build steps 15, 16, 17, 20). Decision: SNES picture mode toggles with SELECT+X (docs/DECISIONS.md).

## Scope
`patches/0007-input.patch`:
- [x] `slot: crates/slot-retro/src/core.rs`: new `enum TurboMode { Turbo, Off, PassThrough }` and `ButtonMask::apply(self, mode, frame)` delegating to the existing `turbo`/`without_turbo` (`:27-42`). `ButtonMask` itself unchanged. Done in the new file `slot-retro/src/turbo_mode.rs` (core.rs is untouched, CONTRIBUTING section 3), plus `TurboMode::from_flags(pass_through, turbo)`.
- [x] `Platform::turbo_mode()`: SNES PassThrough always; NES keeps slot's X/Y turbo. Implemented as `Platform::passes_xy_through()` (bool), because slot-store cannot name `slot_retro::TurboMode` (no cross dependency, none may be added). `from_flags` turns it into the mode.
- [x] `slot: crates/slot/src/emu.rs`: `Shared.turbo` stays an `AtomicBool`; new `Shared.pass_through: AtomicBool` checked first at `:662`. `set_turbo(bool)` unchanged. Also new `set_pass_through` and `passes_through` (the getter lets tests prove the session wiring).
- [x] `slot: crates/slot/src/session.rs`: set turbo mode and pass-through on open. `spawn_core` sets `emu.set_pass_through(...)` and the gesture engine's SELECT+X chord from the platform.
- [x] `owns_shoulders(Snes) = false`. `slot-store/tests/snes_platform.rs` (ours, patch 0005) had a test pinning the old value; it now asserts SNES false and NES true.
- [x] `slot: crates/slot-input/src/gesture.rs:409-424`: `Btn::X => (8192, Action::VideoModeToggle)`, new `Action::VideoModeToggle`. The engine is platform blind, so the chord is gated by a new `Gestures::set_video_mode_chord(bool)` (default off). Without the gate SELECT+X would stop reaching GBA games.
- [x] `slot: crates/slot/src/app.rs` near `:1276`: `VideoModeToggle` arm handled only when the platform is Snes. One line, `self.set_picture(self.video_mode.flipped(self.platform))`; `VideoMode::flipped(platform)` (new file `slot/src/snes_input.rs`) returns the mode unchanged off SNES, so `set_picture` returns early.
- [x] `slot: crates/slot/src/app.rs` near `:1445`: when `!core.has_colour_correction()`, return true with no state change and no toast. Done as a one-token change on the `if` (`&& self.core.has_colour_correction()`), 2 changed lines. The action then falls through `adjust` and is ignored by every later arm (returns false, not true); the 25 line budget left no room for a separate early return. No state change, no toast, proven by tests.

## Tests
| ID | File | Asserts |
|---|---|---|
| T16 | `slot-retro/tests/snes_turbo.rs` | `apply(PassThrough, f)` keeps X/Y; `apply(Turbo, f)` equals upstream `turbo(f)` |
| T17 | `slot/tests/snes_shoulders.rs` | `taken_buttons()` while playing: GBA `[]`, GB `[L1, R1]`, Nes `[L1, R1]`, Snes `[]` |
| T22 | `slot/tests/snes_select.rs` | SNES: SELECT tap reaches the core mask; SELECT+R1 saves a state with the R bit never sent; SELECT held then Y: Y never sent, `colour_correction` unchanged, no toast; SELECT+X: X never sent and video mode toggles |
| T22b | `slot/tests/select_x_gba.rs` | Same SELECT+X sequence on a GBA cart, run in both trees: identical per-frame core input masks and identical state |

Upstream tests stay unmodified, in particular `slot-retro/tests/turbo.rs` and `slot-input` gesture tests (none assert SELECT+X).

## Edge cases
| Case | Expected handling |
|---|---|
| SELECT+X chord added for SNES video mode changes GBA input behaviour | T22b runs the same SELECT+X sequence on a GBA cart in both trees and asserts identical core input masks |
| SELECT+Y on SNES flips `colour_correction` and toasts with no effect | Guard in `app.rs` near 1445: when `!core.has_colour_correction()`, return true with no state change and no toast |

## Acceptance
- [x] T16, T17, T22, T22b green (plus `snes_emu_input.rs`, see Decisions).
- [ ] GBA harness compare 0 diffs (H1, H2). Coordinator runs `task harness:compare`; `select_x_gba.rs` already shows the same masks and state on the pre-change tree.
- [x] `app.rs` changes limited to the two guarded arms plus one-token hunks. 3 changed lines (1 added arm line, 1 changed `if` line = 2), total across 0001 to 0007 is 25.

## Device check (RG34XXSP)
None separate. Button and chord checks are in the phase device check in 11-phase-2-snes.

## Review notes
- Gotcha 5 (X/Y are always stripped): `turbo()` and `without_turbo()` both clear X/Y (`slot: crates/slot-retro/src/core.rs:27-42`); SNES must go through PassThrough.
- The Turbo quick row is a documented no-op on SNES (handled in 23-states-quickmenu-resume).
- SELECT+Y suppression applies to NES too, since `has_colour_correction()` is false for every NES/SNES core.

## References
- docs/PLAN.md: Phase 2 deliverables (0007), Build steps 15, 16, 17, 20, Signature impact table (`ButtonMask`, `Shared`, `gesture.rs`), Edge cases by layer (Input), Open questions (resolved: SNES video mode)
- `slot: crates/slot-input/src/gesture.rs:409-424`; `slot: crates/slot/src/app.rs:1276-1281,1445-1452`; `slot: crates/slot/src/emu.rs:662-664`; `slot: crates/slot-retro/src/core.rs:27-42`

## Decisions (builder, patch 0007)
- New code lives in new files: `slot-retro/src/turbo_mode.rs`, `slot/src/snes_input.rs`. `core.rs` is not touched.
- `Platform::passes_xy_through()` and `Platform::select_x_toggles_picture()` (both exhaustive, in `platform_policy.rs`) replace the issue's `Platform::turbo_mode()`.
- SELECT+X is enabled per game in `Session::spawn_core` and stays enabled until the next spawn. Known edge: with a SNES game running, SELECT held and X pressed inside the 600 ms chord window in the polaroid view is swallowed (X is undo there). The enable flag is not cleared when the cart is ejected, because X does nothing on the shelf.
- A plain SELECT tap is not delayed by `SELECT_CHORD_MS`: the engine is the same on every platform. A tap reaches the game on release (down for 50 ms), a hold reaches it after 600 ms or when another button is pressed. SNES behaves exactly like GBA.
- SELECT+Y is suppressed on NES too (issue review note); `select_and_y_on_nes_...` proves it.
- T22b (`select_x_gba.rs`) uses only APIs that exist upstream and asserts hard coded per-step pad masks (what `Session` hands the core, before turbo) plus `slot.state` text, `video_mode.txt` and the source rect. Identity proof: it passes on the patched tree and on the pre-change tree (`libretro-env`, whose input code equals upstream). The coordinator can also copy it into `build/slot-upstream/crates/slot/tests/` and run it there.
- Extra test file `snes_emu_input.rs` feeds a recording core through the real emu loop to prove X/Y/L/R reach `run_frame` with turbo on and off on SNES, and that X/Y are stripped without pass-through.
- Tests use the mock core (no real snes9x needed), so no `require_core`.
