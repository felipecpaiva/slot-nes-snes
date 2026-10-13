---
title: "Phase 6: deferred work (non-blocking)"
phase: 6
area: docs
type: tracking
size: S
depends_on: [28-phase-5-release]
---

## Why
Items the plan explicitly defers past v1 (docs/PLAN.md "Phase 6+: deferred (non-blocking)", Spec "Out of scope"). Kept as issues so they are visible and not silently dropped. None blocks a release.

## Scope
- [ ] 33-deferred-fds
- [ ] 34-deferred-pal-pacing
- [ ] 35-deferred-stem-key-collision
- [ ] 36-deferred-option-b-video

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [ ] Each child is either closed as won't-do with a reason, or re-planned into a new phase with its own tests.

## Device check (RG34XXSP)
None, nothing ships from this phase.

## Review notes
- Do not start a deferred item without first updating docs/PLAN.md and adding an ADR in docs/adr/.

## References
- docs/PLAN.md: Phase 6+ (deferred), Spec (Out of scope)
