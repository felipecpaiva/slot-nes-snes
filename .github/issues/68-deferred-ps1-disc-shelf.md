---
title: "DEFERRED: Offer a 3D disc or disc stack as an alternative PS1 shelf style"
phase: 6
area: ui-art
type: chore
size: L
depends_on: [32-phase-6-deferred, 64-ps1-cases]
---

## Why
**Deferred.** ADR 0069 makes the jewel case the PS1 look. The maintainer wants an omega-zero-style 3D disc (or a disc stack for multi-disc games, faced with the disc scan) kept as a future alternative style.

## Scope
- [ ] If picked up: a shelf style setting, the disc face from `support-2D`, a stack per `.m3u` count. The jewel case stays the default.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Deferred |

## Edge cases
| Case | Expected handling |
|---|---|
| (none) | |

## Acceptance
- [ ] An ADR recorded before work starts.

## Device check (RG34XXSP)
None, deferred.

## References
- ADR 0069; omega-zero disc model (commits 91225cf, c19495c)
