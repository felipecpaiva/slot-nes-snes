---
title: "DEFERRED: Fix the stem-key collision in selected_core.txt, video_mode.txt and cart_shell.txt"
phase: 6
area: platform
type: chore
size: M
depends_on: [32-phase-6-deferred]
---

## Why
**Deferred, documented only.** These files are keyed by file stem, so the same name on two systems collides. Fixing it means changing upstream file formats; v1 documents it in the README known-gaps section (docs/PLAN.md Phase 6+, Spec "Out of scope").

## Scope
- [ ] If picked up: design a platform-qualified key that unpatched slot still reads safely.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Deferred |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [ ] A decision recorded in docs/DECISIONS.md.

## Device check (RG34XXSP)
None, deferred.

## Review notes
- A format change must keep a downgrade to unpatched slot from panicking.

## References
- docs/PLAN.md: Phase 6+ (deferred), Spec (Out of scope)
- docs/RESEARCH.md: Known ceilings
