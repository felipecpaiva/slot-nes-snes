# 0048. List NES and SNES on the Screen page after the Game Boys

- Status: Accepted. Amends [0043](0043-retro-shader-rows-on-v1-7-0-menus.md) and [0013](0013-five-named-test-sites.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0022](../../patches/0022-screen-platform-list.patch), slot #83, `scripts/check-upstream-tests.sh`, CONTRIBUTING.md section 1

## Context

ADR 0043 left NES and SNES out of v1.7.0's Screen platform list, so the NES shader was only
reachable from the NES shelf or in game. The maintainer wants NES and SNES in the same list as the
others. `crates/slot-ui/tests/quick_menu.rs` pins that list: `QuickRow::SCREEN` is compared with a
three-label literal, the rows that open pages with a literal list, and every row of SCREEN must
have `page() == SCREEN`. The harness hashes every composite frame, the Screen list included.

## Decision

- `QuickRow::SCREEN` becomes Game Boy Advance, Game Boy Color, Game Boy, NES, SNES. ScreenNes and
  ScreenSnes open one-row pages (`SCREEN_NES`, `SCREEN_SNES`) holding the NesShader or SnesShader
  row, labelled Shader, which steps through the nine retro shaders into `shader_nes` or
  `shader_snes`, the same values the in-game Shader row uses. No Color Correction or Palette row.
- Screen opens the list from every shelf; the shelf-dependent jump of ADR 0043 is gone.
- On a card with no NES and no SNES cart the two rows are hidden (`retro_quick::hidden_on_shelf`),
  so GBA, GB and GBC menus and frames stay upstream's.
- Two new named test sites in `crates/slot-ui/tests/quick_menu.rs`, approved by the maintainer
  on 2026-10-15: (g) the Screen labels literal gains `, "NES", "SNES"` after `"Game Boy"`, and
  (h) the opens list line `QuickRow::ScreenGb` gains `, QuickRow::ScreenNes, QuickRow::ScreenSnes`,
  each on its one line.
- No generic upstream branch. Deriving the list from a platform policy would still fail the
  pinned literal on v1.7.0, so it removes no site; it would only help after upstream rewrote its
  own tests for systems it declined to add.

## Consequences

- The NES and SNES shaders are reachable from any shelf when the card holds those carts.
- `slot/tests/quick_menu.rs`'s wrap test needs no site: its card has no NES or SNES cart.
- On each rebase, recheck the two literal lines; the guard fails on any other change.
