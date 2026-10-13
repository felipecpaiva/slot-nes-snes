# 0032. Bring NES and SNES labels to Cart Studio as a credited fork, published once ScreenScraper art is available

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 40](../../.github/issues/40-cart-studio-nes-snes.md), [issue 41](../../.github/issues/41-label-fetcher-cli.md), [ADR 0014](0014-real-label-art.md)

## Context

slot's Cart Studio (BrandonKowalski/slot-cart-studio, GPL-3.0-or-later) writes real label art for
GB, GBC and GBA only. The owner was asked on slot discussion #64 whether NES and SNES should come
as a PR or as a credited fork. He answered "Fork away" (2026-10-12) and asked for the fork's address
so he can allowlist it for his art host (art.slot-cfw.fyi) on Cloudflare. NES and SNES label art
comes from ScreenScraper, whose API needs a developer ID; one was requested on the ScreenScraper
forum (topic 24948) on 2026-10-13.

## Decision

NES and SNES support lives in a GPL-3.0 fork of Cart Studio, credited to the owner in its README
and page footer, built against slot-nes-snes's patched cart code. GB, GBC and GBA output stays
byte-identical to the original. The fork is built and tested locally first, and published (fork
on GitHub, GitHub Pages, its own CNAME, no Cloudflare purge step) only once the developer ID
allows a NES and SNES art harvest. Then the owner gets the address.

## Consequences

- Nothing is published that would show NES and SNES carts with no art.
- Until the ID arrives, the CLI fetcher (issue 41) covers GB, GBC and GBA labels on the card.
- The fork must follow the owner's studio on updates; GB/GBC/GBA identity is checked by
  `examples/identity.rs` (339 files) against his tree.
- No Nintendo art or ROMs are ever committed to either repo.
