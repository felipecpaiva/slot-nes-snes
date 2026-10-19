---
title: "Map the NGP A, B and Option buttons"
phase: 9
area: input
type: feature
size: S
depends_on: [72-platform-ngp]
---

## Why
Step 8. NGP has a stick, A, B and Option. NeoPop reads RetroPad B as A, RetroPad A as B and START as Option.

## Scope
- [ ] Device A and B reach the game as NGP A and B (positionally, like nelynes: left face A, right face B), START as Option.
- [ ] slot keeps L1 and R1 (`owns_shoulders` true); X and Y are turbo A and B, as on Game Gear; SELECT stays slot's (Select+X picture, Select+Y guard).
- [ ] Credit nelynes/slotPlus a8eae4c for the map in the patch commit.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ngp_input.rs` | each device button reaches the core as the documented RetroPad id; L1, R1 and SELECT never reach the game |

## Edge cases
| Case | Expected handling |
|---|---|
| A GBA game after an NGP game | Input as in a GBA-only run (`ngp_then_gba.rs`, issue 77) |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
A, B and Option in a real game menu (issue 79).

## References
- ADR 0090; docs/research/ngp-plan.md section 5
