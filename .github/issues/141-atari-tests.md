---
title: "Test both Atari cores with generated carts"
phase: 14
area: tests
type: test
size: S
depends_on: [124-a2600-core-build, 125-a7800-core-build]
---

## Why
The core facts the integration builds on, pinned with no ROM: picture size, rate, sound, states, switches and the BIOS behaviour.

## Scope
- [x] Patch 0060 `atari_core.rs`, 12 tests (atari-plan section 9). Generated 2600 VSYNC kernel carts and a 7800 Maria cart; the 7800 BIOS test reads `SLOT_7800_BIOS`, else prints a BIOS skip (a ROM skip for run-tests.sh).
- [ ] Platform half: scan, canvas rules, switch rows, `atari_then_gba.rs`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `atari_core.rs` | see the plan's table |

## Edge cases
| Case | Expected handling |
|---|---|
| CI has no BIOS | One test prints `skipping: no 7800 BIOS ...`, listed as a ROM skip |

## Acceptance
- [x] 12 tests pass on the host with and without `SLOT_7800_BIOS`.

## Device check (RG34XXSP)
None.

## References
- ADR 0095; docs/research/atari-plan.md
