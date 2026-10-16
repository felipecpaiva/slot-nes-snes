# 0043. Fit the NES and SNES shader rows into v1.7.0's per-platform menus

- Status: Accepted. Amends [0023](0023-quick-menu-shader-rows.md). Amended by [0048](0048-nes-snes-in-the-screen-platform-list.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), [patch 0016](../../patches/0016-quick-menu-retro-shaders.patch), slot #83

## Context

v1.7.0 turns the Screen page into a platform list (Game Boy Advance, Game Boy Color, Game Boy),
each with Shader, Color Correction and Bezel, and adds an in-game Settings, Screen page whose
Shader, Color Correction and Bezel rows follow the playing platform (`playing_row`). Upstream
tests pin `QuickRow::SCREEN` to those three labels, the rows that open pages and the Screen page
wrap, so NES and SNES cannot join that list without new upstream test exceptions.

## Decision

- In game: `playing_row` maps Shader to NesShader or SnesShader and Bezel to the GBA bezel (ADR
  0005). `retro_quick::hidden_in_game` hides Color Correction and Palette on NES and SNES, and
  Bezel unless the panel is framed. A row that maps to itself shows no value.
- On the shelf: on the NES or SNES shelf, Screen opens that system's one-row shader page, as in
  ADR 0023; every other shelf opens upstream's platform list.
- The six retro modes stay NES and SNES only (ADRs 0026, 0036).

## Consequences

- The GBA, GB and GBC Screen pages are byte-identical to upstream.
- From the GBA shelf there is no way to reach the NES shader; switch shelves or use the in-game
  menu. Adding NES and SNES to the platform list is an open question (it needs test sites).
