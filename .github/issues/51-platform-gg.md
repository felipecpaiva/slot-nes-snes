---
title: "Add Platform::Gg, Game Gear on Genesis Plus GX at 3x"
phase: 7
area: platform
type: feature
size: M
depends_on: [50-sega-tracking]
---

## Why
Game Gear is the smallest Sega step: 160x144 like Game Boy, two buttons and Start, one core, one cart shell. First platform on the Genesis Plus GX core (ADR 0053).

## Scope
- [x] `Platform::Gg` in `SHELVES` (not `ALL`), `Games/GG`, extension `gg`, title from the file stem.
- [x] Canvas 240x160 at 3x via `Core::canvas(core, platform)` (ADR 0050); picture 160x144.
- [x] Game Boy like policy: slot owns L1 and R1, X and Y turbo. Shader list: the retro list (Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap, Line, Pixel), not the Game Boy list, by the maintainer's decision of 2026-10-16, stored per ADR 0051.
- [x] Core options: `genesis_plus_gx_gg_extra=disabled`, `genesis_plus_gx_bios=disabled`, `genesis_plus_gx_lcd_filter` off by default.
- [x] Region from the SMS-style header at 0x7FF0 (`TMR SEGA`), GG codes in the region nibble (`slot_store::sega::sms_region`; the Game Gear has one shell, so the region does not change it).
- [x] Placeholder cart until the cart art issue lands (replaced by patch 0028).

- [x] LCD filter (patch 0031, ADR 0060): the Game Gear Screen row and in-game Shader row offer upstream's LCD3x right after Off (`Shader::GG`), stored as `gg=lcd3x` in `Config/sega_shaders.txt`; Off stays the default and the other systems' lists do not change.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/gg_*.rs` | scan finds `.gg`; the real core boots a free test cart under `SLOT_REQUIRE_CORES=1`; canvas is 240x160; save RAM round trip; a card with `cart_platform=gg` boots to the shelf on upstream |

Upstream tests stay unmodified except named sites.

## Edge cases
| Case | Expected handling |
|---|---|
| SMS-mode GG cart (runs in SMS mode on hardware) | Core detects it; picture follows the frame |
| Save RAM never written | Core trims it to 0, no `.sav` written (Genesis Plus GX quirk) |

## Acceptance
- [x] Tests green, `task check` green, touch-point map regenerated.

## Device check (RG34XXSP)
A GG cart from the maintainer's card at 3x, full speed, buttons 1 and 2 and Start, save and reload.

## References
- ADR 0050, 0051, 0053; docs/PERFORMANCE.md "Sega core" (GG 1.013 ms/frame on the device, 16.5x)
