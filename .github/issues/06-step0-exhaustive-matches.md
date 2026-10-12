---
title: "Patch 0001: Replace silent GBA/GB fallthroughs with exhaustive Platform policy"
phase: 1
area: platform
type: feature
size: S
depends_on: [03-task-check-and-upstream-guard, 05-gba-harness-and-bench]
---

## Why
Several upstream sites use `_ =>` or `!= Platform::Gba` and would silently treat a new platform as GB or as GBA (docs/PLAN.md Phase 1 deliverables, Build step 5, Consumer-grep evidence). This patch is behaviour-identical for GBA/GB/GBC and makes every later variant a compile error until it is handled.

## Scope
`patches/0001-step0-exhaustive-matches.patch`:
- [ ] New file `crates/slot-store/src/platform_policy.rs` (second `impl Platform`) with the policy methods used below (`has_gb_palettes`, `owns_shoulders`, `picker_cores`); `mod` line and exports in `slot: crates/slot-store/src/lib.rs`.
- [ ] `slot: crates/slot-store/src/scan.rs:21-32` `read_header`: exhaustive match, no `_ =>`.
- [ ] `slot: crates/slot/src/core.rs:128` `palette_for`: use `has_gb_palettes()`.
- [ ] `slot: crates/slot/src/app.rs:855` `slot_owns_the_shoulders`: use `owns_shoulders()`.
- [ ] `slot: crates/slot/src/app.rs:2643`: use `picker_cores().is_none()` for the early return.
- [ ] `slot: crates/slot/src/app.rs:2646`: `core_for` becomes `core_for_platform(root, stem, cart.platform)`.
- [ ] `slot: crates/slot/src/app.rs:2701`: upstream `!= Platform::Gba` kept unchanged (link cable stays GBA only).
- [ ] `slot: crates/slot-store/src/core.rs:46` `Core::runs`: exhaustive.
- [ ] `slot: crates/slot-ui/src/cart.rs` `gb_shell_of` Outline `_ =>` arm made exhaustive.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No new T-id. Proven behaviour-identical by the upstream suite and the harness |

T1 and the harness compare must stay green with this patch applied. No upstream test file or `#[cfg(test)]` block changes.

## Edge cases
| Case | Expected handling |
|---|---|
| NES ROM with no selected core goes through `core_for` (`slot: crates/slot/src/app.rs:2646`) and defaults to Mgba | Replaced with `core_for_platform(root, stem, cart.platform)` |

## Acceptance
- [ ] `task check` green; `upstream test code: 0 blocks changed`.
- [ ] GBA harness compare 0 diffs (H1, H2).
- [ ] No `_ =>` arm left on `Platform` in the touched functions.
- [ ] `app.rs` hunks are one token each.

## Device check (RG35XXSP)
None, behaviour-identical refactor. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Every `app.rs` hunk should be a single token or expression swap; policy lives in `platform_policy.rs`.
- `slot: crates/slot/src/session.rs:465` also filters on `Platform::Gba` (link player); leave it unless a later patch needs it.
- Enums are untouched in this patch.

## References
- docs/PLAN.md: Phase 1 deliverables (0001), Build step 5, Approach (policy lives in new files), Consumer-grep evidence
- `slot: crates/slot-store/src/scan.rs:21-32`; `slot: crates/slot/src/core.rs:128`; `slot: crates/slot/src/app.rs:855,2643,2646,2701`; `slot: crates/slot-store/src/core.rs:44-49`
