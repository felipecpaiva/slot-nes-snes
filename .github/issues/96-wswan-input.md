---
title: "Map the WonderSwan X and Y pads for horizontal and vertical games"
phase: 11
area: input
type: feature
size: M
depends_on: [93-platform-wswan]
---

## Why
Step 7, the largest item. The WonderSwan has two 4-way pads (X and Y), A, B and Start; vertical games use the Y pad as their D-pad. With `wswan_rotate_keymap=disabled` (issue 94) the core reads one landscape map (X pad on the D-pad, Y pad on R2 up, R right, L2 down, L left, A, B, START), so slot does all the mapping.

## Scope
- [ ] Horizontal games: D-pad is the X pad, A and B are A and B, START is Start; L held turns the D-pad into the Y pad; R held turns the face diamond (X up, A right, B down, Y left) into the Y pad; X and Y are turbo A and B with no modifier; L and R never reach the core as themselves; SELECT never reaches the core.
- [ ] Vertical games, upright: D-pad is the Y pad turned so up is the game's up, the face diamond is the X pad, L and R are A and B.
- [ ] The flip, vertical games only: a SELECT tap swaps upright and turned, setting `wswan_rotate_display` and the matching map together; remembered per cart in its state. Horizontal games ignore it.
- [ ] SELECT combos stay slot's (Select+X picture, Select+Y guard): the flip fires on a SELECT release with no other button pressed.
- [ ] Our own code and tests, in the `snes_input.rs` pattern; credit nelynes/slotPlus 69b8379, 0f895d3 and 2ab147a for the tables in the patch commit.
- [ ] Device question, recorded in issue 99: whether L2 and R2 should carry the Y pad directly (the core's own descriptors) as an alternative. If kept, it is a Screen-section choice, never a silent change.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `wswan_input.rs` | every device button reaches the core as the documented RetroPad id for each layout and modifier; L, R and SELECT never reach the game; both modifiers at once drive the Y pad from both clusters |
| (new) | `wswan_input.rs` `select_flips_only_a_vertical_game` | real core: SELECT tap turns a vertical cart's frame, not a horizontal one's; Select+X does not flip |

## Edge cases
| Case | Expected handling |
|---|---|
| A GBA game after a WonderSwan game | Input as in a GBA-only run (`wswan_then_gba.rs`, issue 97) |
| A modifier released while a direction is held | The direction moves back to the X pad on the next frame, no stuck Y bit |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
A horizontal game using the Y pad (Klonoa: Moonlight Museum menus) and a vertical one (Gunpey) in both views (issue 99).

## References
- ADR 0092; docs/research/wswan-plan.md section 5; docs/research/fork-nelynes.md section 2.1
