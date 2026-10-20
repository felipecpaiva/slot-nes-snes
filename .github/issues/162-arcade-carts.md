---
title: "Draw the Neo Geo MVS cart and the CPS shelf objects and fetch arcade labels"
phase: 16
area: ui-art
type: feature
size: M
depends_on: [155-platform-arcade]
---

## Why
Arcade has no console cart; each board needs a shelf object at the same fidelity as the existing shells, and real art per game.

## Scope
- [ ] Neo Geo MVS cart, CPS2 B-board case, CPS1 object, each an outline and relief SVG lit by retro_neutrals.rs; every other neutral byte for byte.
- [ ] `tools/fetch-labels.py` arcade systems by set name (ScreenScraper romnom).

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `arcade_cart.rs` | the shells, label wells and colours |
| A2 | `test_fetch_labels.py` | arcade systems, ids and the set-name lookup |

## Edge cases
| Case | Expected handling |
|---|---|
| A set with no label scan | the fallback media, never a screenshot |

## Acceptance
- [ ] A1 and A2 pass; shelf renders compared with an existing shelf.

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
