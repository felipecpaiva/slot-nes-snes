---
title: "DEFERRED: Support the Famicom Disk System as a variant and core"
phase: 6
area: cores
type: chore
size: L
depends_on: [32-phase-6-deferred]
---

## Why
**Deferred, not in v1.** FDS needs a BIOS and a different save model, so it is out of scope for v1 (docs/PLAN.md Phase 6+, Spec "Out of scope", Build step 23 "FDS deferred").

## Scope
- [ ] Decide whether FDS is wanted at all; if yes, plan it as a new phase (BIOS handling, disk-side saves, an FDS cart/disk outline).

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

## Device check (RG35XXSP)
None, deferred.

## Review notes
- Any future work must keep GBA/GB/GBC byte-identical and upstream tests unmodified.

## References
- docs/PLAN.md: Phase 6+ (deferred), Spec (Out of scope), Build step 23
