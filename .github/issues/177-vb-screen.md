---
title: "Give the Virtual Boy its own Screen section with Shader, Picture, VB Speed, Palette and Right Pad"
phase: 16
area: video
type: feature
size: M
depends_on: [176-vb-options]
---

## Why
Every system has its own Screen section; the Virtual Boy adds the palette and the right pad choice.

## Scope
- [x] Shader (retro list, `Config/vb_shader.txt`), Picture (Actual default, Stretch), VB Speed (Native default), Palette (eight colours, red default), Right Pad (Stick default, ABXY) in `Config/vb.txt`.
- [x] The user's choice becomes the default from the next game; an unknown value is logged and read as the factory choice.

## Tests
| ID | File | Asserts |
|---|---|---|
| S1 | `vb_screen.rs` | rows, labels, persistence, palette words equal the core's, the canvas maps 1.875x |

## Edge cases
| Case | Expected handling |
|---|---|
| `palette = black & red` in vb.txt | logged, read as red |

## Acceptance
- [x] S1 passes; upstream sites (g) and (h) take their token.

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
