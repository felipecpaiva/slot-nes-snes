---
title: "Draw the Virtual Boy cart and fetch its labels"
phase: 16
area: ui-art
type: feature
size: M
depends_on: [175-platform-vb]
---

## Why
The shelf must show a real Virtual Boy cart with its label, at the fidelity of the other shells.

## Scope
- [x] `RetroShell::Vb`: outline, relief and darker dust cap, lit into vb_neutral.png; other neutrals byte for byte.
- [x] `tools/fetch-labels.py` system VB: dat Nintendo - Virtual Boy, ScreenScraper 11, Named_Logos for the Logo Only fallback.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `vb_cart.rs` | shell, grey, chosen colour wins, size, label well, cap darker |
| A2 | `tools/tests/test_fetch_labels.py` | VirtualBoy: folder, dat, id 11, CRC match lands in Labels/VB |

## Edge cases
| Case | Expected handling |
|---|---|
| A shell colour in cart_shell.txt | wins over the grey |

## Acceptance
- [x] A1 and A2 pass; shelf renders compared with the 32X shelf.

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
