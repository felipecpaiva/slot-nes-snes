---
title: "Check BIOS/neogeo.zip before a Neo Geo set starts"
phase: 16
area: platform
type: feature
size: S
depends_on: [155-platform-arcade]
---

## Why
FBNeo loads a Neo Geo set without the BIOS and shows its error page instead of the game.

## Scope
- [x] Read the zip directory of `BIOS/neogeo.zip`; launch only with the four default-BIOS CRCs; toast otherwise.

## Tests
| ID | File | Asserts |
|---|---|---|
| B1 | `arcade_bios.rs` | missing BIOS keeps the set on the shelf with a toast, also on resume; with the BIOS it launches; CPS needs none; toast list place |
| B2 | `arcade_core.rs` | FBNeo draws its 640x480 error page without the BIOS |

## Edge cases
| Case | Expected handling |
|---|---|
| A BIOS zip naming the ver. 6 file asia-s3.rom | counts, matched by CRC |
| A zip with only UniBIOS | refused; DIPSWITCH boots ver. 6 |

## Acceptance
- [x] B1 and B2 pass.

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
