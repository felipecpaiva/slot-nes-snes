---
title: "Give Lynx a 240x160 canvas at 4x and its own Screen section"
phase: 12
area: video
type: feature
size: S
depends_on: [105-lynx-options]
---

## Why
Step 7. The Lynx picture is 160x102. At 4x it is 640x408, which fits the 720x480 panel; it is the only system where 4x fits. Every system has its own Screen section (maintainer's rule).

## Scope
- [x] `Core::canvas(MednafenLynx, Lynx) = (240, 160)`; the frame lands at (40, 29) (pinned by `lynx_core.rs`). Source window 180x120 for 4x, the fork's numbers.
- [x] Own Screen section `SCREEN_LYNX`, rows:
  - **Shader**: Off, Grid, Dot, then the shared retro list. No LCD3x (tuned for 3x, the Lynx sits at 4x). Stored in its own `Config/` file (ADR 0051).
  - **Picture**: Actual 4x (default) and Stretch; no Crop (no overscan). Default in `Config/picture.txt` (ADR 0061).
  - **Lynx Speed**: Native / Panel (issue 107).
  - **Turned carts**: Flip right-turned (default) / As drawn (issue 109).
- [x] Options stay available and the player's choice becomes the default, as for every Screen row.
- [x] The upright "tall" view (102x160 at 3x) is deferred.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `lynx_screen.rs` | the section lists the four rows; defaults; flipping one writes only its line |
| (new) | `canvas` test | 160x102 at 4x is 640x408 centred; Stretch fills 720x480 |

## Edge cases
| Case | Expected handling |
|---|---|
| An older card with no Lynx lines | Defaults |

## Acceptance
- [x] `task check` green; render test of the Screen page with the new section (ADR 0070 scrolling).

## Status
Landed as patches 0071 (section, Shader, Picture) and 0074-lynx-screen (Actual at 4x, 2026-10-19). The turned-carts row is "Flip Right Carts" (On/Off) and arrives with 0077; the speed row with 0075.

## Device check (RG34XXSP)
Actual and Stretch on California Games.

## References
- ADR 0050, 0051, 0061, 0070, 0093
