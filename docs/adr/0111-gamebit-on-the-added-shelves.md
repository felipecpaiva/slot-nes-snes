# 0111. Gamebit lists the 23 added shelves, with icons from Libretro's retrosystem set

- Status: Accepted
- Date: 2026-11-08
- Deciders: maintainer (Felipe Paiva)
- Related: [0110](0110-rebase-to-slot-v1-14-0.md), patch 0163, `crates/slot/tests/server_shelves.rs`

## Context

Gamebit, slot's web page for the card, only knew upstream's four Game Boy shelves. A test card with one game on
each added shelf showed it: `/api/tags` listed GBA, GBAV, GBC and GB, and every other shelf answered
`404 platform not found`. The page hard-codes the same four tags, so even a fixed server would have shown
nothing. Saves and states were counted for mgba, gpsp and gambatte only, so a state saved by one of our cores
was invisible and a rename or purge left its state folder behind.

## Decision

- The server keeps `tags` as upstream's four, in upstream's order, and lists the other 23 shelves under a new
  `more` key. Upstream's `tags_are_the_four_platforms` test stays as it is.
- Every shelf route, state route and rename or purge walks `Core::EVERY`, not `Core::ALL`. For the Game Boy
  shelves the result is the same, because `runs` filters it.
- The page gets its own tables for the added shelves (names, cart shapes, icons) and a dashboard card for each: the
  Libretro `retrosystem` icon (the set upstream's three Game Boy icons come from, CC BY 4.0, credited in the page
  footer) or, for PICO-8 which the set lacks, a text card.
  Upstream's `PLATFORM_TAGS`, `HOME_TAGS` and names stay as its `page.spec.ts` pins them. The BIOS tab is
  hidden on the added shelves, whose BIOS files are not one `<tag>_bios.bin`.
- `server_shelves.rs` holds the web table of cart shapes equal to the size the server renders.

## Consequences

- Games on every added shelf can be listed, uploaded, renamed, purged and given art from Gamebit.
- Icons are 22 SVG files committed in `web/public/platforms/` at a pinned retroarch-assets commit (patch 0164, see
  `docs/SUPPLY-CHAIN.md`). Their "LibRetro" marks stay as drawn.
- Not done, on purpose: an icon for PICO-8, multi-file disc uploads (cue plus bin, m3u), games on the Expansion Card (the server only reads
  `Games/`), a BIOS tab per system, and a test on the device over Wi-Fi (the page was driven on the Mac against a
  test card).
- On each upstream rebase: `games.rs`, `states.rs` and the three web files in the touch point map.
