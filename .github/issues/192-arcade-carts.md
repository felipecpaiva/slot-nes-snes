---
title: "Draw the Neo Geo AES cart and the CPS shelf objects and fetch arcade labels"
phase: 17
area: ui-art
type: feature
size: M
depends_on: [185-platform-arcade]
---

## Why
Arcade has no console cart; each board needs a shelf object at the same fidelity as the existing shells, and real art per game.

## Scope
- [x] Neo Geo AES cart (the MVS names its game only on its edge), CPS2 B-board case, CPS1 case, each an outline and relief SVG lit by retro_neutrals.rs; every other neutral byte for byte.
- [x] `tools/fetch-labels.py` arcade systems by set name (ScreenScraper romnom).

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `arcade_cart.rs` | the shells, label wells and colours |
| A2 | `test_fetch_labels_arcade.py` | arcade systems, ids and the set-name lookup |

## Edge cases
| Case | Expected handling |
|---|---|
| A set with no label scan | the fallback media, never a screenshot |

## Acceptance
- [x] A1 and A2 pass; shelf renders compared with an existing shelf.

## Device check (RG34XXSP)
Issue 193.

## References
- ADR 0099
