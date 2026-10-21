---
title: "Give Sega CD the Mega Drive canvas and its own Screen section"
phase: 21
area: video
type: feature
size: S
depends_on: [219-segacd-options]
---

## Why
Step 6. The picture is the Mega Drive VDP's, so the canvas work is a policy line. Every system gets its own Screen section (the maintainer's rule; ADR 0061, 0065).

## Scope
- [x] `Core::canvas(GenesisPlusGx, SegaCd) = (360, 240)` and the Mega Drive picture rule: 320 or 256 x 224, Stretch follows the live frame width (ADR 0052), Picture as Mega Drive: Stretch, Actual, 4:3 (ADR 0062, 0087).
- [x] `SCREEN_SEGACD` with the Mega Drive rows: Shader (Off then the shared retro list, its own `Config/segacd_shader.txt` like the newer shelves), Picture (`Config/picture.txt`, ADR 0061) and PAL Speed (issue 66; European discs run at 49.70).
- [x] The in-game quick menu Shader row offers the same list.
- [x] Named test sites (g) and (h) gain the token (ADR 0055); CONTRIBUTING.md in the same patch.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `segacd_core.rs` `the_real_us_bios_boots_to_its_menu_and_draws_inside_the_mega_drive_picture` | 320 wide, black outside the picture (with `SLOT_SEGACD_BIOS`) |
| (done, 0137) | `segacd_screen.rs` | the section rows; values round-trip through their files |
| (done, 0137) | `segacd_screen.rs` `the_picture_is_the_mega_drive_picture_with_four_three_and_its_own_line` | the canvas and source rects for 320 and 256 equal the Mega Drive's |

## Edge cases
| Case | Expected handling |
|---|---|
| A game switching H32 and H40 mid-play | Stretch follows the frame width (ADR 0052) |
| `Config/picture.txt` has no Sega CD line | The Mega Drive default |

## Acceptance
- [x] `task check` green; frontend cost inside the GBA budget (the Mega Drive path).

## Device check (RG34XXSP)
Shader and Stretch on Sonic CD look like the Mega Drive shelf (issue 216).

## References
- ADR 0050, 0051, 0052, 0061, 0062, 0071, 0104; docs/research/segacd-plan.md section 4
