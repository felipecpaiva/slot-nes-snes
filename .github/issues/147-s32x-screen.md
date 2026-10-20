---
title: "Give the 32X its own Screen section with Shader, Picture, PAL Speed, Renderer and Sound Rate"
phase: 15
area: video
type: feature
size: M
depends_on: [146-s32x-options]
---

## Why
Every system gets its own Screen section. The 32X is heavy, so its speed options are the user's choice, the factory choice being PicoDrive's own default.

## Scope
- [x] Five rows; Config/s32x_shader.txt, picture.txt `32x`, pal_speed.txt `32x`, Config/s32x.txt.
- [x] Renderer and Sound Rate applied when the core opens.

## Tests
| ID | File | Asserts |
|---|---|---|
| S1 | `s32x_screen.rs` | rows, walks, files, next-boot defaults, unknown values, the options PicoDrive is told |

## Edge cases
| Case | Expected handling |
|---|---|
| An unknown value in s32x.txt | logged, read as the factory choice |

## Acceptance
- [x] S1 passes; upstream sites (g) and (h) take their token.

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
