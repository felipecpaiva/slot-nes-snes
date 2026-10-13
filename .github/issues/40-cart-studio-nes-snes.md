---
title: "Bring NES and SNES label art to Cart Studio, as a PR or a credited fork"
phase: 4
area: ui-art
type: feature
size: L
depends_on: [26-cart-art, 27-cart-shell-grammar-region]
---

## Why
Carts must show the real physical cartridge label, never a screenshot, so the shelf feels like the classic consoles (maintainer goal, 2026-10-12). slot's Cart Studio (https://studio.slot-cfw.fyi/, source github.com/BrandonKowalski/slot-cart-studio, GPL-3.0-or-later) does this for GB, GBC and GBA only. The owner was asked on slot discussion #64 (2026-10-12) whether NES and SNES should arrive as a PR to slot-cart-studio or as a credited fork. This issue starts only after his answer.

## Scope
- [x] Record the owner's answer here and in docs/DECISIONS.md.
- [ ] If PR: open an issue on slot-cart-studio first (the owner asks for an issue before a PR), then a PR adding NES and SNES as an optional mode built against slot-nes-snes's patched slot-ui (Studio compiles slot's own cart code, pinned by `slot.ref`).
- [ ] If fork: a GPL-3.0 fork credited to the owner in its README and page footer, built against slot-nes-snes, hosted on this repo's GitHub Pages.
- [x] Platform tables in either case: `card.js` PLATFORMS and EXTENSIONS, `libretro.js` NAMES, `tools/harvest.py` SS_SYSTEM gain NES and SNES.
- [x] Identification: libretro-database no-intro dats. NES CRC32 over the whole file including the 16-byte iNES header (dat sizes are 16384+16); SNES CRC32 after stripping a 512-byte copier header when `len % 1024 == 512`.
- [ ] Art: a NES and SNES harvest (ScreenScraper `support-texture` for Real Label, `wheel` for Logo Only) run with our own ScreenScraper credentials. First probe five known games per system to confirm coverage before building on it.
- [ ] Output: `Labels/NES/<stem>.png` and `Labels/SNES/<stem>.png` pre-cropped to each variant's label box (NES, Famicom, SNES, Super Famicom sizes from 26-cart-art), and `Labels/cart_shell.txt` lines with the `nes`, `famicom`, `snes`, `sfc` outline words from 27-cart-shell-grammar-region.

## Status (2026-10-13)
- Owner's answer on slot discussion #64: "Fork away". This is a credited GPL-3.0 fork. He asked for the studio's address so he can allowlist it for art.slot-cfw.fyi on Cloudflare.
- The fork is built locally (`~/contrib/slot-cart-studio`, branch `nes-snes`): NES/SNES platform tables, CRC rules, label sizes per variant, outline words, credit in README and footer. GB/GBC/GBA output is byte-identical to upstream (339 files). Tests: 65 cargo, 52 node, 17 python.
- Blocked: the NES/SNES art harvest needs a ScreenScraper developer ID (requested on the ScreenScraper forum, topic 24948, 2026-10-13). Publishing waits for it (maintainer's choice): then fork on GitHub, GitHub Pages with a new CNAME and no Cloudflare purge step, CI built against the patched slot, and send Brandon the address.

## Tests
| ID | File | Asserts |
|---|---|---|
| T48 | studio (PR or fork) | A sample card with NES, Famicom, SNES and Super Famicom ROMs gets correctly sized labels and valid cart_shell.txt lines; preview matches slot's rendered cart |

## Edge cases
| Case | Expected handling |
|---|---|
| Owner prefers neither option | Ship only 41-label-fetcher-cli and close this issue with the reason |
| ScreenScraper has no `support-texture` for a game | Fall back to Logo Only (`wheel` on a generated ground), never to a screenshot or box art |
| Studio rewrites a NES/SNES shell line to `auto` | Documented: NES/SNES outline overrides belong in Config/cart_shell.txt, which Studio does not write |

## Acceptance
- [x] Owner's choice recorded.
- [ ] NES and SNES labels and shells written by Studio (or the fork) for the sample card, and shown correctly on the RG34XXSP.
- [x] Nothing from Nintendo committed to any of our repos.

## Device check (RG34XXSP)
Insert the sample card, check every cart on the NES and SNES shelves shows its real label on the right cart shape.

## Review notes
- Studio is the owner's project: follow his answer, credit him, and keep his GB/GBC/GBA behaviour unchanged.
- Label art is Nintendo's: fetched at user time or hosted under the art set's own terms, never committed.

## References
- docs/PLAN.md Phase 4; slot discussion #64; github.com/BrandonKowalski/slot-cart-studio (`studio.js`, `card.js`, `libretro.js`, `src/label.rs`, `src/choice.rs`, `tools/harvest.py`)
- `slot: crates/slot-store/src/scan.rs:75-90` (label matching), `slot: crates/slot/src/label_cache.rs`, `slot: crates/slot-ui/src/art.rs:3-25` (cover fit), `slot: crates/slot-store/src/cart_shell.rs` (grammar)
