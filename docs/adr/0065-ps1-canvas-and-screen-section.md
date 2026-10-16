# 0065. Give PS1 a fixed 640x480 canvas, its own frontend budget and its own Screen section

- Status: Accepted. Amends [0004](0004-fixed-2x-canvas.md), [0050](0050-canvas-per-core-and-platform.md) and [0061](0061-per-system-picture-row.md)
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0048](0048-nes-snes-in-the-screen-platform-list.md), [ADR 0055](0055-sega-tokens-at-named-test-sites.md), [ADR 0061](0061-per-system-picture-row.md), [ADR 0062](0062-crop-overscan-picture.md), [PS1 spike](../research/ps1-spike.md), [issue 60](../../.github/issues/60-ps1-canvas-screen.md)

## Context

pcsx outputs RGB565 at 256, 320, 368, 384, 512 or 640 wide and 240 or 480 high, and the size
changes mid-game. The spike saw 512x240, 320x240, 256x240 and one 640x480 frame. PS1 pixels are
not square: every width is a 4:3 picture. On the 720x480 panel, a 4:3 picture at full height is
exactly 640x480. Converting into a 640x480 canvas took 0.3 to 0.8 ms. Into 320x240 it took 1.6
to 3.6 ms, because wider frames take the box filter. The maintainer's rule is that every system
gets its own Screen filter section.

## Decision

- `Core::canvas(PcsxRearmed, Ps1)` is 640x480 (ADR 0050). Each frame is resampled horizontally
  to 640 wide, so 320 becomes an exact 2x and 640 an exact 1x, and 240-line frames have their
  rows doubled. Issue 36's Option B is not needed.
- PS1 has its own frontend-cost budget line in docs/PERFORMANCE.md: convert at most 2 ms a frame
  (the spike's bar, measured at 0.80 ms worst), and convert plus upload under about 3 ms (the PS1
  plan's go bar). The upload is measured at the device gate. The GBA budget stays as it is for
  every other system.
- PS1 thumbnails and polaroids are 4:3. This replaces ADR 0004's 3:2 consequence for PS1 only.
- PS1 gets its own Screen section (`SCREEN_PS1`, a `ScreenPs1` row) with a Shader row offering
  the shared retro list (Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap, Line, Pixel) and a
  Picture row (ADR 0061). The shader is stored outside slot.state in its own `Config/` file
  (the ADR 0051 pattern), and the picture default in `Config/picture.txt` (ADR 0061).
- Picture values are Actual and Stretch. Actual is the default: at 640x480 it is the 1:1, 4:3,
  full-height picture. Stretch fills the 720x480 panel. **Crop does not apply.** PS1 has no fixed
  overscan band: the display area is set per game and per mode, so a fixed cut would remove
  picture in some games and leave a border in others.

## Consequences

- About 1.2 MB a frame to convert and upload, against about 345 KB for NES and SNES. The upload
  was not measured in the spike and is a device-gate item.
- The retro shaders were tuned for low-res input. At 640x480 input, Grid, Dot, Line and Pixel
  may look different, and their cost is unmeasured. A shader that fails the budget is hidden for
  PS1 in issue 60, not tuned for everyone.
- Adding `ScreenPs1` to `QuickRow::SCREEN` puts new tokens at named test sites (g) and (h), and
  `Platform::Ps1` goes into (b) and (e) by the standing rule of ADR 0055. Issue 60 lists the exact
  lines. CONTRIBUTING.md is updated in that patch, not before.
- `QuickRow::PLAY_SCREEN` stays pinned, so the in-game Screen page gains no PS1 row (as ADR 0061).
