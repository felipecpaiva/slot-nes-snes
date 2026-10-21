# PC Engine SuperGrafx cart art (issue 212)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice. Nothing is guessed.

## The cards

Two shells on the SuperGrafx shelf (patch 0133):

- `RetroShell::Sgx`, the **Super HuCard**, for a `.sgx` file: the five SuperGrafx cards.
- `RetroShell::Hucard`, the TurboGrafx-16 HuCard, for a `.pce` file: Darius Plus and Darius Alpha, which
  are standard PC Engine HuCards with SuperGrafx enhancements.

| Value | Ours | Source |
|---|---|---|
| Five Super HuCards, two standard HuCards | `.sgx` gets the Super HuCard, `.pce` the HuCard | Wikipedia, [PC Engine SuperGrafx](https://en.wikipedia.org/wiki/PC_Engine_SuperGrafx), read 2026-10-21: "There were only five SuperGrafx-specific HuCards produced"; Darius Plus "was the only commercially-released HuCard game to carry the PC-SG mark". No-Intro names the five `.sgx` (`NEC - PC Engine SuperGrafx`) and the two Darius cards `.pce` with `(SG Enhanced)` |
| Size | the HuCard's, seated 240 x 145 (the Sega Card size), drawn 360 x 218 | the same card format: Hudson Soft called the SuperGrafx medium the Super HuCard (Wikipedia, [HuCard](https://en.wikipedia.org/wiki/HuCard), read 2026-10-21); the HuCard size is ADR 0091's |
| Outline | `sgx_cart.svg` is `hucard_cart.svg` | same card |
| Label the other way up | the HuCard turned over: the gold contacts and the cut marks above the label, the ridges below | Wikipedia, PC Engine SuperGrafx: "The labels on SuperGrafx HuCards were upside-down relative to standard HuCards; A standard HuCard will read upside down on a SuperGrafx, while its own are right-side-up." |
| Label well | permille 350, 200, 650, 697 (the HuCard's 350, 303, 650, 800 mirrored top to bottom) | the row above |
| Contact strip | permille 350, 48, 650, 159 (the HuCard's 350, 841, 650, 952 mirrored), painted gold | the row above; the gold is the HuCard's (ADR 0091) |
| Relief | `sgx_cart_detail.svg`: the HuCard ridges and cut marks with their y mirrored and the same light from the top left | the row above; the light is the shelf's, not the card's |
| Branding | on the label scan, not on the shell | the label is the card's printed face; no photo of a Super HuCard shell was found to measure a mark from (Wikimedia Commons, searched 2026-10-21: consoles and controllers only) |

Lit into `assets/retro/sgx_neutral.png` by `examples/retro_neutrals.rs`. Every other neutral regenerates
byte for byte (sha256 compared before and after).

## Shell colour

| Cards | Colour | Source |
|---|---|---|
| Every Super HuCard | `e4 e2 dc`, solid, the HuCard white | Maintainer's choice (ADR 0103): the HuCard white of the TurboGrafx-16 shelf. To be checked against a real card |

A colour in `Config/cart_shell.txt` still overrides it.

## Labels

`tools/fetch-labels.py`, system `SGX`: library folder `supergrafx`; dats `NEC - PC Engine SuperGrafx` (the
five) and `NEC - PC Engine - TurboGrafx 16` (the two Darius cards), libretro-database `metadat/no-intro`;
ScreenScraper `supergrafx` 105 ("PC Engine SuperGrafx", screenscraper.fr `systemeinfos.php?plateforme=105`,
checked 2026-10-21; Skyscraper's `platforms_idmap.csv` at c253bfe has no SuperGrafx row). An
`(SG Enhanced)` card asks under the PC Engine 31, the system No-Intro files it under. libretro-thumbnails has
`NEC - PC Engine SuperGrafx` Named_Logos for all five SuperGrafx cards (checked 2026-10-21) for the Logo
Only fallback; the Darius cards fall back to the ScreenScraper wheel.

Run: `task labels:fetch -- --device --library <library> --only SGX --by-name --logo-fallback`.
