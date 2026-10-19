---
title: "Map the Lynx buttons and turn carts made to be held sideways"
phase: 12
area: input
type: feature
size: M
depends_on: [105-lynx-options]
---

## Why
Step 9. Lynx has A, B, Option 1, Option 2 and Pause. Some carts are made to be held turned left or right. The core turns the pad itself when `lynx_rot_screen` asks (pinned by `the_core_turns_the_pad_for_a_rotated_cart_only_when_lynx_rot_screen_asks_it_to`), so slot drives that option rather than turning the pad in its own code (ADR 0093).

## Scope
- [x] Buttons: RetroPad B is Lynx A, RetroPad A is Lynx B (the core's descriptors), L and R are Option 1 and 2, START is Pause. SELECT stays slot's.
- [x] Which carts are turned: header byte 0x3a; the core's rotated checksum entries (Centipede proto, Lexis, NFL Football and Raiden beta left; Gauntlet III x2 and Klax (USA, Europe) right); nelynes' by-title list (d7d0e74: Klax and Gauntlet III right, Lexis and NFL Football left, any dump); `Config/lynx_rotation.txt` (`<stem> = left | right | none`) wins.
- [x] Raw picture is the Lynx LCD as drawn, so the player turns the handheld. **Turned carts** row (issue 106): "Flip right-turned" (default) draws right carts flipped 180 and sets `lynx_rot_screen=180` (the core turns the pad 180 to match), so every turned cart is played with the handheld turned the same way; "As drawn" sets `0` for all.
- [x] The flip is a reversed row copy in our `canvas.rs` (or answering `SET_ROTATION` 2 as a flip); never a full 90 degree turn in this issue.
- [x] Whether "same way" should be counter-clockwise (nelynes 185257a) or clockwise on the RG34XXSP clamshell is the device check.
- If the maintainer picks Handy: it rotates in software itself (`handy_rot`); the plan becomes "set `handy_rot` per cart", with the same list and override file.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `lynx_core.rs` pad rotation test | unanswered and `0` leave the pad raw; `auto` turns a right cart 270; `180` turns Up into Down (BIOS-gated) |
| (new) | `lynx_rotation.rs` | header byte, title list, override file precedence; the option value handed to the core |
| (new) | canvas test | the 180 flip is a reversed row copy |

## Edge cases
| Case | Expected handling |
|---|---|
| A dump whose header says nothing but the title list does | Turned (title wins over header) |
| Override line with an unknown value | Logged, ignored |

## Acceptance
- [x] `task check` green.

## Status
Landed as patch 0077-lynx-rotation (2026-10-19). As built: the flip answers `SET_ROTATION` 2 (quarter turns refused); the core's own checksum list is not read (its right carts are all on the title list); the row is Flip Right Carts in `Config/lynx_flip.txt`.

## Device check (RG34XXSP)
Klax (right) and Lexis (left): picture upright with the handheld turned, the d-pad matches.

## References
- ADR 0093; nelynes/slotPlus d7d0e74, 185257a, 747cf1d
