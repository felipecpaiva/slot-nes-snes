---
title: "Draw the PICO-8 cart and take its label from the cart itself"
phase: 18
area: ui-art
type: feature
size: S
depends_on: [196-platform-pico8]
---

## Why
Every shelf shows a cart shell at the same fidelity, faced with the game's own art. A PICO-8 cart already is a picture with its label in it.

## Scope
- [x] `RetroShell::Pico8`: our outline and title strip to the export's geometry, seated 240x308, grey 64 64 64.
- [x] `tools/fetch-labels.py` system `PICO8`: crop the label from a PNG cart, draw a text cart's `__label__`, no network.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `pico8_cart.rs` | one grey shell, chosen colours win, proportions and the square well, the cut corner and the darker strip, the label fills the well |
| A2 | `test_fetch_labels.py` `Pico8` | `__label__` to a 128x128 PNG in the palette, the PNG crop at (16, 24), a bare `.png` skipped, no HTTP |

## Edge cases
| Case | Expected handling |
|---|---|
| A text cart with no `__label__` | missing, reported |
| A PNG that is not 160x205 | error, reported, nothing written |

## Acceptance
- [x] A1 and A2 pass; every other neutral regenerates byte for byte.

## Device check (RG34XXSP)
Issue 199.

## References
- ADR 0101; docs/cart-art/PICO8.md
