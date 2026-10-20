---
title: "Add Platform::S32x with its own shelf, a 32X header check and explicit policy"
phase: 15
area: platform
type: feature
size: M
depends_on: [144-s32x-core-build]
---

## Why
`.bin` is also a Mega Drive extension, so the 32X shelf must recognise a 32X cart by its header. Mega Drive must not change.

## Scope
- [x] `Platform::S32x` appended to `SHELVES`, `Core::Picodrive` to `EVERY`.
- [x] `.32x` always lists; `.bin` only with `SEGA 32X` at 0x100 or `MARS CHECK MODE` at 0x3c0.
- [x] Every policy answered like Mega Drive; Saves/32X, States/32X, Labels/32X made at boot.
- [x] dist-device.sh, zip-check.sh and run-tests.sh list the core.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `s32x_platform.rs` | shelf, header rule, Mega Drive shelf unchanged, policies equal Mega Drive's, PicoDrive runs only 32X |
| P2 | `s32x_seat.rs` | a 32X cart seats on PicoDrive through a real session |

## Edge cases
| Case | Expected handling |
|---|---|
| A Mega Drive `.bin` in Games/32X | logged and left off the shelf |
| A 32X game in Games/MD | still lists there on Genesis Plus GX, unchanged |

## Acceptance
- [x] P1 and P2 pass; upstream sites (b) and (e) take their token.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
