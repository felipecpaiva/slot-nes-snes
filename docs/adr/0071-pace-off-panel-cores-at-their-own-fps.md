# 0071. Pace a core more than 2 fps from 60 at its own fps, locked to the panel, with a per-system PAL Speed row (Native default)

- Status: Accepted. Amends [0061](0061-per-system-picture-row.md) (a third Screen row) and [0065](0065-ps1-canvas-and-screen-section.md) (PS1 Screen section), the PAL non-goal in docs/PLAN.md and docs/QUALITY-BAR.md, and patch 0006's `av_rate` stretch (kept as the Panel choice)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 66](../../.github/issues/66-pal-pacing.md) (#129), [issue 34](../../.github/issues/34-deferred-pal-pacing.md) (superseded), patches/0043-pal-pacing.patch, [ADR 0070](0070-backport-upstream-settings-scroll.md) (the Screen platform list scrolls; the PAL Speed rows sit in the per-system sections, which fit)

## Context

Slot paces every core at 60 Hz. On the device the render thread ticks the emu thread once per
panel vsync (about 59.6 Hz, 16.78 ms, docs/DEVICE-GATE.md) and the emu runs one frame per tick
(`driven`/`locked` in `emu.rs`); undriven (host, tests) it sleeps `PRESENT`, 16.667 ms, a frame.
Patch 0006 resamples a 50 fps core's sound from its rate stretched to 60 Hz, so PAL games run and
sound 20% fast.

Every core we ship reports PAL timing in `retro_get_system_av_info` at the pinned commits: fceumm
`NES_PAL_FPS` (50.007, `libretro.c:1881`), nestopia from the PAL clock (50.007, `libretro.cpp:684`),
snes9x 50.007 (`libretro.cpp:1153`), snes9x2005_plus on `Settings.PAL` (`libretro.c:815`), Genesis
Plus GX from `system_clock` and `lines_per_frame` (49.70 on a PAL VDP, `libretro.c:3167`) and
pcsx_rearmed `psxGetFps()` (`libretro.c:1237`). A mid-game change arrives as
`SET_SYSTEM_AV_INFO` and is already handed to the emu loop by patch 0006. NTSC and Game Boy
cores report 59.73 to 60.10.

The panel cannot be relied on for 50 Hz. Upstream's `FbdevSurface` only reads `fb0`'s mode
(`slot-gfx/src/fbdev.rs`, `FBIOGET_VSCREENINFO` and `/sys/class/graphics/fb0/mode(s)`); it never
writes a mode, and nothing in the tree sets a refresh rate. Whether the H700 panel accepts a 50 Hz
timing through `FBIOPUT_VSCREENINFO` is unknown and untested.

Prior art (all GPL-3.0): oauramos/omega-zero paces each core at its own fps (`Pace`, 726cc34);
cloudwithax/unslot keeps a core within 2 Hz of 60 at the panel period and gives any other core
its own period, with `core_hz` built on that period
([4cf8468](https://github.com/cloudwithax/unslot/commit/4cf8468)), but it turns the panel clock
lock off for such a core; nelynes/slotPlus carries a fractional count of frames owed per present
for 75 Hz cores ([0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb),
[b264635](https://github.com/nelynes/slotPlus/commit/b264635)), but only above 62 fps.

## Decision

- **Gate.** `av_rate::period(av, native, PRESENT)` returns `PRESENT` for a core within 2 fps of
  60 (or with no fps), and `1 / fps` for any other core when the system's PAL Speed is Native.
  Every NTSC, GBA, GB and GBC core is inside the window, so it never leaves the upstream path:
  the same period, the same resampler, the same audio ratio, the same ticks. The window is
  unslot's.
- **Locked to the panel (device).** The clock lock stays on. Each tick adds tick period over
  content period to a carry, and the tick runs the whole frames the carry holds
  (`av_rate::owed_frames`, always 1 at `PRESENT`). At 50 fps on a 59.6 Hz panel that is 0 or 1:
  about 9.6 ticks a second repeat the last frame, roughly 1 tick in 6. A later 75 fps core (Lynx,
  WonderSwan) gets 1 or 2 through the same code; upstream's frame trimming still applies to the
  second one. Keeping the lock, rather than unslot's free-running deadline, keeps presents on
  vsync and keeps `wait_frame` and the frametime log as they are.
- **Undriven (host, tests).** The deadline steps by the period instead of `PRESENT`.
- **Audio.** The resampler is built from `core_hz(av, period)`, which is the core's own sample
  rate for a paced core: one second of game feeds one second of sound, at the right pitch. At
  normal speed each frame's sound passes 1:1, and the panel-to-60 Hz `scale` is not applied to a
  paced core (it would add about 0.7% a second, more than the dynamic rate control's 0.5% can
  absorb). Fast forward keeps dividing by the frames it ran.
- **The option.** Each paced system's Screen section (NES, SNES, Master System, Mega Drive,
  PlayStation) gains a third row, **PAL Speed: Native / Panel**, stored as `nes = panel` lines in
  `Config/pal_speed.txt` through upstream's `ini::write`, like `picture.txt`. A missing line is
  Native; an unknown value is logged and read as Native. Panel is the old behaviour (60 Hz with
  the `av_rate` stretch), kept because options stay available. The session hands the choice to the
  emu at spawn (`EmuHandle::set_native_pal`), so a change applies from the next game. No row for
  Game Gear (60 Hz hardware everywhere) or the Game Boys, whose Screen pages are pinned upstream.
- **Default Native.** It is the content's own speed and pitch on any panel; it is not tuned for
  one device. Panel rate is the choice that depends on the panel.
- **SNES is included.** The gate is on the reported fps, so snes9x and snes9x2005_plus PAL content
  is paced with no extra code; the only cost is the Screen row.

## Consequences

- PAL games run at 50 fps with correct pitch. The picture judders: one tick in about six shows
  the previous frame again. Only a 50 Hz panel mode would remove that; it stays an alternative to
  investigate (write a 50 Hz timing with `FBIOPUT_VSCREENINFO` and measure), not something this
  depends on.
- Master System region comes from Genesis Plus GX's own database (about 23 titles marked Europe in
  `sms_cart.c`). Other European SMS games run as NTSC at 60 fps unless the core's region option is
  changed; there is no region row in slot. Mega Drive reads the header's region letters, NES on
  fceumm reads iNES 2.0 timing or the file name ("(Europe)" and the like), PS1 reads the disc.
- `emu.rs` gains small hunks (an atomic, a setter, the period block, the ceiling token, the audio
  ratio, the deadline); the logic lives in our `av_rate.rs`. GBA and NTSC paths are byte-identical
  because their period is always `PRESENT`; the harness compare covers it.
- A pacing change logs `slot: emu: pacing at 50.007 fps`. The frametime log still records panel
  presents (about 16.78 ms), never 50 Hz.
- On a rebase, check `Shared`, the ceiling match and the `set_ratio` line in `emu.rs` keep their
  shape.
