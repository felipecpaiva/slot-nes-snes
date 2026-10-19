# TurboGrafx-16 and PC Engine HuCards on slot-nes-snes: plan (2026-10-18)

"Our tree" means slot v1.7.0 plus patches 0001 to 0057. The integration patches will be written on
the upstream 1.8.0 base once that port lands, so this plan names seams, not line numbers.

- "PCE Fast" means libretro/beetle-pce-fast-libretro at `3f946f2` (ADR 0091).
- The reference is nelynes/slotPlus branch `slotPlusUltra`,
  [92b7022](https://github.com/nelynes/slotPlus/commit/92b7022), for the core, shelf, HuCard art,
  Screen page and tests.
- cloudwithax/unslot [00296a5](https://github.com/cloudwithax/unslot/commit/00296a5) (GPL-3.0) runs
  the same core with the same synthetic HuCard.

We take ideas from both and reimplement them with credit. Nothing is cherry-picked
(docs/research/fork-nelynes.md).

## TL;DR

- **Verdict: go.** It reuses the most of what we already have of any system on the list:
  - 256x240 at 2x is 512x480. That fills the 480-line panel on the SNES 360x240 canvas, with no new
    canvas code;
  - no BIOS for HuCards;
  - a 2-button pad plus Select and Run;
  - 59.82 fps, which is inside ADR 0071's 2 fps window, so no pacing work and no PAL Speed row (the
    system is 60 Hz only).
- **Scope is HuCards.** TurboCD / CD-ROM² (needs a system card BIOS and a CD save model) and
  SuperGrafx (five games, another core) are out of scope, recorded in ADR 0091.
- **Done now (groundwork, this branch):**
  - the core build, pinned for host and device (issue 82);
  - the licence record;
  - host tests with a generated HuCard (`patches/0052-tg16-core-tests.patch`, issue 88). They prove
    no-BIOS boot, the 256x240 picture on the 360x240 canvas, 59.82 fps and sound, states, and the
    backup RAM.
- **Two facts the platform steps must honour, both pinned by tests:**
  - The scanline options must be answered (issue 84). The core starts at lines 0 to 242 and reads
    its declared 3 to 242 only when asked. 243 lines do not fit 240, so `copy_centred` halves the
    picture to 121 rows.
  - Every HuCard gets a 2 KB `.sav` (issue 86). The core exposes its formatted backup RAM as save
    RAM whether or not the game uses it.
- Expected size: 8 patches on the 1.8.0 base, smaller than the Game Gear step, because canvas,
  shaders and the Picture row ride the SNES path.

## 1. What nelynes did (reference only)

| Area | nelynes/slotPlus `slotPlusUltra` | Ours |
|---|---|---|
| Core | beetle-pce-fast `3f946f2`, `platform=unix`, `-mcpu=cortex-a53`, no sha256, default CD and CHD build | Same commit, archive sha256, `HAVE_CDROM=0 HAVE_CHD=0`, static C++ runtime, `--as-needed`, `powf` pinned to GLIBC_2.17, glibc gate (issue 82, done) |
| Enums | `Platform::Tg16` and `Core::Pce` added to upstream's `ALL`; upstream tests edited | `Platform::Tg16` in `SHELVES`, `Core::MednafenPceFast` in `EVERY`, upstream `ALL` and tests untouched (ADR 0091) |
| Shelf | `Games/TG16`, `.pce` | Same |
| Canvas | 720x240 buffer; up to 352 wide at 2x in a 360x240 window; 512 wide across the whole buffer | `Core::canvas(MednafenPceFast, Tg16) = (360, 240)`, the SNES path (ADR 0050); 512 wide halved by `copy_centred` |
| Input | `2 Buttons` pad, II left, I right, Run = Start, Select to the game | Same layout through slot's tables (section 5) |
| Saves | Core save dir `Saves/TG16` | slot's `.sav` path: the core gives save RAM (section 3) |
| Shader | Off, LCD3x, Grid, Dot, inside `slot.state` | Own Screen section, the retro list, setting outside `slot.state` (ADR 0051) |
| Cart | White HuCard, gold contacts, square label, drawn by `assets/src/carts.py` | Retro bitmap HuCard (ADR 0054), their drawing as a credited reference |
| Tests | `pce_core.rs` (spin ROM boots, frame size, state), `tg16_video.rs` | Same HuCard recipe, plus a palette paint, every pixel on the canvas, the options contract and BRAM (patch 0057) |

## 2. Core facts found while building (2026-10-18)

- **Build.** Host `mednafen_pce_fast_libretro.dylib` (arm64, `platform=osx`). Device
  `mednafen_pce_fast_libretro.so`:
  - sha256 `30a4f72253f1b70102f9542303a41a69f83240b9afb608917335f95ba949b69c`;
  - built in rust:1-bullseye `sha256:4730e387...`;
  - all 60 compile lines carry `-mcpu=cortex-a53`;
  - NEEDED is `libc.so.6` and `libm.so.6`, at GLIBC_2.17 or older.
- **The `powf` trap.** The first device build needed `powf@GLIBC_2.27`; `psg.c` calls it for the
  volume table. The build image's glibc 2.31 links the new default version. The fix is a
  force-included header that binds `powf@GLIBC_2.17` (the `device_include` hook in `cores/lib.sh`,
  ADR 0091). No earlier core hit this.
- **Name.** The makefile's `TARGET_NAME` is `mednafen_pce_fast`. So:
  - `Core::as_str()` must be `mednafen_pce_fast`;
  - the option prefix is `pce_fast_`.
- **Loading.** `need_fullpath` is true, so slot loads it by path (ADR 0059, patch 0030). The core
  strips a 512-byte copier header itself (`size & 0x200`) and special-cases Street Fighter II's
  mapper and Populous' cart RAM.
- **Picture.** `video_cb` is RGB565 at a 1024-byte pitch (512 pixels):
  - The width follows the game's VCE dot clock: 256, 320 or 336 to 352 (`pce_fast_hoverscan`,
    default 352), or 512.
  - The height is the scanline window. Declared defaults are 3 to 242, which gives 240 lines. The
    core's own start values, used when the frontend does not answer, are 0 to 242, which gives 243
    lines.
  - The test pins both cases on the 360x240 canvas:
    - answered: 256x240, red in every pixel of x 52 to 307 and y 0 to 239, black bars;
    - unanswered: the picture halved to 121 rows, y 59 to 179.
- **Timing.** 59.82 fps (a constant in `libretro.c`), 44100 Hz. The test pins 59.80 to 59.85 and
  44100.
- **Input.** `pce_fast_default_joypad_type_p1` defaults to `2 Buttons`. The core maps:
  - RetroPad B to II and RetroPad A to I;
  - SELECT to Select and START to Run;
  - X, Y, L, R and L2 to III to VI and Mode for the 6-button pad.

  Select+Run is the console's soft reset. `pce_fast_disable_softreset` (default `disabled`) masks
  the pair. The core has its own turbo, `pce_fast_turbo_toggling` (default `disabled`).
- **Saves.** These facts are proven by `tg16_core.rs`:
  - `retro_get_memory_data(SAVE_RAM)` is the 2 KB backup RAM (BRAM, the CD and Tennokoe memory).
    The core formats it with `HUBM\0\x88\x10\x80` at every load, so it is never blank.
  - `load_save_ram` round-trips it.
  - Populous is the one HuCard with its own battery RAM, 32 KB. The core then exposes that instead
    of BRAM (read in the source, not tested).
  - A state carries BRAM (`SFARRAY(SaveRAM)`).
- **CD code still in the binary.** With `HAVE_CHD=0` the CHD reader and its zlib, lzma and zstd go.
  The `.cue` and `.ccd` image reader and Tremor (CD audio) stay, because the makefile always builds
  them. A `.pce`-only shelf never reaches them.

## 3. Saves (issue 86)

HuCard games mostly keep no saves: passwords, or nothing. A few, mostly Japanese, save to BRAM when
a backup unit (Tennokoe 2, a TurboBooster-Plus or a CD unit) is attached. PCE Fast gives slot that
BRAM as save RAM, so the generic `.sav` path works with no new code:

| Event | What happens |
|---|---|
| Insert | slot loads `Saves/TG16/<stem>.sav` into BRAM if present (`load_save_ram`) |
| Lid, POWER, battery, eject, 60 s autosave | `.sav` written atomically like every core (ADR 0012, 0034, 0072) |
| A game that never saves | A 2 KB `.sav` holding the `HUBM` header and zeros |

Decisions for issue 86:

1. **Accept the 2 KB `.sav` per game** (recommended). It is harmless, is what RetroArch does with
   any save RAM a core exposes, and keeps
   the save path generic. The alternative, skipping a `.sav` that is only the formatted header, is a
   TG16-only rule that `save_ram_trusted` would have to learn. Not worth it unless the maintainer
   wants empty saves gone.
2. Check `save_ram_trusted` treats the header-only buffer as trusted. It is not blank, so the
   zero-buffer guard (ADR 0072) does not fire.
3. Populous: 32 KB `.sav`, same path. A device check, not a code change.
4. **TurboCD is out of scope.** Its BRAM, system card BIOS (`syscard3.pce`) and disc images are a
   separate phase if ever wanted.

## 4. Video and the Screen section (issues 84 and 85)

- Canvas 360x240 through `Core::canvas` (ADR 0050), the SNES path:
  - 256x240 at 2x is 512x480 (Actual, 104-pixel bars).
  - 320 to 352 wide fit at 1x.
  - 512 wide is halved by the 2:1 blend.
  - Stretch fills 720x480 and follows the frame width per game, the Mega Drive precedent (ADR 0052).
- **Options (issue 84):** `pce_fast_initial_scanline=3`, `pce_fast_last_scanline=242` (mandatory,
  see section 2), `pce_fast_hoverscan=352`, `pce_fast_default_joypad_type_p1=2 Buttons`,
  `pce_fast_disable_softreset=disabled` (section 5), `pce_fast_turbo_toggling=disabled`,
  `pce_fast_nospritelimit=disabled`, `pce_fast_ocmultiplier=1`, `pce_fast_frameskip=disabled`.
  Each is answered explicitly with a declared-key test (patch 0003's `core_option_keys.rs`).
- **Own Screen section** `SCREEN_TG16` (the maintainer's rule), with two rows:
  - **Shader**: Off, then the shared retro list (CRT looks; TG16 is a TV system). There is no
    LCD3x, because 2x is not what it is tuned for. Stored in its own `Config/` file (ADR 0051).
  - **Picture**: Actual, Stretch and Crop (ADR 0062; some games leave garbage in the overscan
    edges, as on NES), default in `Config/picture.txt` (ADR 0061). Which default (Crop like
    NES and SNES, or Actual) is the maintainer's call in issue 85.
  - **No PAL Speed row.** TG16 and PC Engine are 60 Hz only, and 59.82 fps is inside ADR 0071's
    window.

## 5. Input (issue 87)

The TurboGrafx pad has II on the left and I on the right, with Select and Run between.

| Device | Game | Note |
|---|---|---|
| B (left) | II | RetroPad B |
| A (right) | I | RetroPad A |
| START | Run | |
| SELECT | Select, after slot's chord hold | as on SNES (upstream c2a27a6) |
| X, Y | Turbo I and Turbo II through slot's turbo | the pad's turbo switches; the core's own turbo stays off |
| L1, R1 | slot's (picture) | `owns_shoulders` true, as Game Gear |

- `pce_fast_disable_softreset=disabled` (recommended), so Select+Run stays the console's soft
  reset. slot has no in-game reset (the power menu's Restart reboots the device), and SELECT
  reaches the game only after the chord hold, so a reset is always deliberate. The other answer,
  `enabled`, masks the pair; it is the maintainer's call in issue 87.
- The 6-button pad is skipped: among HuCards only Street Fighter II' Champion Edition wants it, and
  our X and Y are already turbo. Revisit if asked.

## 6. Shelf, scan, cart art (issues 83 and 89)

- Scan `.pce` onto one `Games/TG16` shelf. `.sgx` and the CD extensions are left out (ADR 0091).
  The title is the file stem: HuCards have no header title.
- Cart: the retro bitmap renderer (ADR 0054), one shape, a white HuCard with gold contacts and a
  square label. nelynes' `carts.py` HuCard (92b7022) is the credited drawing reference. US TurboChip
  vs Japanese HuCard looks are a later nicety.
- Labels: `tools/fetch-labels.py` gets a `TG16` row:
  - folder `pcengine`;
  - extensions `{".pce"}`;
  - dat `NEC - PC Engine - TurboGrafx 16` (libretro-database `metadat/no-intro`, checked 2026-10-18);
  - ScreenScraper id **31**, from Skyscraper's `platforms_idmap.csv` (Gemba/skyscraper
    [ccd49ae](https://github.com/Gemba/skyscraper/blob/ccd49ae/platforms_idmap.csv), row
    `pcengine,31,40,34`; unchanged at master c253bfe).

  The script must CRC the ROM **without a 512-byte copier header** (size % 8192 == 512), as it
  already does for iNES and SMC headers, or headered dumps miss the dat.

## 7. Issue list (Phase 10)

| Issue | Title | Size | Needs the 1.8.0 base |
|---|---|---|---|
| 81 | Tracking: TurboGrafx-16 and PC Engine HuCards on Beetle PCE Fast | L | n/a |
| 82 | Build Beetle PCE Fast from a pinned commit for host and device and record its licence | S | No, done |
| 83 | Add `Platform::Tg16` with its own shelf, scan and explicit policy | M | Yes |
| 84 | Set the TG16 core options, the scanline window first | S | Yes |
| 85 | Give TG16 the 360x240 canvas and its own Screen section with Shader and Picture rows | S | Yes |
| 86 | Keep TG16 backup RAM in `.sav` like every core; TurboCD out of scope | S | Yes |
| 87 | Map the TG16 pad: II, I, Select, Run and turbo | S | Yes |
| 88 | Test TG16 with a generated HuCard | S | Partly: core tests done, platform tests per step |
| 89 | Draw HuCards and fetch their labels | M | Yes |
| 90 | TG16 device gate on the RG34XXSP | S | Yes |

## 8. Device gate (issue 90)

1. Play Bonk's Adventure, R-Type, Air Zonk and Blazing Lazers for 10 minutes each under
   `SLOT_TRACE`: full speed, zero audio underruns, and the ms a frame recorded (estimate 1.5 to
   3 ms, unmeasured).
2. Width modes: a game that switches to a wider dot clock (find one under `SLOT_TRACE` before the
   gate, the trace logs the frame width), and a 512-wide screen if one is found. The 2:1 blend must
   look right, and Stretch must follow the width.
3. A BRAM save (a HuCard that saves to backup RAM, or Populous): save, close the lid, pull the
   battery, boot. The save is there.
4. Eject and GBA: the GBA leg equals a GBA-only run.

## 9. What remains for the integration step (done on main-1b20432, 2026-10-19; see ADR 0091)

Issues 83 to 87 and 89 to 90, plus the platform half of 88, in that order. When the platform patch
lands:

- the three licence files moved from `cores/mednafen_pce_fast/` to `licenses/` (done, patch 0058);
- the core joins `scripts/dist-device.sh` and `scripts/zip-check.sh`: the cores list, the `req` and
  `ok` lists, the licence file list, and the strings cross-check pair. The pinned `.so` contains
  `Beetle PCE Fast` (its library name), so the pair is `mednafen_pce_fast:Beetle.PCE.Fast`;
- `zip-check.sh` gains `TG16` in its `games` list;
- the README row changes from "planned, not shipped".

Merge notes: NGP's groundwork (branch `ngp-groundwork`) also adds itself to `SLOT_PIN`,
`taskfile.yml`, the `SLOT_REQUIRE_CORES` line in `scripts/run-tests.sh`, LICENSING.md, the
INDEX and PLAN.md. Those are textual conflicts, kept as one line per core. This branch also
changes `cores/lib.sh` (the optional `device_include`), which NGP does not; any other core
branch that edits `lib.sh` must keep it, and the device stamp gains a `device_include=` line only
for cores that set it. The patch numbers (0057 onward),
ADR 0091, issues 81 to 90 and Phase 10 may be renumbered at merge (the Lynx and WonderSwan
groundwork may claim the same numbers).
