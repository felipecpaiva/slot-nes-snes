# 0037. Host the NES and SNES label art in a public art repo of our own

- Status: Accepted
- Date: 2026-10-14
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0032](0032-cart-studio-credited-fork.md), [issue 40](../../.github/issues/40-cart-studio-nes-snes.md), repo felipecpaiva/slot-nes-snes-art

## Context

The Cart Studio fork (ADR 0032) needs NES and SNES label art over https. Brandon's studio does the
same for GB, GBC and GBA with a harvested ScreenScraper set on his own host (art.slot-cfw.fyi).
ScreenScraper's media are CC BY-NC-SA 4.0: they may be shared non-commercially, with credit, under
the same licence. Our developer ID was granted on 2026-10-14. Issue 40 had said no Nintendo art
would be committed to any of our repos.

## Decision

The NES and SNES art set lives in its own public repo, felipecpaiva/slot-nes-snes-art, served by
GitHub Pages: CRC-named images plus index.json, licensed CC BY-NC-SA 4.0 with credit to
ScreenScraper. It is separate from slot-nes-snes and from the studio fork, which stay free of
Nintendo art. The maintainer chose this after the device had its labels from the CLI fetcher.

## Consequences

- The web studio shows real NES and SNES labels for every user.
- The set is shared non-commercially only, and must keep its licence and credit.
- If ScreenScraper or a rights holder asks, the art repo can be taken down on its own without
  touching the code repos.
- Amends issue 40's rule: Nintendo art stays out of the code repos, but the art set is published.
