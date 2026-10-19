---
title: "Sega CD / Mega-CD on Genesis Plus GX, the disc half of the Mega Drive"
phase: 13
area: device
type: tracking
size: L
depends_on: [53-platform-md, 56-ps1-tracking]
---

## Why
Sega CD is the first system on the next-systems ranking (2026-10-19): about 62 owned games, no new core (Genesis Plus GX already ships, ADR 0053, and our pinned build has `HAVE_CHD = 1`), the US, EU and JP BIOS files on hand and matching the GPGX doc, and the PS1 disc machinery to reuse. The decision is ADR 0094; the plan is docs/research/segacd-plan.md.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0094 and these issues.
- [x] 2. 121-segacd-tests, core half: patch 0057 (groundwork; the platform half grows with each step below)
- [ ] 3. 114-platform-segacd
- [ ] 4. 115-segacd-bios-check
- [ ] 5. 116-segacd-options
- [ ] 6. 117-segacd-canvas-screen
- [ ] 7. 118-segacd-backup-ram (after NGP issue 75's staging code)
- [ ] 8. 119-segacd-discs
- [ ] 9. 120-segacd-input
- [ ] 10. 122-segacd-cases
- [ ] 11. Device gate (below)

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 3 to 10 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1`.
- [ ] Harness: a Sega CD game, eject, GBA leg equals the GBA-only run (a `segacd_then_gba.rs` test, the `sega_then_gba.rs` precedent); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say Sega CD shipped, with the BIOS rule (user-supplied, never shipped, never in CI).

## Device check (RG34XXSP)
The device gate of plan section 8:
1. Sonic CD, Lunar: The Silver Star, Snatcher and Final Fight CD for 10 minutes each under `SLOT_TRACE`: full speed, zero audio underruns, ms a frame recorded (estimate 4 to 6 ms, unmeasured). One FMV title (Night Trap or Sewer Shark) for CD audio plus CHD decode.
2. Backup RAM: save in Lunar, close the lid, pull the battery, boot; the save is there resuming and starting fresh. The reload timing of issue 118 recorded.
3. A two-disc game: swap, eject, reinsert, the disc is remembered.
4. Eject and GBA: the GBA leg equals a GBA-only run.

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 13 is new: `scripts/setup-github-project.py` lists "Phase 13: Sega CD". No `numbers.json` entries until the next board sync.
- Written while other branches integrate NGP (70 to 79), TG16 (81 to 90), WonderSwan (91 to 99) and Lynx (101 to 112). Numbers 113 to 122, ADR 0094 and patch 0057 may be renumbered at merge.

## References
- ADR 0053, 0067, 0069, 0094; docs/research/segacd-plan.md
