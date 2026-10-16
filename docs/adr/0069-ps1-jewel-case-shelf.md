# 0069. Show PS1 games as jewel cases with front cover art, and the disc on insert

- Status: Accepted. Amends [0014](0014-real-label-art.md)
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0037](0037-public-nes-snes-art-set.md), [ADR 0054](0054-bitmap-retro-carts.md), [ADR 0057](0057-sms-box-art-tall-well.md), [issue 64](../../.github/issues/64-ps1-cases.md), [issue 68](../../.github/issues/68-deferred-ps1-disc-shelf.md)

## Context

PS1 games are discs, so there is no cart label. ADR 0014 bans screenshots, not covers, and ADR
0057 already uses the front box for Master System. The forks drew PS1 differently:

- bently: a jewel case with an open-and-insert animation;
- gmaster: a printed disc;
- tray: a disc into a slot-loading drive;
- omega-zero: a low-poly disc, or a disc stack for multi-disc games, faced with the disc scan.

## Decision

- Each PS1 game is a jewel case on the shelf, drawn from generated neutral bitmaps with
  upstream's Overlay (the ADR 0054 method), faced with the front cover (ScreenScraper `box-2D`,
  fetched by the user, never committed, as in ADR 0057).
- Region styles: US, EU and JP. The JP case carries the spine strip (obi). The region comes from
  the file name tags or the disc serial in `SYSTEM.CNF` (SLUS and SCUS for US, SLES and SCES for
  EU, SLPS, SCPS and SLPM for JP).
- A multi-disc game is a double jewel case, from its `.m3u` disc count.
- On insert, the case opens and the disc slides in, faced with its label scan (ScreenScraper
  `support-2D`). No label means a plain printed disc, never a screenshot.
- A placeholder flat case ships first, as Phases 1 to 3 did for NES and SNES.
- Deferred: an omega-zero-style 3D disc, or a disc stack, faced with the disc scan, as an
  alternative shelf style (issue 68).

## Consequences

- PS1 shows box art, the second platform after Master System. Every other platform keeps ADR
  0014's label rule.
- Two fetched images per game (cover and disc). `tools/fetch-labels.py` gains a PS1 route.
- Case colours and outlines need cited sources and a blind render check, like the cart art.
- This is the biggest UI item (L). It does not block the PS1 playing patches.
