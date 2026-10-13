---
title: "Patch 0014: Give NES and SNES their own shaders stored as shader_nes and shader_snes"
phase: 3
area: video
type: feature
size: S
depends_on: [20-core-picker-pairs]
---

## Why
NES borrowed `shader_gb` provisionally in Phase 1. NES and SNES get their own shader list and stored choice, changed with in-game SELECT+B/A, with no new quick menu rows (docs/PLAN.md Phase 3 deliverables, Build step 19). Decision: no new quick menu rows; NES/SNES shaders via SELECT+B/A (docs/DECISIONS.md).

## Scope
`patches/0014-shaders.patch`:
- [x] `Shader::RETRO = [Off, Grid, Dot]`; `Platform::shader_choices()`.
- [x] `slot: crates/slot-store/src/slot_state.rs`: append `SlotState.shader_nes` and `shader_snes` (default Off); write them with a separate `push_str` after the `format!` at `:130`; parse with `unwrap_or(Off)`, never `?`; a value outside `RETRO` (for example Lcd3x) falls back to Off.
- [x] `slot: crates/slot/src/app.rs:1044-1047` and `:1407-1410`: Nes/Snes arms move off `shader_gb` to their own fields and `Shader::RETRO`.
- [x] Confirm by eye all 55 `SlotState {` sites under `*/tests/` use `..Default::default()`. One does not: `a_card_from_before_the_settings_keeps_all_its_values` in `durability.rs`; see the decision below.

## Tests
| ID | File | Asserts |
|---|---|---|
| T25 | `slot-store/tests/nes_shader_state.rs` | Round-trip `shader_nes=dot`; an old file without the keys gives Off defaults with the other fields intact; Lcd3x in `shader_nes` falls back |

Upstream tests stay unmodified, in particular every `SlotState {` literal under `*/tests/` and both `quick_menu.rs` tests (`slot: crates/slot-ui/tests/quick_menu.rs:85-91`, `slot: crates/slot/tests/quick_menu.rs:239-255`, which pin SCREEN at 4 rows).

## Edge cases
| Case | Expected handling |
|---|---|
| `slot.state` written by unpatched slot (no `shader_nes`) | Parsed with `unwrap_or`; T25 asserts Off defaults with the other fields intact |

## Acceptance
- [x] T25 green. `task check` green (2026-10-13, exit 0).
- [x] GBA harness compare 0 diffs (H1, H2): `task check` 2026-10-13 exit 0, compare 0 diffs (H1, H1G, H2, B1, H3). `slot.state` bytes for a GBA-only session match upstream up to the appended lines: verified by `a_gba_only_slot_state_matches_upstream_up_to_the_appended_lines` and `select_x_gba`.
- [x] `slot: crates/slot-store/src/slot_state.rs:130` `format!` line untouched.

## Decision (2026-10-13)
Option A approved by the maintainer. `crates/slot-store/tests/durability.rs`, test `a_card_from_before_the_settings_keeps_all_its_values`, builds a full `SlotState` literal with no `..Default::default()`. It gains exactly `shader_nes: Shader::Off,` and `shader_snes: Shader::Off,` and nothing else. This is named exception (f) in CONTRIBUTING.md and in `scripts/check-upstream-tests.sh`, which fails if any other line of that file differs, if a shader line moves, or if either is missing.

## Result
- `crates/slot/src/app.rs` net diff against the pinned release is 23 (was 25): the Nes and Snes arms move off the patched `Gb | Gbc | Nes | Snes` arms.
- Our own `select_x_gba.rs` pins the GBA `slot.state` bytes; its expected text gains the two appended lines.
- Extra test: `nes_snes_shader.rs` (SELECT+A and SELECT+B cycle RETRO and leave `shader_gb` alone, NES and SNES).

## Device check (RG34XXSP)
None separate. Shader cycling is in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 9 (the `slot_state` `format!` line conflicts): `slot: crates/slot-store/src/slot_state.rs:130` changes on most upstream releases. Never edit it; use a separate `push_str` and `unwrap_or` parsing.
- `QuickRow::SCREEN` stays at 4 rows. No quick menu shader rows: decided 2026-10-11 (docs/DECISIONS.md).

## References
- docs/PLAN.md: Phase 3 deliverables (0009), Build step 19, Approach (new `slot.state` keys), Signature impact table (`SlotState`), Open questions (resolved: shaders)
- `slot: crates/slot-store/src/slot_state.rs:130`; `slot: crates/slot/src/app.rs:1043-1048,1406-1411`
