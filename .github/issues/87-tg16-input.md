---
title: "Map the TG16 pad: II, I, Select, Run and turbo"
phase: 10
area: input
type: feature
size: S
depends_on: [83-platform-tg16]
---

## Why
Step 8. The TurboGrafx pad is II (left), I (right), Select and Run, plus two turbo switches. PCE Fast maps RetroPad B to II, A to I, SELECT to Select and START to Run, and treats Select+Run as the console's soft reset.

## Scope
- [x] B is II, A is I, START is Run.
- [x] SELECT reaches the game after slot's chord hold, as on SNES (upstream c2a27a6); Select+X picture and Select+Y guard stay slot's.
- [x] X and Y are Turbo I and Turbo II through slot's turbo (the Game Gear precedent); the core's own turbo (`pce_fast_turbo_toggling`) stays off.
- [x] L1 and R1 stay slot's (`owns_shoulders` true).
- [x] Decide `pce_fast_disable_softreset` (issue 84 answers it). Recommended `disabled`: Select+Run stays the console's soft reset, the only in-game reset there is (slot's power menu Restart reboots the device), and SELECT reaches the game only after the chord hold, so it is deliberate. `enabled` masks the pair.
- [x] The 6-button pad is skipped (among HuCards only Street Fighter II' Champion Edition wants it).
- [x] Credit nelynes/slotPlus 92b7022 for the layout.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `tg16_input.rs` | each device button reaches the core as the RetroPad id above; turbo pulses; SELECT only after the hold |

## Edge cases
| Case | Expected handling |
|---|---|
| SELECT (after the hold) and START together | The game soft-resets, unless the option masks it |
| Turbo held across a state load | Same as the other turbo platforms |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
II on B and I on A feel right in the four gate games, turbo fires in a shooter (issue 90).

## References
- ADR 0091; docs/research/tg16-plan.md section 5

## Outcome (2026-10-19)
Patch `0056-tg16-input`. Select+Run soft reset kept (`pce_fast_disable_softreset=disabled`). Turbo: main-1b20432 no longer hands X and Y to a non-pass-through system, so TG16 gets a new `Platform::turbo_on_xy()` (TG16 only) that feeds them to slot's turbo (ADR 0091). Tests: `slot/tests/tg16_input.rs` (B, A, START by position; X and Y raw to slot; I and II pulse with turbo on; nothing with turbo off; only TG16 feeds the turbo; X and Y reach the emulator on the real core; L1 and R1 stay slot's; SELECT only after the chord hold, then Select+Run together).
