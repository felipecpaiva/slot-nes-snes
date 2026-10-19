# 0093. Bring Atari Lynx into scope on pinned Beetle Lynx, with a BIOS check, our own rotation and pacing from the game's real frame rate

- Status: Accepted. Beetle Lynx is the core; Handy is rejected for now because `lynx/lynxdec.cpp` has no licence (maintainer, 2026-10-19). Integrated on slot main 1b20432 as patches 0070 to 0079; the device gate (issue 112) is pending. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-18, integration 2026-10-19
- Deciders: maintainer (Felipe Paiva)
- Related: [Lynx plan](../research/lynx-plan.md), [nelynes survey](../research/fork-nelynes.md) section 3, [ADR 0071](0076-pace-off-panel-cores-at-their-own-fps.md) (pacing), [ADR 0083](0088-rebase-to-slot-main-1b20432.md) (the base it lands on), [issue 101](../../.github/issues/101-lynx-tracking.md), [issue 102](../../.github/issues/102-lynx-core-build.md), patch `patches/0065-lynx-core-tests.patch`

## Context

The 2026-10-18 fork review put Atari Lynx last on the new-system list: small library, the smallest
picture, a BIOS we cannot ship, rotated carts, and a frame rate that is not 60. nelynes/slotPlus
(`main`, 749523c, d7d0e74, 185257a) runs it on libretro/beetle-lynx-libretro. We reimplement and
credit.

What the core does at `fcdefcf` (read in the source and pinned by `lynx_core.rs`):

- **No BIOS, no boot, no error.** `CRom` fills the 512-byte boot ROM with 0x88 when `lynxboot.img`
  is missing or shorter than 512 bytes, and returns. A `.lnx` cart then loads without error, no
  display frame ever ends, every `retro_run` stops at the 700000-cycle cap (43.75 ms), and the
  picture is the core's undrawn fill, `MAKECOLOR(30, 30, 30)`. There is no high-level boot for carts.
  Only BS93 homebrew (`.o`) skips the boot ROM: it is copied into RAM and started directly.
- **The reported 75 fps is not the game's rate.** `retro_get_system_av_info` returns a constant 75.0
  (60.0 with `lynx_force_60hz`), but `retro_run` emulates exactly one Lynx display frame, whose
  length the game programs. The boot ROM leaves the timers at 59.9 Hz (159 us a line, 105 lines): a
  synthetic cart booted through the real boot ROM gives 736 sample frames per run at 44.1 kHz. A
  game that sets 75 Hz gives 588. So the fork review's line "`lynx_force_60hz` slows games 20%" is
  true only for a 75 Hz game; for a game left at the boot ROM's rate it is the one correct number,
  and pacing from the reported 75 runs that game 25% fast.
- **The core does turn the pad.** `lynx.rotateinput` is hard-wired to 0 in mednafen's settings, but
  the libretro glue remaps the pad itself (`update_input`, `map[rotate_screen]`) whenever
  `lynx_rot_screen` turns the screen, and calls `SET_ROTATION` and `SET_GEOMETRY` (aspect swapped).
  Its declared default is `auto`: LEFT carts turn 90, RIGHT carts 270. slot today answers no
  `GET_VARIABLE` for an unset key, so nothing turns; any change that starts answering declared
  defaults would turn the pad over an unturned picture.
- **Rotation source.** The LNX header byte 0x3a (1 left, 2 right) is overridden by the core's own
  87-entry checksum list when the headerless body matches. Seven entries are rotated: Centipede
  proto, Lexis, NFL Football and Raiden beta left; two Gauntlet III dumps and Klax (USA, Europe)
  right.
- **Saves.** Only `SYSTEM_RAM` (64 KB) is exposed. There is no EEPROM emulation at this pin (one
  comment in `mikie.cpp`). States carry everything.
- **Files.** `.lnx` (64-byte header: title 0x0a, 32 bytes; rotation 0x3a) and headerless `.lyx`,
  which loads only at exactly 128, 256 or 512 KB; any other size goes "illegal" and also fails
  silently.

Other cores, checked in source on 2026-10-18:

| Core | Boot without BIOS | Saves | Rate | Licence | Notes |
|---|---|---|---|---|---|
| **Beetle Lynx** (libretro/beetle-lynx-libretro `fcdefcf`) | No (BS93 homebrew only) | States only | One game frame per run, reports 75 | GPL-2.0 `COPYING`; 9 or-later files, 20 zlib Handy files, 20 headerless | nelynes runs it. Built and tested here |
| **Handy** (libretro/libretro-handy `bc55d46`) | **Yes**: an HLE boot (`HLE_BIOS_FE19`/`FE4A`, `lynxdec.cpp`) when the BIOS is missing or its CRC is wrong. A throwaway local probe booted our synthetic cart with no BIOS and drew it | **EEPROM** (93C46 family) to `<save dir>/<name>.eeprom`, written only at `retro_reset` and `retro_deinit` | Fixed cycles per run (`handy_refresh_rate`, declared default 60; 75 if unanswered), frames between video events dropped | **No top-level licence file.** `lynx/license.txt` and the Handy files are zlib; `lynxdec.cpp` (the HLE decrypt, always compiled) has no licence at all and credits a forum post | Rotates in software itself (`handy_rot`) |
| Gearlynx (drhelius) | No: the libretro port refuses a BIOS that is not 512 bytes | EEPROM | | GPL-3.0 | No slot fork runs it |
| Holani (LLeny/holani-retro, Rust) | Not established | | | GPL-3.0 | No slot fork runs it |

No free replacement boot ROM was found. Handy's HLE is an emulation of the boot (decrypt and
jump), not a ROM image. The encrypted loader the tests use is cart-side code from cc65 (zlib), not
a BIOS.

## Decision

- Lynx is in scope as Phase 12, one shelf `Games/Lynx` for `.lnx` and `.lyx`. `Platform::Lynx` is
  appended to `SHELVES` and `Core::MednafenLynx` to `EVERY`, upstream's `ALL` untouched, every policy
  method answered explicitly (the PS1 shape).
- **Core: libretro/beetle-lynx-libretro, pinned at `fcdefcfb3c11d6d2e71be076a5d3df2e88ab73ed`** (its
  HEAD on 2026-10-18 and nelynes' pin). Archive sha256
  `3dd45a6f6585c444a415cb097996c572467754748e7163eca466d89b31bd8b37`, checked by `build.sh fetch`.
  Root `Makefile`, `platform=unix -mcpu=cortex-a53` on the device, `platform=osx` on the host,
  `-static-libstdc++ -static-libgcc`; the device `.so` needs only glibc at 2.17 or older and
  `task core:device:mednafen_lynx` fails otherwise. Output `mednafen_lynx_libretro.<ext>`, so the
  core name is `mednafen_lynx` and the option prefix `lynx`.
  - **Handy, rejected for now:** it would remove the black-screen failure (HLE boot) and give EEPROM
    saves, but it builds an unlicensed source file (`lynx/lynxdec.cpp`), writes its EEPROM only on
    unload, and no slot fork runs it. Revisit if `lynxdec.cpp` gains a licence; issues 102, 104, 107
    and 108 say what would change.
- **BIOS: never shipped, never downloaded.** Before launch slot checks `BIOS/lynxboot.img`: present,
  512 bytes, crc32 `0x0d973c9d` (the `[BIOS] Atari Lynx` entry in the core's own list). Missing or
  short: refuse to launch and toast where to put it. Wrong checksum: launch, toast once (a modified
  boot ROM may be deliberate). BS93 `.o` files are not on the shelf, so they need no exception.
- **Rotation is ours, through the core's own pad turn.** slot always sets `lynx_rot_screen`, never
  leaves it to the declared `auto`: `0` (raw picture, raw pad) for upright and left carts, `180`
  for right carts, with slot drawing that frame flipped (a reversed row copy, or answering
  `SET_ROTATION` 2 as a flip). The player turns the handheld one way for every turned cart. Which
  cart is turned comes from `Config/lynx_rotation.txt` (wins), then nelynes' by-title list (d7d0e74,
  matched on the stem or the header title), then header byte 0x3a. The core's own checksum list is
  not read: its right-turned entries (Klax, two Gauntlet III dumps) are all on the title list, and a
  left cart is drawn as made anyway. The upright tall view (`90`/`270`, full host rotation) is
  deferred. The choice of flip direction is a device check.
  - As built (patch 0077): slot answers `SET_ROTATION` 0 and 2 (a reversed copy of the canvas, the
    picture sits symmetrically in it) and refuses quarter turns. The Screen row is **Flip Right
    Carts** (On by default, `Config/lynx_flip.txt`, `right = on|off`); Off sets `0` for every cart.
    Only a Lynx session answers `SET_ROTATION`; every other core is still refused it, because Beetle
    Cygne turns a vertical WonderSwan game itself only when the frontend says no (found when the
    two platforms were stacked, 2026-10-19).
- **Pacing follows the game's real frame rate, not the reported 75.** The Lynx Screen section gets a
  **Lynx Speed** row: **Native** (default) paces each game at the rate its frames carry (sample frames
  per run over the sample rate, smoothed), through ADR 0071's owed-frames path, which already runs 1 or
  2 frames a tick above 60; **Panel** runs one frame per vsync with the sound resampled from what each
  frame carried (a 75 Hz game then plays at 80%). `lynx_force_60hz` stays disabled: it changes only
  the reported number. Native is the default for the same reason as ADR 0071: it is the content's
  own speed on any panel. A 59.9 Hz game is inside ADR 0071's 2 fps window either way.
  - As built (patch 0075): the emu measures only for a core that does not report its own rate
    (`Core::reports_its_frame_rate`, false for Beetle Lynx alone), over windows of 20 frames, and
    takes a rate once two windows in a row agree within 0.5 fps and it moved more than 0.1 fps; a
    window outside 50 to 80 fps or a frame with no sound is ignored. Until the first measure the game
    runs one frame a tick at the core's own sample rate. The row is stored as `lynx` in
    `Config/pal_speed.txt`, beside the PAL Speed rows.
  - Measured on the host with the real boot ROM over 20 seconds of each of the 88 carts of the
    maintainer's set (2026-10-19): most run at 59.9 Hz; Batman Returns, Checkered Flag, Desert Strike,
    European Soccer Challenge, Klax, Rampart and Switchblade II at 75; Lemmings, Lexis, Ninja Gaiden,
    Dinolympics, Super Off-Road and five prototypes at 50.1; Krazy Ace at 52.6; Ishido and California
    Games change rate between screens. The 50 Hz games take the same Native path as PAL content.
- **Canvas**: 160x102 in a 240x160 canvas, shown at 4x (640x408) on the 720x480 panel; its own
  Screen section (Shader, Picture, Lynx Speed, Flip Right Carts). Actual is a centred 180x120 window
  of the canvas (`Platform::actual_scale`); Stretch crops to the 160x102 picture and fills the panel
  (`stretch_crops_height` is true for Lynx, against issue 103's first draft, so Stretch fills).
- **Upstream test sites:** (b) and (e) take `| Platform::Lynx` and `| Core::MednafenLynx`, (g) and
  (h) take `, "Lynx"` and `, QuickRow::ScreenLynx` after the PlayStation tokens, as PS1 did (ADR 0065).
- **Saves: states only.** The README says so, with the EEPROM gap named.
- **Licence**: the combined core is GPL-3.0-or-later; counts and lists in LICENSING.md. Two licence
  files ship with the platform patch: `COPYING` and `mednafen/lynx/license.txt` (Handy, zlib), which
  nelynes' single `lynx-GPL-2.0.txt` leaves out.
- **Credit** nelynes/slotPlus (749523c core and shelf, d7d0e74 rotation list and override file,
  185257a turned play) in the patch commits and LICENSING.md.

## Consequences

- Ten patches, 0070 to 0079 (issues 102 to 111; 112 is the device gate). Nothing touches GBA, GB or GBC; the GBA harness compare stays
  at 0 diffs.
- **CI cannot boot a cart.** The no-BIOS tests (homebrew draw, real rate, state, the missing-BIOS
  signature) run everywhere; the cart-through-BIOS tests run only with `SLOT_LYNX_BIOS` and print a
  BIOS skip otherwise, which `run-tests.sh` lists as a ROM skip, not a missing core.
- Lynx is the first system whose pacing cannot trust `av_info.fps`. Issue 107 must not land as a
  PAL Speed row reusing the reported rate.
- On a rebase, check the pin still builds and `lynx_core.rs` still passes, in particular the
  rotation and rate tests: they are the contract issues 107 and 109 build on.
