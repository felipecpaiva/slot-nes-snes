---
title: "Add Platform::Sms, Master System on Genesis Plus GX at 2x"
phase: 7
area: platform
type: feature
size: M
depends_on: [51-platform-gg]
---

## Why
Master System at 256x192 fits the 360x240 canvas at 2x like NES, with two buttons, on the same core as Game Gear (ADR 0053).

## Scope
- [ ] `Platform::Sms` in `SHELVES`, `Games/SMS`, extension `sms` (`sg` later), title from the stem.
- [ ] Canvas 360x240 at 2x; picture 256x192 (taller extended modes follow the frame).
- [ ] NES like policy: slot owns L1 and R1, X and Y turbo; START is Pause.
- [ ] Core option `genesis_plus_gx_left_border` hides the blank left column; `genesis_plus_gx_ym2413` left at its default.
- [ ] Region from the header nibble at 0x7FFF.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/sms_*.rs` | scan, real-core boot, canvas 360x240, save RAM round trip, downgrade to shelf on upstream |

## Edge cases
| Case | Expected handling |
|---|---|
| Sega Card (My Card) dumps | Same `.sms` path, no special handling |
| Pause on START | Reaches the game; slot chords on SELECT are unchanged |

## Acceptance
- [ ] Tests green, `task check` green, touch-point map regenerated.

## Device check (RG34XXSP)
An SMS cart from the maintainer's card, full speed, both buttons and Pause, save and reload.

## References
- ADR 0053; docs/PERFORMANCE.md "Sega core" (SMS 1.302 ms/frame on the device, 12.8x)
