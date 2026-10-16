---
title: "Crop the NES and SNES overscan edges in a new default picture mode"
phase: 7
area: video
type: feature
size: S
depends_on: [54-system-picture]
---

## Why
On the RG34XXSP in Stretch, NES games that mask their left 8 pixels show a band of about 22 panel columns on the left, and SNES Knights of the Round (USA) shows 39 black rows at the top and none at the bottom. A CRT hid these edges. The maintainer wants a Crop picture mode, on by default for NES and SNES. Decision: [ADR 0062](../../docs/adr/0062-crop-overscan-picture.md).

## Scope
`patches/0033-crop-overscan.patch`:
- [x] `VideoMode::Crop` appended after `Stretch`, stored as `crop`; old `stretch` and `actual` lines keep their meaning.
- [x] `Platform::overscan` in `platform_policy.rs`: NES (8, 8), SNES (0, 8), every other platform (0, 0).
- [x] `platform_video::shown` crops the picture `App::source_rect` hands to `video_mode::source_rect`; `video_mode::source_rect` is unchanged and core options are unchanged.
- [x] NES and SNES default to Crop; Picture choices Crop, Stretch, Actual for NES and SNES, Stretch, Actual elsewhere.
- [x] The Picture row steps Right forward and Left back (`SystemPictures::step`); SNES SELECT+X cycles Crop, Stretch, Actual; NES L1 moves between Crop and Stretch, R1 stays Actual.
- [x] `QuickValue::Crop` ("Crop") after Stretch and Actual in `every()`.
- [x] Crop hides the GBA bezel like Stretch (`shown_game_bezel`).
- [x] Game Gear, Master System and Mega Drive unchanged: Genesis Plus GX already hides their borders (`genesis_plus_gx_overscan` default `disabled`, `left_border` set by slot).

## Tests
| ID | File | Asserts |
|---|---|---|
| T91 | `slot/tests/crop_overscan.rs` `nes_crop_takes_eight_pixels_off_every_edge_of_the_240_line_picture`, `snes_crop_takes_eight_lines_off_...` | Source rect per mode: NES Crop 240x224 at (60, 8), Stretch 256x240, Actual whole; SNES Crop 256x208 at (52, 16), Stretch 256x224, Actual whole |
| T92 | `slot/tests/crop_overscan.rs` `a_239_line_snes_frame_crops_to_the_same_208_lines_as_a_224_line_one` | Same rect with and without a live frame width |
| T93 | `slot/tests/crop_overscan.rs` `nes_and_snes_start_in_crop_...`, `a_never_played_nes_cart_seats_with_the_crop_rect`, `slot/tests/nes_video_mode.rs` | Crop is the NES and SNES default, in `video_mode_for` and in a seated session; other defaults unchanged |
| T94 | `slot/tests/crop_overscan.rs` `only_nes_and_snes_offer_crop_...`, `the_picture_row_cycles_...`, `l1_on_nes_moves_...`, `slot/tests/snes_select.rs`, `slot/tests/system_picture.rs` | Choices per platform, cycle order both ways in the Picture row, SELECT+X on SNES, L1 on NES |
| T95 | `slot/tests/crop_overscan.rs` `a_crop_line_round_trips_through_both_files`, `a_stretch_line_saved_before_crop_existed_...` | `crop` round-trips through `video_mode.txt` and `picture.txt`; old `stretch` lines still mean Stretch |
| T96 | `slot/tests/crop_overscan.rs` `crop_on_a_system_without_overscan_draws_the_same_as_stretch` | GG, SMS, MD and GB Crop rect equals Stretch |
| T97 | `slot/tests/crop_overscan.rs` `frame::frames_with_blank_overscan_edges_fill_the_panel_once_cropped` (macOS, GL) | A NES frame with 8 blank top lines and 8 blank left columns, and SNES 224 and 239-line frames with 8 blank top lines, leave no black panel row or column in Crop; Stretch shows the bands |
| T98 | `slot-ui/tests/retro_faces.rs` (ours) | Crop face follows Stretch and Actual and answers to its own index |
| T99 | harness | GBA, GB and GBC 0 diffs |

## Acceptance
- [x] T91 to T98 green. Mutation: SNES overscan (0, 8) to (0, 4) fails T91, T92 and T97.
- [x] Our own `system_picture.rs`, `snes_select.rs`, `nes_video_mode.rs` and `retro_faces.rs` assumed two picture modes; updated.
- [x] T99 `task harness:compare`: 0 diffs (H1, H1G, H2, B1); `task check`, `task patches:check` and the upstream-test guard green.
- [ ] On the RG34XXSP: Super Mario Bros. 3 in a level shows no left band in Crop; Knights of the Round shows a smaller top band (about 23 rows, the game blanks about 18 lines); SELECT+X and L1 cycle as above.

## References
- ADR 0046, 0061, 0062
- NESdev wiki "Overscan"; SNESdev wiki "Timing"; snes9x `libretro.cpp` `OVERSCAN_CROP_16`; fceumm and nestopia `libretro_core_options.h` at the pinned commits
