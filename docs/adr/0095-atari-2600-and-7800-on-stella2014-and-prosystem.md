# 0095. Bring Atari 2600 and Atari 7800 into scope on pinned Stella 2014 and ProSystem, built the NES and SNES way

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems; integration decisions added 2026-10-20
- Date: 2026-10-19
- Deciders: maintainer (Felipe Paiva)
- Related: [Atari plan](../research/atari-plan.md), [ADR 0050](0050-canvas-per-core-and-platform.md), [ADR 0071](0071-pace-off-panel-cores-at-their-own-fps.md), [issue 153](../../.github/issues/153-atari-tracking.md), [issue 154](../../.github/issues/154-a2600-core-build.md), [issue 155](../../.github/issues/155-a7800-core-build.md), patch `patches/0098-atari-core-tests.patch`. Atari ST is out of scope and not planned.

## Context

The maintainer owns 578 Atari 2600 dumps and 73 Atari 7800 dumps (66 games, the rest BIOS, tools and
test carts), all No-Intro named and zipped, plus both 7800 BIOS files (`7800 BIOS (U).rom` md5
`0763f1ffb006ddbe32e52d497ee848ae`, `7800 BIOS (E).rom` md5 `397bb566584be7b9764e7a68974c4263`).
Both consoles are joystick-and-one-or-two-button systems with a few console switches, cheap to
emulate on the A53 and cheap to fit on the 720x480 panel.

The libretro choices:

- **2600.** libretro/stella2014-libretro (Stella 3.9.3, `STELLA_VERSION` in
  `stella/src/common/Version.hxx`) or current Stella (stella-emu/stella, whose `src/os/libretro`
  builds the libretro core). Stella 2014 is the one handheld distributions use on weak CPUs. It is
  still maintained: HEAD on 2026-10-19 is `7d1361e` (2026-09-04), with CDF and BUS cart types
  backported from Stella 7. Current Stella is C++20, heavier, and lives outside the libretro
  organisation that `cores/lib.sh` fetches from.
- **7800.** libretro/prosystem-libretro (ProSystem, Greg Stanton) is the only libretro 7800 core.
  HEAD on 2026-10-19 is `8a88014` (2026-08-22).

## Decision

- Atari 2600 and Atari 7800 are in scope as Phase 14, two shelves: `Games/A2600` (`.a26`, `.bin`)
  and `Games/A7800` (`.a78`, headered or not). The platforms are `Platform::A2600` and
  `Platform::A7800`, appended to `SHELVES`; the cores are `Core::Stella2014` and `Core::Prosystem`,
  appended to `EVERY`. Upstream's `ALL` stays untouched and every policy method is answered
  explicitly, as for PS1 (ADR 0063).
- **2600 core:** libretro/stella2014-libretro pinned at `7d1361e407e63f29e52892655069e5fb4096e691`,
  archive sha256 `c0f5e53f3c21e7760e434784634d44a02e57a30917da5279cfd3add4736afd82`. Root `Makefile`,
  output `stella2014_libretro.<ext>`, so the core name is `stella2014`. C++: the device build links
  `-static-libstdc++ -static-libgcc`; the `.so` needs only `libc.so.6` at GLIBC_2.17.
- **7800 core:** libretro/prosystem-libretro pinned at `8a88014287c7a01cd568067e5a557d0a2b2a051f`,
  archive sha256 `23401c8b104ef24db111bbc4b13e37f224ffe16febfb89c704c70cdb269603bc`. Root
  `Makefile`, output `prosystem_libretro.<ext>`, core name `prosystem`. Plain C, no C++ runtime.
  CoreTone calls `pow`, which glibc 2.29 re-versioned; `cores/prosystem/glibc-2.17.h`, force-included
  through `device_include` (the hook the TurboGrafx-16 groundwork added to `cores/lib.sh`, taken
  verbatim), binds `pow@GLIBC_2.17`. The `.so` needs `libc.so.6` and `libm.so.6` at GLIBC_2.17.
- One core per system, no picker.
- **Licences.** Neither core has a GPL-2.0-only file, so both combine with slot under
  GPL-3.0-or-later. Details and counts are in LICENSING.md.
  - Stella 2014: every Stella file says only "See the file License.txt", and that file is the bare
    GPL-2.0 text. The or-later grant is Stella's own `Copyright.txt` at tag `release-3.9.3` ("either
    version 2 of the License, or any later version"), which the libretro fork does not carry. We ship
    a verbatim copy beside the GPL text. The grant is upstream, not in the tree; if that reading were
    ever disputed, current libretro Stella (GPL-2.0-or-later in its own `Copyright.txt`) is the
    fallback, at a performance cost to measure.
  - ProSystem: 31 files carry Greg Stanton's GPL-2.0-or-later header; CoreTone (`bupboop/`, Osman
    Celimli) is zlib, shipped as its own licence text.
  - The licence files stay in `cores/<core>/` until the core ships with its platform patch, because
    `scripts/dist-device.sh` copies all of `licenses/` into the release (the Genesis Plus GX
    precedent, ADR 0053).
- **BIOS.** The 2600 has none. ProSystem loads `7800 BIOS (U).rom` (or `(E)` for a PAL cart) from
  the system dir when present and otherwise starts the cart directly. The BIOS is a signature check
  and a logo: a signed game shows the logo for about two seconds and then plays; an unsigned cart
  (homebrew, our test cart) never draws (pinned by a test). There is no core option for it. slot
  defaults to **BIOS Off** and hides the file from the core by opening ProSystem with a system dir
  that does not hold it (issue 165).
- **No 7800 high score cart.** ProSystem at this pin has no High Score Cartridge code at all (no
  HSC symbol, no option). It is not offered. 7800 saves are save states only, like the 2600.
- **Console switches are input, not options.** Neither core exposes TV type or difficulty as a core
  option. Stella reads them from the RetroPad (L/L2 left difficulty A/B, R/R2 right, L3 Colour, R3
  Black/White, SELECT Select, START Reset) and latches the difficulty and TV switches. ProSystem
  reads L and R (difficulty), X (Reset), SELECT and START (Pause) only while held. slot keeps L1 and
  R1 for itself, so the latched switches become Screen rows that slot applies itself (issues 159 and
  167).
- **Picture.** Stella hands 160 columns and the game's own rows (210 by default, up to 256; 250 on
  PAL); ProSystem hands 320x223 NTSC and 320x272 PAL. Both go through the 360x240 canvas with a
  per-platform vertical rule (issues 158 and 166).
- **Pacing.** Stella reports 59.92 fps NTSC (inside ADR 0071's window, the upstream path) and 49.92
  PAL; ProSystem reports exactly 60 or 50. PAL titles get ADR 0071's paced path and a PAL Speed row.

## Integration decisions (2026-10-20, patches 0099 and 0100)

The groundwork was rebased onto main after the 32X (ADR 0096): the ADR keeps 0095 (main never used
it), the issues moved to 153 to 172 and the core test patch to 0098. Two patches follow:
`0099-platform-atari` (both shelves, policy, options, canvases, Screen sections, switches, BIOS row)
and `0100-atari-carts` (the two shells).

- **Canvases, not a new copy path.** Stella draws into a 360x256 canvas and ProSystem into 360x272,
  so `copy_centred` never halves a PAL frame (250 or 272 rows) and the shared RGB565 path is not
  touched. The 2600's 160 columns are not doubled by slot: the 4:3 and Stretch rects scale the
  160x210 picture to the panel, which keeps the 2600's wide pixels.
- **Picture.** 4:3 is the factory choice on both shelves (the 2600 and 7800 drew on a 4:3 TV and
  their pixels are not square), then Stretch and Actual. 4:3 and Stretch use the NTSC height (210,
  223); a PAL frame is shown by its middle rows there, and whole in Actual.
- **Switches are held, every frame.** Both cores read the console switches from the RetroPad (Stella
  latches L/L2, R/R2, L3/R3; ProSystem reads L and R only while held). slot keeps L1, R1, L2 and R2,
  so the pad never carries them; `atari_switches::remap` clears those bits and adds the chosen
  switch every frame, which survives state loads, rewind and resume with no extra code. The rows
  live in `Config/atari.txt`. 2600 factory choice: Auto (no button, Stella keeps the game's own
  default from its database); 7800 factory choice: left B, right A, ProSystem's own default
  (`retro_load_game`, "fixes Tower Toppler"). The pad code rides on the WonderSwan pad channel
  (`set_ws_pad`), re-sent each update, so a row changed in the in-game menu applies at once.
- **Buttons.** 2600: A and B both fire, and also press RetroPad Y, Stella's paddle button. X and Y
  pass through (Stella ignores X). 7800: B is button 1, A button 2, X Reset (passed through, so no
  menu row is needed), SELECT Select, START Pause. No turbo on either shelf.
- **Paddles.** In scope through the left stick: slot answers analog queries for Stella
  (`analog_pad` returns the plain RetroPad, so the port stays a joypad) and Stella reads the left
  stick X for every game its database marks as paddles. Not device-verified yet (issue 162).
  Keypad, driving, Mindlink and Kid Vid games stay out (issue 172).
- **7800 BIOS row.** Off by default: ProSystem is opened with `Saves/A7800/.system` (empty) as its
  system dir, so a BIOS in `BIOS/` is never loaded. On uses `BIOS/`. No md5 check: a wrong file
  only means ProSystem shows nothing for an unsigned cart, which the row's Off fixes.
- **Core options.** Stella: 24-bit colour, standard palette, no frame mixing, no low-pass filter.
  ProSystem: 24-bit colour, no low-pass filter, the dual-stick hack off. Both draw XRGB8888.
- **Licences.** No non-commercial term in either core (checked by grep over both trees), so neither
  needs the snes9x treatment. ProSystem's TIA and POKEY sound carry Ron Fries' LGPL-2 notice, which
  converts to GPL-2.0-or-later (LICENSING.md). The licence texts moved to `licenses/`.
- **Carts.** One shell per system, both 82 by 98 mm (Atari Corp. reused the 2600 shell size for the
  7800): the 2600 Atari Inc. shell with a ribbed grip over the label, the 7800 Atari Corp. shell
  with a raised cap and side grips, in two blacks. Labels: ScreenScraper 26 and 41, dats
  `Atari - 2600` and `Atari - 7800`; libretro Named_Logos exist for the 2600 only.

## Consequences

- About 16 patches (issues 156 to 170), two shelves that share nothing with GBA, GB or GBC, so the
  GBA harness compare stays at 0 diffs.
- Both cores are in `task core:host`, `task core:device`, `task check` and `SLOT_REQUIRE_CORES`
  from now on. They join `dist:device` and `zip-check.sh` only with their platform patches, so no
  release ships an unused core (the issue 57 rule).
- The maintainer's library is zipped and slot reads no zip (the non-goal stands). The same
  unzipped-library-copy path `tools/hacks.py` uses (#147) is the way in; no zip support is planned.
- Paddle (35 of his 559 recognised 2600 dumps), keypad (15) and the other special controllers are
  out of scope at first (issue 172).
- On a rebase, check that both pins still build and that `atari_core.rs` still passes; the switch
  and BIOS tests are the contract issues 159, 165 and 167 build on.
