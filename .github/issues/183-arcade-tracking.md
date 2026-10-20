---
title: "Arcade: Neo Geo, CPS1 and CPS2 on FinalBurn Neo, a shelf per board"
phase: 17
area: device
type: tracking
size: L
depends_on: [143-s32x-tracking]
---

## Why
The maintainer asked for arcade: Neo Geo, CPS1 and CPS2 on one FinalBurn Neo, pinned at `2dbbac7`, three shelves (ADR 0099). CPS3 is out until a device gate shows it at full speed.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0099 and these issues.
- [x] 2. 184-arcade-core-build
- [x] 3. 191-arcade-tests, core half: patch 0110
- [x] 4. 185-platform-arcade (patch 0111)
- [x] 5. 186-arcade-options (patch 0112)
- [x] 6. 187-arcade-screen (patch 0113)
- [x] 7. 188-neogeo-bios (patch 0114)
- [x] 8. 189-arcade-saves and 190-arcade-input (patch 0115, tests)
- [x] 9. 192-arcade-carts (patch 0116, tools/fetch-labels.py)
- [ ] 10. 193-arcade-device-gate

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
- [ ] Device gate (issue 193).

## Device check (RG34XXSP)
Issue 193.

## References
- ADR 0099
