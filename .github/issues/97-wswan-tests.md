---
title: "Test WonderSwan with a generated cart that paints, turns and saves"
phase: 11
area: tests
type: test
size: S
depends_on: [92-wswan-core-build]
---

## Why
Every WonderSwan behaviour needs a real-core test with no copyrighted game (ADR 0092). Cygne needs no BIOS, so the only fixture is a generated cart.

## Scope
- [x] `crates/slot/tests/wswan_core.rs` (patch `0064-wswan-core-tests`, new file only): a 64 KB WonderSwan Color cart built in code. The reset jump at 0xfff0 to F000:0000 follows cloudwithax/unslot `crates/slot-retro/tests/systems.rs` (00296a5), credited in the file, the patch commit and LICENSING.md. Our code fills the footer (colour flag, save type, vertical flag, checksum), switches the display to colour mode (port 0x60), writes palette 0 colour 0 at 0xfe00 (red or blue), and optionally writes or reads a marker in SRAM through bank 1.
- [x] The core is opened as slot opens every core today: `LibretroCore::open_with(dylib, root::bios_dir, root::saves_dir)`, options set before load. `require_core("mednafen_wswan")` first, so a missing core fails under `SLOT_REQUIRE_CORES=1`.
- [ ] Platform tests land with each later step (`wswan_platform.rs`, `wswan_seat.rs`, `wswan_options.rs`, `wswan_screen.rs`, `wswan_canvas.rs`, `wswan_input.rs`, `wswan_saves.rs`, `wswan_then_gba.rs`); move the cart builder to `wswan_common/mod.rs` when a second file needs it.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `wswan_core.rs` `a_wonderswan_cart_boots_with_no_bios_and_draws_224_by_144_in_the_middle_of_240_by_160` | every pixel: red inside (8, 8)..(232, 152), black outside; 44100 Hz; audio |
| (new) | `wswan_core.rs` `with_60hz_mode_set_the_core_reports_60_38_fps` | 75.47 x 4/5 within 0.01 |
| (new) | `wswan_core.rs` `unanswered_60hz_mode_runs_at_the_native_75_47_fps_despite_its_declared_default` | 75.47 within 0.01 |
| (new) | `wswan_core.rs` `both_modes_play_the_game_at_its_own_speed_60hz_mode_runs_five_frames_in_four` | 600 calls give 600 x 44100 / fps sound frames within 1%, in both modes |
| (new) | `wswan_core.rs` `portrait_turns_the_picture_in_the_core_to_144_by_224_with_no_rotation_from_slot` | frame 144 wide; every pixel of 144x224 at (108, 8) in 360x240 |
| (new) | `wswan_core.rs` `the_core_ignores_the_footers_vertical_flag_so_slot_must_read_it` | vertical footer, no rotate option: frame 224 wide |
| (new) | `wswan_core.rs` `select_turns_the_picture_only_while_rotate_display_is_left_on_manual` | landscape: SELECT keeps 224; unanswered: SELECT turns it to 144 |
| (new) | `wswan_core.rs` `a_wonderswan_state_round_trips_in_60hz_mode` | 7 frames in (mid cycle), serialize, run, unserialize, serialize again is byte-equal |
| (new) | `wswan_core.rs` `cygne_hands_slot_the_cart_sram_as_save_ram_with_no_rtc` | 8192 bytes, marker at 0, rest zero |
| (new) | `wswan_core.rs` `the_save_ram_size_follows_the_footer_save_type_and_a_cart_with_none_has_none` | None, 128, 2048, 8192 |
| (new) | `wswan_core.rs` `sram_written_back_after_load_is_what_the_game_reads_on_the_next_boot` | no file in `Saves/`; blank SRAM paints blue; `load_save_ram` after load paints red |

Seen to fail with the behaviour broken (each mutation run and reverted, 2026-10-18): dropping the 60 Hz option fails the 60.38 test and the sound-count test; dropping `landscape` fails the SELECT test; skipping `load_save_ram` fails the read-back test.

## Edge cases
| Case | Expected handling |
|---|---|
| The host canvas is the GBA one | It records no frame size there, so frame-width asserts use a 360x240 canvas |

## Acceptance
- [x] `cargo test -p slot --test wswan_core` green with `SLOT_REQUIRE_CORES=1` on the M5 Max (11 tests, about 1.3 s).
- [ ] Green on macOS CI with the host dylib (not run from here, no push).

## Device check (RG34XXSP)
None (host tests).

## References
- ADR 0092; cloudwithax/unslot 00296a5 `crates/slot-retro/tests/systems.rs`; the NGP fixture precedent (its own branch)
