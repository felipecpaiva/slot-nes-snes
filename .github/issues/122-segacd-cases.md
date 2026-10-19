---
title: "Draw Sega CD games as jewel cases and fetch their covers"
phase: 13
area: ui-art
type: feature
size: M
depends_on: [114-platform-segacd]
---

## Why
Step 10. Sega CD games are discs, so ADR 0069's jewel case applies: the case on the shelf faced with the front cover, the disc sliding in on insert faced with its label scan. The renderer exists (patch 0039); this adds the Sega CD styles and the art route.

## Scope
- [ ] Reuse `disc_insert.rs` and the jewel neutrals. Styles: US and EU jewel case; JP with the spine strip (obi), as PS1. The US long box is a deferred alternative style (like issue 68), not v1.
- [ ] Region: file name tags, then the 0x20b byte for `.cue` and `.iso` (shared with issue 115), else US. Double case from an `.m3u` of two or more discs.
- [ ] `tools/fetch-labels.py`: a `SEGACD` entry, ScreenScraper system id **20** (Skyscraper `platforms_idmap.csv` row `segacd,20,20,21`, Gemba/skyscraper `290d2c0`), front cover `box-2D` to `Labels/SEGACD/<stem>.png`, disc `support-2D` to `Labels/SEGACD/disc/<stem>.png`, matched by name (Redump "Sega Mega CD & Sega CD" dat, `redump.org/datfile/mcd/`), the PS1 route.
- [ ] libretro-thumbnails `Sega_-_Mega-CD_-_Sega_CD` (Named_Boxarts, Named_Logos, Named_Snaps, Named_Titles) for the logo fallback, as GG and PS1.
- [ ] Case colours and any outline differences cited in docs/cart-art/SEGACD.md, blind render check.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot-ui/tests/segacd_cases.rs` | region style picks, double case from an m3u, cover fitted, no cover gives a plain case with the title |
| (new) | `tools/tests/test_fetch_labels_segacd.py` | the SEGACD entry's id, folders and media |

## Edge cases
| Case | Expected handling |
|---|---|
| A cover with the long-box aspect | Fitted whole on its edge colour (`box_contain`, ADR 0057) |
| No disc scan | A plain printed disc with the title, never a screenshot |

## Acceptance
- [ ] `task check` green; the neutrals of every other platform byte-identical when the example reruns.

## Device check (RG34XXSP)
The shelf with covers fetched for the 62 games; insert and eject animations at full speed.

## References
- ADR 0014, 0057, 0069, 0094; docs/cart-art/PS1.md; docs/research/segacd-plan.md section 6
