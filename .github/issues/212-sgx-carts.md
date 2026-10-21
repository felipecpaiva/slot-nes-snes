---
title: "Draw the Super HuCard and fetch SuperGrafx labels"
phase: 20
area: ui-art
type: feature
size: M
depends_on: [211-platform-sgx]
---

## Why
Super HuCards carry their label the other way up from standard HuCards; the shelf should show that, with real labels.

## Scope
- [x] `RetroShell::Sgx`: the HuCard turned over (contacts above the label), the HuCard white; `.sgx` gets it, `.pce` keeps the HuCard.
- [x] `sgx_cart.svg`, `sgx_cart_detail.svg`, `retro/sgx_neutral.png`; every other neutral byte for byte.
- [x] `tools/fetch-labels.py` system SGX: folder supergrafx, both dats, ScreenScraper 105, SG Enhanced under 31.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `slot-ui/tests/sgx_card.rs` | shell by extension, size and colour, mirrored label and strip, gold contacts, label art and generated label |
| A2 | `retro_bitmap.rs`, `render_nes_shelves.rs` | the Super HuCard in every shell loop |
| A3 | `tools/tests/test_fetch_labels.py` | SGX config, a CRC match under 105, an SG Enhanced card from the PC Engine dat under 31 |

## Edge cases
| Case | Expected handling |
|---|---|
| A SuperGrafx dump named `.pce` | the plain HuCard; the core still runs it as a SuperGrafx |

## Acceptance
- [x] A1 to A3 pass.

## Device check (RG34XXSP)
Issue 214.

## References
- ADR 0103; docs/cart-art/SGX.md
