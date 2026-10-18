# 0076. Give the Master System Screen section a Region row mapped to Genesis Plus GX's region option

- Status: Accepted. Amends [0061](0061-per-system-picture-row.md) (a fourth row in the Master System section)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 69](../../.github/issues/69-sms-region.md), [ADR 0071](0071-pace-off-panel-cores-at-their-own-fps.md), patches/0047-sms-region.patch

## Context

PAL pacing (ADR 0071) engages when the core reports PAL timing. A Master System cart has no PAL
flag in its header, so Genesis Plus GX picks the region from its own database
(`sms_cart_region_detect`, `core/loadrom.c:1148` at the pinned 393f70c). Only 23 entries in
`core/cart_hw/sms_cart.c` are `REGION_EUROPE`. Every other European Master System cart runs as
NTSC at 59.92 fps, about 20% fast, and many Master System games were released only in Europe.
The core declares `genesis_plus_gx_region_detect` (`auto`, `ntsc-u`, `pal`, `ntsc-j`,
`libretro/libretro_core_options.h:120`), which overrides the detection (`core/loadrom.c:1161`).
Its `config_default()` runs on every `retro_load_game`, so an answer does not leak into the next
game.

## Decision

- The Master System Screen section becomes Shader, Picture, PAL Speed, **Region**. Region shows
  Auto, Japan, USA or Europe; Left or Right steps through them.
- The choice is per system, stored as `sms = europe` in `Config/region.txt` through upstream's
  `ini::write`, like `picture.txt` and `pal_speed.txt`. A missing file or line is Auto; an unknown
  value is logged and read as Auto.
- When a Master System game opens, `sms_region::apply` answers `genesis_plus_gx_region_detect`
  with `ntsc-j`, `ntsc-u` or `pal`. Auto answers nothing, so the core behaves exactly as before.
  Game Gear and Mega Drive on the same core never get the option (the test proves a Game Gear
  cart would drop to 50 Hz if they did). A change applies from the next game start.
- Per system, not per cart, as the maintainer asked. A per-cart override (a line per stem, as
  `video_mode.txt` does for pictures) is a possible later extension if a mixed card needs it.

## Consequences

- With Region Europe, every Master System game runs PAL timing, paced at 49.70 fps by ADR 0071
  (or at 60 Hz with PAL Speed set to Panel). American and Japanese games on the same card then
  also run at 50 Hz until the row goes back to Auto; that is the cost of per system.
- A game that checks the console region may refuse a wrong one, as on hardware. Auto restores it.
- One new hunk in upstream's `core.rs` `open_named`, beside the other option calls. The rest is
  menu plumbing in the files ADR 0061 and 0071 already touch.
- On a rebase, check the option key and values against the pinned Genesis Plus GX.
