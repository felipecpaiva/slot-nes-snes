---
title: "32X saves: the ordinary .sav, written only for games that save"
phase: 15
area: platform
type: chore
size: S
depends_on: [145-platform-s32x]
---

## Why
PicoDrive reports save RAM before the first frame and afterwards only when the game wrote it.

## Scope
- [x] Tests only; no 32X-only save code.

## Tests
| ID | File | Asserts |
|---|---|---|
| V1 | `s32x_saves.rs` | a .sav survives eject and reinsert; a saving game writes 16 KB on eject and on lid close; a game that never saves leaves none |

## Edge cases
| Case | Expected handling |
|---|---|
| A game that never writes SRAM | no zero-filled .sav |

## Acceptance
- [x] V1 passes.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
