---
title: "Add a SuperGrafx Pad row: 2 Buttons or the 6-button Avenue Pad"
phase: 20
area: input
type: feature
size: M
depends_on: [211-platform-sgx]
---

## Why
Beetle SuperGrafx emulates the 6-button Avenue Pad, which takes III to VI from RetroPad Y, X, L and R: slot's turbo buttons and picture keys on this shelf. No SuperGrafx title uses it, so 2 buttons stays the default, but the pad is the core's and the player can choose it.

## Scope
- [x] `QuickRow::SgxPad` in the SuperGrafx section, `Config/sgx.txt` `pad = 2` or `6`, answered as `sgx_default_joypad_type_p1` when the next card starts (patch 0134).
- [x] With 6 buttons, latched at seat: X and Y raw to the core (no slot turbo), L1 and R1 to the game, the picture toggle on SELECT+X.

## Tests
| ID | File | Asserts |
|---|---|---|
| D1 | `sgx_platform.rs` | the row walks 2 and 6 into sgx.txt; the option is answered per mode and only on the SuperGrafx |
| D2 | `sgx_platform.rs` | with 6 buttons X, Y, L1, R1 reach the core as X, Y, L, R and slot takes no button; with 2 buttons L1 and R1 stay slot's |
| D3 | `sgx_then_gba.rs` | a GBA game after a six-button SuperGrafx game gets the GBA-only input and picture |

## Edge cases
| Case | Expected handling |
|---|---|
| A 2-button game with the 6-button pad | the core's own warning; the player switches back, the default is 2 |
| An unknown pad word in sgx.txt | 2 Buttons, logged |

## Acceptance
- [x] D1 to D3 pass; breaking the shoulder hand-over turns D2 red.

## Device check (RG34XXSP)
Issue 214.

## References
- ADR 0103; docs/cart-art/SGX.md
