---
title: "Add Platform::Vb with its own shelf and explicit policy"
phase: 16
area: platform
type: feature
size: M
depends_on: [154-vb-core-build]
---

## Why
The Virtual Boy needs its own shelf, Games/VB, and every policy answered explicitly.

## Scope
- [x] `Platform::Vb` appended to `SHELVES`, `Core::MednafenVb` to `EVERY`; `.vb` and `.vboy`, titled by stem.
- [x] The 384x256 canvas (3:2), no picker, no crop, rewind on, Select+X picture toggle; Saves/VB, States/VB and Labels/VB made at boot.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `vb_platform.rs` | shelf, extensions, policies, Beetle VB runs only the Virtual Boy, resume, shader file |
| P2 | `vb_seat.rs` | a cart seats on Beetle VB through a real session and shows one eye |

## Edge cases
| Case | Expected handling |
|---|---|
| A hidden `._` file | left off the shelf |

## Acceptance
- [x] P1 and P2 pass; upstream sites (b) and (e) take their token.

## Device check (RG34XXSP)
Issue 162.

## References
- ADR 0097; docs/cart-art/VB.md
