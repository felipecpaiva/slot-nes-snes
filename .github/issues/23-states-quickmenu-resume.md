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
- [x] Polaroids: full 360x240 canvas thumbnails, no crop (decided). T27 decodes the polaroid at 360x240 and checks the black border is kept.
- [x] Quick menu works on NES/SNES with the existing rows; the Turbo row is a documented no-op on SNES (README, T26). The menu opens on the shelf only, as upstream (`slot: crates/slot/tests/quick_menu.rs` `the_quick_menu_is_only_on_the_carousel`), so T26 drives it on the NES and SNES shelves and checks what reaches the core with a recording core.
- [x] Resume on boot through `slot.state` `cart_platform`.
- [x] Saves and autosave under `Saves/NES|SNES` on eject.
- [x] Downgrade behaviour documented in the README: unpatched slot boots to the shelf when `cart_platform=nes`. Checked by `sh scripts/check-downgrade.sh` (T30b, `harness/downgrade.rs` run as an example in `build/slot-upstream`).
- [x] New test files committed on the `nes-snes` branch and exported with the concern they exercise. Committed as `parity-proofs` in `work/slot`; export with `scripts/export-patches.sh`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T26 | `slot/tests/nes_quick_menu.rs` | `SLOT_REQUIRE_CORES=1`. Quick menu on the NES and SNES shelf opens and navigates; Rewind/FF rows change state; Turbo row on SNES changes nothing at the core |
| T27 | `slot/tests/nes_states.rs` | `SLOT_REQUIRE_CORES=1`. SELECT+R1 then SELECT+L1 on NES and SNES (battery ROMs): state files under `States/NES|SNES`; polaroid decodes at 360x240; load restores the frame |
| T30 | `slot/tests/nes_resume.rs` | `SLOT_REQUIRE_CORES=1`. `cart=Mario`, `cart_platform=nes`, boot: boots into the NES cart. T30b, run on the upstream tree: shows the shelf, no panic |
| T33 | `slot/tests/nes_eject_save.rs` | `SLOT_REQUIRE_CORES=1`. Eject on battery `nes_rom` and `snes_rom`: `.sav` written under `Saves/NES|SNES` and reloaded |

Upstream tests stay unmodified, in particular `slot: crates/slot-ui/tests/quick_menu.rs:85-91` and `slot: crates/slot/tests/quick_menu.rs:239-255` (SCREEN pinned at 4 rows).

## Edge cases
| Case | Expected handling |
|---|---|
| Downgrade to unpatched slot with `cart_platform=nes` | Upstream `platform_value` returns None, so it boots to the shelf. T30b runs this on the upstream tree and asserts no panic. Documented |

## Acceptance
- [x] T26, T27, T30 (with T30b), T33 green under `SLOT_REQUIRE_CORES=1`. T26 6 tests, T27 2, T30 2, T33 2, plus a shared `tests/real_seat/mod.rs`; T30b printed `downgrade: ok` against `build/slot-upstream`.
- [ ] GBA harness compare 0 diffs (H1, H2).
- [x] AC-to-code coverage rows Insert and eject, Resume on boot, Saves and autosave, Save states and polaroids, Quick menu, Turbo and Settings/volume/sleep each point at a passing test (table below).

## Device check (RG34XXSP)
None separate. Lid close, sleep, volume and brightness are in the phase device check in 18-phase-3-parity.

## Review notes
- T30b needs a test run against `build/slot-upstream`; keep it as a new file in this repo's harness or test runner, never inside upstream test code.
- No quick menu row is added or reordered.

## References
- docs/PLAN.md: Phase 3 deliverables (polaroids, quick menu), Build step 21, Edge cases by layer (State), AC-to-code coverage stub
- `slot: crates/slot/src/emu.rs:884`; `slot: crates/slot/src/session.rs:438`

## AC-to-code coverage (passing tests)
| Row | Test |
|---|---|
| Insert and eject | T9 `slot/tests/nes_emu.rs`, T21 `slot/tests/snes_emu.rs` (boot), T33 `slot/tests/nes_eject_save.rs` (eject), upstream `slot/tests/eject.rs` |
| Resume on boot | T30 `slot/tests/nes_resume.rs`; `slot-store/tests/nes_state.rs`, `slot-store/tests/snes_state.rs` (the `cart_platform` round trip) |
| Saves and autosave | T33 `ejecting_a_battery_cart_writes_its_sav_under_saves_for_its_platform` and `a_sav_on_the_card_is_loaded_into_the_core_when_the_cart_goes_back_in` (NES, SNES Lo and Hi, 8 KB battery); upstream `slot/tests/flush.rs`, `eject.rs` for the autosave and unchanged-save rules, which are platform-agnostic |
| Save states and polaroids | T11 `slot/tests/nes_thumb.rs`, T27 `slot/tests/nes_states.rs`; upstream `slot/tests/polaroids.rs` |
| Quick menu | T26 `the_quick_menu_opens_and_walks_the_same_rows_on_the_nes_and_snes_shelves`, `the_rewind_row_...`, `the_fast_forward_row_...`; upstream `slot/tests/quick_menu.rs` unchanged |
| Turbo | T16 `slot-retro/tests/snes_turbo.rs`; T26 `the_turbo_row_flips_its_setting_...`, `the_turbo_setting_changes_nothing_that_reaches_the_snes_core`, `the_turbo_setting_does_change_what_reaches_the_nes_core` |
| Settings / volume / sleep | T26 (rows persist to `slot.state`); upstream `slot/tests/volume.rs`, `slot/tests/power.rs`, `slot-store/tests/volume.rs`, all platform-agnostic. Volume, brightness and lid sleep with a NES or SNES cart stay in the phase device check (18-phase-3-parity) |

## Findings
- The quick menu opens only from the shelf, so "seated" in T26 means the NES or SNES shelf. The in-game menu is a different screen.
- An eject resume state includes the battery RAM, so a hand-written `.sav` is only visible after boot when `eject_save` is off. The reload half of T33 turns it off for that reason.
- Not run for this issue: GBA harness compare (H1, H2). The patch touches no source file, only tests.
