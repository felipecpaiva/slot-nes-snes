---
title: "TurboGrafx-16: PC Engine and TurboGrafx HuCards on Beetle PCE Fast, built the NES and SNES way"
phase: 10
area: device
type: tracking
size: L
depends_on: [56-ps1-tracking]
---

## Why
The 2026-10-18 fork review approved TurboGrafx-16 / PC Engine HuCards (docs/research/fork-review-2026-10-18.md item 17). 256x240 at 2x fills the 480-line panel on the SNES 360x240 canvas, no BIOS is needed, and the library is large. One core, Beetle PCE Fast pinned at `3f946f2`, one shelf `Games/TG16` (ADR 0091). The plan is docs/research/tg16-plan.md.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0091 and these issues.
- [x] 2. 82-tg16-core-build (groundwork, on the v1.7.0 base)
- [x] 3. 88-tg16-tests, core half: patch 0052 (groundwork; the platform half grows with each step below)
- [x] 4. 83-platform-tg16 (on the 1.8.0 base, like everything below)
- [x] 5. 84-tg16-options
- [x] 6. 85-tg16-canvas-screen
- [x] 7. 86-tg16-saves
- [x] 8. 87-tg16-input
- [x] 9. 89-tg16-carts
- [ ] 10. 90-tg16-device-gate

Out of scope (ADR 0091): TurboCD / CD-ROM² / Super CD-ROM² / Arcade CD (system card BIOS, disc images, CD save model) and SuperGrafx.

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 to 9 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the mednafen_pce_fast dylib.
- [ ] Harness: a TG16 game, eject, GBA leg equals the GBA-only run (or a `tg16_then_gba.rs` test, the PS1 precedent); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say TG16 shipped, with the nelynes/slotPlus and unslot credit of ADR 0091.

## Device check (RG34XXSP)
Issue 90.

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 10 is new: `scripts/setup-github-project.py` now lists "Phase 10: TurboGrafx-16", which the board's Phase field gets on the next sync. No `numbers.json` entries until then.
- Written beside the stacked branches (patches and ADRs 0084 to 0088), the hack tool (ADR 0089) and NGP (ADR 0090). Patches 0052 onward, ADR 0091, issues 81 to 90 and Phase 10 may be renumbered at merge.

## References
- ADR 0091; docs/research/tg16-plan.md; docs/research/fork-nelynes.md section 4
