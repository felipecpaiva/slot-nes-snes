# PICO-8 cart art (issue 206)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice. Nothing is guessed.

## The cart

One cart for every PICO-8 game, `RetroShell::Pico8` (patch 0129). PICO-8 has no physical cart; its cart
is the 160x205 PNG every cart is saved as, so the shell takes that picture's shape. Lexaloffle's frame
bitmap is not used: the outline and the strip are drawn by us from the measurements below.

| Value | Ours | Source |
|---|---|---|
| Size | seated 240 x 308, drawn 312 x 400 | the export is 160 x 205 on all 39 of the maintainer's carts (measured 2026-10-21); 205 / 160 x 240 = 307.5, rounded up |
| Outline | top corners and bottom left corner r 3 of 160, a 10 px cut at the bottom right, one unit inside the box | the export's opaque pixels on all 39 carts: rows 0 to 2 start at x 3, 2, 1, and the right edge runs from x 159 at row 195 to x 149 at row 204 |
| Label well | x 16 to 144, y 24 to 152 of 160 x 205 (permille 100, 117, 900, 741), 128 x 128 | where the export keeps the cart's label picture on all 39 carts |
| Title strip | x 15 to 145, y 163 to 195, drawn darker (black at 0.85) | the export's darker band, colour 34 34 34 against the body's 64 64 64, same place on all 39 |

Drawn by us as `crates/slot-ui/assets/pico8_cart.svg` (outline) and `pico8_cart_detail.svg` (the strip),
lit into `assets/retro/pico8_neutral.png` by `examples/retro_neutrals.rs`. Every other neutral
regenerates byte for byte (sha256 compared before and after).

## Shell colour

| Carts | Colour | Source |
|---|---|---|
| Every PICO-8 cart | `64 64 64`, solid | the export's body colour, measured on the 39 carts with the low two bits of each channel masked off (they carry the cart's data) |

A colour in `Config/cart_shell.txt` still overrides it.

## Labels

The label is the cart's own picture, not a scan. `tools/fetch-labels.py`, system `PICO8`, needs no network
and no dat: it crops x 16, y 24, 128 x 128 from a PNG cart, or draws a text cart's `__label__` section (128
lines of 128 digits, 0 to 9 and a to v) in PICO-8's 16 colours and its 16 secret ones, and writes
`Labels/PICO8/<stem>.png`. All 39 of the maintainer's carts gave a label.
