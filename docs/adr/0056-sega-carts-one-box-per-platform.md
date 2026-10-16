# 0056. Draw the Sega carts from generated neutrals, one box per platform

- Status: Accepted. Extends [0054](0054-bitmap-retro-carts.md). Amended by [0057](0057-sms-box-art-tall-well.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 50](../../.github/issues/50-sega-tracking.md), [patch 0028](../../patches/0028-sega-carts.patch), [docs/cart-art/SEGA.md](../cart-art/SEGA.md)

## Context

The maintainer asked for Game Gear, Master System (cartridge and Sega Card) and Mega Drive
(Japanese and Western) cart shapes, made like the NES and SNES carts of ADR 0054. `seated_box`
and `cart_box` take a platform, not a cart, so every variant of a platform shares one box. The
cited shells differ inside a platform: the Sega Card is portrait (0.632) and the Master System
cartridge landscape (1.565); the Japanese Mega Drive cart (1.388) is taller than the Western one
(1.557), which Genesis and PAL Mega Drive share.

## Decision

- `RetroShell::Sega` with five shells: `gg`, `sms`, `segacard`, `megadrive`, `genesis`, drawn by
  the existing `retro_neutrals.rs` example from our own outline and detail SVGs, coloured with the
  same Overlay. No separate PAL outline: the only dimension source says it is the Genesis mould.
- One box per platform: Game Gear 240 x 234, Master System 240 x 145 (the cartridge; the card is
  drawn at the box height, centred), Mega Drive 240 x 164 (the Japanese cart; the Western cart is
  drawn 146 high, bottom aligned, like the Famicom inside the NES box).
- The shell follows `cart_shell.txt` words `gg`, `sms`, `segacard`, `megadrive`, `genesis`, then
  the rules in SEGA.md section 6: Master System files under 16 KB are Sega Cards; a Japan only
  Mega Drive header region gives the Japanese cart, anything else the Western one.
- Plastic defaults are the photo samples of SEGA.md section 2; `eval-colour-sources.sh` accepts a
  colour recorded in SEGA.md.

## Consequences

- A Sega Card stands smaller on its shelf than a Master System cartridge, and a Genesis cart a
  little lower than a Japanese Mega Drive cart, both at their true proportions.
- No Japanese Mark III cart, EA tab or per-title colour yet: no sourced outline or sample.
- The NES, Famicom, SNES and SFC neutrals are byte-identical when the example is rerun.
