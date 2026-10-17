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
- [x] Research pass first: jewel case outlines and colours (US, EU, JP with the spine strip; double case), cited or photo-sampled, in `docs/cart-art/PS1.md`. (The obi width is an estimate; US and EU share the mould.)
- [x] Generated neutral bitmaps coloured with upstream's Overlay (ADR 0054 method), single and double case.
- [x] Front cover (`box-2D`) in the case well, contain fit; region from file tags or the `SYSTEM.CNF` serial.
- [x] Insert: the case opens and the disc slides in, faced with `support-2D`, or a plain printed disc when none.
- [x] `tools/fetch-labels.py` PS1 route for `box-2D` and `support-2D`, cached by serial (CRC when the disc has none), never committed.
- [x] Placeholder flat case can ship first. (Skipped: the bitmap cases shipped directly.)

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot-ui` case tests (`crates/slot-ui/tests/ps1_case.rs`) | single and double case geometry; region pick from tags and serial; no screenshot ever used |
| (new) | `tools/tests/test_fetch_labels_ps1.py` | serial from SYSTEM.CNF and PARAM.SFO, CHD by CRC and name, m3u and (Disc N) games, both images from one call |

## Edge cases
| Case | Expected handling |
|---|---|
| No cover fetched | Plain case with the title |
| Cover not 1:1 | Contain fit on the edge colour, never cut |

## Acceptance
- [ ] Blind render judged against reference photos; tests green. (Tests green; the blind render is still to do.)

## Device check (RG34XXSP)
Shelf frame time with 50 cases inside the shelf budget.

## References
- ADR 0014, 0037, 0054, 0057, 0069
