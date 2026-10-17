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

## Amendment, 2026-10-17: what was built (patch 0039-ps1-cases)

- Four generated neutrals in `crates/slot-ui/assets/retro/`, from `examples/retro_neutrals.rs`
  with the ADR 0054 lighting: `jewel_us`, `jewel_eu`, `jewel_jp` and `jewel_double`
  (360 x 317, the cited 142 x 125 mm case), plus `disc_neutral.png` (360 x 360). The nine cart
  neutrals are byte identical when the example is rerun. Outlines, wells and colours are cited in
  [docs/cart-art/PS1.md](../cart-art/PS1.md); the tray black #1f1f1f is sampled from a CC0 photo.
- US and EU are the same mould: no front-visible difference was found, so the region style shows
  only on the Japanese case, as the obi strip over the cover's left edge. Its width is an estimate
  until the blind render check.
- The double case is drawn as a second case behind the front one (the source describes a chubby
  case as about two cases thick). Every PS1 case shares one box, as ADR 0056 does per platform.
- The cover (`Labels/PS1/<stem>.png`) is fitted whole on its edge colour (`box_contain`, ADR 0057)
  in a square well. No cover gives a plain case with the title.
- Region: file name tags, then the `SYSTEM.CNF` serial, then US. Double: an `.m3u` of two or more
  discs. The pick is cached per disc file.
- Insert: `SlotChrome` hands PS1 to `disc_insert.rs` (one upstream line). The lid swings open at
  the shelf spot over the black tray, then the disc travels along upstream's insert path into the
  slot while the case fades; eject runs it backwards. The disc face (`support-2D` at
  `Labels/PS1/disc/<stem>.png`, else the title colour with the title printed) is built as the
  cart's interior and reaches the slot through `Shelf::behind`.
- `tools/fetch-labels.py` PS1 route: one `jeuInfos.php` call per game (system 57) fetches both
  images. ScreenScraper asks for a crc, md5 or sha1 and the size with every call, so the disc file's
  CRC32, size and name are sent, with `serialnum` when the serial is readable (a `.cue`'s first
  track, a `.pbp`'s PARAM.SFO; not a `.chd`). The serial format ScreenScraper expects is not
  documented; the tool sends the Redump form `SLUS-00594`, and `romtype=iso` (the documentation's
example sends `rom`; the values come from `romTypesListe.php`), both unverified against the live
API. A disc's CRC is kept in the cache by path, size and mtime, so a rerun never reads a disc
twice, and a dry run or a run without credentials reads none. Images
  are cached by serial, or by CRC when there is none, not by a dat CRC, because discs are in no
  No-Intro dat. Tests use fakes only; the live API was not called.
