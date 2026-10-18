---
title: "NeoGeo Pocket: NGP and Pocket Color on Beetle NeoPop, built the NES and SNES way"
phase: 9
area: device
type: tracking
size: L
depends_on: [56-ps1-tracking]
---

## Why
The 2026-10-18 fork review approved NeoGeo Pocket and Pocket Color as the first new system after PS1 (docs/research/fork-review-2026-10-18.md tier 4). It is a 3x fit on the 480-line panel, needs no BIOS and no rotation. One core, Beetle NeoPop pinned at `a50d5ac`, one shelf `Games/NGP` (ADR 0090). The plan is docs/research/ngp-plan.md.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0090 and these issues.
- [x] 2. 71-ngp-core-build (groundwork, on the v1.7.0 base)
- [x] 3. 77-ngp-tests, core half: patch 0052 (groundwork; the platform half grows with each step below)
- [ ] 4. 72-platform-ngp (on the 1.8.0 base, like everything below)
- [ ] 5. 73-ngp-options
- [ ] 6. 74-ngp-canvas-screen
- [ ] 7. 75-ngp-flash-saves
- [ ] 8. 76-ngp-input
- [ ] 9. 78-ngp-carts
- [ ] 10. 79-ngp-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 to 9 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the mednafen_ngp dylib.
- [ ] Harness: an NGP game, eject, GBA leg equals the GBA-only run (or an `ngp_then_gba.rs` test, the PS1 precedent); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say NGP shipped, with the nelynes/slotPlus credit of ADR 0090.

## Device check (RG34XXSP)
Issue 79.

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 9 is new: `scripts/setup-github-project.py` now lists "Phase 9: NeoGeo Pocket", which the board's Phase field gets on the next sync. No `numbers.json` entries until then.
- Written while another branch ports the patch set to upstream 1.8.0. Steps 4 on wait for that base; issue numbers 70 to 79 and ADR 0090 may be renumbered at merge.

## References
- ADR 0090; docs/research/ngp-plan.md; docs/research/fork-nelynes.md section 1
