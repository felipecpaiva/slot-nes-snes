---
title: "Add Platform::Md, Mega Drive on Genesis Plus GX with 6-button input and live-width Stretch"
phase: 7
area: platform
type: feature
size: L
depends_on: [52-platform-sms]
---

## Why
Mega Drive is the heaviest of the three: 6-button pads, H32 and H40 widths that can change mid-game, interlace mode 2, and the most core cost (ADR 0053). The go for Genesis Plus GX is provisional on the heavy-title device gate.

## Scope
- [x] `Platform::Md` in `SHELVES`, `Games/MD`, extensions `md`, `gen`, `bin` (folder scoped), title from the header (overseas title at 0x150, else the domestic one if it is ASCII, else the stem).
- [x] Canvas 360x240 at 2x; Stretch follows the last frame width, 320 or 256 (ADR 0052); default Stretch.
- [x] SNES like input policy: X, Y, L, R reach the game (core map: Y to A, B to B, A to C, L to X, X to Y, R to Z, SELECT to MODE), picture toggle on SELECT+X (ADR 0007).
- [x] Core options: `genesis_plus_gx_render=single field`, `genesis_plus_gx_ym2612` left at `mame (ym2612)` (Nuked costs 11.76 ms/frame on the device).
- [x] Region from the header at 0x1F0 (`slot_store::sega::md_regions`, read as Genesis Plus GX reads it; it picks the Japanese or Western cart).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/md_*.rs` | scan, real-core boot, canvas, XYZ input mask, Stretch rect for 320 and 256 frames, border clear when the width changes, save RAM round trip, downgrade to shelf on upstream |

## Edge cases
| Case | Expected handling |
|---|---|
| Game switches H32 and H40 mid-game | Borders cleared, Stretch rect follows on the next frame |
| MODE on SELECT conflicts with slot's SELECT hold | Accepted; MODE is only needed to force 3-button mode at power on |
| `.bin` outside `Games/MD` | Not claimed, folder scoped |

## Acceptance
- [x] Tests green, `task check` green, touch-point map regenerated.
- [ ] Heavy-title device gate passed, or PicoDrive added as the MD fallback.

## Device check (RG34XXSP)
Virtua Racing, Sonic 3D, Street Fighter II SCE (6-button), Thunder Force IV and Vectorman from the maintainer's own card: full speed, fast-forward, rewind, save and reload.

## References
- ADR 0052, 0053; docs/PERFORMANCE.md "Sega core" (MD 3.305 ms/frame on a light cart, 5.05x)
