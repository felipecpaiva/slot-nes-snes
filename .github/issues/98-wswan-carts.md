---
title: "Draw WonderSwan carts (black and clear shells) and fetch their labels"
phase: 11
area: ui-art
type: feature
size: M
depends_on: [93-platform-wswan]
---

## Why
Step 9. Every shelf gets real-looking carts (ADR 0006, 0054).

## Scope
- [ ] WonderSwan cart in the retro bitmap renderer (ADR 0054), two shells: black (WonderSwan) and clear (Color), chosen by the footer colour flag (issue 93), falling back to the extension when the footer is unreadable.
- [ ] nelynes/slotPlus 77fd357 and 21cc4b0 as a drawing reference only, credited (GPL-3.0); we draw our own.
- [ ] `tools/fetch-labels.py`: a `WS` entry with both dats, `Bandai - WonderSwan` and `Bandai - WonderSwan Color` (libretro-database `metadat/no-intro`), extensions `.ws .wsc`. ScreenScraper ids `wonderswan` 45 and `wonderswancolor` 46 (Skyscraper `platforms_idmap.csv` at ccd49ae, rows `wonderswan,45,48,4925` and `wonderswancolor,46,49,4926`). Pick the id per ROM from the footer colour flag, the same per-system id choice NGP needs (issue 78 on its branch); do not add a second shelf.
- [ ] docs/cart-art/WS.md with the shell references and sources.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `tools/tests` | a Color footer asks ScreenScraper for id 46, a mono one for 45; both dats match by CRC |
| (new) | card tests | the two shells render at the shelf size with and without a label |

## Edge cases
| Case | Expected handling |
|---|---|
| A ROM in neither dat | Placeholder label, shell from the footer |
| A mono-compatible Color game (footer says mono, listed in the Color dat) | The footer decides the shell; the dat only finds the label |

## Acceptance
- [ ] `task check` green, card tests included.

## Device check (RG34XXSP)
The shelf with ten carts, both shells, scrolls without a dropped frame.

## References
- ADR 0006, 0054, 0092; docs/research/wswan-plan.md section 7
