# 0023. Show a NES and an SNES shader row on the quick menu Screen page

- Status: Accepted. Supersedes [0008](0008-no-new-quick-menu-rows.md)
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 44](../../.github/issues/44-quick-menu-retro-shaders.md), [patch 0018](../../patches/0018-quick-menu-retro-shaders.patch)

## Context

Users look for settings in the same place on every system. GBA and GB offer their shader on the
quick menu Screen page; NES and SNES shaders were reachable only by SELECT+A/B in game
([0008](0008-no-new-quick-menu-rows.md)).

## Decision

The Screen page lists a NES shader row on the NES shelf and an SNES shader row on the SNES shelf
(Off, Grid, Dot, stored in `shader_nes` and `shader_snes`), where GBA and GB show their shader row.
`QuickRow::SCREEN` stays 4 rows.

## Consequences

- SELECT+A/B in game still works and shares the stored value.
- The new variants are appended and the Screen row opens a page per shelf, so every upstream quick
  menu test is unmodified.
- Picture mode stays per cart and in game; upstream has no picture-mode row, so none is added.
