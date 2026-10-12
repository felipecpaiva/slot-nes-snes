---
title: "Add task check with shared host cores and the upstream-test-unmodified guard"
phase: 1
area: tests
type: test
size: M
depends_on: [02-patch-pipeline]
---

## Why
Success criterion 1 requires all ~1,400 upstream tests to pass with zero hunks in upstream test code, and real-core tests must not pass vacuously (docs/PLAN.md "Spec", "Quality bar"). Decision: macOS is the primary test job (docs/DECISIONS.md).

## Scope
- [ ] `task core:host`: run slot's `core:mgba:host` and `core:gpsp:host` (`slot: taskfile.yml:83-127`, macOS only) into the shared `vendor/`. Record the gpSP dylib sha256 in `vendor/gpsp_libretro.dylib.sha` on first fetch.
- [ ] `task test`: `cargo test --workspace` in `build/slot`.
- [ ] `task check`: build both trees, build or fetch all host cores, assert `vendor/mgba_libretro.dylib` and `vendor/gpsp_libretro.dylib` exist, then with `SLOT_REQUIRE_CORES=1` run `cargo test --workspace`, `test:card` (`card/test-*.sh`) and `scripts/check-upstream-tests.sh` (05-gba-harness-and-bench adds the harness tasks to it). Print a skip report of ROM-dependent upstream tests.
- [ ] `scripts/check-upstream-tests.sh`: fail if any file under `crates/*/tests/` differs between `build/slot-upstream` and `build/slot`, and fail if any `#[cfg(test)] mod` block in a patched src file differs. Print `upstream test code: 0 blocks changed` on success.
- [ ] `SLOT_REQUIRE_CORES=1` is the single project-level env flag, read only by this repo's tests.
- [ ] The upstream-test guard diffs build/slot against build/slot-upstream (two plain trees), not against a git baseline.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | upstream suite in `build/slot` + `scripts/check-upstream-tests.sh` | `cargo test --workspace` with mgba/gpsp vendored: 0 failures; 0 changed files under `crates/*/tests/`; 0 changed `#[cfg(test)]` blocks in any patched src file |

Every upstream test stays unmodified, including the shape-pinning ones: `slot: crates/slot-store/tests/platform.rs:5,11`, `slot: crates/slot-store/tests/core.rs:203`, `slot: crates/slot-ui/tests/quick_menu.rs:85`, `slot: crates/slot/tests/quick_menu.rs:239`, `slot: crates/slot/tests/render_shelf.rs:49-62` and the in-source `host_with()` at `slot: crates/slot-retro/src/libretro.rs:701-718`.

## Edge cases
| Case | Expected handling |
|---|---|
| gpSP host dylib from the nightly buildbot changes between runs and shifts upstream results | sha256 recorded on first fetch; `task check` fails with "gpsp host dylib changed" until someone re-baselines on purpose |
| Upstream suite passes vacuously because mgba/gpsp are not in `vendor/` | `task check` runs slot's core tasks into the shared `vendor/` and asserts both dylibs exist before `cargo test` |
| A patch touches an in-source `#[cfg(test)]` module (for example `host_with()` in `libretro.rs`) | `check-upstream-tests.sh` extracts every `#[cfg(test)] mod` block from each patched src file in both trees and fails if any differ |

## Acceptance
- [ ] `task check` on macOS: `test result: ok` for every crate and `upstream test code: 0 blocks changed`.
- [ ] Skip report lists only ROM-dependent upstream tests (those needing `sdcard/Games/...`).
- [ ] Changing one line in any `crates/*/tests/` file of `build/slot` makes the guard fail.

## Device check (RG34XXSP)
None, host only. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Gotcha 1 (real-core tests pass vacuously): upstream helpers return early when `vendor/<core>` is missing, so a green suite means nothing unless the cores are proven present. A stub must never be the only thing that ran.
- Real-core upstream tests that silently skip without vendored cores: `slot/tests/bios.rs`, `core.rs`, `e2e.rs`, `gb_palette_recolour.rs`, `gpsp.rs`, `mgba_link.rs`, `link_ui.rs`, `render_gb_palette.rs`, `render_colour_correction.rs`, and slot-retro `rumble.rs`, `netpacket.rs` and the in-source libretro tests (hardcoded `vendor/mgba_libretro.dylib`, `slot: crates/slot-retro/tests/rumble.rs:9`).
- Open question 1 default (upstream tests stay literally unmodified) is enforced by this script.
- Known conflict to settle in this PR: 14-libretro-env-and-hires adds one new `#[cfg(test)] mod env_tests;` line to `libretro.rs`. The guard must compare existing upstream blocks and allow that single new declaration by name, without loosening anything else.

## References
- docs/PLAN.md: Quality bar, Existing-test inventory, Edge cases by layer (Tests), Verification step 2, Gotchas, Open questions
- `slot: taskfile.yml:83-127`; `slot: crates/slot-retro/tests/rumble.rs:9`; `slot: crates/slot-gfx/src/lib.rs:7,23`
