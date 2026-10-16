---
title: "PlayStation: PS1 on pcsx_rearmed, built the NES and SNES way"
phase: 8
area: device
type: tracking
size: L
depends_on: [50-sega-tracking]
---

## Why
The maintainer brought PS1 into scope (ADR 0063) after the device spike passed every bar (docs/research/ps1-spike.md, Results). One core, pcsx_rearmed pinned at `c8816799`, one shelf `Games/PS1`. The decisions are ADRs 0063 to 0069. The steps follow the 12-step order from the fork survey (2026-10-16), with the maintainer's choices where they differ: declared defaults are answered (ADR 0064), and the canvas is a fixed 640x480 (ADR 0065).

## Scope
Child work, in merge order:
- [x] 1. `need_fullpath` load: patch 0030, ADR 0059 (upstream-first, drop when upstream lands).
- [x] 2. Device spike: docs/research/ps1-spike.md, Results (RG34XXSP, 2026-10-16). Verdict go.
- [x] 3. Decision records: ADRs 0063 to 0069 and these issues.
- [ ] 4. 57-ps1-core-build
- [ ] 5. 58-platform-ps1
- [ ] 6. 59-ps1-options
- [ ] 7. 60-ps1-canvas-screen
- [ ] 8. 61-ps1-disk-control
- [ ] 9. 62-ps1-input
- [ ] 10. 63-ps1-tests (its fixture can land with step 4 and grow with each step)
- [ ] 11. 64-ps1-cases
- [ ] 12. 65-ps1-analog (v2, not blocking v1)

Separate tickets that came out of the same review, not blocking PS1:
- [ ] 66-pal-pacing (NES, SMS, MD and PS1 at 50 Hz)
- [ ] 67-crash-guard (upstream-first)
- [ ] 68-deferred-ps1-disc-shelf (deferred, listed in 32-phase-6-deferred)

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 to 11 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the pcsx_rearmed dylib.
- [ ] Harness: a PS1 game, eject, GBA leg equals the GBA-only run; `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say PS1 shipped, with the fork credits of ADR 0063.

## Device check (RG34XXSP)
1. SotN, Spyro: Year of the Dragon and Gran Turismo 2 in play (not the intros) for 10 minutes each under `SLOT_TRACE`: full speed, zero audio underruns.
2. Check the 25 to 38 ms Spyro frames from the spike: no audible drop.
3. One PAL and one NTSC-J title, and one multi-disc game swapped to disc 2.
4. Lid-close save time for a 4.4 MB state; battery and SoC temperature with threaded rendering on.

## Review notes
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 8 is new: the board's Phase field needs a "Phase 8: PlayStation" option before these issues are synced.

## References
- ADRs 0059, 0063 to 0069; docs/research/ps1-plan.md; docs/research/ps1-spike.md
