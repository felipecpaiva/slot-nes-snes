# slot NES/SNES: deep research (2026-10-11)

Basis: slot v1.6.0 at `9d7c795`, read-only code audit + core/CFW/licence research. Nothing built
or run on a device yet. Companion to `EVAL.md` (decision history).

## Chosen approach

Patch set over pinned slot releases (the way slot ships mGBA), adding `Platform::Nes` and
`Platform::Snes` with their own shelves, cores and settings.

## Cores

| System | Default | Alternative | Why |
|---|---|---|---|
| NES | fceumm (GPL-2+) | nestopia (GPL-2+) | Every NES core is full speed on A53. fceumm = widest mappers, default on Knulli / muOS / NextUI / MinUI |
| SNES | snes9x current (non-commercial licence) | snes9x2005_plus (same licence, faster) | Default on ROCKNIX, Knulli, muOS (since 2410.2), NextUI. GPL-clean option: Beetle Supafaust (unverified on H700) |

- No H700 numbers for Super FX / SA-1 games. On-device test list: Star Fox, Yoshi's Island, Kirby
  Super Star, Super Mario RPG, Seiken Densetsu 3. One muOS report (RG40XXH) fixed SA-1 pops by
  switching the CPU governor to `interactive`.
- Build with `make platform=unix` (NOT `arm64`, which yields `.dll` for these cores) and
  `CFLAGS/CXXFLAGS=-mcpu=cortex-a53`. fceumm: `-f Makefile.libretro`; nestopia/snes9x: `libretro/`.

## Licence (decision needed)

snes9x family is non-commercial, GPL-incompatible. GPL FAQ treats dlopen plugins sharing data as
one combined program. RetroArch / ROCKNIX / Knulli ship it anyway. Clean fix is a GPLv3 section 7
exception from slot's copyright holders (Brandon Kowalski, 453 commits; GamerAnim, 1). Or ship
GPL-only cores (fceumm + Supafaust) and let users supply snes9x.

## slot changes, by area

**Data/policy (new methods on `Platform`, keep app.rs hunks one token):** `owns_shoulders`,
`turbo_mode`, `shaders`, `has_gb_palettes`, `canvas`, `picker_cores`, `default_shell`.

**Silent-fallthrough fixes:** `scan.rs:28`, `slot/src/core.rs:128`, `app.rs:855` (SNES would lose
L/R to picture-mode toggle), `app.rs:2643/2646` (use `core_for_platform`), `Core::runs`
(`Mgba => true`), `Core::parse`, `quick_menu.rs` `page()` wildcard, `root.rs` DIRS.

**Runtime panic to avoid:** a third `Core` makes `SOCKET_U[i]` (`board.rs:164`) index out of bounds
via `frontend.rs:602-609` / `app.rs:2244`. Fix: picker takes a per-platform `(left, right)` pair.

**Input:** `turbo/without_turbo` strip X/Y always. Add a `PassThrough` turbo mode for SNES, plumbed
through `Shared` like `set_turbo`.

**Video (the big one):** fixed 3x canvas, `SRC_W/H = 240x160` (`slot-gfx/pipeline.rs:7-9`);
`video_refresh` crops to 240x160 (`libretro.rs:321-330`); frame size is carried nowhere.
- Option A (recommended): per-platform canvas. NES/SNES use 360x240 at 2x (same 3:2, fills 720x480).
  NES 256x240 is a perfect 2x. GBA/GB byte-identical. SNES hi-res (512 wide) blended 2:1, rare titles.
- Option B: true variable frames up to 512x480. Better hi-res, much bigger patch.

**libretro env:** add `SET_GEOMETRY` (return true), `SET_SYSTEM_AV_INFO` (update fps/rate, re-init
resampler; fceumm calls it on region/rate option change), `GET_AUDIO_VIDEO_ENABLE` (snes9x skips
render in FF). Others safe as false.

**Performance watch-points:** RGB565 per-pixel conversion (snes9x/fceumm), full-buffer publish copy,
rewind serialize every 2 frames with a blocking `sync_channel(4)`, PNG thumb encode on save, PAL
titles run ~20% fast (pacing assumes 60 fps), FF depends on the core declaring `*_frameskip`.
Measure with `crates/slot-retro/examples/core_bench.rs` / `task bench:device` / `SLOT_TRACE`.

**Cart art:** cheapest parity maps NES/SNES to the GBA shape with own default colour. Real NES/SNES
shells = new SVG assets + Spec arm (design work).

**Tests:** need `write_nes_cart`/`write_snes_cart` helpers in `crates/slot/tests/common/mod.rs`;
real-core tests skip silently without the dylib, so taskfile must build the new cores or twins pass
vacuously. Edit asserts: `slot-store/tests/platform.rs:11`, `tests/core.rs:160,203`. Twins listed in
the audit (app, core_picker, core_options, gb_palettes negative, emu 256x240, thumb, polaroids,
render_picture_modes, pipeline 2x canvas, turbo pass-through, quick_menu, dist/boot DIRS).
No CI test workflow exists upstream.

**Known ceilings:** stem-keyed `selected_core.txt` / `video_mode.txt` / `cart_shell.txt` collide
across platforms; zip unsupported.
