---
title: "Neo Geo CD: discs on NeoCD, a shelf of its own"
phase: 23
area: device
type: tracking
size: L
depends_on: [222-segacd-tracking]
---

## Why
The maintainer asked for the Neo Geo CD as its own platform, holding only his CD-exclusive games: Crossed Swords II and the English translation of Shinsetsu Samurai Spirits - Bushidou Retsuden (Samurai Shodown RPG). A new core, NeoCD (libretro/neocd_libretro, LGPL-3.0 with a non-commercial Z80 core); one shelf `Games/NEOCD`; the player's own CDZ, Front Loader or Top Loader BIOS checked, never shipped (ADR 0106).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0106 and these issues.
- [x] 2. 234-neocd-core-build and the core half of the tests (patch 0147)
- [x] 3. 235-platform-neocd (patch 0148)
- [x] 4. 236-neocd-bios (patch 0149)
- [x] 5. 237-neocd-cases (patch 0150 and tools/fetch-labels.py)
- [ ] 6. 238-neocd-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 5 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1`.
- [x] README, docs/PLAN.md and LICENSING.md describe the Neo Geo CD.
- [x] The library: `docs/rom-library/best-copy/neocd-adds.tsv` (workspace), the two CHDs staged off the Mac.
- [ ] Device gate (issue 238).

## Device check (RG34XXSP)
Issue 238.

## References
- ADR 0106; docs/cart-art/NEOCD.md; ADR 0099 (the Neo Geo shelf), ADR 0104 (the CD precedent)
