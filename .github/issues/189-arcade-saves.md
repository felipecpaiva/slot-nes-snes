---
title: "Arcade saves: the board's NVRAM in Saves/fbneo, progress in states"
phase: 17
area: platform
type: chore
size: S
depends_on: [185-platform-arcade]
---

## Why
FBNeo exposes no SAVE_RAM; it writes NVRAM and EEPROM itself at unload.

## Scope
- [x] Document and test where the board's data lands; rewind on.

## Tests
| ID | File | Asserts |
|---|---|---|
| V1 | `arcade_core.rs` | no save RAM; the EEPROM file is written at unload |
| V2 | `arcade_seat.rs` | ending a session writes Saves/fbneo/<set>.nv |

## Edge cases
| Case | Expected handling |
|---|---|
| A power cut mid-game | settings and scores since the start are lost; the resume state holds progress |

## Acceptance
- [x] V1 and V2 pass.

## Device check (RG34XXSP)
Issue 193.

## References
- ADR 0099
