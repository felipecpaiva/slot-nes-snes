---
title: "Test the arcade boards with zero-filled sets FBNeo reads from BIOS/fbneo/patched"
phase: 16
area: tests
type: test
size: S
depends_on: [154-arcade-core-build]
---

## Why
No commercial ROM may be committed; FBNeo's patched-romset folder takes members by name and size.

## Scope
- [x] `arcade_common` writes zips with the dat's member names and sizes; `arcade_core.rs` pins sizes, rates, BIOS behaviour, rotation, states and NVRAM.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `arcade_core.rs` | CPS1 384x224 at 59.63 Hz, CPS2 no BIOS, Neo Geo 304x224 at 59.18 Hz, error page without BIOS, quarter turn asked, state round trip, NVRAM at unload |

## Edge cases
| Case | Expected handling |
|---|---|
| A set with a missing member | FBNeo refuses it |

## Acceptance
- [x] T1 passes.

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
