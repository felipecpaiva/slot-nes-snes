---
title: "Give Sega CD the Mega Drive canvas and its own Screen section"
phase: 13
area: video
type: feature
size: S
depends_on: [116-segacd-options]
---

## Why
Step 6. The picture is the Mega Drive VDP's, so the canvas work is a policy line. Every system gets its own Screen section (the maintainer's rule; ADR 0061, 0065).

## Scope
- [ ] `Core::canvas(GenesisPlusGx, SegaCd) = (360, 240)` and the Mega Drive picture rule: 320 or 256 x 224, Stretch follows the live frame width (ADR 0052), Crop as Mega Drive (ADR 0062).
- [ ] `SCREEN_SEGACD` with the Mega Drive rows: Shader (Off then the shared retro list, a Sega CD entry in `Config/sega_shaders.txt`, ADR 0051), Picture (`Config/picture.txt`, ADR 0061) and PAL Speed (issue 66; European discs run at 49.70).
- [ ] The in-game quick menu Shader row offers the same list.
- [ ] Named test sites (g) and (h) gain the token (ADR 0055); CONTRIBUTING.md in the same patch.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `segacd_core.rs` `the_real_us_bios_boots_to_its_menu_and_draws_inside_the_mega_drive_picture` | 320 wide, black outside the picture (with `SLOT_SEGACD_BIOS`) |
| (new) | `segacd_screen.rs` | the section rows; values round-trip through their files |
| (new) | `segacd_canvas.rs` | the canvas and source rects for 320 and 256, Actual, Stretch and Crop |

## Edge cases
| Case | Expected handling |
|---|---|
| A game switching H32 and H40 mid-play | Stretch follows the frame width (ADR 0052) |
| `Config/picture.txt` has no Sega CD line | The Mega Drive default |

## Acceptance
- [ ] `task check` green; frontend cost inside the GBA budget (the Mega Drive path).

## Device check (RG34XXSP)
Shader and Stretch on Sonic CD look like the Mega Drive shelf (issue 113).

## References
- ADR 0050, 0051, 0052, 0061, 0062, 0071, 0094; docs/research/segacd-plan.md section 4
