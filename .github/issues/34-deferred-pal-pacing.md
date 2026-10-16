---
title: "DEFERRED: Pace PAL titles at 50 Hz"
phase: 6
area: video
type: chore
size: M
depends_on: [32-phase-6-deferred]
---

## Why
**Superseded by 66-pal-pacing (2026-10-17).** The maintainer brought PAL pacing back for NES, Master System, Mega Drive and PS1, after PS1 step 2. Kept for history.

**Deferred, out of scope by spec.** Slot's pacing assumes 60 fps, so PAL titles run about 20% fast. v1 documents this in the README known-gaps section (30-release-workflow) instead of fixing it (docs/PLAN.md Phase 6+, Spec "Out of scope").

## Scope
- [ ] If picked up: pace from the core's reported fps (`SET_SYSTEM_AV_INFO` already stores it in `HostExtra`) without changing GBA pacing.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Deferred |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [ ] A decision recorded as an ADR in docs/adr/.

## Device check (RG34XXSP)
None, deferred.

## Review notes
- Any pacing change touches the shared emu loop; it would need the GBA harness compare at 0 diffs.

## References
- docs/PLAN.md: Phase 6+ (deferred), Spec (Out of scope)
- docs/QUALITY-BAR.md: Known gaps
