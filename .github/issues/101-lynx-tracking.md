---
title: "Atari Lynx: Lynx on Beetle Lynx, with a BIOS check, our own rotation and real-rate pacing"
phase: 12
area: device
type: tracking
size: L
depends_on: [56-ps1-tracking]
---

## Why
The 2026-10-18 fork review put Atari Lynx last on the new-system list (docs/research/fork-review-2026-10-18.md, docs/research/fork-nelynes.md section 3). It needs a BIOS we never ship, turns some carts on their side, and runs at whatever rate the game programs while the core reports 75. One core, Beetle Lynx pinned at `fcdefcf`, one shelf `Games/Lynx` (ADR 0093). The plan is docs/research/lynx-plan.md. The maintainer picked Beetle Lynx; Handy is out while `lynxdec.cpp` has no licence (ADR 0093).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0093 and these issues.
- [x] 2. 102-lynx-core-build (groundwork, on the v1.7.0 base)
- [x] 3. 110-lynx-tests, core half: patch 0070 (groundwork; the platform half grows with each step below)
- [x] 4. 103-platform-lynx (on slot main 1b20432 (ADR 0083), like everything below)
- [x] 5. 104-lynx-bios-check
- [x] 6. 105-lynx-options
- [x] 7. 106-lynx-canvas-screen
- [x] 8. 107-lynx-pacing (after issue 66, ADR 0071)
- [x] 9. 109-lynx-input-rotation
- [x] 10. 108-lynx-saves
- [x] 11. 111-lynx-carts
- [ ] 12. 112-lynx-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 to 11 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the mednafen_lynx dylib, and green again locally with `SLOT_LYNX_BIOS` set.
- [ ] Harness: a Lynx game, eject, GBA leg equals the GBA-only run (or a `lynx_then_gba.rs` test); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say Lynx shipped, with the nelynes/slotPlus credit of ADR 0093 and "bring your own `lynxboot.img`".

## Device check (RG34XXSP)
Issue 112. Needs the maintainer's own BIOS (now at `/mnt/sdcard/BIOS/lynxboot.img`).

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 12 is new: `scripts/setup-github-project.py` lists "Phase 12: Atari Lynx" (assuming TG16 and WonderSwan take 10 and 11). Integrated on 2026-10-19 as patches 0070 to 0079 with ADR 0093 (0089 to 0092 were taken or reserved).

## References
- ADR 0093; docs/research/lynx-plan.md; docs/research/fork-nelynes.md section 3
