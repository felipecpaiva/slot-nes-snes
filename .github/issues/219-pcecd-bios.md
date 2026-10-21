---
title: "Check BIOS/syscard3.pce before a PC Engine CD starts"
phase: 21
area: platform
type: feature
size: S
depends_on: [218-platform-pcecd]
---

## Why
The core refuses a disc without the System Card 3.0. slot never ships or fetches it, so it must say why a disc does not start.

## Scope
- [x] `slot_store::pcecd::bios`: skip a 512-byte header by the core's rule, then 262144 bytes, crc32 6d9a73ef (System.dat md5 38179df8...).
- [x] Missing or wrong size refuses with "PC Engine CD needs BIOS/syscard3.pce"; another 256 KB card launches with "syscard3.pce is not the known dump" once a session; a disc resumed at boot is checked.

## Tests
| ID | File | Asserts |
|---|---|---|
| B1 | `slot/tests/pcecd_bios.rs` | missing, short, long, unknown and headered files; the maintainer's card is known with and without a header |
| B2 | `slot/tests/pcecd_bios.rs` | refusal toast, resume check, unknown toast, known card silent, a HuCard never checked, toast order |

## Edge cases
| Case | Expected handling |
|---|---|
| The headered top-level copy | known: the core boots it the same |

## Acceptance
- [x] B1 and B2 pass.

## Device check (RG34XXSP)
Issue 221.

## References
- ADR 0104; ADR 0101; ADR 0093
