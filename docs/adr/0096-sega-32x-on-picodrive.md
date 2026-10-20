# 0096. Bring Sega 32X into scope on pinned PicoDrive, a shelf of its own beside an unchanged Mega Drive

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-20
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0053](0058-genesis-plus-gx-for-sega.md) (Genesis Plus GX, the non-commercial precedent next to snes9x), [ADR 0059](0064-need-fullpath-load.md), [ADR 0071](0071-pace-off-panel-cores-at-their-own-fps.md), [ADR 0091](0091-tg16-on-beetle-pce-fast.md) (the static build and glibc symbol precedent), [issue 143](../../.github/issues/143-s32x-tracking.md), patches `0090-s32x-core-tests` to `0097-s32x-carts`

## Context

The maintainer asked for Sega 32X as a full platform. 28 of the games on the device's Mega Drive
shelf are 32X games: Genesis Plus GX, the Mega Drive core (ADR 0053), has no 32X, so they do not run
there. The 32X is the heaviest system slot would carry: two SH-2 CPUs at 23 MHz beside the 68000,
the Z80, the Mega Drive VDP and the 32X frame buffers.

The libretro 32X cores:

- **PicoDrive** (libretro/picodrive). notaz's and irixxxx's Mega Drive, Sega CD and 32X emulator,
  with an SH-2 dynarec that has an aarch64 back end (`cpu/drc/emit_arm64.c`). It is what RetroArch,
  RetroPie and the handheld frontends run for 32X on ARM.
- **Genesis Plus GX** has no 32X. **Ares** and **BlastEm** have no usable 32X for this device.

## Decision

- 32X is in scope as Phase 15 (Sega CD and Atari 2600/7800 groundwork, not yet merged, hold 13 and
  14, and ADRs 0094 and 0095 and issues 113 to 142 on their local branches, so this ADR is 0096 and
  the issues start at 143). One shelf `Games/32X`. The platform is `Platform::S32x`, appended to
  `SHELVES`; the core is `Core::Picodrive`, appended to `EVERY`. Upstream's `ALL` stays untouched and
  every policy method answers 32X explicitly, the same as Mega Drive. One core and no picker.
- **Core pin.** libretro/picodrive `1890c2932234c9d30f4cd3851d02228baae8f09e` (its master on
  2026-09-26), archive sha256 `123871ce...d523`. The GitHub archive has no submodules, and the
  libretro build needs three: `emu2413` (compiled by `pico/sound/ym2413.c`), `dr_libs`
  (`platform/common/mp3_drmp3.c`) and `libpicofe` (`platform/libpicofe/plat.h`, included by
  `libretro.c`). Each is pinned in `SLOT_PIN` at the commit the core pins (emu2413 `a2dfc20`,
  dr_libs `dd762b8`, libpicofe `9ed5822`) with its archive sha256, fetched and checked by
  `cores/lib.sh`'s new optional `modules` variable, unpacked into the source, and shipped beside the
  core as `picodrive-<name>-src.tar.gz`. cyclone (ARM32 only) and libchdr (CD images) are not built and
  not shipped. A build from the bare archive plus those three tarballs was the test that they are
  enough. The other eleven cores' stamps and source metas are byte-identical with `modules` in lib.sh.
- **Build.** `make -f Makefile.libretro platform=unix` and `-mcpu=cortex-a53` on the device,
  `platform=osx` on the host, with `use_libchdr=0` (CD images are out of scope, the TG16
  `HAVE_CHD=0` precedent), `PLATFORM_TREMOR=1` and `PLATFORM_ZLIB=1` (otherwise picked from whatever
  headers the builder has), and `GIT_REVISION=-1890c29` (the makefile asks git, which inside `build/`
  finds this repo). On aarch64 the makefile turns on the SH-2 dynarec (`use_sh2drc`, `compiler.o`
  is in the device build); `Makefile.libretro` turns every DRC off on Apple, so the Mac core runs the
  SH-2 interpreter. The sound code calls `log` and `pow`, which glibc 2.29 re-versioned: as for Beetle
  PCE Fast's `powf`, `cores/picodrive/glibc-2.17.h` binds both to `GLIBC_2.17`, and because the makefile
  builds with `-flto`, `-flto-partition=one` keeps the `.symver` lines and the calls in one link
  partition. NEEDED is `libc.so.6` and `libm.so.6`.
- **Licence.** PicoDrive's `COPYING` is the MAME-style non-commercial licence, the same text as
  Genesis Plus GX's: "Redistributions may not be sold, nor may they be used in a commercial product or
  activity", the complete source must ship with a modified build, and the copyright notice must be
  reproduced. It is handled exactly like snes9x and Genesis Plus GX: LICENSING.md names it and its terms,
  `licenses/picodrive-LICENSE.txt` (the file verbatim) ships in `System/licenses/`, the pinned source and
  the three submodule tarballs ship with every release, the plugin boundary stance applies, the zip is
  never sold and never carries a donation or sponsor link, and the notice text names PicoDrive. Of the
  103 sources compiled into the device core none says GPL; 42 carry the MAME licence line, 23 have no
  licence text (`licenses/picodrive-headerless-files.txt`, with the command), and the rest are MIT
  (emu2413, libretro-common), zlib, Xiph BSD (Tremor) and public domain or MIT-0 (dr_mp3). The emu2413
  MIT text and Tremor's BSD text ship as their own licence files.
- **Shelf.** `.32x` and `.bin`. A `.32x` always lists. A `.bin` lists only with a 32X header:
  `SEGA 32X` at 0x100, or the `MARS CHECK MODE` module name at 0x3c0 (`slot_store::s32x`). Either word
  alone is enough: on the maintainer's dumps Star Wars Arcade has `SEGA 32X` and its own name at 0x3c0,
  and FIFA Soccer 96 has `SEGA MEGA DRIVE` and `MARS CHECK MODE`. Every commercial 32X dump in the
  backup (`Roms/sega32x` and its duplicates) carries one or both; the SDK samples carry
  `MARS CHECK MODE`; three `.32x` files carry neither because they are scrambled dumps (BC Racers (W),
  Brutal Unleashed (U), Darxide (E)), and they still list by their extension. None of the 1,385 other
  files on the device's Mega Drive shelf carries either word (each checked through its backup copy by
  CRC). PicoDrive itself needs no header: it starts the 32X when the 68000
  sets ADEN at 0xa15101 (`pico/32x/memory.c`, `PicoWrite8_32x`, at the pin). A `.bin` without either
  word is logged and left off the 32X shelf.
- **Mega Drive is not touched.** Its shelf still lists every `.md`, `.gen` and `.bin`, a 32X game left
  there included, and still starts them on Genesis Plus GX. A Mega Drive game played after a 32X game
  in the same session gets the same input, frame, picture and shader as a Mega Drive only run
  (`s32x_then_md.rs`). GBA, GB and GBC paths are not touched.
- **Options** (`core_options_policy::PICODRIVE`): the six-button pad on port 1 (PicoDrive's libretro map
  is Genesis Plus GX's: Y to A, B to B, A to C, L to X, X to Y, R to Z, Select to Mode), region Auto,
  `picodrive_drc` enabled (declared only on the device build; slot answers it everywhere), the audio
  filter, the sprite limit removal and the 68000 overclock off. The frameskip is `auto` like every
  core that declares one, so frames are skipped only in fast-forward.
- **Speed is the user's choice.** The 32X Screen section has a Renderer row (Accurate, Good, Fast,
  `picodrive_renderer`) and a Sound Rate row (44 kHz, 22 kHz, `picodrive_sound_rate`), kept in
  `Config/s32x.txt`. The factory choice is PicoDrive's own default, Accurate and 44 kHz, never retuned
  for this device; the user's choice becomes the default from the next game. The dynarec is not a row:
  it is the device's only way to run the SH-2s at speed.
- **Screen section**: Shader (the retro list, `Config/s32x_shader.txt`), Picture (the Mega Drive's:
  Stretch by default following the frame width, Actual, 4:3), PAL Speed (Native by default; a PAL cart
  reports 50 fps and ADR 0071 paces it), Renderer, Sound Rate. The canvas is the Mega Drive's 360x240;
  PicoDrive draws 320x224 in the middle of it.
- **Rewind on, run-ahead off.** A PicoDrive state is 679,178 bytes for every Mega Drive cart (its
  `retro_serialize_size` always adds the 32X chunks), about a sixth of a PS1 state, and saving one took
  0.026 ms on the Mac. Rewind stays on, as for Mega Drive, and the Gameplay Rewind row turns it off.
  Run-ahead is gated to mGBA and stays so.
- **Saves.** The ordinary `.sav` in `Saves/32X`. PicoDrive gives every cart 16 KB of save RAM, reported
  before the first frame (when slot loads the `.sav`) and afterwards only once the game wrote a byte,
  so a game that never saves leaves no `.sav`.
- **Cart.** One 32X cart for every region (Sega Retro, "Sega 32X cartridges", checked 2026-10-20:
  "While the dimensions are similar, the shape differs with the 32X and (labels aside) the design is
  consistent across all regions", with no end labels): the Mega Drive size, rounded top corners, a
  top cap, ridged sides, in the Mega Drive black. The yellow 32X band is on the label art.
- **Labels.** `tools/fetch-labels.py` system `32X`: dat `Sega - 32X` (libretro-database
  metadat/no-intro), ScreenScraper id 19 (Skyscraper `platforms_idmap.csv` at ccd49ae, row
  `sega32x,19,21,33`); a name search drops the word 32X. libretro-thumbnails has no `Sega - 32X`
  Named_Logos (404, 2026-10-20).

## Performance

Host only, and only a direction: the Mac core has no SH-2 dynarec, and its CPU is many times the H700's
Cortex-A53. `core_bench` on the maintainer's dumps after 600 idle frames (the attract or title screen),
median ms a frame over 600 frames, 3 repeats:

| Game | Accurate 44 kHz | Accurate 22 kHz | Fast 44 kHz | Fast 22 kHz |
|---|---|---|---|---|
| Virtua Racing Deluxe (E) | 1.05 | 1.06 | 1.05 | 1.07 |
| Star Wars Arcade (JU) | 1.26 | 1.29 | 1.22 | 1.21 |
| Knuckles' Chaotix (JU) | 1.10 | 1.11 | 1.10 | 1.09 |
| Doom (JU) | 1.19 | 1.26 | 1.22 | 1.13 |

On the host the renderer and the sound rate move the cost by less than the run-to-run spread: the
SH-2 interpreter dominates. On the device the SH-2s run on the dynarec, so the 68000 interpreter (FAME),
the renderer and the FM synthesis are a larger share; that is where Fast and 22 kHz can help. We expect
the 2D games (Chaotix, Kolibri, Mortal Kombat II) to hold 60 fps on Accurate and the polygon games
(Virtua Racing Deluxe, Star Wars Arcade, Virtua Fighter) to be the ones near the 16.7 ms budget. The
device gate (issue 152) measures it with `bench:device` and real play; nothing here is a device number.

## Consequences

- Eight patches, 0090 to 0097. No GBA, GB or GBC path changes, so the harness compare stays at 0 diffs.
- Upstream test sites (b), (e), (g) and (h) take one more token each, in order: `| Platform::S32x`,
  `| Core::Picodrive`, `"32X"` and `QuickRow::ScreenS32x`, by the standing rule.
- `cores/lib.sh` grows `modules`. On a pin bump, re-check the submodule commits the new pin records
  (`git submodule status` at the pin) and whether `log` and `pow` are still the only re-versioned libm
  symbols (`task core:device:picodrive` fails otherwise).
- The 28 32X games now on the device's Mega Drive shelf keep failing there until they are moved to
  `Games/32X`; slot does not move them.
