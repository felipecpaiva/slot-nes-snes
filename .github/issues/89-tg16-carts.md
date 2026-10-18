---
title: "Draw HuCards and fetch their labels"
phase: 10
area: ui-art
type: feature
size: M
depends_on: [83-platform-tg16]
---

## Why
Step 9. Every shelf shows its own cart shape with label art (ADR 0054, 0056). HuCards are credit-card sized, white with gold contacts and a square label.

## Scope
- [ ] Retro bitmap HuCard (ADR 0054): one shape, the label square in the lower half; nelynes/slotPlus 92b7022 `assets/src/carts.py` as the credited drawing reference. US TurboChip vs Japanese HuCard looks are a later nicety.
- [ ] `tools/fetch-labels.py` `SYSTEMS` row `"TG16": ("pcengine", {".pce"}, ["NEC - PC Engine - TurboGrafx 16"], 31)`. The id is cited from Skyscraper's `platforms_idmap.csv` (Gemba/skyscraper ccd49ae, row `pcengine,31,40,34`; unchanged at master c253bfe, 2026-10-18); the dat is libretro-database `metadat/no-intro`.
- [ ] CRC a `.pce` without its 512-byte copier header when `size % 8192 == 512`, as the script does for iNES and SMC headers, so headered dumps match the No-Intro dat.
- [ ] The label fetcher's Logo Only fallback (patch 0049) covers TG16 if libretro-thumbnails has `NEC - PC Engine - TurboGrafx 16` logos; check, do not assume.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | slot-ui cart test | the HuCard bitmap draws with and without a label |
| (new) | `tools/test_fetch_labels.py` | a headered and a headerless `.pce` give the same CRC; the TG16 row uses id 31 |

## Edge cases
| Case | Expected handling |
|---|---|
| A ROM not in the dat | By-name pass, then Logo Only, as for other systems |
| A headered dump | Header skipped before the CRC |

## Acceptance
- [ ] `task check` green; a dry run of the fetcher on a sample TG16 folder finds labels.

## Device check (RG34XXSP)
The HuCards look right on the shelf and seated (issue 90).

## References
- ADR 0054, 0056, 0091; docs/research/tg16-plan.md section 6
