---
title: "Add Platform::NeoGeo, Cps1 and Cps2 with a set table, full titles and explicit policy"
phase: 17
area: platform
type: feature
size: M
depends_on: [184-arcade-core-build]
---

## Why
An arcade game is a romset zip named after its set; a shelf must list only sets of its board that the pinned core runs, under their full titles.

## Scope
- [x] Three platforms appended to `SHELVES`, `Core::Fbneo` to `EVERY`.
- [x] `slot_store::arcade` and `arcade_sets.tsv` from `tools/arcade-sets.py`; `admits` per board.
- [x] Full titles name, sort and letter-jump the shelf (`Cart::shelf_name`).
- [x] Every policy answered like Mega Drive; CPS canvas 432x288; Neo Geo follows the frame width.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `arcade_platform.rs` | shelves, board filter, BIOS set never a game, titles and sort, table parents and orientation, zip directory CRCs, shader files |
| P2 | `arcade_seat.rs` | a set of each board seats on FBNeo through a real session |

## Edge cases
| Case | Expected handling |
|---|---|
| A CPS1 set in Games/CPS2 | logged and left off |
| neogeo.zip in Games/NEOGEO | left off, it is the BIOS |
| A .7z | not listed |

## Acceptance
- [x] P1 and P2 pass; upstream sites (b) and (e) take their tokens.

## Device check (RG34XXSP)
Issue 193.

## References
- ADR 0099
