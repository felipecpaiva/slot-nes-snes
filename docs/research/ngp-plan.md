# NeoGeo Pocket and Pocket Color on slot-nes-snes: plan (2026-10-18)

> **Status 2026-10-19:** written on the v1.7.0 tree (patches 0001 to 0057 then); the integration
> landed on upstream main 1b20432 as patches 0080 to 0087 (ADR 0083 for the base, ADR 0090 for the
> core, ADR 0094 for the flash). Where this plan says "the 1.8.0 base", read upstream main 1b20432.
> Two deltas from the text below: Stretch crops the 4-row bars (`stretch_crops_height` true, so it
> fills 720x480 as section 4 says), and both cart shells are the nelynes dark grey (maintainer's choice,
> ADR 0090), not a separate Color shell.

"Our tree" means slot v1.7.0 plus patches 0001 to 0057. The integration patches will be written on
the upstream 1.8.0 base once that port lands, so this plan names seams, not line numbers. "NeoPop"
means libretro/beetle-ngp-libretro at `a50d5ac` (ADR 0090). The reference is nelynes/slotPlus
branch `slotPlusUltra` ([a8eae4c](https://github.com/nelynes/slotPlus/commit/a8eae4c) for the core,
shelf, cart and Screen page, [1ef7226](https://github.com/nelynes/slotPlus/commit/1ef7226) for
stretch, [ceb7052](https://github.com/nelynes/slotPlus/commit/ceb7052) for the bezel). We take ideas
from it and reimplement them with credit. Nothing is cherry-picked (docs/research/fork-nelynes.md).

## TL;DR

- **Verdict: go.** It is the cheapest new system on the list:
  - 160x152 at 3x is 480x456, which fills the 480-line panel with 12-pixel bars;
  - no BIOS;
  - no rotation;
  - one 4-way pad, two face buttons and Option;
  - 60.25 fps, which is inside ADR 0071's 2 fps window, so no pacing work and no PAL Speed row.
- **Done now (groundwork, this branch):**
  - the core build, pinned for host and device (issue 71);
  - the licence record;
  - host tests with a generated cart. They prove boot, the 160x152 picture, states, and the
    flash-save contract (`patches/0075-ngp-core-tests.patch`, issue 77).
- **The one new problem is flash durability** (issue 75):
  - NeoPop gives slot no `SAVE_RAM`.
  - It writes its own `<name>.flash` only when the game unloads, truncating the file in place.
  - slot's persist path (`.sav` writes, ADR 0072's no-state path, `save_ram_trusted`) never sees
    the flash.
- Expected size: 8 patches on the 1.8.0 base, about as big as the Game Gear step plus one
  M-sized save item.

## 1. What nelynes did (reference only)

| Area | nelynes/slotPlus `slotPlusUltra` | Ours |
|---|---|---|
| Core | beetle-ngp `a50d5ac`, `make platform=unix`, `-mcpu=cortex-a53`, no sha256 | Same commit, pinned with archive sha256, static C++ runtime, glibc gate (issue 71, done) |
| Enums | `Platform::Ngp` and `Core::Ngp` added to upstream's `ALL`; upstream tests edited | `Platform::Ngp` in `SHELVES`, `Core::MednafenNgp` in `EVERY`, upstream `ALL` and tests untouched (ADR 0090) |
| Shelf | `Games/NGP`, `.ngp .ngc .ngpc` | Same |
| Canvas | 160x152 inside the 240x160 buffer at 3x | Same: `Core::canvas(MednafenNgp, Ngp) = (240, 160)`, the GBA-sized path (ADR 0050) |
| Saves | Core save dir pointed at `Saves/NGP`, core stopped before power-off | Same direction, plus an atomic publish and the flush points (section 3) |
| Shader | `shader_ngp` inside `slot.state` | Own Screen section, setting outside `slot.state` (ADR 0051) |
| Cart | Bitmap pak drawn by `assets/src/carts.py` | Retro bitmap cart (ADR 0054), their drawing as a credited reference |
| Tests | `ngp_core.rs`: spinning 64 KB cart boots, state round-trips | Same header recipe, plus paint, flash write and restart (patch 0080) |

## 2. Core facts found while building (2026-10-18)

- **Build.** Host `mednafen_ngp_libretro.dylib` (arm64, `platform=osx`). Device
  `mednafen_ngp_libretro.so`:
  - sha256 `55c5fa86044e5bffd0c97bbfeff6a4731c722ec84ed08e6c54fffe65a033edb9`;
  - built in rust:1-bullseye `sha256:4730e387...`;
  - all 37 compile lines carry `-mcpu=cortex-a53`;
  - NEEDED is `libc.so.6` only, at GLIBC_2.17 or older.
- **Name.** The makefile's `TARGET_NAME` is `mednafen_ngp`. So:
  - `Core::as_str()` must be `mednafen_ngp`;
  - the option prefix is `ngp_` (the core's one option is `ngp_language`, english or japanese,
    default english).
- **Picture.** The core always calls `video_cb` with 160x152, RGB565, at a pitch of 320 bytes.
  slot's GBA-sized path centres it at (40, 4) in 240x160. The test pins every pixel of that.
- **Timing.** 60.25 fps (a constant in `libretro.c`), 44100 Hz. The test pins 60.0 to 60.5 and
  44100.
- **Input.** RetroPad B is the NGP A button, RetroPad A is the NGP B button, START is Option. There
  are no shoulder buttons, and SELECT is unused.
- **Saves.** These facts are proven by `ngp_core.rs`. Each test fails when the behaviour is
  broken.
  - `retro_get_memory_data(SAVE_RAM)` is NULL. Only system RAM (16 KB) is exposed. So
    `RetroCore::save_ram()` is `None`.
  - Game writes go through the flash command at 0x205555 or 0x202AAA. The core records a 256-byte
    block and keeps it in RAM.
  - `retro_unload_game` writes `<save_dir>/<name>.flash`, where the name is the ROM stem because
    slot does not answer `GET_GAME_INFO_EXT`. It writes only when the game wrote flash. The write
    goes through libretro-common `filestream` (stdio, since slot answers no `GET_VFS_INTERFACE`)
    opened for write, so the file is truncated first. A power cut in that window leaves a torn
    file, with two outcomes:
    - Cut before the 8-byte header is written: the `0x0053` id check fails and NeoPop silently
      starts with blank flash.
    - Cut after the header: the check passes. `system_io_flash_read` reports success on a short
      read. `flash_read` allocates `total_file_length` bytes and fills only what the file holds.
      `do_flash_read` then walks `block_count` block headers with no bounds check, so heap garbage
      lands in the cart flash, and a torn block header can read past the buffer.

    So slot must never hand the core a torn file.
  - `retro_load_game` reads the file back into the cart.
  - `retro_serialize` includes the flash blocks (`FLASH_StateAction`). `retro_unserialize`
    restores them, and the next unload writes them out. **A resume state alone brings the flash
    back.**
  - Today slot hands every core `Saves/` (`slot::core::open_named`), so NeoPop would write
    `Saves/<stem>.flash`, beside the platform folders rather than in `Saves/NGP/`.
- **Colour or mono.** Header byte 0x23 is 0x10 for a Pocket Color cart and 0x00 for a mono one.
  The title is 12 bytes at 0x24. The core picks the mode from the header, so slot needs the byte
  only for the shelf and the cart shell.
- **RACE** is the other libretro NGP core. It has the same flash-on-shutdown shape, exposes no
  memory at all, and bundles an undocumented `koyote.bin` BIOS blob. Not taken (ADR 0090).

## 3. Flash durability (issue 75)

The bar is ADR 0012 and 0034's rule for `.sav`: progress written by the game survives these
events.

| Event | `.sav` cores today | NeoPop if we do nothing |
|---|---|---|
| Lid close, POWER tap, battery critical (`flush_resume`) | `.sav` and `resume.state` written atomically | `resume.state` written (it carries the flash); `.flash` not written |
| Eject | `.sav` written, core dropped | Core dropped, so `.flash` written, but non-atomically and to `Saves/` |
| 60 s autosave | `.sav` written | Nothing for the flash beyond the state |
| Power cut with no flush | Last autosave | Last autosave's state, if slot resumes it |
| Start fresh (no resume) after a crash | `.sav` from the last write | `.flash` from the last clean eject, so progress since then is lost |

Options, smallest first. They combine.

1. **Point the core at `Saves/NGP/`.** A per-platform core save dir through a policy method, so
   the file sits beside the platform's `.sav` files and moves with ADR 0082's hack updates. Small.
2. **Atomic publish.** Give the core a staging dir (`Saves/NGP/.core/`). Before load, copy
   `Saves/NGP/<stem>.flash` in. After unload, write it out with `persist`'s temp, fsync and rename.
   This makes the truncate window harmless: a torn file never reaches the final path, and so it
   never reaches the core at the next load. Small, and it reuses the atomic writer.
3. **Flush by reload.** On `flush_resume`, eject and autosave for NGP: serialize, unload (the flash
   is written), publish (option 2), load, unserialize. The game carries on. NeoPop's state is small
   and the reload is a file read, so measure the cost on the device first (target: under one frame,
   16.6 ms, at the lid-close flush).
4. **Answer `GET_VFS_INTERFACE`** with a writer that is atomic on close. It is general, but every
   core that uses `filestream` would start going through it (pcsx_rearmed opens discs and memory
   cards that way), so the blast radius is every system. Not recommended.
5. **Rely on the resume state.** Already true (tested). It is not enough alone, because "start
   fresh", a deleted resume or a cart moved to another card loses everything since the last eject.

**Recommendation: 1 + 2 + 3, with 5 as the backstop that already exists.** Issue 75 decides and
records it in an ADR. The proof is a host test that closes the lid mid-game on a real `Session` and
finds the marker in `Saves/NGP/<stem>.flash`. The device test is a lid close followed by a battery
pull.

## 4. Video and the Screen section (issue 74)

- Canvas 240x160 through `Core::canvas` (ADR 0050). The picture is 160x152 at exact 3x, so Actual
  is 480x456 centred. Stretch fills 720x480 (nelynes 1ef7226, stretch both ways).
- **Own Screen section** `SCREEN_NGP` (the maintainer's rule), with two rows:
  - **Shader**: Off, then upstream's LCD3x (exact 3x is what it is tuned for, the ADR 0060 Game
    Gear precedent), then the shared retro list. It is stored in its own `Config/` file (ADR 0051).
  - **Picture**: Actual (default) and Stretch, no Crop, because NGP has no overscan. The default
    lives in `Config/picture.txt` (ADR 0061).
  - **No PAL Speed row.** NGP has no PAL variant, and 60.25 fps is inside ADR 0071's window.
- The Transparent look (nelynes 9201b8a, an unlit reflective LCD) is a later, separate item. If
  wanted it is a new retro mode in `RETRO_FRAG`, not a `GAME_FRAG` hunk (fork review).
- The NGP bezel (nelynes ceb7052) is out of v1. It is a follow-up with its own art licence check.

## 5. Input (issue 76)

The device's A and B map to the NGP A and B through the RetroPad swap the core expects (RetroPad B
is A). START is Option. There are no shoulders, so slot keeps L1 and R1 (`owns_shoulders` true).
X and Y are turbo A and B, like Game Gear. SELECT stays slot's (Select+X picture, Select+Y guard).

## 6. Shelf, scan, cart art (issues 72 and 78)

- Scan `.ngp`, `.ngc` and `.ngpc` onto one `Games/NGP` shelf. `.npc` is in the core's list but
  appears in no No-Intro dat, so it is left out. The title is the file stem. The colour flag (0x23)
  is read once for the cart shell.
- Cart: the retro bitmap renderer (ADR 0054), two shells, mono (grey) and Color (the colour shell).
  The shell is chosen by the header byte, not the extension, because `.ngp` files that are Color
  carts exist.
- Labels: `tools/fetch-labels.py` `SYSTEMS` takes one ScreenScraper id per shelf, but NGP has two:
  `ngp` 25 and `ngpc` 82 (Skyscraper `platforms_idmap.csv` at ccd49ae). Dats are `SNK - Neo Geo
  Pocket` and `SNK - Neo Geo Pocket Color`. The choice for issue 78: one `NGP` entry with both
  dats, and the id chosen per ROM by the header byte, which the script can read as it already reads
  headers for NES and SNES. The alternative is two shelves, which the scan does not want.

## 7. Issue list (Phase 9)

| Issue | Title | Size | Needs the 1.8.0 base |
|---|---|---|---|
| 70 | Tracking: NeoGeo Pocket and Pocket Color on Beetle NeoPop | L | n/a |
| 71 | Build Beetle NeoPop from a pinned commit for host and device and record its licence | S | No, done |
| 72 | Add `Platform::Ngp` with its own shelf, scan and explicit policy | M | Yes |
| 73 | Set the NGP core options and answer NeoPop's declared defaults | S | Yes |
| 74 | Give NGP a 240x160 canvas and its own Screen section with Shader and Picture rows | S | Yes |
| 75 | Keep NGP cart flash safe: core save dir, atomic publish, flush by reload | M | Yes |
| 76 | Map the NGP A, B and Option buttons | S | Yes |
| 77 | Test NGP with a generated cart that paints and writes flash | S | Partly: core tests done, platform tests per step |
| 78 | Draw NGP carts (mono and Color shells) and fetch their labels | M | Yes |
| 79 | NGP device gate on the RG34XXSP | S | Yes |

## 8. Device gate (issue 79)

1. Play SNK vs. Capcom: Match of the Millennium, Metal Slug 2nd Mission and Sonic the Hedgehog
   Pocket Adventure for 10 minutes each under `SLOT_TRACE`: full speed, zero audio underruns, and
   the ms a frame recorded (estimate 1 to 2 ms, unmeasured).
2. Flash: save in-game, close the lid, pull the battery, boot. The save is there with and without
   the resume.
3. Eject and GBA: the GBA leg equals a GBA-only run.

## 9. What remains for the integration step (on 1.8.0)

Issues 72 to 76 and 78 to 79, plus the platform half of 77, in that order. When the platform patch
lands:

- `licenses/mednafen_ngp-GPL-2.0.txt` moves out of `cores/mednafen_ngp/`;
- the core joins `scripts/dist-device.sh` and `scripts/zip-check.sh` (the cores list, the `req`
  and `ok` lists, the licence file list and the strings cross-check pair `mednafen_ngp:NeoPop`);
- `zip-check.sh` gains `NGP` in its `games` list;
- the README gets a "planned, not shipped" row.
