---
title: "Add Platform::Sgx with its options, Screen section, saves and the TurboGrafx-16 pad"
phase: 18
area: platform
type: feature
size: M
depends_on: [195-sgx-core-build]
---

## Why
The SuperGrafx needs its own shelf, Games/SGX, every policy answered explicitly, and the TurboGrafx-16 quality bar: Screen section, saves, states, the pad.

## Scope
- [x] `Platform::Sgx` appended to `SHELVES`, `Core::MednafenSupergrafx` to `EVERY`; `.sgx` and `.pce`, titled by stem; Saves/SGX, States/SGX and Labels/SGX made at boot; release date 8 December 1989 in `RELEASED`.
- [x] Options: the TurboGrafx-16 list under `sgx_`, plus `sgx_forcesgx=enabled`; the CD keys unanswered.
- [x] Screen section: Shader (retro list, `Config/sgx_shader.txt`) and Picture (Crop default, Stretch, Actual, 4:3, `Config/picture.txt` `sgx`).
- [x] Input: the TurboGrafx-16 pad, X and Y as turbo (`turbo_on_xy`), 2 buttons.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `slot-store/tests/sgx_platform.rs` | shelf, extensions, policies equal to TG16, Beetle SuperGrafx runs only the SuperGrafx, resume, shader file |
| P2 | `slot/tests/sgx_platform.rs` | options answered with declared values, CD keys unanswered, a `.pce` card runs as a SuperGrafx through slot's open path, Screen rows, shader and picture walks, folders |
| P3 | `slot/tests/sgx_platform.rs` | BRAM `.sav` round trip through Saves/SGX, the 2 KB sav on eject, pad, SELECT after the chord, X and Y reach the core |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.sgx` file on the TG16 shelf | skipped there, as before |
| A `.pce` card on the TG16 shelf | stays a TurboGrafx-16 card |
| Darius Alpha (not in the core's CRC table) | runs as a SuperGrafx through `sgx_forcesgx` |

## Acceptance
- [x] P1 to P3 pass; upstream sites (b), (e), (g) and (h) take their token.

## Device check (RG34XXSP)
Issue 199.

## References
- ADR 0101; docs/cart-art/SGX.md
