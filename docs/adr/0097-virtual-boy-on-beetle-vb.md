# 0097. Bring the Nintendo Virtual Boy into scope on pinned Beetle VB, one eye on a flat screen, a shelf of its own

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-20
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0068](0068-ps1-input-digital-then-analog.md) (the sticks and the triggers-to-the-game mode), [ADR 0071](0071-pace-off-panel-cores-at-their-own-fps.md), [ADR 0091](0091-tg16-on-beetle-pce-fast.md) (the Beetle build precedent), [ADR 0096](0096-sega-32x-on-picodrive.md), [issue 153](../../.github/issues/153-vb-tracking.md), patches `0099-vb-core-tests` to `0106-vb-carts`, [docs/research/next-systems-2026-10-20.md](../research/next-systems-2026-10-20.md) section 6

## Context

The maintainer asked for the Virtual Boy as a full platform, ranked seventh in the 2026-10-20 research.
He owns 28 titles (22 games once betas, protos and duplicates are dropped,
`docs/rom-library/best-copy/vb-adds.tsv` in the workspace). The Virtual Boy is a stereoscopic system: two
384x224 eyes in red on black, two D-pads on the controller, no BIOS. The device is a flat 720x480 (3:2)
panel with two analog sticks (ADR 0068).

The libretro Virtual Boy core is **Beetle VB** (libretro/beetle-vb-libretro, Mednafen's VB emulator). No
other libretro core runs it.

## Decision

- The Virtual Boy is in scope as Phase 16, after the 32X (Phase 15). One shelf `Games/VB`. The platform is
  `Platform::Vb`, appended to `SHELVES`; the core is `Core::MednafenVb`, appended to `EVERY`. Upstream's
  `ALL` stays untouched and every policy method answers the Virtual Boy explicitly. One core, no picker.
- **Core pin.** libretro/beetle-vb-libretro `d5ae54c8e23b573a3b34e888b2d48a588027e92c` (its master on
  2026-10-12, "Show both eyes through the unified VR view API"), archive sha256 `ccbed557...c08189`. The
  recent VR view needs OpenGL; the makefile leaves it out by default (`HAVE_VR ?= 0`), and the build says
  `HAVE_VR=0` so a changed default cannot pull GL in. With it off `libretro_vr.cpp` is stubs and the
  `vb_vr*` options are not declared.
- **Build.** `make platform=unix` and `-mcpu=cortex-a53` on the device, `platform=osx` on the host, the
  Beetle PCE Fast recipe (ADR 0091). The V810 is C++, so the device build links the C++ runtime
  statically with `--as-needed`; `task core:device:mednafen_vb` fails unless NEEDED is `libc.so.6` and
  `libm.so.6` at GLIBC_2.17 or older.
- **Licence.** GPL-2.0-or-later (`COPYING`, the Mednafen headers), with one GPL-3.0-or-later header
  (`mednafen/msvc_compat.h`), Blip_Buffer under LGPL-2.1-or-later and the SoftFloat 2b notice on the V810
  FPU, so the combined core is GPL-3.0-or-later like slot. `licenses/mednafen_vb-GPL-2.0.txt` and
  `licenses/mednafen_vb-headerless-files.txt` ship in `System/licenses/` with the source tarball.
  LICENSING.md has the counts.
- **Shelf.** `.vb` and `.vboy`, titled by the file stem (the header title is often Japanese). No header
  check: no other shelf uses these extensions.

### What the screen shows: the left eye, flat

Beetle VB's `vb_3dmode` offers anaglyph, cyberscope, side-by-side, vli and hli; `vb_anaglyph_preset`
picks the two anaglyph colours or `disabled`; `vb_color_mode` is the palette. We read the source at the
pin and then measured it.

- **Source.** With the preset `disabled`, `SettingChanged` uses `vb.anaglyph.lcolor` and `rcolor`, which
  `check_variables` sets from `vb_color_mode` to the palette colour and `0x000000` (libretro.cpp, the
  `vb_color_mode` block). The anaglyph copy (`mednafen/vb/vip.c`, `CopyFBColumnToTarget_Anaglyph_BASE`)
  writes the left eye and ORs the right eye on top in its colour, which is black. So the picture is the
  left eye alone in the palette colour, one 384x224 image.
- **Measured on the host core** (`vb_core.rs`, a generated cart that draws a band of columns 40 to 79 in
  the left frame buffer and 300 to 339 in the right one, with the drawing engine off):
  - anaglyph, preset disabled: only columns 40 to 79 are lit, in the palette colour (red `0xdf0000`, white
    `0xdfdfdf` with the white palette); a cart that draws only the right eye shows nothing;
  - anaglyph, preset `red & blue`: both bands are lit, one over the other, which is the doubled picture
    that needs glasses;
  - side-by-side: a 768x224 frame, both eyes next to each other, each at 384 wide, which on a 720 panel
    is two half-size pictures.
  - The same holds on the maintainer's dumps (read only, never committed): on Virtual Boy Wario Land after
    the title (900 frames, Start pressed), the anaglyph frame equals the side-by-side left half pixel for
    pixel (0 of 86,016 differ) and differs from the right half in 1,008 pixels.
- **Choice: anaglyph with the preset disabled.** It is a clean single image, it is the core's own default,
  and it costs nothing (the fast copy path, no blending). Side-by-side, cyberscope, vli and hli need
  hardware this device does not have. `vb_3dmode` asks for a restart, so it is answered before the game
  loads and never changed. Parallax is lost; every game we tried is playable with one eye, as the
  research expected.

### Screen section

The Virtual Boy gets its own Screen section, last in the list and shown only when the card has Virtual
Boy games: **Shader** (Off and the retro list, `Config/vb_shader.txt`), **Picture**, **VB Speed**,
**Palette** and **Right Pad**.

- **Canvas and Picture.** The canvas is 384x256, 3:2 like the panel, so it maps to 720x480 at exactly
  1.875x. **Actual** (the default) draws the 384x224 picture 720x420 with a 30 px band above and below;
  **Stretch** fills the panel (720x480, the picture stretched 14% taller). No crop (no overscan) and no 4:3. Stored as `vb` in
  `Config/picture.txt`.
- **VB Speed** is the ADR 0071 row: Beetle VB reports 50.27 fps, and Native (the default) paces it at its
  own rate; Panel is the 60 Hz stretch.
- **Palette** is the core's eight `vb_color_mode` choices, in its order: black and red (default, the
  hardware's red LEDs), black and white, blue, cyan, electric cyan, green, magenta, yellow. Applied at the
  start of the next game.
- **Right Pad**: Stick (default) or ABXY, below. Applied at the start of the next game.
- Both live in `Config/vb.txt` (`palette = red`, `right_pad = stick`). The factory choice is the
  hardware's; the user's choice becomes the default and is never retuned. A missing line is the factory
  choice; an unknown one is logged and read as it.

### Input

The Virtual Boy pad has two D-pads, A, B, L, R, Start and Select. Beetle VB maps the right D-pad to the
libretro ids L2 (up), R3 (right), L3 (down) and R2 (left), and reads JOYPAD_X as the low battery switch.

- **Stick (default).** The device D-pad is the left D-pad. A, B, L, R, Start and Select are themselves.
  The **right analog stick is the right D-pad**: `vb_right_analog_to_digital=enabled`, and slot plugs
  Beetle VB as a plain pad (`analog_pad` gives `PLAIN_PAD`, the joypad id) so the core is answered
  `RETRO_DEVICE_ANALOG` like pcsx; every other core still gets centre. L2 and R2 stay slot's rewind and
  fast-forward.
- **ABXY.** For games that use the right D-pad as buttons: X up, A right, B down, Y left (the face
  buttons by position), and the console's A and B move to R2 and L2. L2 and R2 then go to the game in
  the PS1 way (ADR 0068): the mode is latched at the start of the game, fast-forward is SELECT+R2, and
  there is no rewind button in this mode. Rewind recording stays on, so a game started in Stick mode can
  still be rewound.
- **X and Y never reach the core in either mode**, so the low battery switch is never thrown.
  `ButtonMask` gains `L3` and `R3` (bits 14 and 15, the libretro ids).
- Where it matters:
  - **Red Alarm**: the right D-pad moves the ship up, down and forward; Stick plays it, ABXY makes thrust
    and climb buttons.
  - **Teleroboxer**: each D-pad is one fist; the stick for the right fist is the natural fit, ABXY if the
    stick feels loose.
  - **Virtual Boy Wario Land**, **Jack Bros.**, **Mario Clash**, **Vertical Force**: the right D-pad is
    unused or a menu key; Stick (the default) is fine.
- Opposite directions are refused (`vb_opposite_directions=disabled`), the core's default.

### Speed, saves and states

- **CPU.** `vb_cpu_emulation=fast`, the core's default. Accurate is not a row: nothing on the host
  suggests a game needs it (it costs about 15% more). It can become a row if the device gate finds one.
- **Saves.** Beetle VB gives every cart 64 KB of cart RAM, so every game has the ordinary `.sav` in
  `Saves/VB`, also when it never saves, as a HuCard leaves its backup RAM (ADR 0091). A RetroArch `.srm`
  loads when there is no `.sav`.
- **Rewind on, run-ahead off.** A state is 395,675 bytes on Wario Land and saving one took 0.025 ms on
  the Mac (median of 300). Run-ahead stays gated to mGBA.

### Cart

One Virtual Boy cart for every game, `RetroShell::Vb`. ConsoleMods' [Dimensions for Game
Cartridges](https://consolemods.org/wiki/Dimensions_for_Game_Cartridges) (checked 2026-10-20): 68.36 mm
tall, 75.8 mm wide, 6.61 mm thick, 73.74 mm tall with the dust cap; "the NTSC-U and NTSC-J cartridges are
identical". The shape, the grey plastic, the large label well and the dark dust cap along the bottom are
from the Wikimedia Commons photo [Virtual Boy Game Paks](https://commons.wikimedia.org/wiki/File:Virtual_Boy_Game_Paks.jpg)
(Joshua W, CC BY-SA 2.0, used for reference only, not shipped). Seated 240x234, drawn 360x351. The grey is
the SNES grey `9f 9c a2`, our choice: the photo is too warm and small to measure. docs/cart-art/VB.md has
every value.

### Labels

`tools/fetch-labels.py` system `VB`: dat `Nintendo - Virtual Boy` (libretro-database
metadat/no-intro), ScreenScraper id 11 (Skyscraper `platforms_idmap.csv` at ccd49ae, row
`virtualboy,11,38,4918`). libretro-thumbnails has `Nintendo - Virtual Boy` Named_Logos (22 files,
2026-10-20) for the Logo Only fallback. On the maintainer's four test dumps all four labels came by CRC.

## Performance

Host only, a direction and not a device number: `core_bench` on the maintainer's dumps after 600 frames,
median ms a frame over 600 frames, 3 repeats, Apple M-series.

| Game | fast | accurate |
|---|---|---|
| Virtual Boy Wario Land | 0.88 | 1.10 |
| Red Alarm | 0.85 | 1.02 |
| Jack Bros. | 0.87 | 1.03 |
| Teleroboxer | 0.85 | 0.96 |

That is about the PicoDrive cost on the same host. The research estimated 2 to 4 ms a frame on the A53;
the budget at 50.27 fps is 19.9 ms. The device gate (issue 162) measures it with `bench:device`
(`CORE=mednafen_vb`) and real play.

## Consequences

- Eight patches, 0099 to 0106. No GBA, GB or GBC path changes. The input changes (`analog_pad`, the
  triggers latch, `ButtonMask::L3`/`R3`) are only reached for the Virtual Boy; a GBA game after a
  Virtual Boy game in ABXY mode gets the GBA-only input and picture (`vb_then_gba.rs`).
- Upstream test sites (b), (e), (g) and (h) take one more token each, in order: `| Platform::Vb`,
  `| Core::MednafenVb`, `"Virtual Boy"` and `QuickRow::ScreenVb`, by the standing rule.
- Parallax depth is not shown. A future glasses mode (a real anaglyph preset) would be one more Screen
  row; nothing in this ADR rules it out.
- On a pin bump, check that `HAVE_VR` still defaults to 0, that the palette words are unchanged
  (`vb_screen.rs` tests the declared list), and the right D-pad ids in `update_input`.
