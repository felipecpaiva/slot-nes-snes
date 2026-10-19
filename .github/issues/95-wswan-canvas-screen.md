---
title: "Give WonderSwan its canvases and its own Screen section with Shader, Picture and Refresh rows"
phase: 11
area: video
type: feature
size: M
depends_on: [94-wswan-options]
---

## Why
Step 6. Every system gets its own Screen section (the maintainer's rule; ADR 0061, 0065). Horizontal games are an exact 3x fit, vertical ones a 2x fit, and the speed choice of ADR 0092 lives here.

## Scope
- [ ] Canvas chosen once per game from the footer, through the per-game canvas seam of issue 93 (today `Core::canvas` is per platform): horizontal `(240, 160)`, the 224x144 frame centred at (8, 8), Actual 672x432; vertical `(360, 240)`, the 144x224 frame at (108, 8), Actual 288x448. Stretch fills 720x480 in both.
- [ ] The turned view of a vertical game (issue 96's SELECT flip) is a 224x144 frame in the 360x240 canvas, 2x. No per-frame source window in v1 (plan section 4 tradeoff).
- [ ] `SCREEN_WS` section, three rows:
  - Shader: Off, LCD3x (3x horizontal picture; on a 2x vertical picture LCD3x draws as Off, logged once), then the shared retro list; its own `Config/` file (ADR 0051).
  - Picture: Actual (default), Stretch; no Crop. `Config/picture.txt` (ADR 0061).
  - Refresh: 60 Hz (default) and Native, stored like `Config/pal_speed.txt` (ADR 0071's `ini::write`), read at spawn, handed to the options of issue 94. A missing line is 60 Hz; an unknown value is logged and read as 60 Hz.
- [ ] Native runs through `av_rate::owed_frames` with 2-frame ticks; add the host test that path lacks (75.47 fps on a 59.6 Hz tick: about 1.27 frames a tick, never 0, never 3).
- [ ] **No PAL Speed row**: no PAL WonderSwan exists.
- [ ] The in-game quick menu Shader row offers the same list.
- [ ] Named test sites (g) and (h) gain the WonderSwan Screen tokens (ADR 0055); CONTRIBUTING.md in the same patch.
- [ ] Credit nelynes/slotPlus ceed887 (360x240 buffer) and eabb24e (own shader row).

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `wswan_core.rs` `portrait_turns_the_picture_in_the_core_to_144_by_224_with_no_rotation_from_slot` | every pixel of 144x224 at (108, 8) in 360x240 |
| (new) | `wswan_screen.rs` | the section lists Shader, Picture and Refresh; values round-trip through their files |
| (new) | `wswan_canvas.rs` | horizontal and vertical carts get their canvases through a real `Session` |
| (new) | `av_rate` unit test | owed frames for 75.47 fps on a 59.6 Hz tick are 1 or 2 and sum to the right count over 10 s |

## Edge cases
| Case | Expected handling |
|---|---|
| `Config/picture.txt` has no WS line | Actual |
| An unknown shader value in the WS file | Off, logged |
| A vertical cart flipped to turned, then a state loaded | The canvas stays 360x240; the frame shape follows the state's rotation |

## Acceptance
- [ ] `task check` green; frontend cost inside the GBA budget for horizontal games, measured for the 360x240 path.

## Device check (RG34XXSP)
LCD3x and Stretch on a horizontal cart, Actual on a vertical one, both Refresh values (issue 99).

## References
- ADR 0050, 0051, 0060, 0061, 0071, 0092; docs/research/wswan-plan.md sections 3 and 4
