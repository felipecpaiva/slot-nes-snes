---
title: "Test NGP with a generated cart that paints and writes flash"
phase: 9
area: tests
type: test
size: S
depends_on: [71-ngp-core-build]
---

## Why
Every NGP behaviour needs a real-core test with no copyrighted game (ADR 0090). NeoPop needs no BIOS, so the only fixture is a generated cart.

## Scope
- [x] `crates/slot/tests/ngp_core.rs` (patch `0080-ngp-core-tests`, new file only): a 64 KB Pocket Color cart built in code. The header recipe (SNK signature, start address at 0x1c, colour byte at 0x23, `jr t,-2`) follows nelynes/slotPlus `ngp_core.rs` (a8eae4c), credited in the file, the patch commit and LICENSING.md. Our code paints the screen red (palette words at 0x83e0 and 0x83f0) and, optionally, sends the flash command (AA to 0x205555, 55 to 0x202aaa, A0 to 0x205555) then writes a marker byte to 0x20f000.
- [x] The core is opened as slot opens every core today: `LibretroCore::open_with(dylib, root::bios_dir, root::saves_dir)`. `require_core("mednafen_ngp")` first, so a missing core fails under `SLOT_REQUIRE_CORES=1`.
- [ ] Platform tests land with each later step (`ngp_platform.rs`, `ngp_seat.rs`, `ngp_screen.rs`, `ngp_canvas.rs`, `ngp_input.rs`, `ngp_flash.rs`, `ngp_then_gba.rs`); move the cart builder to `ngp_common/mod.rs` when a second file needs it.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ngp_core.rs` `a_neogeo_pocket_cart_boots_with_no_bios_and_draws_160_by_152_in_the_middle_of_240_by_160` | every pixel: red inside (40, 4)..(200, 156), black outside; 60.0 to 60.5 fps; 44100 Hz; audio |
| (new) | `ngp_core.rs` `a_neogeo_pocket_state_round_trips` | serialize, run, unserialize, serialize again is byte-equal |
| (new) | `ngp_core.rs` `neopop_gives_the_frontend_no_save_ram` | `save_ram()` is None after the game wrote flash |
| (new) | `ngp_core.rs` `neopop_writes_the_cart_flash_into_slots_save_dir_only_when_the_game_unloads` | no file while running; after drop, `Saves/Flash.flash` is 272 bytes, id 0x0053, one block at 0x20f000, marker at 16 |
| (new) | `ngp_core.rs` `a_cart_that_never_writes_flash_leaves_no_flash_file` | no file |
| (new) | `ngp_core.rs` `the_cart_flash_survives_a_restart_through_slots_save_dir` | second boot runs no frame; delete the file after load; it comes back with the marker, so the core read it back |
| (new) | `ngp_core.rs` `a_state_carries_the_cart_flash_with_no_flash_file` | file deleted, fresh boot, unserialize the state, drop: the file comes back with the marker |

Seen to fail with the behaviour broken: no paint code fails the boot test; deleting the file before the second load fails the restart test; skipping `unserialize` fails the state test; a cart without the flash command fails the three flash tests.

## Edge cases
| Case | Expected handling |
|---|---|
| Only the AA write, no 55 and A0 | NeoPop accepts it (it watches the command addresses, not the sequence); the cart sends the real sequence anyway |

## Acceptance
- [x] `cargo test -p slot --test ngp_core` green with `SLOT_REQUIRE_CORES=1` on the M5 Max (7 tests, 0.2 s).
- [ ] Green on macOS CI with the host dylib (not run from here, no push).

## Device check (RG34XXSP)
None (host tests).

## References
- ADR 0090; nelynes/slotPlus a8eae4c `crates/slot/tests/ngp_core.rs`; the PS1 fixture precedent (issue 63)
