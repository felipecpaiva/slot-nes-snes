---
title: "Sega: Game Gear, Master System and Mega Drive on Genesis Plus GX"
phase: 7
area: device
type: tracking
size: L
depends_on: [39-cross-platform-performance]
---

## Why
The maintainer wants Game Gear, Master System and Mega Drive shelves. One core, Genesis Plus GX, serves all three (ADR 0050), each as its own `Platform` with no core picker yet. The four maintainer decisions are recorded as ADR 0047 (canvas per core and platform, GG at 3x), ADR 0048 (Sega shaders outside slot.state), ADR 0049 (MD Stretch follows the frame width) and ADR 0050 (one core, one platform each).

## Scope
Child work, in merge order:
- [x] Core build and measurement, no frontend code: `cores/genesis_plus_gx/build.sh`, pin in `SLOT_PIN`, `task core:genesis_plus_gx:host`, `task core:device:genesis_plus_gx`, host and device `core_bench` (docs/PERFORMANCE.md "Sega core").
- [ ] Canvas per (core, platform) (ADR 0047) and the width-change border clear, before the first Sega platform.
- [ ] 51-platform-gg
- [ ] 52-platform-sms
- [ ] 53-platform-md
- [ ] Sega shaders in their own `Config/` file (ADR 0048).
- [ ] Cart art for all three after a VARIANTS-style research pass (outlines and colours cited or photo-sampled, our own procedural renderer, ADR 0042).
- [ ] Ship the core: add it to `core:host`, `core:device`, `dist:device` and `zip-check.sh`, move its licence to `licenses/`. Not before the first platform patch, so no release carries an unused core.

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each platform owns its scan, boot, canvas, input, save and downgrade tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] All child issues done; `task check` green with `SLOT_REQUIRE_CORES=1` and the Genesis Plus GX dylib.
- [ ] Harness: a Sega cart, eject, GBA leg equals the GBA-only run (H3 pattern); `bench:compare` GBA within 2%.
- [ ] Release notes and README carry Genesis Plus GX in the non-commercial notice.

## Device check (RG34XXSP)
1. Heavy MD gate on the maintainer's own cards: Virtua Racing (SVP), Sonic 3D, Street Fighter II SCE (6-button), Thunder Force IV, Vectorman. Full speed, or PicoDrive becomes the MD fallback.
2. `task perf:eval` and `task perf:play` rows for GG, SMS and MD.

## Review notes
- Genesis Plus GX is non-commercial (Charles MacDonald, Eke-Eke, MAME portions). Same stance as snes9x (LICENSING.md).
- Upstream-first: slot#30 says no more systems upstream; nothing system-specific goes upstream.
- Research and plan: the 2026-10-15 Sega plan (slotPlus review, core comparison, input map, save quirk).

## References
- docs/adr/0047 to 0050, docs/PERFORMANCE.md "Sega core", LICENSING.md "Genesis Plus GX"
