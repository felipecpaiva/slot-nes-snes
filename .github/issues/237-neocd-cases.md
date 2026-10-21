---
title: "Draw Neo Geo CD discs in the jewel case and fetch their covers and disc scans"
phase: 23
area: ui-art
type: feature
size: S
depends_on: [235-platform-neocd]
---

## Why
Neo Geo CD games shipped in the standard jewel case, Japanese releases with a spine card.

## Scope
- [x] The PlayStation jewel case (ADR 0069), the Japanese style for a disc tagged (Japan), the disc from `Labels/NEOCD/disc/`.
- [x] `tools/fetch-labels.py` system NEOCD, ScreenScraper 70, by name like the Sega CD; docs/cart-art/NEOCD.md.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `slot-ui/tests/neocd_case.rs` | the case box, the style per region, the disc art path, a Neo Geo cart has no disc |
| A2 | `tools/tests/test_fetch_labels_neocd.py` | the system entry, a disc by name under 70 with cover and disc scan, never hashed |

## Edge cases
| Case | Expected handling |
|---|---|
| The translated disc has no Redump entry | by name, with the sibling alias in docs/cart-art/NEOCD.md for the logo |

## Acceptance
- [x] A1 and A2 pass.

## Device check (RG34XXSP)
Issue 238.

## References
- ADR 0107; ADR 0069; ADR 0104
