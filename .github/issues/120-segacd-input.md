---
title: "Hand the Mega Drive 3 and 6 button pad to Sega CD games"
phase: 13
area: input
type: feature
size: S
depends_on: [114-platform-segacd]
---

## Why
Step 9. The Sega CD uses the Mega Drive pad. The Mega Drive mapping already ships (patch 0026), so this step answers the input policy for `Platform::SegaCd` the same way and proves it on the real core.

## Scope
- [ ] `Platform::SegaCd` answers the input policy like `Platform::Md`: SNES-like layout, X, Y, L and R as its X, Y, Z buttons and the game's own keys, `owns_shoulders` false, the 6-button pad by default.
- [ ] SELECT is MODE, as on Mega Drive, and keeps slot's chords (Select+X picture, Select+Y guard, SELECT+L2 disc swap from issue 119).
- [ ] A per-game 3-button choice only if the device gate finds a game that misreads the 6-button pad.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `segacd_input.rs` | the bindings equal Mega Drive's; with the real BIOS (`SLOT_SEGACD_BIOS`), START moves the BIOS menu cursor, else a BIOS skip |

## Edge cases
| Case | Expected handling |
|---|---|
| SELECT+L2 on a one-disc game | As PS1 (ADR 0067) |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Final Fight CD: all six buttons do what the game's controls page says.

## References
- ADR 0053, 0094; patch 0026; `md_seat.rs`
