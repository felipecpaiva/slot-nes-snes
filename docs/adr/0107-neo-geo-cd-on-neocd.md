# 0107. Bring the Neo Geo CD into scope on pinned NeoCD, a disc shelf of its own with a BIOS model row

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0099](0099-arcade-on-finalburn-neo.md) (the Neo Geo shelf and the non-commercial core precedent), [ADR 0104](0104-pc-engine-cd-on-beetle-pce-fast.md) (the CD shelf, CHD and the BIOS check), [ADR 0105](0105-sega-cd-on-genesis-plus-gx.md), [ADR 0069](0069-ps1-jewel-case-shelf.md) (the jewel case), [ADR 0098](0098-expansion-card.md), [ADR 0100](0100-shelf-order-option.md), [issue 233](../../.github/issues/233-neocd-tracking.md), patches `0147-neocd-core-tests` to `0150-neocd-carts`, [docs/cart-art/NEOCD.md](../cart-art/NEOCD.md)

## Context

The maintainer asked for the Neo Geo CD as its own platform, holding only the games he owns that never came
out on the Neo Geo cartridge: Crossed Swords II and the English translation (1.10) of Shinsetsu Samurai
Spirits - Bushidou Retsuden. Every other Neo Geo CD game he owns is the cartridge game, which the Neo Geo
shelf already plays. SNK released the Neo Geo CD in Japan on 9 September 1994 ([Wikipedia, "Neo Geo
CD"](https://en.wikipedia.org/wiki/Neo_Geo_CD), read 2026-10-21; the same article: the CDZ "includes a
double-speed CD-ROM drive", the earlier models' loads "could vary from 30 to 60 seconds").

Two cores could run it:

- **FinalBurn Neo's Neo Geo CD driver**, in the core slot ships for arcade (ADR 0099). At the pin it boots only
  the CDZ BIOS set `neocdz.zip`, it takes a disc as Neo Geo CD only through its subsystem or when the disc's
  parent folder is named exactly `neocd` (`libretro.cpp`, a case-sensitive compare, so `Games/NEOCD` misses
  it), and adding the driver would rebuild the arcade binary every Neo Geo, CPS1 and CPS2 set runs on.
- **NeoCD** (libretro/neocd_libretro), a Neo Geo CD emulator of its own. Read at the pin `b1e04c7`
  (`libretro.cpp`, `libretro_bios.cpp`, `libretro_variables.cpp`, `path.cpp`, `bios.cpp`), pinned by
  `neocd_core.rs`:
  - **Formats.** `valid_extensions` is `cue|chd`, `need_fullpath`. The CHD reader is libretro-common's
    `rchd`, one hunk decoded and cached at a time in the emulation thread (`chdfile.cpp`).
  - **BIOS.** At `retro_init` it scans `<system>/neocd/` recursively for any `.bin` or `.rom` of at least
    512 KB (zips too), identifies each by content (Front Loader, Top Loader, CDZ, with the SMKDan and
    Universe variants) and declares `neocd_bios` with one value per file, `"<file name> (<model>)"`, sorted.
    An unknown value falls back to the first, silently. **With no BIOS found it boots its own built-in
    high-level BIOS, with a warning only in the log**; the README calls it a work in progress.
  - **Options** (legacy variables, since slot does not answer `GET_CORE_OPTIONS_VERSION`; the first value is
    the default): `neocd_region` Japan, USA, Europe; `neocd_cdspeedhack` On, Off (replaces the BIOS's CD
    busy loop); `neocd_loadskip` On, Off (runs loading frames in fast-forward inside one `retro_run`);
    `neocd_per_content_saves` Off, On; `neocd_aspect_ratio`, `neocd_overscan_h` (8), `neocd_cpu_overclock`.
  - **Saves.** `RETRO_MEMORY_SAVE_RAM` is the console's 8 KB backup RAM. The core also reads and writes its
    own file, named in `retro_load_game` before the options are read: with per-content saves at their
    default, that is one shared `<system>/neocd/neocd.srm`.
  - **States.** About 8 MB (8,231,939 bytes): 2 MB RAM, 4 MB sprite RAM, 1 MB PCM RAM and the 512 KB BIOS
    ROM. `SET_SERIALIZATION_QUIRKS` 0; a state loads into a fresh core, and under another BIOS model, since
    it carries the ROM.
  - **Timing.** 59.60 fps, 44.1 kHz, 320x224 drawn as 304 wide with the 8-pixel overscan mask.

## Decision

- **Scope.** The Neo Geo CD is in scope as Phase 23. One shelf `Games/NEOCD` for `.cue` and `.chd`.
  `Platform::Neocd` is appended to `SHELVES` after the Sega CD, `Core::Neocd` (`neocd`, "NeoCD") to
  `EVERY`; upstream's `ALL` lists are untouched and every policy method answers it explicitly. No picker.
- **Core: NeoCD**, libretro/neocd_libretro `b1e04c738cb48a1dae0574b8877f6a116d270ca1` (its master on
  2026-10-03), archive sha256 `fac1ec58...2418`. It is the only one of the two that offers all three console
  models, reads `Games/NEOCD` as it is, and leaves the shipped arcade core alone. `cores/neocd/build.sh`:
  `HAVE_CDROM=0` (no physical drive code) and `USE_LTO=0`, because link-time optimisation drops the
  `.symver` bindings of `cores/neocd/glibc-2.17.h` (`exp`, `logf`, `pow` to GLIBC_2.17); the C++ runtime is
  linked statically. The device core is 2,935,208 bytes and needs only `libc`, `libm` and `libpthread` at
  GLIBC_2.17 (`task core:device:neocd`, 2026-10-21). No NeoCD source file is changed.
- **Licence.** NeoCD is LGPL-3.0 (`LICENSE.md`; `licenses/neocd-LGPL-3.0.txt` with the GPL-3.0 text it
  incorporates). Its Musashi 68000 core is version 4.60, MIT. **Its Z80 core is "freeware for
  non-commercial purposes"** (Juergen Buchmueller, from MAME) and its YM2610 core names its MAME authors and
  no licence, so the core is handled exactly like snes9x, PicoDrive and FinalBurn Neo (ADR 0099): named
  and quoted in LICENSING.md, notices in `System/licenses/neocd-notices.txt`, the source with every
  release, the zip never sold, and the standing rule that this project asks for no donations, anywhere.
  The release notice names NeoCD.
- **Options** (`core_options_policy::NEOCD`): `neocd_bios` the chosen model (below), `neocd_region` USA (a
  dual-language disc such as Crossed Swords II shows its English text, and the Samurai Shodown RPG
  translation turns on its quality-of-life settings under a US or European region, per its readme),
  `neocd_cdspeedhack` On and `neocd_loadskip` On (the short loads the maintainer asked for),
  `neocd_per_content_saves` Off (stated, see Saves), `neocd_aspect_ratio` 1:1 PAR (slot draws the aspect),
  `neocd_cpu_overclock` 100%. Overscan stays at the core's 8.
- **BIOS: never shipped, never fetched, a model row.** The Neo Geo CD section has a **BIOS** row: **CDZ**
  (the default), Front Loader, Top Loader, kept in `Config/neocd.txt` as `bios = cdz|front|top`. Each model
  is one file in `BIOS/neocd/`, the MAME names of libretro-database `dat/System.dat` (fetched 2026-10-21):
  `neocd.bin` (CDZ, crc `DF9DE490`, md5 `f39572af7584cb5b3f70ae8cc848aba2`), `front-sp1.bin` (crc
  `CAC62307`, md5 `5c2366f25ff92d71788468ca492ebeca`), `top-sp1.bin` (crc `C36A47C0`, md5
  `122aee210324c72e8a11116e6ef9c0d0`). Before a disc starts slot checks the chosen file: missing or not
  524,288 bytes refuses with "Neo Geo CD needs BIOS/neocd/<file>" (the Lynx, Disk System and PC Engine CD
  shape); another 512 KB file launches with "<file> is not the known dump" once a session. A disc resumed
  at boot is checked the same way. The check also keeps NeoCD's high-level BIOS from ever running a disc,
  and it pins the file the option names, so the core's silent fallback to its first file cannot pick
  another model. slot sends `neocd_bios` as the value NeoCD declares for that file
  (`neocd_bios::prepare`, before the load). The CDZ is the default because it loads fastest: on the host
  with Crossed Swords II its longest loading stall (one `retro_run` running the load in fast-forward) is
  0.31 s against 0.51 s for both other models. The row is **hidden in game**: a model change resets the
  console in NeoCD, so it applies at the next insert; a resume state made under another model still
  loads, because it carries the ROM it ran. Universe BIOS and the SMKDan patched BIOSes are not offered.
- **The maintainer's BIOS files** (`/Volumes/B3Tb/Emulation/Bios/neocd/`, md5 checked 2026-10-21):
  `neocd.bin`, `front-sp1.bin`, `top-sp1.bin`, `neocd_f.rom`, `neocd_sf.rom`, `neocd_st.rom`,
  `neocd_sz.rom`, `neocd_t.rom` and `uni-bioscd.rom` all match System.dat. His `neocd_z.rom` (in
  `neocd/` and at `Bios/`) has the md5 of `neocd.bin`, the CDZ BIOS not byte-swapped, where System.dat's
  `neocd_z.rom` row is the swapped dump (md5 `11526d58...`); NeoCD swaps either, so it is the same BIOS
  under another name. `neocdz.zip` is FinalBurn Neo's set (`neocd.bin` and `000-lo.lo`) and NeoCD does not
  need `000-lo.lo`. Staged: `neocd.bin`, `front-sp1.bin`, `top-sp1.bin`.
- **Policy: the Neo Geo shelf's.** NeoCD's own map: A, B, C and D on B, A, Y and X; SELECT is the CD pad's
  Select and START its Start (no coin on a Neo Geo CD); L1 is B+C. So L1 and R1 belong to the game
  (`owns_shoulders` false), X and Y pass through, the picture toggle is SELECT+X, and L2 and R2 stay slot's
  rewind and fast-forward keys (`owns_triggers`), as on the Neo Geo shelf (ADR 0099). On slot v1.8.0 (ADR 0106) that
  means: upstream's Turbo A and Turbo B rows stay off X and Y and are hidden in game (`xy_to_game`), and
  the flip is the Picture Next shortcut, SELECT+X by default. The 360x240 canvas,
  following the 304-wide frame.
- **Saves: the `.sav`, per game.** `Saves/NEOCD/<stem>.sav`, the 8 KB backup RAM through `SAVE_RAM`, which
  slot loads over whatever the core read. A game with no `.sav` yet gets a blank 8 KB backup RAM
  (`neocd_save::sav_or_blank`), so the shared `neocd.srm` the core reads first never hands one game
  another's saves; NeoCD's BIOS formats it. The core still writes its own `BIOS/neocd/neocd.srm` at
  unload; slot never reads it.
- **States on, rewind off.** About 8 MB a state, against the PlayStation's 4.4 MB that turned rewind off
  there (ADR 0066). Save states, resume, the crash guard, doze and fast-forward work as on every shelf.
- **Screen section** after the Sega CD: Shader (the retro list, `Config/neocd_shader.txt`), Picture
  (Stretch by default, then Actual and 4:3, `neocd` in `Config/picture.txt`, the Neo Geo shelf's rows) and
  BIOS. No PAL Speed: the core runs one rate.
- **Release order.** `RELEASED` gets `(Platform::Neocd, 1994, 9, 9)`, between CPS2 and the 32X (ADR 0100
  lists it).
- **Shelf object: the CD jewel case.** Neo Geo CD games came in the standard jewel case, Japanese releases
  with a spine card (Racketboy, ["Neo-Geo CD Price Guide and English Version
  Rarity"](https://racketboy.com/?p=11240): "Typically with case and manual, but without spine card", mint
  copies "would include spine card"; read 2026-10-21; [Wikipedia, "Obi
  (publishing)"](https://en.wikipedia.org/wiki/Obi_(publishing))). So a disc is drawn in the PlayStation's
  jewel case at the same fidelity (ADR 0069, as the PC Engine CD, ADR 0104), its front cover in the well,
  and the disc with its printed label slides out into the slot; a disc tagged `(Japan)` wears the spine
  strip, every other disc the plain case, by the name tags only. Both of the maintainer's discs are
  Japanese. The values and what was not found are in [docs/cart-art/NEOCD.md](../cart-art/NEOCD.md).
- **Labels.** `tools/fetch-labels.py` system `NEOCD`, ScreenScraper id 70 (Skyscraper
  `platforms_idmap.csv` at 290d2c0, row `neogeocd,70,54,4956`), by name like the Sega CD (`--by-name`), the
  cover (`box-2D`) and the disc scan (`support-2D`). The Redump dat (libretro-database `metadat/redump`,
  "SNK - Neo Geo CD") lists only the data track, which a CHD does not expose, and the translated disc has
  no entry at all. libretro-thumbnails "SNK - Neo Geo CD" has Named_Logos for both originals (103 logos,
  2026-10-21); the translation takes its logo through a sibling alias (docs/cart-art/NEOCD.md).
- **Titles.** The original's file name is its Redump name, `Crossed Swords II (Japan) (En,Ja)`. The
  translation is named as its readme says it is "better known outside of Japan", `Samurai Shodown RPG
  (Japan) (En)` (the patch's own localized title, "Samurai Shodown: Tales of the Bushido", has a colon a
  FAT or exFAT file name cannot hold). The shelf drops the tags as on every shelf.
- **Expansion Card.** `Games/NEOCD` is planned on the Expansion Card: `Games/NEOCD` on `/mnt/expansion` and
  the line `NEOCD` in `Config/expansion.txt` (ADR 0098). No code change.
- **Upstream test sites**, by the standing rule: (b) gains `| Platform::Neocd` after `| Platform::SegaCd`,
  (e) gains `| Core::Neocd` after `| Core::MednafenSupergrafx`, (g) gains `, "Neo Geo CD"` after
  `"Sega CD"`, (h) gains `, QuickRow::ScreenNeocd` after `QuickRow::ScreenSegaCd`.

## The maintainer's discs

`docs/rom-library/best-copy/neocd-adds.tsv` (workspace) lists both. Each archive on B3Tb
(`Roms/neogeocd/`, kept as the backup) was unpacked in `/tmp` and repacked with `chdman createcd`. The
default hunk (8 sectors) is kept for both: `-c cdlz,cdzl,cdfl -hs 489600` was larger for Crossed Swords
II (251,410,019 against 250,682,352 bytes) and only 7% smaller for the translation (282,312,659 against
302,296,176), and its 200-sector hunk means one large decode in the emulation thread every 2.7 s of CD
audio, which ADR 0104 left as a device question; NeoCD reads the same way. The PC Engine CD device run
has since answered it: discs repacked with `-hs 489600` starve the audio while CD audio streams, and
discs at the default hunk play clean, so the default hunk and codecs (`cdlz,cdzl,cdfl`) are the rule here. For each CHD the data SHA1 of
both settings agreed, and `chdman extractcd` gave back a bin whose SHA1 equals the source tracks
concatenated. Crossed Swords II's data track matches Redump (`2ece2bc1...`); the translation's track 01 is
the patched one, with no Redump hash by design. Staged in `/Volumes/B3Tb/Emulation/_staging/neocd/`
(`Games/NEOCD/`, `BIOS/neocd/`) with a resumable copy and a sha256 check.

## Performance

Host only, a direction: M5 Max, `core_bench` with the CDZ BIOS, median ms a frame over 1,200 frames after
1,200 frames of warm-up, 3 repeats: Crossed Swords II 0.306, Samurai Shodown RPG 0.233. FinalBurn Neo's
Neo Geo sets measured 0.21 to 0.30 on the same host (ADR 0099), so NeoCD sits in the same range; both
use the C Musashi 68000 core. NeoCD's README: it "runs perfect on Raspberry Pi 3". On the host each disc
boots through the BIOS to its title with picture and CD audio under every model (`neocd_core.rs` with
`SLOT_NEOCD_BIOS` and `SLOT_NEOCD_DISC`). The device gate (issue 238) measures the H700.

## Consequences

- Four patches, 0147 to 0150. No GBA, GB or GBC path changes, so the harness compare stays at 0 diffs.
- **CI cannot boot a real disc.** The core tests use a generated cue and bin and placeholder BIOS files that
  carry only the bytes NeoCD identifies a model by; they cannot boot a game. A real BIOS folder and disc
  are read from `SLOT_NEOCD_BIOS` and `SLOT_NEOCD_DISC`, and the tests print a skip without them.
- `zip-check.sh` cannot find NeoCD by its library name: FinalBurn Neo's strings name its own Neo Geo CD
  driver "NeoCD". It uses the option key `neocd_cdspeedhack`.
- Known gaps: no rewind; the core's own `neocd.srm` is written beside the BIOS; Universe BIOS is not
  offered; one disc per game (no `.m3u`).
- On a NeoCD pin bump, rerun `neocd_core.rs`: the option values, the `neocd_bios` value format, the BIOS
  folder, the high-level BIOS fallback, the `neocd.srm` naming, the state size, and the libm symbols
  (`task core:device:neocd`); recount the licence classes in LICENSING.md.
