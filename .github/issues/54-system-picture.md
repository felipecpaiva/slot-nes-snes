---
title: "Choose each retro system's default picture mode from its Screen section"
phase: 7
area: video
type: feature
size: S
depends_on: [43-nes-snes-default-stretch, 53-platform-md]
---

## Why
The picture mode (Stretch or Actual) is only reachable in game, with SELECT+X on SNES and Mega Drive and L1/R1 on NES, Game Gear and Master System, and it is saved per cart. The maintainer wants a Picture row in each system's Screen section that sets the default every cart without its own choice uses. Decision: [ADR 0061](../../docs/adr/0061-per-system-picture-row.md).

## Scope
`patches/0032-system-picture.patch`:
- [x] `SCREEN_NES`, `SCREEN_SNES`, `SCREEN_GG`, `SCREEN_SMS` and `SCREEN_MD` become Shader, Picture (`QuickRow::NesPicture` and the others, appended). The row shows `Stretch` or `Actual` and Left/Right flips it.
- [x] `QuickValue::Stretch` and `QuickValue::Actual` after the retro faces in `every()`; `QuickValue::ALL` unchanged.
- [x] `Config/picture.txt` (`nes = actual` style lines, `ini::write`), read at boot into `App`, written on change. slot.state untouched.
- [x] `platform_video::video_mode_for`: cart line, then `Config/picture.txt`, then the ADR 0022 default.
- [x] SELECT+X and L1/R1 still change only the running cart's line in `Config/video_mode.txt`.
- [x] GBA, GB and GBC get no row (upstream pins their Screen pages; GBA has no picture toggle).
- [x] No in-game Picture row: `QuickRow::PLAY_SCREEN` is pinned by an upstream test (ADR 0061).

## Tests
| ID | File | Asserts |
|---|---|---|
| T83 | `slot/tests/system_picture.rs` `each_retro_screen_section_shows_a_picture_row_under_its_shader` | Each of the five sections is Shader, Picture, labelled Picture, shows its factory default, wraps |
| T84 | `slot/tests/system_picture.rs` `the_picture_row_walks_stretch_and_actual_and_saves_only_its_own_system` | Right and Left flip the value, `Config/picture.txt` holds only that system's line, no write before a change, slot.state unchanged, a reboot reads it back |
| T85 | `slot/tests/system_picture.rs` `a_cart_with_no_line_of_its_own_takes_its_system_picture` and `a_cart_seats_in_its_system_picture` | A cart without its own line uses the system default, in `video_mode_for` and in a seated session |
| T86 | `slot/tests/system_picture.rs` `a_cart_line_still_wins_over_the_system_picture` | A saved cart line beats the system default |
| T87 | `slot/tests/system_picture.rs` `select_x_still_sets_...` and `l1_still_sets_...` | SNES and MD (SELECT+X), NES, GG and SMS (L1) write the cart line and leave `Config/picture.txt` as it was |
| T88 | `slot/tests/system_picture.rs` `an_unreadable_system_picture_reads_as_the_factory_default`, `the_game_boy_sections_gain_no_picture_row` | Bad values fall back; GBA, GB and GBC pages have no Picture row |
| T89 | `slot-ui/tests/retro_faces.rs` (ours) | Stretch and Actual faces follow the retro faces and answer to their own index |
| T90 | harness | GBA, GB and GBC 0 diffs |

## Acceptance
- [x] T83 to T89 green. Mutations: `video_mode_for` back to the factory default fails T85, T87 (4 tests); dropping the `save` call on a Picture flip fails T84; swapping the Stretch and Actual face indexes fails T89.
- [x] Our own `slot/tests/quick_retro_shader.rs` and `slot-ui/tests/quick_retro.rs` pinned one-row NES/SNES/Sega pages; they now expect Shader, Picture.
- [x] T90 `task harness:compare`: 0 diffs (H1, H1G, H2, B1, H3 held against H1).
- [ ] On the RG34XXSP, set NES Picture to Actual on the shelf, insert a never-played NES cart: it starts in Actual; L1 switches that cart to Stretch and only that cart.

## References
- ADR 0007, 0022, 0048, 0051, 0058, 0061
