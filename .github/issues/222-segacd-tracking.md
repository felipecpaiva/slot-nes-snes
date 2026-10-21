---
title: "Sega CD / Mega-CD on Genesis Plus GX, the disc half of the Mega Drive"
phase: 22
area: device
type: tracking
size: L
depends_on: [53-platform-md, 56-ps1-tracking, 216-pcecd-tracking]
---

## Why
Sega CD is the first system on the next-systems ranking (docs/research/next-systems-2026-10-20.md): 59 owned titles on 61 discs, no new core (Genesis Plus GX already ships, ADR 0053, and our pinned build has `HAVE_CHD = 1`), the US, EU and JP BIOS files on hand, and the PS1 disc machinery to reuse. The decision is ADR 0105; the plan is docs/research/segacd-plan.md (written on the `segacd-groundwork` branch as ADR 0094, issues 113 to 122 and patch 0057, renumbered on integration).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0105 and these issues.
- [x] 2. 230-segacd-tests, core half: patch 0139.
- [x] 3. 223-platform-segacd and 225-segacd-options: patch 0140.
- [x] 4. 226-segacd-canvas-screen: patch 0141.
- [x] 5. 224-segacd-bios-check: patch 0142.
- [x] 6. 228-segacd-discs: patch 0143.
- [x] 7. 227-segacd-backup-ram: patch 0144.
- [x] 8. 229-segacd-input and the platform half of 230: patch 0145.
- [x] 9. 231-segacd-cases: patch 0146, `tools/fetch-labels.py` SEGACD.
- [ ] 10. 232-segacd-device-gate.

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 9 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1`.
- [x] A Sega CD game with a swapped disc, eject, then a GBA game equals a GBA-only run (`segacd_then_gba.rs`).
- [x] README, docs/PLAN.md and docs/DEVICE-GATE.md say Sega CD is in the patch set, with the BIOS rule (user-supplied, never shipped, never in CI).

## Device check (RG34XXSP)
Issue 232.

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 22: `scripts/setup-github-project.py` lists "Phase 22: Sega CD".
- Numbers 222 to 232, ADR 0105 and patches 0139 to 0146 follow the PC Engine CD (216 to 221, ADR 0104, patches 0135 to 0138), which merged first.

## References
- ADR 0053, 0067, 0069, 0094, 0098, 0105; docs/research/segacd-plan.md
