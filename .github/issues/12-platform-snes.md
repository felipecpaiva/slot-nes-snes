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
- [x] `slot: crates/slot-store/src/platform.rs`: append `Platform::Snes`; `dir_name` "SNES"; extensions `["sfc", "smc"]`; `picture` (256, 224). `SHELVES` grows to `[Gba, Gb, Gbc, Nes, Snes]`; `ALL` unchanged.
- [x] `slot: crates/slot/src/root.rs` DIRS: `Games/SNES`, `Labels/SNES`, `Saves/SNES`, `States/SNES` (DIRS becomes `[&str; 28]`).
- [x] New file `crates/slot-store/src/snes.rs`: title from the internal header. LoROM/HiROM probe by checksum complement; skip the 512-byte copier header when `len % 1024 == 512`; fall back to the stem when the bytes are not printable ASCII (JIS X 0201 titles). `read_header` arm in `slot: crates/slot-store/src/scan.rs:21-32`.
- [x] `Core::Snes9x` appended in `slot: crates/slot-store/src/core.rs`; `default_for(Snes) = Snes9x`; `text` "Snes9x"; `colour_option(Snes9x) = None` (`slot: crates/slot/src/core.rs:151`); `canvas()` (360, 240); `option_prefix()`.
- [x] Provisional shader and cart arms like NES (cart solid `#b4b4bc`).
- [x] `snes_rom(map, copier, sram_kb)` generator added to `crates/slot/tests/nes_common/mod.rs`: LoROM/HiROM, map/type byte 0x02 (ROM+RAM+battery) and SRAM size when battery is wanted, CGRAM backdrop colour 0.

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
- [x] T4 (with Snes) and T15 green; `task check` green (1460 passed, 0 failed, lint 0 new, `check-upstream-tests.sh` 0 blocks changed, `task patches:check` rebuilds HEAD exactly).
- [x] GBA harness compare 0 diffs (H1, H2). Coordinator's `task check` on 6be060e: 1460 passed, 0 failed; control 0 diffs; compare 0 diffs (H1, H1G, H2, B1, H3); inject ok.
- [x] `Platform::ALL.len() == 3` and `Core::ALL.len() == 2` still.

- [x] `app.rs` changed lines across 0001 to 0005: 6 + 8 + 0 + 4 + 4 = 22 (budget 25).

## Decisions
- `owns_shoulders(Snes)` is true, grouped with NES, until issue 15 (patch 0007) sets it false with the input changes.
- No `#![allow(dead_code)]` in our helpers. `nes_common/mod.rs` holds the NES helpers (`require_core`, `fceumm`, `nes_rom`); `snes_common/mod.rs` holds `snes_rom`, `Map` and `SNES_TITLE`, used by `snes_rom.rs` and later SNES tests. `cargo clippy -p slot --tests` shows no dead_code from either.
- The header probe accepts a candidate only if the complement/checksum pair matches (checksum not 0x0000 or 0xFFFF) and the map-mode byte at header+0x15 is `001x_mmmm` with a low nibble that fits the probe: 0x7FC0 takes 0, 2, 3 (LoROM, SDD-1, SA-1), 0xFFC0 takes 1, 5. When both validate, LoROM wins (pinned by a test). ExHiROM (0x40FFC0, a handful of carts over 4 MB, mostly Japanese titles) is not probed and falls back to the stem.
- The two earlier tests `nes_platform.rs` (SHELVES) and `nes_core.rs` (EVERY) now assert prefixes (`SHELVES[..4]`, `EVERY[..3]`), because the lists grew. They are ours, not upstream.
- `option_prefix` "snes9x" confirmed from libretro/snes9x master `fae2fea0` (`libretro_core_options.h` keys `snes9x_region`, `snes9x_overscan`, and so on). That file declares no frameskip key, so the existing "declares no frameskip option" log line will print for snes9x. Issue 13 pins the commit.
- Every new test was shown red under a throwaway mutation (22 mutations across `snes_header`, `snes_platform`, `snes_core`, `snes_rom` and the `snes.rs` in-source tests).

## Device check (RG35XXSP)
None on its own. The phase device check is in 11-phase-2-snes.

## Review notes
- `.fig`/`.swc` are not accepted unless requested (Build step 7).
- Header parse must never panic on short files; the fallback is the stem.
- The region byte is not read here; region auto-pick is in 27-cart-shell-grammar-region.

## References
- docs/PLAN.md: Phase 2 deliverables (0005), Build steps 6, 7, 8, Signature impact table (`root::DIRS`), Test plan (ROM generators)
- `slot: crates/slot-store/src/scan.rs:21-32`; `slot: crates/slot-store/src/core.rs:44-55`; `slot: crates/slot/src/core.rs:151`
