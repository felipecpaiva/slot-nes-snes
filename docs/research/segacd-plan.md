# Sega CD / Mega-CD on slot-nes-snes: plan (2026-10-19)

> **Integrated 2026-10-21 (ADR 0105, patches 0139 to 0146).** Written on the `segacd-groundwork` branch
> as ADR 0094, issues 113 to 122, patch 0057 and Phase 13; renumbered on integration to ADR 0105, issues
> 222 to 231 (232 is the device gate), patch 0139 and Phase 22. Where the integration differs from this
> plan, ADR 0105 wins: `genesis_plus_gx_cart_size` is left unanswered (the pin stores "disabled" as 0xff
> and mounts a cart), the state trailer is the PS1 one, the BIOS check uses crc32 and knows both US dumps,
> there is no Region row, and the cases are the PS1 jewel cases unchanged.

"Our tree" means the patch set on slot main 1b20432 (ADR 0083), patches 0001 to 0051. The
integration patches will be written on whatever base is current when this phase starts, so this plan
names seams, not line numbers. "GPGX" means libretro/Genesis-Plus-GX at our pin `393f70c` (ADR 0053),
the core that already plays Game Gear, Master System and Mega Drive. Core line numbers below are
`libretro/libretro.c` at that pin unless another file is named.

## TL;DR

- **Verdict: go.** It is the cheapest disc system on the list:
  - no new core, no new licence, no new build: GPGX already ships, and our pinned build has
    `HAVE_CHD = 1` (`Makefile.libretro` line 4);
  - the picture is the Mega Drive's (256 or 320 x 230, the 360x240 canvas, ADR 0052);
  - 59.92 fps (US, JP) or 49.70 (EU), both handled by ADR 0071 the way Mega Drive is;
  - the controls are the Mega Drive's (3 or 6 buttons);
  - discs and jewel cases reuse the PS1 machinery (ADR 0067, 0069).
- **Done now (groundwork, this branch):** host tests on the pinned core
  (`patches/0139-segacd-core-tests.patch`, issue 230). They prove, on CI with no real BIOS:
  - a disc with no BIOS is refused;
  - the region byte picks `bios_CD_U.bin`, `bios_CD_E.bin` or `bios_CD_J.bin`;
  - cue/bin, iso and chd discs load at 59.92 fps on the 360x240 canvas, with no `SAVE_RAM`;
  - where the backup RAM file lands, when it is written, that it is read back, that a state does
    not carry it, and that a flush by reload writes it and leaves the game where it was;
  - how GPGX reads an `.m3u`.
  With `SLOT_SEGACD_BIOS` set, the real US BIOS boots to its menu and draws the 320-wide picture.
- **The one new problem is backup RAM durability** (issue 227). GPGX writes the Sega CD's internal
  backup RAM (`.brm`) itself, only in `retro_unload_game`, truncating the file in place. Unlike
  NGP, the save state does **not** carry it, so a resume state is no backstop. The NGP design
  (issue 75 on the NGP branch) applies, and the flush by reload is cheap on the host (0.8 ms for a
  synthetic CHD, about 2 ms for Final Fight CD). It still needs a device measurement.
- Expected size: 9 patches, about as big as the Mega Drive step plus the NGP flash item.

## 1. Core facts at the pin (verified 2026-10-19)

Each fact is pinned by a test in `segacd_core.rs` (patch 0139) unless it says "source".

### Loading a disc

- **Formats.** `cdd_load` (`core/cd_hw/cdd.c` line 390) takes:
  - a `.cue` (`MODE1/2048` or `MODE1/2352` data, audio tracks as raw BINARY or WAVE);
  - a raw `.bin` or `.img` (sync pattern) or a cooked `.iso` (starts `SEGADISCSYSTEM`), each
    auto-mounting a same-stem `.cue` when there is one;
  - a `.chd` (CD metadata v1 or v2).
  The data track is padded to 150 sectors if shorter (a BIOS requirement, source).
- **`need_fullpath` is true** (line 3131), already handled by ADR 0059.
- **BIOS by region.** The core reads the disc's region from the security code byte at 0x20b
  (`get_region`, `core/loadrom.c` line 1065): 0x64 is Europe, 0xa1 is Japan, anything else is the
  US. It then opens exactly one file, `bios_CD_E.bin`, `bios_CD_J.bin` or `bios_CD_U.bin`, from
  the system dir (lines 3525 to 3527), which slot sets to `BIOS/`. If that file is missing the
  load fails (tested: no BIOS, and a PAL or Japanese disc with only the US BIOS present).
- **The core checks nothing in the BIOS file** beyond opening it and reading more than zero bytes
  (`load_bios`, `core/loadrom.c` line 394). A junk file of the right name "boots" to a black screen.
  The tests rely on this (a 128 KB dummy that spins), and slot's BIOS check (issue 224) must hash
  the file, because the core will not.
- **Known BIOS dumps** (GPGX libretro doc, and the maintainer's files, md5 checked 2026-10-19):

  | File | Size | md5 | crc32 |
  |---|---|---|---|
  | `bios_CD_U.bin` | 131072 | `854b9150240a198070150e4566ae1290` | `9f6f6276` |
  | `bios_CD_E.bin` | 131072 | `e66fa1dc5820d254611fdcdba0662372` | `529ac15a` |
  | `bios_CD_J.bin` | 131072 | `278a9397d192149e84e820ac621a8edd` | `9d2da8f2` |

  The PicoDrive doc lists another US revision (md5 `2efd74e3...`), the RetroPie copy he also has.
  Issue 224 decides whether that one is accepted too (it boots in GPGX, unmeasured).
- **The BIOS alone** loaded as content boots the CD unit to its menu (the `ROMType` "BR" branch,
  `core/loadrom.c` from line 797). Tested with the real US BIOS: 320 wide, the menu drawn inside the
  picture, black bars outside.
- **Security code.** A disc boots into its program only if its first sector carries the security
  block for its region at 0x200. That block is Sega's code. It is not in the BIOS as a plain copy
  (searched the US BIOS for the first bytes of a real disc's block: no match), so a test cannot copy
  it from the user's BIOS either. **So no synthetic disc in this repo runs a program**: the real
  BIOS stops at its menu on our discs. That is enough for every contract slot needs (load, region,
  timing, picture, backup RAM path), and a real game is a device-gate item.

### Timing and picture

- 59.92 fps for a US or Japanese disc, 49.70 for a European one, 44.1 kHz (tested). Both sides of
  ADR 0071's window already work for Mega Drive; the PAL Speed row of issue 66 applies.
- The picture is the Mega Drive VDP's, so the canvas, Stretch and Crop rules of Mega Drive apply
  unchanged (ADR 0050, 0052, 0061). The real BIOS draws 320 wide inside the 360x240 canvas (tested).
- The state is 1,036,288 bytes, the same fixed size as Mega Drive (`STATE_SIZE 0xfd000`,
  `core/state.h` line 42; tested). Rewind costs what it costs on Mega Drive.
- The state is not byte-stable across a plain unserialize and serialize: five bytes of timing
  differ (seen in the tests). Any test that compares states compares against a round trip, not the
  original bytes.

### Saves: backup RAM

- **No `SAVE_RAM`.** `retro_get_memory_data(SAVE_RAM)` returns the cart SRAM, which is off for a
  CD (tested: `save_ram()` is `None`). slot's `.sav` path, ADR 0072's no-state path and
  `save_ram_trusted` never see Sega CD saves.
- **Not in the memory maps either.** `set_memory_maps` (line 2738) lists 68K RAM, PRG-RAM and word
  RAM for a CD, not `scd.bram` (source). slot cannot read the backup RAM while the game runs.
- **Not in the state.** `scd_context_save` (`core/cd_hw/scd.c` line 2009) saves PRG-RAM and word
  RAM but not `scd.bram` (source; tested by searching a state for a marker planted in the file).
- **Where.** `bram_load` (line 1043) runs in `retro_load_game` (line 3675) and `bram_save` (line
  1140) in `retro_unload_game` (line 3730). The file is in the save dir slot hands the core (today
  `Saves/`, `slot::core::open_named`):
  - default (`genesis_plus_gx_system_bram` unset or `per bios`): `Saves/scd_U.brm`,
    `Saves/scd_E.brm` or `Saves/scd_J.brm`, one 8 KB file shared by every game of that region
    (lines 1385 to 1392; tested `scd_U.brm`);
  - `per game`: `Saves/<stem>.brm`, where the stem is the content file's, so the `.m3u` stem for a
    playlist (lines 1394 to 1401; tested `Lunar.brm` and `Night Trap.brm`).
- **When.** Only at unload, never while the game runs (tested). The write is libretro-common
  `filestream` opened for write, so the file is truncated first. A power cut in that window
  leaves a short file. A short file still passes the core's format check only if its last 0x20
  bytes happen to be right; otherwise the core formats a fresh RAM and **the saves are gone
  silently** at the next load.
- **What triggers a write.** The core keeps a crc32 of what it loaded and writes only when the RAM
  changed (tested: an unchanged file is not rewritten). When it finds no file it formats a fresh
  8 KB RAM and zeroes the crc, so **the first unload always writes a formatted file** even if the
  game saved nothing (tested).
- **Read back at load** (tested: a planted file is read, so an unchanged unload writes nothing).
- **RAM cart.** GPGX can mount a backup RAM cartridge (`genesis_plus_gx_cart_size`, declared
  default `4meg`, a 512 KB `4Mbit_cart.brm` shared by every game, lines 1404 to 1500). slot answers
  no option it was not given, so the core reads the option as unset, leaves `cart_size` at 0 and
  mounts no cart (`cd_cart_init`, `core/cd_hw/cd_cart.c` line 178; tested: only `scd_U.brm` is
  written). Issue 225 makes that explicit.
- **Flush by reload works.** Serialize, `load` the same disc (slot's `load` unloads first, so the
  core writes the `.brm`), unserialize: the `.brm` is on disk and the state is the state an
  unserialize alone gives (tested). Host timings on the M5 Max:
  - synthetic 16-sector CHD: 0.75 to 0.87 ms;
  - Final Fight CD (USA) `.chd` (owned dump, read-only, `SLOT_SEGACD_DISC`): min 2.00, median 2.06,
    max 2.54 ms over five reloads; the first load from the USB disk took 237 ms (cold read).
  `genesis_plus_gx_cd_precache` must stay off: on, every reload reads the whole CHD into memory.

### Discs and playlists

- GPGX registers the legacy disk-control interface (13) in `retro_init` (line 3835) and withdraws
  it at load for anything but a CD (line 3677). It does not ask for the EXT interface (57, 58), so
  there is no `set_initial_image`: a remembered disc is restored by a swap after load.
- At most 4 discs (`MAX_DISKS`, line 2762).
- **`.m3u`.** Only a lowercase `m3u` extension is read as a playlist (line 3564). Each line is
  joined to the playlist's own directory, so an absolute line fails (tested). slot's PS1 playlists
  write absolute paths (`write_playlist`, patch 0034), so that code cannot be reused as is: Sega CD
  playlists must hold paths relative to the playlist, or sit beside the discs.

## 2. Backup RAM durability (issue 227)

The bar is ADR 0012 and 0034's rule for `.sav`: progress the game wrote survives these events.

| Event | `.sav` cores today | Sega CD if we do nothing |
|---|---|---|
| Lid close, POWER tap, battery critical (`flush_resume`) | `.sav` and `resume.state` written atomically | `resume.state` written, **without** the backup RAM; `.brm` not written |
| Eject | `.sav` written, core dropped | Core dropped, so `.brm` written, non-atomically, to `Saves/` |
| 60 s autosave | `.sav` written | Nothing |
| Power cut with no flush | Last autosave | Saves since the last clean eject are lost, **resume or not** |
| Start fresh after a crash | `.sav` from the last write | `.brm` from the last clean eject |

The NGP options carry over, with one change: option 5 (rely on the state) is not available.

1. **Per-platform core save dir** `Saves/SEGACD/` through a policy answer read by `open_named`, the
   NGP issue 75 seam. The file sits beside the platform's other saves and follows ADR 0082's hack
   updates. Small.
2. **Per-game file**: `genesis_plus_gx_system_bram = per game`, so one game cannot clobber
   another's saves and a torn write loses one game, not a region's worth. Small (issue 225).
3. **Atomic publish.** The core writes into a staging dir (`Saves/SEGACD/.core/`). Before load slot
   copies `Saves/SEGACD/<stem>.brm` in; after unload it publishes with `persist`'s temp, fsync and
   rename. A torn file never reaches the final path. Small, reuses the atomic writer and NGP's
   staging code.
4. **Check before staging.** A `.brm` that is not exactly 8192 bytes or lacks the format footer
   (`SEGA_CD_ROM` at 0x1fe0, `RAM_CARTRIDGE___` at 0x1ff0) is moved aside and logged, never handed
   to the core, which would format over it silently.
5. **Flush by reload** on `flush_resume`, eject and the 60 s autosave: serialize, reload the disc,
   publish, unserialize, the game carries on. 2 ms on the host for a real CHD; the device cost is
   the open question (section 3).
6. **A small core patch** that exposes `scd.bram` as `RETRO_MEMORY_SAVE_RAM` for a CD would let
   slot's own `.sav` path take it with no reload. Rejected for now: ADR 0002 builds every core from
   its pinned upstream with no patches, and the file format would change (`.sav` instead of
   `.brm`). Only if option 5 fails the device bar, and then upstream first (ADR 0047).

**Recommendation: 1 + 2 + 3 + 4 + 5**, the NGP design, decided in ADR 0105 with option 5 conditional
on the device number. If the reload misses the bar at lid close, the fallback is to flush by reload
only at eject and autosave, and accept up to 60 s of loss at a lid close.

## 3. Measuring the reload on the device (issue 227)

What to measure: the wall time of serialize, `load` of the same disc, unserialize, on the RG34XXSP,
for real CHDs on the SD card. The host number is 2 ms; the A53 is roughly 10 to 15 times slower on
CPU work and the SD card is far slower than the Mac's disk, so the estimate is 20 to 60 ms
(unmeasured).

How, when integration starts (needs adb and the device, not available to the groundwork):

1. Build the device test binary or add a `--reload N` mode to `core_bench`: load the disc, run 600
   frames, then N times: serialize, reload, unserialize, run 60 frames. Print min, median and max,
   and separately the `load` call alone.
2. Run it under `SLOT_TRACE` on three discs of different shapes: Final Fight CD (data plus many
   audio tracks), Sonic CD (big data track), Lunar: The Silver Star (the save-heavy RPG), all
   `.chd` from the maintainer's card. Each cold (after `echo 3 > /proc/sys/vm/drop_caches`) and
   warm.
3. Repeat with `genesis_plus_gx_cd_precache` off (the policy) to confirm a reload reads only the
   CHD header, TOC and first hunk, not the disc.

The bar:

| Flush point | Bar | Why |
|---|---|---|
| Lid close, POWER, battery critical | under 100 ms warm, no audio glitch before the screen goes dark | slot already writes `resume.state` (about 1 MB) there; the reload must not double the wait |
| Eject | under 250 ms | the eject animation hides it |
| 60 s autosave | under one frame (16.6 ms) or done on a frame the player cannot see | it happens mid-game |

If the autosave misses its bar, the autosave flush moves to the next pause (quick menu open), which
already stops the game.

## 4. Video and the Screen section (issue 226)

- `Core::canvas(GenesisPlusGx, SegaCd) = (360, 240)`, the Mega Drive canvas (ADR 0050). Stretch
  follows the live frame width (ADR 0052), Crop and Picture as Mega Drive (ADR 0061, 0062).
- **Own Screen section** `SCREEN_SEGACD` (the maintainer's rule), the Mega Drive rows: Shader (the
  shared retro list, stored outside `slot.state` like the other Sega shelves, `Config/sega_shaders.txt`,
  ADR 0051), Picture, and PAL Speed (issue 66),
  because European discs run at 49.70.
- Named test sites (g) and (h) gain the token (ADR 0055); CONTRIBUTING.md in that patch.

## 5. Input (issue 229)

The Mega Drive policy as shipped (patch 0026): SNES-like layout, X, Y, L and R as the 6-button row,
slot keeps no shoulders (`owns_shoulders` false), SELECT is MODE and keeps slot's chords. GPGX picks 3 or 6 buttons per port by its device
type. Default 6-button, like Mega Drive. A game that misreads a 6-button pad is a device-gate
finding, and a per-game 3-button choice is added only then.

## 6. Shelf, scan, discs, cases, art (issues 223, 228, 231)

- **Shelf** `Games/SEGACD`, `Platform::SegaCd`, appended to `SHELVES`; `Saves/SEGACD`,
  `States/SEGACD`, `Labels/SEGACD`, short like `Games/MD`. The shelf title is "Sega CD"; the EU and
  JP case styles say "Mega-CD".
- **Scan** `.chd`, `.cue`, `.m3u`, and `.iso` (a cooked single-track dump). A `.bin` is never a game
  (it is a track; the PS1 rule). A playlist hides the discs it names (PS1 code, reused). Discs
  named `(Disc N)` with no playlist get one generated, **with relative paths** (section 1).
- **Discs** (issue 228): ADR 0067's swap (SELECT+L2 on PS1; on Sega CD L2 is free too), rollback,
  `Saves/SEGACD/<stem>.disc`, and the state trailer. Differences: legacy interface only, so the
  remembered disc is set by a swap right after load; 4 discs at most. Multi-disc games in his
  library: Night Trap and Prize Fighter (two discs each).
- **Cases** (issue 231): the PS1 jewel case renderer (ADR 0069) with Sega CD styles:
  - US: the long box era and later the jewel case; v1 draws the jewel case only (the long box is a
    deferred style, like issue 68);
  - EU and JP: the jewel case; JP with its spine strip (obi), as PS1.
  Region from the file name tags, then the disc region byte at 0x20b for a `.cue`/`.iso` (cheap to
  read; a `.chd` needs a hunk decode, so a `.chd` with no tag is US).
- **Art**: ScreenScraper `segacd` id **20** (Skyscraper `platforms_idmap.csv`, row `segacd,20,20,21`,
  Gemba/skyscraper `290d2c0`). Dat: Redump "Sega Mega CD & Sega CD" (`redump.org/datfile/mcd/`).
  libretro-thumbnails `Sega_-_Mega-CD_-_Sega_CD` has Named_Boxarts, Named_Logos, Named_Snaps and
  Named_Titles (checked 2026-10-19). `tools/fetch-labels.py` gains an entry next to PS1: front cover
  (`box-2D`) and disc scan (`support-2D`), disc games matched by name since a disc has no CRC in a
  No-Intro dat.

## 7. Issue list (Phase 22)

| Issue | Title | Size |
|---|---|---|
| 222 | Tracking: Sega CD / Mega-CD on Genesis Plus GX (holds the device gate) | L |
| 223 | Add `Platform::SegaCd` with its own shelf, disc scan and explicit policy | M |
| 224 | Check the region's Sega CD BIOS before a launch and toast instead of a black screen | S |
| 225 | Set the Sega CD core options: per-game backup RAM, no RAM cart, no precache | S |
| 226 | Give Sega CD the Mega Drive canvas and its own Screen section | S |
| 227 | Keep Sega CD backup RAM safe: core save dir, atomic publish, check, flush by reload | M |
| 228 | Swap Sega CD discs, remember the disc, record it in states | S |
| 229 | Hand the Mega Drive 3 and 6 button pad to Sega CD games | S |
| 230 | Test Sega CD with synthetic discs, a dummy BIOS and the real BIOS when given | S |
| 231 | Draw Sega CD games as jewel cases and fetch their covers | M |

## 8. Device gate (in issue 222)

1. Play Sonic CD, Lunar: The Silver Star, Snatcher and Final Fight CD for 10 minutes each under
   `SLOT_TRACE`: full speed, zero audio underruns, the ms a frame recorded (estimate 4 to 6 ms,
   unmeasured; MD is 3.3 ms). Include an FMV-heavy title (Night Trap or Sewer Shark) for CD-DA and
   CHD decode cost.
2. Backup RAM: save in Lunar, close the lid, pull the battery, boot. The save is there, resuming and
   starting fresh. Time the reload (section 3).
3. A two-disc game: swap, eject, reinsert, the disc is remembered.
4. Eject and GBA: the GBA leg equals a GBA-only run.

## 9. What remains for the integration step

Issues 223 to 229 and 231, plus the platform half of 230, in issue order. Nothing to build: the core
is already in `task core:host`, `task core:device`, `dist:device` and `zip-check.sh`. When the
platform patch lands, `zip-check.sh` gains `SEGACD` in its `games` list and the README row moves
from planned to shipped. NGP issue 75's staging code should land first so issue 227 reuses it.
