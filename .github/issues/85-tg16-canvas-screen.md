---
title: "Give TG16 the 360x240 canvas and its own Screen section with Shader and Picture rows"
phase: 10
area: video
type: feature
size: S
depends_on: [84-tg16-options]
---

## Why
Step 6. Every system gets its own Screen section (the maintainer's rule; ADR 0061, 0065). TG16 rides the SNES canvas, so the picture work is small.

## Scope
- [x] `Core::canvas(MednafenPceFast, Tg16) = (360, 240)`: 256x240 at x 52, Actual 512x480 on the panel; 320 to 352 wide at 1x; 512 wide halved by `copy_centred`'s 2:1 blend (patch 0006).
- [x] Stretch fills 720x480 and follows the frame width, as Mega Drive does (ADR 0052).
- [x] `SCREEN_TG16` section with a Shader row (Off, then the shared retro list; no LCD3x, the picture is 2x) stored in its own `Config/` file (ADR 0051), and a Picture row (Actual, Stretch, Crop; ADR 0061, 0062) in `Config/picture.txt`. Default: the maintainer's call, Crop like NES and SNES or Actual.
- [x] **No PAL Speed row**: the system is 60 Hz only, and 59.82 fps is inside ADR 0071's 2 fps window.
- [x] The in-game quick menu Shader row offers the same list.
- [x] Named test sites (g) and (h) gain the TG16 Screen tokens (ADR 0055); CONTRIBUTING.md in the same patch.
- [x] Credit nelynes/slotPlus 92b7022 (Screen page).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `tg16_screen.rs` | the section lists Shader and Picture only; values round-trip through their files |
| (new) | `tg16_canvas.rs` | every pixel of the 256x240 picture at (52, 0), black bars, on the real core through slot's open path |

## Edge cases
| Case | Expected handling |
|---|---|
| `Config/picture.txt` has no TG16 line | The chosen default |
| An unknown shader value in the TG16 file | Off, logged |
| A game switching width mid-play | Canvas fixed; source rect follows the frame (ADR 0050, 0052) |

## Acceptance
- [ ] `task check` green; frontend cost inside the SNES budget (same 360x240 path).

## Device check (RG34XXSP)
Shaders, Crop and Stretch look right on a real HuCard; a wide-mode game (issue 90).

## References
- ADR 0050, 0051, 0052, 0061, 0062, 0071, 0091; docs/research/tg16-plan.md section 4

## Outcome (2026-10-19)
In patch `0053-platform-tg16` (see issue 83). Default Picture: Crop, 8 lines off the top and bottom (ADR 0091). Tests: `slot/tests/tg16_screen.rs` (section rows and labels, no PAL Speed, the row shows only with TG16 games, the shader walks the retro list into `Config/tg16_shader.txt`, the Picture row walks Crop, Stretch, Actual into `Config/picture.txt`, a `picture.txt` with no TG16 line gives Crop, the Crop and Stretch source rects, the in-game Shader row) and `slot-store/tests/tg16_platform.rs` (an unknown shader value reads Off).
