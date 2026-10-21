# 0104. Bring the PC Engine CD into scope on the shipped Beetle PCE Fast, built with its CHD reader, a disc shelf of its own

- Status: Accepted. Amends [0002](0002-cores.md), the docs/PLAN.md "Who it's NOT for" line on more systems, and [0091](0091-tg16-on-beetle-pce-fast.md) ("HuCards only", `HAVE_CHD=0`)
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0091](0091-tg16-on-beetle-pce-fast.md) (the core and the TurboGrafx-16 policy this follows), [ADR 0069](0069-ps1-jewel-case-shelf.md) (the jewel case), [ADR 0101](0101-famicom-disk-system-on-fceumm.md) and [ADR 0093](0093-lynx-on-beetle-lynx.md) (the BIOS check), [ADR 0098](0098-expansion-card.md), [ADR 0100](0100-shelf-order-option.md), [issue 216](../../.github/issues/216-pcecd-tracking.md), patches `0135-pcecd-core-tests` to `0138-pcecd-carts`, [docs/cart-art/PCECD.md](../cart-art/PCECD.md), [docs/research/next-systems-2026-10-20.md](../research/next-systems-2026-10-20.md) (PC Engine CD, rank 2)

## Context

The maintainer asked for the PC Engine CD-ROM² and TurboGrafx-CD as a platform of its own. The
2026-10-20 research ranked it second: 27 owned discs, all CHD, ten in his genres (Rondo of Blood, the Ys
games, Dungeon Explorer II), on the core slot already ships for HuCards. NEC released the CD-ROM² in Japan
on 4 December 1988 ([Wikipedia, "TurboGrafx-16"](https://en.wikipedia.org/wiki/TurboGrafx-16), section
"CD-ROM² / TurboGrafx-CD": "released in Japan on December 4, 1988"; the "TurboGrafx-CD" article only
redirects there; read 2026-10-21).

What Beetle PCE Fast does with a disc at the pin `3f946f2` (read in `libretro.c` and `Makefile.common`,
pinned by `pcecd_core.rs`):

- **Formats.** `MEDNAFEN_CORE_EXTENSIONS` is `pce|cue|ccd|chd|toc|m3u`; a `.cue`, `.ccd`, `.chd`, `.toc`
  or `.m3u` goes to `MDFNI_LoadCD`. CHD needs `HAVE_CHD`, which ADR 0091 turned off. The makefile's own
  default is `HAVE_CHD = 1`; only the Xbox target sets 0.
- **BIOS.** `LoadCD` opens the System Card named by `pce_fast_cdbios` in the system directory (`BIOS/`):
  "System Card 3" is `syscard3.pce`, the core's default. Without it the load fails ("Firmware not
  found"). `HuCLoadCD` skips a 512-byte copier header when the size has the 0x200 bit set, copies at most
  256 KB, and maps it over banks 0 to 0x3F like a HuCard.
- **Discs.** An `.m3u` opens every disc it names, but `LoadCD` mounts only the first and the core
  registers no libretro disk-control interface (no `SET_DISK_CONTROL_INTERFACE` in the tree), so a
  second disc can never be inserted.
- **Saves.** `RETRO_MEMORY_SAVE_RAM` is the same 2 KB backup RAM a HuCard gets, formatted `HUBM` at load,
  so a CD game's saves are an ordinary `.sav`.
- **Arcade Card.** `mednafen/settings.c` answers `pce_fast.arcadecard` with 1, so the Arcade Card's 2 MB is
  always there for an Arcade CD-ROM² disc (Garou Densetsu Special).
- **Reading.** `CDAccess_CHD.c` decodes one hunk at a time in the emulation thread when a sector of a new
  hunk is read (`chd_read`), and caches that one hunk.

BIOS: libretro-database `dat/System.dat`, comment "NEC - PC Engine - TurboGrafx 16 - SuperGrafx", row
`syscard3.pce size 262144 crc 6D9A73EF md5 38179df8f4ac870017db21ebcbf53114` (fetched 2026-10-21). The
maintainer's `Bios/RetroPieBIOS-master/BIOS/syscard3.pce` in the unified backup has that md5; the top-level
`Bios/syscard3.pce` is the same card with a 512-byte header (262,656 bytes, body crc 6d9a73ef).

## Decision

- The PC Engine CD is in scope as Phase 21. One shelf `Games/PCECD` for `.cue`, `.chd` and `.ccd`. The
  platform is `Platform::Pcecd`, appended to `SHELVES` after the SuperGrafx. **No new core**: it runs on
  `Core::MednafenPceFast`, which now runs the TurboGrafx-16 and the PC Engine CD. `Core::EVERY`, `SLOT_PIN`
  and the zip's core list are unchanged. No picker. The TurboGrafx-16 shelf stays `.pce` only.
- **Core build: `HAVE_CHD=1`.** `cores/mednafen_pce_fast/build.sh` sets `HAVE_CDROM=0 HAVE_CHD=1`.
  libchdr, the LZMA SDK files, the zstd decoder, six zlib inflate files and dr_flac are linked in; their
  notices are copied verbatim into `licenses/mednafen_pce_fast-chd-notices.txt` (LICENSING.md). The device
  build still needs only `libc.so.6` and `libm.so.6` at GLIBC_2.17 (`task core:device:mednafen_pce_fast`,
  2026-10-21); the `.so` is 4,524,656 bytes. The macOS build needs `-Dfdopen=fdopen`: zlib 1.2.11's
  `zutil.h` takes the SDK's `TARGET_OS_MAC` for classic Mac OS and defines `fdopen` to `NULL`, which breaks
  `stdio.h`. That goes through a new optional `host_cflags` in `cores/lib.sh`, in the host stamp only, so no
  other core's stamp changes. `pcecd_core.rs` fails if the binary loses the CHD reader (it looks for the
  `chd_load` log line), since CI cannot make a CHD. The TurboGrafx-16 binary is the same file, so it gains
  the reader too; no HuCard path reaches it.
- **Options.** The Beetle PCE Fast list gains `pce_fast_cdbios` "System Card 3" (so the file slot checks
  is the file the core opens) and `pce_fast_cdimagecache` disabled (a disc is streamed, never loaded whole
  into the device's RAM). Both are declared values at the pin. CD speed (1x), the ADPCM, CD-DA and PSG
  volumes (100) and the ADPCM filter stay at the core's own defaults. The list is per core, so the
  TurboGrafx-16 answers them too; a HuCard never reads them.
- **BIOS: never shipped, never fetched.** Before a disc starts slot checks `BIOS/syscard3.pce`. It skips a
  512-byte header by the core's rule (size with the 0x200 bit set), then wants 262,144 bytes with crc32
  `0x6d9a73ef`. Missing or another size: refuse with "PC Engine CD needs BIOS/syscard3.pce" (the Lynx and
  Disk System shape). Another 256 KB card: launch, toast "syscard3.pce is not the known dump" once a
  session. A disc resumed at boot is checked the same way. The check is crc32 with
  `slot_store::lynx::crc32`, as for the Disk System; the md5 is cited above. A headered copy of the right
  card is known, because the core boots it the same; refusing it, or calling it unknown, would be wrong.
- **Policy: the TurboGrafx-16's.** B is II, A is I, START is Run, SELECT after the chord hold (so Select and
  Run stay the soft reset), X and Y feed slot's turbo (`turbo_on_xy`), L1 and R1 stay slot's picture
  keys, L2 and R2 rewind and fast-forward. 360x240 canvas, 8 lines of overscan off the top and bottom.
- **States and rewind on.** A CD state carries the CD drive, the ADPCM RAM and the Super System Card RAM:
  415,222 bytes with a generated disc (`pcecd_core.rs`), against the PlayStation's 4.4 MB that turned
  rewind off there (ADR 0066). The rewind ring stores XOR deltas, so the 20 MB budget holds many
  seconds; the device gate measures it in play.
- **Saves: the ordinary `.sav`.** `Saves/PCECD/<stem>.sav`, the 2 KB backup RAM, written for every disc.
- **No multi-disc.** `.m3u` is not scanned and `swaps_discs` stays false: the core cannot insert a second
  disc (above), and none of the maintainer's discs needs one. A disc set would need a disk-control
  interface in the core first; this ADR is amended then.
- **Screen section** after the SuperGrafx: Shader (the retro list, `Config/pcecd_shader.txt`) and Picture
  (Crop by default, then Stretch, Actual, 4:3; `pcecd` in `Config/picture.txt`), the SuperGrafx's rows.
  No PAL Speed: every disc is NTSC.
- **Release order.** `RELEASED` gets `(Platform::Pcecd, 1988, 12, 4)`, between the Mega Drive and the Game
  Boy (ADR 0100 lists it).
- **Shelf object: the CD jewel case.** PC Engine CDs came in the standard three-piece jewel case the
  PlayStation shelf already draws (ADR 0069), so a disc is drawn in that case at the same fidelity, with
  its front cover in the well, and the disc with its printed label slides out of the case into the slot.
  A disc tagged `(Japan)` wears the paper spine strip, which Japanese releases fold over the left side of
  CDs and video games ([Wikipedia, "Obi (publishing)"](https://en.wikipedia.org/wiki/Obi_(publishing)),
  read 2026-10-21); every other disc the plain case. The region comes from the name tags only (no
  SYSTEM.CNF on a PC Engine disc). The values and what was not found are in
  [docs/cart-art/PCECD.md](../cart-art/PCECD.md).
- **Labels.** `tools/fetch-labels.py` system `PCECD`, the PlayStation route: the front cover (`box-2D`) to
  `Labels/PCECD/<stem>.png` and the disc scan (`support-2D`) to `Labels/PCECD/disc/<stem>.png`, from one
  jeuInfos call under ScreenScraper id 114 (Skyscraper `platforms_idmap.csv` at c253bfe, row
  `pcenginecd,114,45,4955`). The Redump dat (libretro-database `metadat/redump`, "NEC - PC Engine CD -
  TurboGrafx-CD") lists only each disc's data track, which a CHD does not expose, so the tool loads no dat;
  the library work below checked every disc against it instead. libretro-thumbnails has no Named_Logos for
  it (404, 2026-10-21), so the logo fallback takes the ScreenScraper wheel.
- **Expansion Card.** Discs are large (281 MB for Rondo of Blood), so `Games/PCECD` is planned on the
  Expansion Card: `Games/PCECD` on `/mnt/expansion` and the line `PCECD` in `Config/expansion.txt`
  (ADR 0098). No code change: the bind mount makes it `Games/PCECD`.
- **Upstream test sites**, by the standing rule: (b) gains `| Platform::Pcecd` after `| Platform::Sgx`,
  (g) gains `, "PC Engine CD"` after `"SuperGrafx"`, (h) gains `, QuickRow::ScreenPcecd` after
  `QuickRow::ScreenSgx`. (e) is unchanged: no new core.

## The maintainer's discs

`docs/rom-library/best-copy/pcecd-adds.tsv` (workspace) lists one best copy per game, 27 in his genre order:
USA first, then the Japanese release (none of his Japanese discs has an English translation besides Ys IV,
which is the translated image). Each was repacked with `chdman createcd -c cdlz,cdzl,cdfl -hs 489600`, the
PlayStation settings, its data SHA1 (`chdman info`) checked equal to the source, and each disc's data track
SHA1 matched against the Redump dat. Names drop Redump's ring codes (`(FABT, FACT)`); Ys IV is `(Japan)
(En)`. Rondo of Blood had two copies with different data; the one whose data track matches Redump is kept.

## Consequences

- Four patches, 0135 to 0138. No GBA, GB or GBC path changes, so the harness compare stays at 0 diffs.
- **CI cannot boot a real disc.** The core tests use a generated cue and bin and a 256 KB placeholder card
  (the TurboGrafx-16 paint program padded), under which the core loads the disc, maps the card, paints,
  saves and serializes. A real card and disc are read from `SLOT_PCECD_BIOS` and `SLOT_PCECD_DISC`, and the
  tests print a skip without them.
- **The CHD hunk size is a device question.** At `-hs 489600` a hunk is 200 sectors, so CD audio at 1x
  asks for a new hunk about every 2.7 seconds, decoded in the emulation thread. The PlayStation proof was a
  different core's reader. The device gate listens for a periodic tick in Ys Book I and II and the Rondo
  of Blood intro; the originals are untouched, so restaging at chdman's default hunk is cheap if it ticks.
- Known gaps: no multi-disc; Games Express discs (unlicensed, they need `gexpress.pce`) are not handled;
  the System Card 3.0 is the only card slot checks.
- On a Beetle PCE Fast pin bump, re-check that the core still loads CHD, still reads `pce_fast_cdbios`,
  still skips the copier header by the 0x200 bit, and whether it gained a disk-control interface
  (`pcecd_core.rs`).
