---
title: "Atari 2600 and Atari 7800 on Stella 2014 and ProSystem, built the NES and SNES way"
phase: 14
area: device
type: tracking
size: L
depends_on: [56-ps1-tracking]
---

## Why
The maintainer owns 578 Atari 2600 and 73 Atari 7800 dumps. Both are joystick systems that are cheap on the A53 and fit the 360x240 canvas at 2x. One core each, Stella 2014 pinned at `7d1361e` and ProSystem pinned at `8a88014`, two shelves `Games/A2600` and `Games/A7800` (ADR 0095). The plan is docs/research/atari-plan.md. Atari ST is out of scope.

## Scope
- [x] 1. Decision record: ADR 0095 and these issues.
- [x] 2. 154-a2600-core-build and 155-a7800-core-build (groundwork)
- [x] 3. 171-atari-tests, core half: patch 0098 (groundwork; the platform half grows with each step below)
- [x] 4. 156-platform-a2600, 157, 158, 159, 160, 161 (patches 0099 and 0100)
- [x] 5. 163-platform-a7800, 164, 165, 166, 167, 168, 169 (patches 0099 and 0100)
- [ ] 6. 162-a2600-device-gate and 170-a7800-device-gate
- [x] 7. 172: paddles came in with 0099 (left stick); keypad, driving and Mindlink stay deferred

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 and 5 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and both dylibs.
- [ ] Harness: an Atari game, eject, GBA leg equals the GBA-only run (`atari_then_gba.rs`, the PS1 and NGP precedent); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say both shipped.

## Device check (RG34XXSP)
Issues 162 and 170.

## Review notes
- Phase 14 is new: `scripts/setup-github-project.py` lists "Phase 14: Atari 2600 and 7800", which the board's Phase field gets on the next sync.
- Written while NGP, TurboGrafx-16, WonderSwan, Lynx and Sega CD groundwork is in flight. Issue numbers 153 to 172, ADR 0095, Phase 14 and patch 0098 may be renumbered at merge.

## References
- ADR 0095; docs/research/atari-plan.md
