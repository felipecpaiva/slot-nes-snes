---
title: "Patch 0009: Give NES and SNES their own shaders stored as shader_nes and shader_snes"
phase: 3
area: video
type: feature
size: S
depends_on: [20-core-picker-pairs]
---

## Why
NES borrowed `shader_gb` provisionally in Phase 1. NES and SNES get their own shader list and stored choice, changed with in-game SELECT+B/A, with no new quick menu rows (docs/PLAN.md Phase 3 deliverables, Build step 19). Decision: no new quick menu rows; NES/SNES shaders via SELECT+B/A (docs/DECISIONS.md).

## Scope
`patches/0009-shaders.patch`:
- [ ] `Shader::RETRO = [Off, Grid, Dot]`; `Platform::shader_choices()`.
- [ ] `slot: crates/slot-store/src/slot_state.rs`: append `SlotState.shader_nes` and `shader_snes` (default Off); write them with a separate `push_str` after the `format!` at `:130`; parse with `unwrap_or(Off)`, never `?`; a value outside `RETRO` (for example Lcd3x) falls back to Off.
- [ ] `slot: crates/slot/src/app.rs:1044-1047` and `:1407-1410`: Nes/Snes arms move off `shader_gb` to their own fields and `Shader::RETRO`.
- [ ] Confirm by eye all 55 `SlotState {` sites under `*/tests/` use `..Default::default()` (49 confirmed by grep).

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
- [ ] T25 green; `task check` green.
- [ ] GBA harness compare 0 diffs (H1, H2): `slot.state` bytes for a GBA-only session match upstream up to the appended lines.
- [ ] `slot: crates/slot-store/src/slot_state.rs:130` `format!` line untouched.

## Device check (RG34XXSP)
None separate. Shader cycling is in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 9 (the `slot_state` `format!` line conflicts): `slot: crates/slot-store/src/slot_state.rs:130` changes on most upstream releases. Never edit it; use a separate `push_str` and `unwrap_or` parsing.
- `QuickRow::SCREEN` stays at 4 rows. No quick menu shader rows: decided 2026-10-11 (docs/DECISIONS.md).

## References
- docs/PLAN.md: Phase 3 deliverables (0009), Build step 19, Approach (new `slot.state` keys), Signature impact table (`SlotState`), Open questions (resolved: shaders)
- `slot: crates/slot-store/src/slot_state.rs:130`; `slot: crates/slot/src/app.rs:1043-1048,1406-1411`
