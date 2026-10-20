# Atari 2600 and 7800 cart art (issues 161 and 169)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice.

## The carts

One cart per system, `RetroShell::A2600` and `RetroShell::A7800` (patch 0101).

| Value | Ours | Source |
|---|---|---|
| Size, both systems | 82 x 98 mm, seated 240 x 287, drawn 312 x 373 | Atari 2600 cartridge 98 mm high, 82 mm wide, 20 mm deep (search result citing ConsoleMods' "Dimensions for Game Cartridges", checked 2026-10-20; the page itself is behind a bot wall); 7800 carts are the same size and shape as the 2600 ones (The Video Game Critic, [7800 page](https://videogamecritic.com/7800info.htm); AtariAge forum, [will 7800 cartridge shells work for 2600 games](https://forums.atariage.com/topic/325112-will-7800-cartridge-shells-work-for-2600-games/)) |
| 2600 shell | the Atari Inc. cart: a ribbed grip across the top, a groove, the label well below (permille 100, 330, 900, 960) | maintainer's choice from the Atari Inc. carts in the library; the rib count and spacing are ours |
| 7800 shell | the Atari Corp. cart: a raised top cap, short grip ridges down both sides, the label well higher (permille 110, 160, 890, 950) | same sources (Atari Corp. made one thicker shell for 2600 and 7800 games); the relief is ours |
| Plastic | 2600 black 0x22 0x21 0x22, 7800 black 0x2c 0x2c 0x2e | maintainer's choice: near the Mega Drive black, the 7800 shell a shade lighter so the two shelves read apart |
| Activision, Parker Brothers and other third-party 2600 shells | not drawn; every 2600 game takes the Atari shell | maintainer's choice for now |

Drawn by us as `crates/slot-ui/assets/a2600_cart.svg`, `a7800_cart.svg` and their detail SVGs, lit into
`assets/retro/a2600_neutral.png` and `a7800_neutral.png` by `examples/retro_neutrals.rs`. Every other
neutral regenerates byte for byte.

## Labels

`tools/fetch-labels.py` systems `A2600` and `A7800`: dats `Atari - 2600` and `Atari - 7800`
(libretro-database metadat/no-intro), ScreenScraper ids 26 and 41 (Skyscraper `platforms_idmap.csv` at
c253bfe, rows `atari2600,26,28,22` and `atari7800,41,34,27`). A headered `.a78` is also hashed without its
128-byte header. libretro-thumbnails has `Atari - 2600` Named_Logos (the `--logo-fallback` source) and
no `Atari - 7800` ones (404, checked 2026-10-20), so a 7800 game without a label falls back to its
ScreenScraper wheel.
