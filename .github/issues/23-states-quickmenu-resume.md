---
title: "Prove save states, polaroids, quick menu, resume on boot and eject saves on NES and SNES"
phase: 3
area: platform
type: test
size: M
depends_on: [21-shaders]
---

## Why
These parity rows are mostly upstream code that becomes platform-aware through earlier patches; they need tests that prove it on NES and SNES (docs/PLAN.md Phase 3 deliverables (polaroids, quick menu), AC-to-code coverage stub).

## Scope
- [ ] Polaroids: full 360x240 canvas thumbnails, no crop (decided).
- [ ] Quick menu works on NES/SNES with the existing rows; the Turbo row is a documented no-op on SNES.
- [ ] Resume on boot through `slot.state` `cart_platform`.
- [ ] Saves and autosave under `Saves/NES|SNES` on eject.
- [ ] Downgrade behaviour documented in the README: unpatched slot boots to the shelf when `cart_platform=nes`.
- [ ] New test files committed on the `nes-snes` branch and exported with the concern they exercise.

## Tests
| ID | File | Asserts |
|---|---|---|
| T26 | `slot/tests/nes_quick_menu.rs` | `SLOT_REQUIRE_CORES=1`. Quick menu on seated NES/SNES opens and navigates; Rewind/FF rows change state; Turbo row on SNES changes nothing at the core |
| T27 | `slot/tests/nes_states.rs` | `SLOT_REQUIRE_CORES=1`. SELECT+R1 then SELECT+L1 on NES and SNES (battery ROMs): state files under `States/NES|SNES`; polaroid decodes at 360x240; load restores the frame |
| T30 | `slot/tests/nes_resume.rs` | `SLOT_REQUIRE_CORES=1`. `cart=Mario`, `cart_platform=nes`, boot: boots into the NES cart. T30b, run on the upstream tree: shows the shelf, no panic |
| T33 | `slot/tests/nes_eject_save.rs` | `SLOT_REQUIRE_CORES=1`. Eject on battery `nes_rom` and `snes_rom`: `.sav` written under `Saves/NES|SNES` and reloaded |

Upstream tests stay unmodified, in particular `slot: crates/slot-ui/tests/quick_menu.rs:85-91` and `slot: crates/slot/tests/quick_menu.rs:239-255` (SCREEN pinned at 4 rows).

## Edge cases
| Case | Expected handling |
|---|---|
| Downgrade to unpatched slot with `cart_platform=nes` | Upstream `platform_value` returns None, so it boots to the shelf. T30b runs this on the upstream tree and asserts no panic. Documented |

## Acceptance
- [ ] T26, T27, T30 (with T30b), T33 green under `SLOT_REQUIRE_CORES=1`.
- [ ] GBA harness compare 0 diffs (H1, H2).
- [ ] AC-to-code coverage rows Insert and eject, Resume on boot, Saves and autosave, Save states and polaroids, Quick menu, Turbo and Settings/volume/sleep each point at a passing test.

## Device check (RG34XXSP)
None separate. Lid close, sleep, volume and brightness are in the phase device check in 18-phase-3-parity.

## Review notes
- T30b needs a test run against `build/slot-upstream`; keep it as a new file in this repo's harness or test runner, never inside upstream test code.
- No quick menu row is added or reordered.

## References
- docs/PLAN.md: Phase 3 deliverables (polaroids, quick menu), Build step 21, Edge cases by layer (State), AC-to-code coverage stub
- `slot: crates/slot/src/emu.rs:884`; `slot: crates/slot/src/session.rs:438`
