---
title: "Patch 0005: Add Platform::Snes, Core::Snes9x and SNES header titles"
phase: 2
area: platform
type: feature
size: M
depends_on: [09-canvas]
---

## Why
SNES gets its own shelf and folders, and carts are titled from the internal header like GBA, with a safe fallback (docs/PLAN.md Phase 2 deliverables, Build steps 6, 7, 8).

## Scope
`patches/0005-platform-snes.patch`:
- [ ] `slot: crates/slot-store/src/platform.rs`: append `Platform::Snes`; `dir_name` "SNES"; extensions `["sfc", "smc"]`; `picture` (256, 224). `SHELVES` grows to `[Gba, Gb, Gbc, Nes, Snes]`; `ALL` unchanged.
- [ ] `slot: crates/slot/src/root.rs` DIRS: `Games/SNES`, `Labels/SNES`, `Saves/SNES`, `States/SNES` (DIRS becomes `[&str; 28]`).
- [ ] New file `crates/slot-store/src/snes.rs`: title from the internal header. LoROM/HiROM probe by checksum complement; skip the 512-byte copier header when `len % 1024 == 512`; fall back to the stem when the bytes are not printable ASCII (JIS X 0201 titles). `read_header` arm in `slot: crates/slot-store/src/scan.rs:21-32`.
- [ ] `Core::Snes9x` appended in `slot: crates/slot-store/src/core.rs`; `default_for(Snes) = Snes9x`; `text` "Snes9x"; `colour_option(Snes9x) = None` (`slot: crates/slot/src/core.rs:151`); `canvas()` (360, 240); `option_prefix()`.
- [ ] Provisional shader and cart arms like NES (cart solid `#b4b4bc`).
- [ ] `snes_rom(map, copier, sram_kb)` generator added to `crates/slot/tests/nes_common/mod.rs`: LoROM/HiROM, map/type byte 0x02 (ROM+RAM+battery) and SRAM size when battery is wanted, CGRAM backdrop colour 0.

## Tests
| ID | File | Asserts |
|---|---|---|
| T15 | `slot-store/tests/snes_header.rs` | LoROM/HiROM, with and without copier header, plus a JIS X 0201 title: title parsed in the 4 ASCII cases; non-ASCII and garbage fall back to the stem |

`crates/slot-store/src/snes.rs` also carries a `#[cfg(test)]` module for the header parser (new file). T4 is extended for `+ Snes`. Upstream tests stay unmodified, in particular `slot: crates/slot-store/tests/platform.rs:5,11` and `slot: crates/slot-store/tests/core.rs:203`.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Copier header and non-ASCII titles are covered by T15 above |

## Acceptance
- [ ] T4 (with Snes) and T15 green; `task check` green.
- [ ] GBA harness compare 0 diffs (H1, H2).
- [ ] `Platform::ALL.len() == 3` and `Core::ALL.len() == 2` still.

## Device check (RG35XXSP)
None on its own. The phase device check is in 11-phase-2-snes.

## Review notes
- `.fig`/`.swc` are not accepted unless requested (Build step 7).
- Header parse must never panic on short files; the fallback is the stem.
- The region byte is not read here; region auto-pick is in 27-cart-shell-grammar-region.

## References
- docs/PLAN.md: Phase 2 deliverables (0005), Build steps 6, 7, 8, Signature impact table (`root::DIRS`), Test plan (ROM generators)
- `slot: crates/slot-store/src/scan.rs:21-32`; `slot: crates/slot-store/src/core.rs:44-55`; `slot: crates/slot/src/core.rs:151`
