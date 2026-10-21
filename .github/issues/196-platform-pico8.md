---
title: "Add Platform::Pico8 on FAKE-08 with a 3x picture, its own Screen section, Saves/PICO8 and no states"
phase: 18
area: platform
type: feature
size: M
depends_on: [195-pico8-core-build]
---

## Why
PICO-8 carts need their own shelf, their own picture rules and an honest answer to every policy method.

## Scope
- [x] `Platform::Pico8` (`PICO8`, "PICO-8", `.p8` and `<name>.p8.png`, picture 128x128), `Core::Fake08`; appended to SHELVES and EVERY.
- [x] `pico8::admits` (no bare `.png`) and the title rule (first comment line of a text cart, the file name of a PNG cart).
- [x] 240x160 canvas: Actual is an integer 3x; Stretch fills; FAKE-08's scale and crop fixed (`FAKE08`).
- [x] Screen section (Shader, Picture), `Config/pico8_shader.txt`, `pico8` in picture.txt; shelf order 2015-04-18.
- [x] NES-like input; Saves/PICO8 as the core's save dir; no rewind; the in-game States page hidden.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `pico8_platform.rs` | shelf, extensions, titles, policy answers, core, resume of the platform, shader file |
| P2 | `pico8_screen.rs` | section last with Shader and Picture, shown only with PICO-8 carts, Actual 3x and Stretch rects, shader walk |
| P3 | `pico8_seat.rs` | a real session draws the band at (56, 16); B is O; cartdata in Saves/PICO8/cdata; no rewind, R2 fast-forwards; no state on eject |

## Edge cases
| Case | Expected handling |
|---|---|
| A cover picture `cover.png` in Games/PICO8 | not a cart, logged |
| A text cart with no title comment | titled by its file name |
| Two carts with the same cartdata id | they share it, as in PICO-8 |

## Acceptance
- [x] P1 to P3 pass; upstream sites (b), (e), (g) and (h) take one token each.

## Device check (RG34XXSP)
Issue 199.

## References
- ADR 0101
