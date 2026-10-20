---
title: "Draw the 32X cart and fetch its labels"
phase: 15
area: ui-art
type: feature
size: M
depends_on: [145-platform-s32x]
---

## Why
The 32X cart differs from the Mega Drive cart in shape, the same in every region.

## Scope
- [x] `RetroShell::S32x`, outline and relief SVGs, neutral PNG, black shell.
- [x] fetch-labels.py system `32X`, ScreenScraper 19.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `s32x_cart.rs` | one shell for every region, size, label well, black, label art in the well |
| A2 | `test_fetch_labels.py` Sega32X | dat, id 19, label lands in Labels/32X, name search drops 32X |

## Edge cases
| Case | Expected handling |
|---|---|
| Every other neutral PNG | regenerates byte for byte |

## Acceptance
- [x] A1 and A2 pass.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
