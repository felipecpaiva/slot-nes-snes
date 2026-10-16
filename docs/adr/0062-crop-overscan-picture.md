# 0062. Add a Crop picture mode that hides the NES and SNES overscan edges, default for both

- Status: Accepted. Amends [0046](0046-retro-stretch-crops-height.md) and [0061](0061-per-system-picture-row.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0007](0007-snes-select-x-picture-mode.md), [ADR 0022](0022-nes-snes-default-stretch.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [issue 55](../../.github/issues/55-crop-overscan.md), patches/0033-crop-overscan.patch

## Context

Measured on the RG34XXSP (720x480 panel, shader Off) in Stretch:

- NES: many games (Super Mario Bros. 3 in levels, for one) blank their leftmost 8 pixels with the
  PPU left mask. fceumm and nestopia run with every overscan key at 0 (`core_options_policy.rs`), so
  a band of about 22 panel columns shows on the left.
- SNES Knights of the Round (USA): 39 black panel rows at the top and none at the bottom, with every
  shader. The game blanks its own top lines (about 18 source lines at 480/224); placement is correct
  and unchanged since v1.6.0.

A CRT hid these edges. The maintainer wants a picture that is balanced and fills the panel, on by
default for NES and SNES.

Sources for the amounts:

- NESdev wiki "Overscan" (nesdev.org/wiki/Overscan): 256x224 is the centre most NTSC TVs show;
  measured CRTs hide about 12 to 15 lines at the top and 8 to 11 at the bottom; PocketNES crops 8
  pixels left and right.
- The pinned cores' own defaults: fceumm `fceumm_overscan_v_top` and `_v_bottom` default to 8 and
  `_h_left`/`_h_right` offer 8; nestopia `nestopia_overscan_v_top` and `_v_bottom` default to 8.
- snes9x at the pinned commit: `snes9x_overscan` ("Crop Overscan") value `16_pixels` sets the height
  to 208 (`OVERSCAN_CROP_16` in `libretro.cpp`), 8 lines off the top and bottom of 224. Its default
  already folds a 239-line frame to 224, so 239-line frames reach slot only from snes9x2005_plus.
- SNESdev wiki "Timing": lines 1 to 224, or 1 to 239 with overscan, carry the picture.
- Genesis Plus GX: `genesis_plus_gx_overscan` defaults to `disabled`, which already hides the Mega
  Drive and Master System border area, and slot sets `genesis_plus_gx_left_border` to `left border`,
  which drops the Master System's blank left column (ADR 0053).

## Decision

- `VideoMode` gains `Crop`, appended after `Stretch`, written `crop`. `stretch` and `actual` lines in
  `Config/video_mode.txt` and `Config/picture.txt` keep their meaning.
- `Platform::overscan` (our `platform_policy.rs`) gives the crop per edge pair in source pixels: NES
  8 on each side and 8 top and bottom (256x240 to 240x224), SNES 8 top and bottom only (256x224 to
  256x208). Game Gear, Master System and Mega Drive get none: the core already hides their borders.
- Crop is done in slot's source rect (the ADR 0046 path), not with core options:
  `platform_video::shown` shrinks the picture that `App::source_rect` hands to `video_mode::source_rect`,
  and the centred rect of the smaller picture is the crop. It is the same for both NES cores and
  both SNES cores, and core state and save states are untouched. The shader picture rect (`u_pic`)
  stays the uncropped picture, so scanline phase keeps to source lines.
- A 239-line SNES frame is centred in the canvas like today's Stretch, and Crop takes the same 208
  rows at the same scale as for 224, the middle 208 of the frame.
- Picture choices: NES and SNES are Crop, Stretch, Actual; the others stay Stretch, Actual. NES and
  SNES default to Crop; Master System and Mega Drive stay Stretch, Game Gear Actual.
- The Screen section's Picture row shows `Crop`, `Stretch` or `Actual`; Right steps forward through
  the choices and Left back. SNES SELECT+X cycles Crop, Stretch, Actual. NES L1 moves between Crop
  and Stretch (from Actual it goes to Crop) and R1 is Actual. Mega Drive SELECT+X and L1 on Game
  Gear and Master System are unchanged.
- Crop hides the GBA bezel like Stretch.

## Consequences

- GBA, GB and GBC never see Crop: their default, choices and source rect are unchanged.
- A `crop` line on a system without overscan (hand edited) draws as Stretch.
- 8 lines only partly balance Knights of the Round: about 10 of its 18 blank lines stay, roughly 23
  panel rows. These are starting values; a per-game or larger crop is a later decision.
- A 239-line frame loses 16 lines at the top and 15 at the bottom, where snes9x's `16_pixels` would
  take 8 and 23. Matching it needs the live frame height in `App`; not done.
- On a rebase, check `VideoMode` is still two values upstream and `shown_game_bezel` still tests
  the mode.
