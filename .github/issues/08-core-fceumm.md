---
title: "Patch 0003: Add Core::Fceumm, Core::EVERY and per-core option prefixes"
phase: 1
area: cores
type: feature
size: M
depends_on: [07-platform-nes, 04-fceumm-core-build]
---

## Why
NES carts must open fceumm by default without growing `Core::ALL`, which upstream tests pin at 2 (docs/PLAN.md Phase 1 deliverables, Build step 8, Approach).

## Scope
`patches/0003-core-fceumm.patch`:
- [x] `Core::runs`: replace upstream's `Core::Mgba => true` with an exhaustive `match platform` (Mgba runs Gba, Gb, Gbc only). This arm can never cause a compile error on a new platform, so it must be changed here by hand; T6 proves a `Mario = mgba` line is dropped for a NES cart.
- [x] `slot: crates/slot-store/src/core.rs`: append `Core::Fceumm`; `as_str` = `fceumm` (dylib stem); `text` "FCEUmm"; `parse`, `runs`, `default_for(Nes) = Fceumm` arms (`:44-55`).
- [x] New file `crates/slot-store/src/core_policy.rs`: `Core::EVERY`, `option_prefix()`, `has_colour_correction()` (false for Fceumm).
- [x] `core_for_platform(root, stem, platform)`: a `selected_core.txt` line naming a core that does not run the platform is dropped.
- [x] `slot: crates/slot/src/core.rs:151` `colour_option(Fceumm) = None`.
- [x] `apply_core_options` (`slot: crates/slot/src/core.rs:178`): set `{prefix}_frameskip` only when the core declares it; set fceumm's overscan options so the full 256x240 is shown.
- [x] Named upstream test exception: `crates/slot/tests/gpsp.rs` `both_cores_are_told_about_colour_correction_in_their_own_words` matches exhaustively over `Core`; its `Core::Mgba` arm gains `| Core::Fceumm` (one token, checked byte for byte by `scripts/check-upstream-tests.sh`).

## Tests
| ID | File | Asserts |
|---|---|---|
| T6 | `slot-store/tests/nes_core.rs` | `core_for_platform(Nes)` = Fceumm; a `Mario = mgba` line is dropped; `Core::ALL.len() == 2`; `parse(as_str())` round-trips over `EVERY` |

Upstream tests stay unmodified, in particular `slot: crates/slot-store/tests/core.rs:95,203`, `slot: crates/slot-ui/tests/board.rs:221` and `slot: crates/slot/tests/core_options.rs:59` (all iterate `Core::ALL`).

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Missing fceumm dylib at runtime is handled in 09-canvas (`MockCore::sized`) |

## Acceptance
- [x] T6 green; `task check` green (1418 passed, 0 failed).
- [x] GBA harness compare 0 diffs (H1, H1G, H2, B1): mgba still gets `mgba_frameskip` exactly as upstream (32 mgba and gpsp option sets compared with upstream, identical); `core_bench` minimum of medians 99.0% to 100.0% of upstream.
- [x] `Core::ALL.len() == 2` still.

## Device check (RG34XXSP)
None on its own. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Plan circularity, flagged not resolved: the plan takes fceumm's overscan key names "from the T32 dump", but T32 (`core_option_keys.rs`) is a Phase 3 test in 22-ff-and-rewind. For this patch, read the keys from fceumm's declared options at the pinned commit and note the source in the PR description (commits here have no body, CONTRIBUTING section 7); T32 later confirms them.
- `slot: crates/slot/src/frontend.rs:602,606` still read `Core::ALL` in this patch; they move to `EVERY` in 20-core-picker-pairs.
- Confirm `apply_core_options` for Mgba/Gpsp is byte-for-byte the upstream behaviour.

## References
- docs/PLAN.md: Phase 1 deliverables (0003), Build step 8, Consumer-grep evidence (`Core::ALL`, frameskip key)
- `slot: crates/slot-store/src/core.rs:44-55`; `slot: crates/slot/src/core.rs:151,178`
