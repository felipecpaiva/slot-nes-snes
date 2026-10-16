---
title: "Draw PS1 games as jewel cases with cover art, region styles and the disc on insert"
phase: 8
area: ui-art
type: feature
size: L
depends_on: [58-platform-ps1]
---

## Why
Step 11. ADR 0069: the shelf look for discs.

## Scope
- [ ] Research pass first: jewel case outlines and colours (US, EU, JP with the spine strip; double case), cited or photo-sampled, in `docs/cart-art/PS1.md`.
- [ ] Generated neutral bitmaps coloured with upstream's Overlay (ADR 0054 method), single and double case.
- [ ] Front cover (`box-2D`) in the case well, contain fit; region from file tags or the `SYSTEM.CNF` serial.
- [ ] Insert: the case opens and the disc slides in, faced with `support-2D`, or a plain printed disc when none.
- [ ] `tools/fetch-labels.py` PS1 route for `box-2D` and `support-2D`, cached by CRC, never committed.
- [ ] Placeholder flat case can ship first.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot-ui` case tests | single and double case geometry; region pick from tags and serial; no screenshot ever used |

## Edge cases
| Case | Expected handling |
|---|---|
| No cover fetched | Plain case with the title |
| Cover not 1:1 | Contain fit on the edge colour, never cut |

## Acceptance
- [ ] Blind render judged against reference photos; tests green.

## Device check (RG34XXSP)
Shelf frame time with 50 cases inside the shelf budget.

## References
- ADR 0014, 0037, 0054, 0057, 0069
