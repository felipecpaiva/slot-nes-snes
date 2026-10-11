---
title: "Build the deterministic GBA/GB/GBC frame-hash harness and the core_bench compare"
phase: 1
area: tests
type: test
size: L
depends_on: [03-task-check-and-upstream-guard]
---

## Why
Success criterion 1: GBA, GB and GBC must be byte-identical to unpatched slot, proven by a blind frame-hash compare after a control run shows the harness is deterministic, and GBA frame cost must stay within 2% (docs/PLAN.md "Spec", "Quality bar", Build step 26).

## Scope
- [ ] `harness/frame_dump.rs`: driven headless Frontend run that prints a per-frame sha256. Copied into `crates/slot/examples/` of both `build/slot-upstream` and `build/slot` (not a patch).
- [ ] `harness/roms/` + `harness/roms/LICENSES/`: legal homebrew or public-domain GBA/GB/GBC carts with their licence files. Candidates: the 240p Test Suite ports and Yerrick's GB/GBA homebrew. Each licence verified before commit.
- [ ] `harness/root-template/`: the ROMs, `Config/slot.state` with `clock_set=1` and no `cart=`, and a label cache (`System/Cache/Labels`, `slot: crates/slot/src/label_cache.rs:12`) pre-built by `task harness:warm`.
- [ ] Legs: H1 (shelf, quick menu and its screen rows, insert with a mid-insert mark, every GBA shader, blue light, colour correction, L1 and R1, Start and Select, 600 driven frames, SELECT+R1 save state and SELECT+L1 load state, eject with a mid-eject mark) and H2 (the same for GB and GBC, every GB shader, Stretch and Actual on L1 and R1, GB palettes on a DMG-only cart). H3 is added in 09-canvas.
- [ ] Each run copies the template into a fresh temp dir, boots with the emu driven (`set_driven`), waits until `rebuilding_labels()` is false (`slot: crates/slot/src/frontend.rs:417`) plus 120 settle frames, then hashes every published core frame and composited frames at settle points (shelf idle, in-game steady, quick menu steady, after eject).
- [ ] `task harness:warm`, `task harness:control` (same tree twice, must be 0 diffs), `task harness:compare` (upstream vs patched, refuses to run until control passes).
- [ ] Wire `harness:control` then `harness:compare` into `task check` after `check-upstream-tests.sh`.
- [ ] `task bench:compare`: `core_bench` (`slot: crates/slot-retro/examples/core_bench.rs`) on `harness/roms/` carts for mgba and gpsp in both trees.

## Tests
| ID | File | Asserts |
|---|---|---|
| T2 | `harness/frame_dump.rs` | Control run, then H1/H2 across trees: control 0 diffs, then cross-tree 0 diffs |
| T3 | `task bench:compare` | `core_bench` mgba and gpsp, `--frames 6000 --warmup 300 --repeats 5`, three attempts, min of the repeat medians per tree, `harness/roms/`: within 2% |

No upstream test file is touched; `frame_dump.rs` is copied as an example in both trees, never patched in.

## Edge cases
| Case | Expected handling |
|---|---|
| Two runs of the same tree differ (label cache, wall clock, background label check) | Fresh temp copy of the pre-warmed root per run, driven emu, wait for `rebuilding_labels() == false` plus settle, mandatory control run. Any frame that differs in the control run fails the harness before the cross-tree compare |

## Acceptance
- [ ] `task harness:control`: `control: 0 diffs`, with `retries: upstream N, patched M` printed.
- [ ] `task harness:compare`: `compare: 0 diffs (H1, H2)`, each leg run twice per tree, all four runs identical, and patched needing at most upstream's retries plus one.
- [ ] `task bench:compare`: the minimum repeat median of the patched tree over three attempts is within 2% of upstream's for mgba and gpsp (`--frames 6000`), and the output says whether the slot-retro crates are byte-identical between the trees.
- [ ] Failure injection: `task harness:inject` builds a cold-cache root whose twelve label PNGs (6000x6000 greyscale, the decoder's limit is 64 MiB) are generated at run time into a temporary root and never committed, runs `frame_dump composite --no-wait` on it twice (no label wait, composites hashed from frame 1) and fails unless it reports diffs; it also fails if the same `--no-wait` run on a warm cache reports any diff, or if the normal run with the wait on the same cold labels reports any diff.
- [ ] Every ROM in `harness/roms/` has a licence file; no commercial ROM is committed. The GPL carts ship with their v0.23 source tarball and a written source offer in `harness/roms/README.md`.

## Device check (RG35XXSP)
None, host only (macOS, `HeadlessSurface`). The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Gotcha 13 (the harness is non-deterministic by default): label cache, slot.state and saves written between runs, the background label check and wall-clock `now()` all vary. Check every one is neutralised.
- Both trees must link the same `vendor/` cores, or the compare is meaningless.
- `bench:compare` is informational on CI runners (see 29-ci-test-workflow) but gating locally.

## References
- docs/PLAN.md: Phase 1 deliverables (harness, bench), Build step 26, Edge cases by layer (Harness), Gotchas, Verification steps 2 and 3
- `slot: crates/slot/src/frontend.rs:417`; `slot: crates/slot/src/label_cache.rs:12`; `slot: crates/slot-retro/examples/core_bench.rs`
