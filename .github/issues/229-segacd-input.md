---
title: "Hand the Mega Drive 3 and 6 button pad to Sega CD games"
phase: 22
area: input
type: feature
size: S
depends_on: [223-platform-segacd]
---

## Why
Step 9. The Sega CD uses the Mega Drive pad. The Mega Drive mapping already ships (patch 0026), so this step answers the input policy for `Platform::SegaCd` the same way and proves it on the real core.

## Scope
- [x] `Platform::SegaCd` answers the input policy like `Platform::Md`: SNES-like layout, X, Y, L and R as its X, Y, Z buttons and the game's own keys, `owns_shoulders` false, the 6-button pad by default.
- [x] SELECT is MODE, as on Mega Drive, and keeps slot's chords (Select+X picture, Select+Y guard, SELECT+L2 disc swap from issue 228).
- [x] A per-game 3-button choice only if the device gate finds a game that misreads the 6-button pad.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done, 0145) | `segacd_then_gba.rs` `a_sega_cd_game_gets_the_mega_drive_pad_and_slot_keeps_the_triggers`; `segacd_platform.rs` (the policy answers equal the Mega Drive's) | X reaches the game, slot keeps L2 and R2 |

## Edge cases
| Case | Expected handling |
|---|---|
| SELECT+L2 on a one-disc game | As PS1 (ADR 0067) |

## Acceptance
- [x] `task check` green.

## Device check (RG34XXSP)
Final Fight CD: all six buttons do what the game's controls page says.

## References
- ADR 0053, 0105; patch 0026; `md_seat.rs`
