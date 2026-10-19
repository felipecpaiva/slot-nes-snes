---
title: "Add Platform::Ws with its own shelf, scan, footer reader, saves and explicit policy"
phase: 11
area: platform
type: feature
size: M
depends_on: [92-wswan-core-build]
---

## Why
Step 4. The shelf, the policy answers and the saves, built on the main 1b20432 base (ADR 0092).

## Scope
- [ ] `Platform::Ws` in `SHELVES` (not `ALL`), `Core::MednafenWswan` in `EVERY` with `as_str() == "mednafen_wswan"` (the dylib name) and option prefix `wswan` (not the core name). Folders `Games/WS`, `Labels/WS`, `Saves/WS`, `States/WS`.
- [ ] Scan `.ws` and `.wsc` (not `.pc2`, in no No-Intro dat); `._` files skipped; title from the stem (WonderSwan ROMs carry no title).
- [ ] Footer reader in our own `slot_store::ws` module: colour flag at `len-9` (0xfff7 in a 64 KB image), save type at `len-5`, flags at `len-4` (bit 0 vertical). A file under 64 KB lists, horizontal and mono, and is not seated (the core refuses it), with a toast.
- [ ] Every policy method answers explicitly, like PS1 (patch 0034): `owns_shoulders` **false** (L and R are game inputs: the Y-pad modifiers on horizontal games, A and B on vertical ones, issue 96; the Mega Drive answer), `passes_xy_through` **true** (X and Y must reach the WonderSwan remapper, which decides turbo itself; with `false` the turbo conversion would eat R+X and R+Y before the remap), `select_x_toggles_picture` true, `picker_cores` None, `stretch_crops_height` false, `overscan` (0, 0), `follows_frame_width` false, `has_gb_palettes` false, `rewinds` true.
- [ ] **New seam, per game:** `Core::canvas(core, platform)` is static per platform, read by `slot::core::open_named` (`set_canvas`) and by `App::source_rect`. WonderSwan needs `(240, 160)` for a horizontal cart and `(360, 240)` for a vertical one (issue 95), so the canvas must come from the cart: a per-game answer (for example `canvas_for(core, platform, &RomInfo)` with the footer's vertical bit, scanned once) used by both call sites, every other platform returning today's value. The input map of issue 96 reads the same bit. Keep it the one new policy input, and propose it upstream with ADR 0058's `PlayPolicy` if it fits.
- [ ] Placeholder cart until issue 98.
- [ ] Named test sites (b) and (e) take `Platform::Ws` and `Core::MednafenWswan` (ADR 0055).
- [ ] Release: move `cores/mednafen_wswan/mednafen_wswan-GPL-2.0.txt` to `licenses/`; add the core to `scripts/dist-device.sh` and every list in `scripts/zip-check.sh` (cores, `req`, `ok`, the licence and srcmeta checks, the strings pair `mednafen_wswan:Beetle.WonderSwan`), and `WS` to its `games` list. README row "planned, not shipped". The McPhail credit ADR 0092 promises: a line in the README licence section and in `scripts/release-notes.sh` output for the release that first ships the core ("NEC V30MZ emulator by Bryan McPhail").
- [ ] Saves: unlike NeoPop (the NGP groundwork, on its own branch), Cygne hands the cart's SRAM or EEPROM to slot as `SAVE_RAM` and writes no file of its own (pinned by `wswan_core.rs`), so the existing `.sav` machinery applies (ADR 0012, 0034, 0072) and this step only proves it end to end: `Saves/WS/<stem>.sav` on autosave, eject and `flush_resume`; ADR 0072's no-state path and `save_ram_trusted` unchanged; ADR 0082's hack updates keep it; a cart with no save type writes no `.sav`. Record in the patch commit what the `.sav` does not hold: no RTC (the core exposes none; RTC carts keep their clock in states and re-read the host clock at boot), the internal EEPROM owner profile (rebuilt from options each boot, issue 94 fixes the values), and that WonderWitch images persist SRAM plus 512 KB flash as one block through the same path, untested.
- [ ] Credit nelynes/slotPlus 273ded9 for the shelf shape in the patch commit.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `wswan_platform.rs` `a_wsc_cart_lands_on_the_ws_shelf` | scan, folders, title from the stem |
| (new) | `wswan_platform.rs` `the_footer_gives_colour_save_type_and_vertical` | each flag read at its offset from the end, for 64 KB and 1 MB images |
| (new) | `wswan_platform.rs` `a_short_file_lists_but_does_not_seat` | under 64 KB: listed, refused with a toast, never panics |
| (new) | `wswan_seat.rs` `a_ws_cart_seats_on_cygne_through_a_real_session` | `require_core("mednafen_wswan")`, picture 224x144 in 240x160 |
| (done) | `wswan_core.rs` `sram_written_back_after_load_is_what_the_game_reads_on_the_next_boot` | the game sees what slot writes after load; the core writes nothing to `Saves/` |
| (new) | `wswan_saves.rs` `a_lid_close_mid_game_writes_saves_ws_sav` | real `Session`, SRAM marker in `Saves/WS/<stem>.sav` after `flush_resume` |
| (new) | `wswan_saves.rs` `an_eject_then_reseat_reads_the_save_back` | marker cart, eject, reseat: the read-back cart paints red |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.ws` file whose footer says Color | Shell from the footer flag (issue 98), the core runs it either way (it always emulates a Color) |
| A ROM size that is not a power of two (`.wsr`-style padding) | The footer is still the last 16 bytes; the core pads, slot only reads |
| A `.sav` shorter or longer than the cart's save RAM (another emulator's file) | `load_save_ram` copies what fits, the rest stays zero (the generic path) |

## Acceptance
- [ ] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
A WonderSwan cart boots from the shelf. Full gate in issue 99.

## References
- ADR 0012, 0034, 0050, 0055, 0072, 0082, 0092; docs/research/wswan-plan.md section 6; patch 0034 for the shape; docs/research/wswan-plan.md section 7
