# 0061. Give each retro system's Screen section a Picture row for its default picture mode

- Status: Accepted. Amends [0022](0022-nes-snes-default-stretch.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0007](0007-snes-select-x-picture-mode.md), [ADR 0048](0048-nes-snes-in-the-screen-platform-list.md), [ADR 0051](0051-sega-shaders-outside-slot-state.md), [ADR 0058](0058-propose-modular-platform-registry-upstream.md), [issue 54](../../.github/issues/54-system-picture.md), patches/0032-system-picture.patch

## Context

The picture mode is only reachable in game: SELECT+X on SNES and Mega Drive (ADR 0007), L1 and R1
on NES, Game Gear and Master System, like upstream's Game Boy. Each change is saved per cart in
`Config/video_mode.txt`. A cart with no line takes the factory default of ADR 0022 (Stretch, Game
Gear Actual). The maintainer wants to choose that default per system from the menu.

`VideoMode` has two values, Actual and Stretch. There is no Aspect mode in slot v1.7.0, and adding
one is renderer work and a new value, so it is not part of this.

## Decision

- The NES, SNES, Game Gear, Master System and Mega Drive Screen pages (`SCREEN_NES` and the
  others, our own constants) become Shader, Picture. The Picture row (`NesPicture` and the others,
  appended to `QuickRow`) shows `Stretch` or `Actual` with the usual carets, and Left or Right
  flips it. The values are two new `QuickValue` variants after the retro ones in `every()`;
  `QuickValue::ALL` stays upstream's 18.
- The row sets the system default, stored in `Config/picture.txt`, one `nes = stretch` line per
  system the user changed, written through upstream's `ini::write` the moment the row changes. A
  missing file or line, or an unknown value (logged), means the ADR 0022 default. slot.state is
  untouched, so named test site (f) stays as it is.
- `platform_video::video_mode_for` reads in this order: the cart's own line in
  `Config/video_mode.txt`, then `Config/picture.txt`, then the factory default. SELECT+X and L1/R1
  keep writing the running cart's line only.
- No Picture row for GBA, GB or GBC: their Screen pages are pinned by upstream's quick menu tests
  and hashed by the harness, and GBA has no picture toggle at all.
- No Picture row in the in-game Screen page: `QuickRow::PLAY_SCREEN` is a pinned four-row literal
  in upstream's `slot-ui/tests/quick_menu.rs`, and widening it is not a token on a match arm, so it
  would need a maintainer-approved test site. In game the existing chords stay the way to change
  the running cart.

## Consequences

- No new upstream test site, and GBA, GB and GBC menus and frames stay upstream's.
- A second small per-system file next to `sega_shaders.txt`. It is keyed by platform so ADR 0058's
  registry can absorb it, and it never collides with a cart stem in `video_mode.txt`.
- Changing the system default does not move carts that already have their own line; that is the
  point of the per-cart choice, and the in-game chord resets one cart.
- On a rebase, check `ini::value` and `ini::write` keep their signatures.
