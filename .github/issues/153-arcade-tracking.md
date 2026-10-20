---
title: "Arcade: Neo Geo, CPS1 and CPS2 on FinalBurn Neo, a shelf per board"
phase: 16
area: device
type: tracking
size: L
depends_on: [143-s32x-tracking]
---

## Why
The maintainer asked for arcade: Neo Geo, CPS1 and CPS2 on one FinalBurn Neo, pinned at `2dbbac7`, three shelves (ADR 0097). CPS3 is out until a device gate shows it at full speed.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0097 and these issues.
- [x] 2. 154-arcade-core-build
- [x] 3. 161-arcade-tests, core half: patch 0098
- [x] 4. 155-platform-arcade (patch 0099)
- [x] 5. 156-arcade-options (patch 0100)
- [x] 6. 157-arcade-screen (patch 0101)
- [x] 7. 158-neogeo-bios (patch 0102)
- [x] 8. 159-arcade-saves and 160-arcade-input (patch 0103, tests)
- [ ] 9. 162-arcade-carts (patch 0104, tools/fetch-labels.py)
- [ ] 10. 163-arcade-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 2 to 9 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the fbneo dylib.
- [ ] README, docs/PLAN.md and LICENSING.md describe the arcade shelves, with the notice naming FinalBurn Neo and the no-donations rule.
- [ ] Device gate (issue 163).

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
