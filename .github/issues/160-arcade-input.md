---
title: "Arcade input: FBNeo's Classic map, L1 and R1 to the game"
phase: 16
area: input
type: feature
size: S
depends_on: [155-platform-arcade]
---

## Why
Six-button CPS games need L1 and R1; coin is SELECT.

## Scope
- [x] `owns_shoulders` false, X and Y pass through, SELECT+X toggles the picture; FBNeo's own Classic map cited in ADR 0097.

## Tests
| ID | File | Asserts |
|---|---|---|
| I1 | `arcade_platform.rs` | the arcade policies (shoulders, pass-through) |

## Edge cases
| Case | Expected handling |
|---|---|
| Turned vertical game | D-pad turned, buttons kept (S1) |

## Acceptance
- [x] I1 passes; the map is checked on the device (issue 163).

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
