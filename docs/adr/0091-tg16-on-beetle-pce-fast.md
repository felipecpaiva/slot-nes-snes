# 0091. Bring TurboGrafx-16 and PC Engine HuCards into scope on pinned Beetle PCE Fast, built the NES and SNES way

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [TG16 plan](../research/tg16-plan.md), [fork review](../research/fork-review-2026-10-18.md) item 17, [nelynes survey](../research/fork-nelynes.md) section 4, [ADR 0050](0050-canvas-per-core-and-platform.md), [ADR 0053](0058-genesis-plus-gx-for-sega.md), [ADR 0059](0064-need-fullpath-load.md), [ADR 0063](0068-ps1-in-scope-on-pcsx-rearmed.md), [issue 81](../../.github/issues/81-tg16-tracking.md), [issue 82](../../.github/issues/82-tg16-core-build.md), patch `patches/0052-tg16-core-tests.patch`

## Context

The 2026-10-18 fork review approved TurboGrafx-16 / PC Engine HuCards (item 17). The common
256x240 picture at 2x is 512x480, which fills the height of the 480-line panel, and the SNES
360x240 canvas already holds every HuCard width: 256, 320, 336 and 352 fit at 1x, and 512 wide is
halved by the 2:1 blend that `copy_centred` gives any frame wider than the canvas (patch 0006, not
keyed to a core). No BIOS is needed for HuCards. nelynes/slotPlus (`slotPlusUltra`,
[92b7022](https://github.com/nelynes/slotPlus/commit/92b7022)) and cloudwithax/unslot
([00296a5](https://github.com/cloudwithax/unslot/commit/00296a5)) both run it on
libretro/beetle-pce-fast-libretro. nelynes edits `Host`, upstream tests and `Platform::ALL`, which
ADRs 0009, 0013 and 0015 forbid, so we reimplement and credit.

The libretro PC Engine cores:

- **Beetle PCE Fast** (`mednafen_pce_fast`): Mednafen's speed-tuned pce_fast, plain C,
  GPL-2.0-or-later. HuCards and CD; no SuperGrafx. Both forks use it.
- **Beetle PCE** (`mednafen_pce`): the accurate Mednafen module, with SuperGrafx. Heavier, and
  nothing in our scope needs the accuracy.
- **Beetle SuperGrafx**: SuperGrafx only matters for 5 HuCards. Out of scope.
- **Geargrafx** (drhelius): newer, GPL-3.0. Not built or measured, and no slot fork runs it.

## Decision

- TG16 is in scope as Phase 10, one shelf `Games/TG16` for `.pce`. The platform is
  `Platform::Tg16`, appended to `SHELVES`; the core is `Core::MednafenPceFast`, appended to `EVERY`.
  Upstream's `ALL` stays untouched and every policy method is answered explicitly, as for PS1
  (ADR 0063) and NGP.
- **HuCards only.** CD-ROM², Super CD-ROM², Arcade CD (`.cue`, `.ccd`, `.chd`, `.toc`, `.m3u`, all
  in the core's extension list) and SuperGrafx (`.sgx`) are out of scope. The shelf scans `.pce`
  alone, so no system card BIOS is asked for.
- Core: libretro/beetle-pce-fast-libretro, pinned at `3f946f277aef3aa99a95551618bbcd1dd2bda0d9`
  (its HEAD on 2026-10-18, the commit nelynes pins). Archive sha256
  `1bc1d96f2a0957e97d50c009d25ae5725d60e80eada679dafbb214afa84cda29`, checked against GitHub by
  `build.sh fetch` and equal to the fork review's download.
  - It builds through `cores/lib.sh` with the root `Makefile`: `platform=unix` and
    `-mcpu=cortex-a53` on the device, `platform=osx` on the host.
  - `make_args="HAVE_CDROM=0 HAVE_CHD=0"`. The unix platform turns on physical CD drive access on
    Linux; we turn it off, the pcsx_rearmed `HAVE_PHYSICAL_CDROM=0` precedent. `HAVE_CHD=0` leaves
    libchdr, lzma, zstd and zlib out of the binary because CD images are out of scope. The core
    still builds its `.cue` and `.ccd` reader and the Tremor decoder; neither is reachable from a
    `.pce` shelf.
  - The makefile links with `$(CXX)` and adds `-lrt`, though every compiled file is C. The device
    build links `-static-libstdc++ -static-libgcc -Wl,--as-needed`, so NEEDED is `libc.so.6` and
    `libm.so.6` only.
  - `psg.c` calls `powf`, and glibc 2.27 gave `powf` a new default symbol version. Built in
    rust:1-bullseye (glibc 2.31), the core needed `GLIBC_2.27`, and `needs_old_glibc_only` failed.
    `cores/mednafen_pce_fast/glibc-2.17.h`, force-included into every device compile through a new
    optional `device_include` variable in `cores/lib.sh`, binds `powf@GLIBC_2.17`. That is the same
    function without the old SVID error handling. No core before this one needed it, and other cores'
    stamps do not change.
  - The output is `mednafen_pce_fast_libretro.<ext>`, so the core name is `mednafen_pce_fast` in
    `SLOT_PIN` keys, in `vendor/` and in `Core::as_str()`. The option prefix is `pce_fast_`.
- One core, no picker, the same rule as Genesis Plus GX, pcsx_rearmed and Beetle NeoPop.
- Licence: we treat the combined core as GPL-3.0-or-later. The counts, the headerless list and the
  permissive parts are in LICENSING.md. No file is GPL-2.0-only. The licence files (`COPYING`
  verbatim, and Tremor's Xiph BSD `COPYING`, which the binary must carry) stay in
  `cores/mednafen_pce_fast/` until the core ships with the platform patch. They stay there because
  `scripts/dist-device.sh` copies all of `licenses/` into the release (the Genesis Plus GX
  precedent, ADR 0053).
- The core facts the platform steps build on are pinned by `tg16_core.rs`, each with a test that
  fails when the behaviour breaks:
  - It boots with no BIOS and loads by path (`need_fullpath`, ADR 0059).
  - It runs at 59.82 fps and 44100 Hz. That is inside ADR 0071's 2 fps window, so there is no
    pacing work and no PAL Speed row.
  - It draws 256x240 on the 360x240 canvas, but only when the frontend answers
    `pce_fast_initial_scanline` and `pce_fast_last_scanline`. Unanswered, it starts at lines 0 to
    242. Its 243 lines do not fit and are halved to 121 rows. Issue 84 answers them.
  - It hands every game its 2 KB backup RAM as save RAM, formatted with the `HUBM` header, so
    slot will write a 2 KB `.sav` for every HuCard (issue 86).
- Credit: the build recipe and the synthetic HuCard come from nelynes/slotPlus (92b7022). unslot
  (00296a5) uses the same HuCard recipe. Both are credited in the patch commit and in LICENSING.md.

## Consequences

- About 8 patches (issues 82 to 90). TG16 work does not touch GBA, GB or GBC, so the GBA harness
  compare stays at 0 diffs.
- The video path is the SNES one: no new canvas code. The scanline options are the one thing
  that must not be dropped, and the unanswered-options test guards it.
- The core is in `task core:host`, `task core:device`, `task check` and `SLOT_REQUIRE_CORES`
  from now on. It joins `dist:device` and `zip-check.sh` only with the platform patch (issue 83),
  so no release ships an unused core. This is the issue 57 rule.
- `cores/lib.sh` grows `device_include`. On a rebase or a pin bump, check whether the bullseye
  image still re-versions `powf`, and whether the new pin calls other re-versioned libm functions:
  `exp`, `exp2`, `log`, `log2` and `pow` moved to GLIBC_2.29, and `expf`, `exp2f`, `logf`,
  `log2f` and `powf` to GLIBC_2.27. `task core:device:mednafen_pce_fast` fails if one appears.

## Integration on main-1b20432 (2026-10-19)

Patches 0057 to 0063 put the platform on the base of ADR 0083. The decisions the plan left open, and
the places where the base changed what the plan assumed:

- **Picture.** Crop is offered and is the factory default, the NES and SNES choice (ADR 0062), so the
  Picture row walks Crop, Stretch, Actual. Crop takes 8 lines off the top and bottom
  (`Platform::Tg16.overscan() == (0, 8)`, 256x240 to 256x224, the SNES amount). The source for the
  edges: standalone Mednafen hides some by default too (`pce_fast.slstart` 4 and `pce_fast.slend`
  235 of 0 to 239, 232 lines; mednafen.github.io/documentation/pce_fast.html, checked 2026-10-19), and
  the NESdev figures of ADR 0062 put a CRT's visible picture near 224 lines. Stretch follows the frame width (the Mega Drive rule, ADR 0052), so a
  352-wide screen fills the panel. Changing the default to Actual is one token in
  `platform_video::default_video_mode`; the user's choice in the row always wins
  (`Config/picture.txt`).
- **Options.** `pce_fast_frameskip` is not set to `disabled` as issue 84 listed: slot already
  answers every core's `<prefix>_frameskip` with `auto`, which skips only the frames slot does not
  show during fast-forward (`set_frame_skip`), never a frame in normal play. Every other key of issue
  84 is answered as listed, with `pce_fast_disable_softreset=disabled`.
- **Soft reset.** Select+Run stays the console's soft reset (issue 87's recommendation). SELECT
  reaches the game only after slot's chord hold, so the reset is always deliberate.
- **Saves.** Every HuCard keeps a 2 KB header-only `.sav` (issue 86's recommendation); no TG16-only
  rule. `save_ram_trusted` accepts it: the buffer is not blank.
- **Turbo.** The plan put turbo I and II on X and Y "as on Game Gear". On main-1b20432 upstream's
  `Pad::mask` never sets X or Y, so Game Gear and NES turbo went quiet in the rebase (ADR 0083). TG16
  gets the plan's turbo through one new policy, `Platform::turbo_on_xy()` (TG16 only), which lets
  `raw_buttons.rs` hand X and Y to the emulator; slot's existing `ButtonMask::turbo` then pulses I and
  II, and the Turbo Buttons row turns it off. The core's own turbo stays off. Game Gear and NES are
  unchanged; giving them the same seam is a separate decision.
- **Cart art.** One HuCard shell, the Sega Card's size (both are credit cards), white, with gold
  contacts painted like the PS1 obi strip. libretro-thumbnails has no `Named_Logos` for
  `NEC - PC Engine - TurboGrafx 16` (checked 2026-10-19, 404), so the Logo Only fallback uses the
  ScreenScraper wheel alone.
