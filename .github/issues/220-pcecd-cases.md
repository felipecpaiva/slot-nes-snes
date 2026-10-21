---
title: "Draw PC Engine CDs in the jewel case with their disc, and fetch covers and disc scans"
phase: 21
area: ui-art
type: feature
size: S
depends_on: [218-platform-pcecd]
---

## Why
Every shelf has a real object. A PC Engine CD shipped in the standard jewel case the PlayStation shelf already draws.

## Scope
- [x] `Platform::Pcecd` wears the jewel case, the Japanese spine strip for a `(Japan)` disc, the plain case otherwise; the disc slides out on insert, its scan from `Labels/PCECD/disc/`.
- [x] `tools/fetch-labels.py` system `PCECD`: cover and disc scan from one jeuInfos call under ScreenScraper 114.

## Tests
| ID | File | Asserts |
|---|---|---|
| A1 | `slot-ui/tests/pcecd_case.rs` | the PS1 box, case by region tag, no serial or double case, the disc and its art path, a HuCard carries no disc |
| A2 | `tools/tests/test_fetch_labels_ps1.py` (`PcEngineCd`) | system row, cover and disc under 114, disc-tagged files stay separate |

## Edge cases
| Case | Expected handling |
|---|---|
| No cover or disc scan | the plain case and a disc in the title colour |

## Acceptance
- [x] A1 and A2 pass.

## Device check (RG34XXSP)
Issue 221.

## References
- ADR 0104; docs/cart-art/PCECD.md; ADR 0069
