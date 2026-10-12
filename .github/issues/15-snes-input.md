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
- [ ] `slot: crates/slot-retro/src/core.rs`: new `enum TurboMode { Turbo, Off, PassThrough }` and `ButtonMask::apply(self, mode, frame)` delegating to the existing `turbo`/`without_turbo` (`:27-42`). `ButtonMask` itself unchanged.
- [ ] `Platform::turbo_mode()`: SNES PassThrough always; NES keeps slot's X/Y turbo.
- [ ] `slot: crates/slot/src/emu.rs`: `Shared.turbo` stays an `AtomicBool`; new `Shared.pass_through: AtomicBool` checked first at `:662`. `set_turbo(bool)` unchanged.
- [ ] `slot: crates/slot/src/session.rs`: set turbo mode and pass-through on open.
- [ ] `owns_shoulders(Snes) = false`.
- [ ] `slot: crates/slot-input/src/gesture.rs:409-424`: `Btn::X => (8192, Action::VideoModeToggle)`, new `Action::VideoModeToggle`.
- [ ] `slot: crates/slot/src/app.rs` near `:1276`: `VideoModeToggle` arm handled only when the platform is Snes.
- [ ] `slot: crates/slot/src/app.rs` near `:1445`: when `!core.has_colour_correction()`, return true with no state change and no toast.

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
- [ ] T16, T17, T22, T22b green.
- [ ] GBA harness compare 0 diffs (H1, H2).
- [ ] `app.rs` changes limited to the two guarded arms plus one-token hunks.

## Device check (RG34XXSP)
None separate. Button and chord checks are in the phase device check in 11-phase-2-snes.

## Review notes
- Gotcha 5 (X/Y are always stripped): `turbo()` and `without_turbo()` both clear X/Y (`slot: crates/slot-retro/src/core.rs:27-42`); SNES must go through PassThrough.
- The Turbo quick row is a documented no-op on SNES (handled in 23-states-quickmenu-resume).
- SELECT+Y suppression applies to NES too, since `has_colour_correction()` is false for every NES/SNES core.

## References
- docs/PLAN.md: Phase 2 deliverables (0007), Build steps 15, 16, 17, 20, Signature impact table (`ButtonMask`, `Shared`, `gesture.rs`), Edge cases by layer (Input), Open questions (resolved: SNES video mode)
- `slot: crates/slot-input/src/gesture.rs:409-424`; `slot: crates/slot/src/app.rs:1276-1281,1445-1452`; `slot: crates/slot/src/emu.rs:662-664`; `slot: crates/slot-retro/src/core.rs:27-42`
