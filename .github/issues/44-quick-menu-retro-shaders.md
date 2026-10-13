---
title: "Patch: Offer the NES and SNES shaders in the quick menu"
phase: 3
area: video
type: feature
size: S
depends_on: [21-shaders]
---

## Why
Users look for settings in the same place on every system. GBA and GB offer their shader in the quick menu (Screen page); NES and SNES shaders were reachable only by SELECT+A/B in game. The maintainer decided on 2026-10-13 that the NES and SNES shelves show their shader in the quick menu too. This reverses the 2026-10-11 decision "no new quick menu rows" for shaders (docs/DECISIONS.md). Picture mode is per cart and set in game; upstream has no picture-mode row, so none is added.

## Scope
`patches/NNNN-quick-menu-retro-shaders.patch`:
- [x] `QuickRow::NesShader` and `QuickRow::SnesShader` appended to the enum and `ALL`, with labels "NES Shader" and "SNES Shader". `QuickRow::SCREEN` stays 4 rows.
- [x] Own pages `NES_SCREEN` and `SNES_SCREEN`, one row each (Color Correction and GB Palettes do nothing there), in new `crates/slot-ui/src/quick_retro.rs`, with `QuickRow::child_for(platform)`: the Screen row opens the page of the shelf the menu was opened on; GBA, GB and GBC open `SCREEN` as before.
- [x] `slot: crates/slot/src/app.rs`: `quick_value`, `open_quick_row` and `change_setting` get the two new rows (value and step in new `crates/slot/src/retro_quick.rs`, stepping through `Shader::RETRO`, stored by the existing `persist`); the Screen row calls `child_for(shelf platform)`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T60 | `slot-ui/tests/quick_retro.rs` | NES and SNES pages hold only their row; labels; `child_for` per platform |
| T61 | `slot/tests/quick_retro_shader.rs` | NES and SNES shelves open their own shader row; Right/Left cycle Off, Grid, Dot and persist; other shaders untouched |
| T62 | `slot/tests/quick_retro_shader.rs` | GBA and GB shelves still show the four upstream rows in order |
| T63 | `slot/tests/render_quick_retro.rs` | GL render of the NES shelf quick menu: label and value drawn on one centred row |

Upstream tests stay unmodified, in particular both `quick_menu.rs` tests that pin `SCREEN` at 4 rows.

## Edge cases
| Case | Expected handling |
|---|---|
| `shader_nes` or `shader_snes` outside `RETRO` in an old card | Already parsed to Off (issue 21) |
| SELECT+A/B in game | Unchanged, shares the same stored value |
| GBC shelf | Opens `SCREEN`, like GB |

## Acceptance
- [x] T60 to T63 green (`cargo test --no-fail-fast -p slot-ui -p slot`, sandbox off for GL: 1197 passed, 0 failed, work/slot commit `quick-menu-retro-shaders`).
- [x] Each test mutation-proven: child_for Nes arm to SCREEN, step on `Shader::GB`, SNES row writing `shader_nes`, Gba arm opening the NES page, a second row on the NES page, swapped label, `quick_value` NES reading `shader_snes`, empty NES label (render test). Each turns at least one test red.
- [x] rustfmt --check clean on files added or changed.
- [x] `task check` green, harness compare 0 diffs for GBA, GB, GBC (2026-10-13: exit 0, compare 0 diffs H1, H1G, H2, B1, H3).
- [x] `docs/UPSTREAM-TOUCHPOINTS.md` regenerated with the new hunks and reasons (`task diffsurface:check`: map is current, every row has a reason).

## Device check (RG34XXSP)
Open the quick menu on the NES shelf, Screen, change the NES shader, start a NES game: the shader shows. Same on SNES. On GBA and GB the Screen page looks as before.

## Review notes
- The new variants are appended, so `QuickRow::index()` of every existing row is unchanged.
- GBA, GB and GBC quick menus render the same rows as upstream.

## References
- docs/DECISIONS.md (2026-10-13), issue 21-shaders
