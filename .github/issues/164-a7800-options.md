---
title: "Set the ProSystem core options and say there is no high score cart"
phase: 14
area: cores
type: feature
size: S
depends_on: [163-platform-a7800]
---

## Why
ProSystem has colour depth, low-pass and a dual-stick hack, and nothing for BIOS, region or the High Score Cartridge (atari-plan section 2). The HSC is not supported by the core at this pin, so slot does not offer it.

## Scope
- [ ] `prosystem_color_depth=24bit`, `prosystem_low_pass_filter=disabled`, `prosystem_gamepad_dual_stick_hack=disabled`; every declared option answered.
- [ ] README: 7800 saves are save states only; no high score cart.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `core_option_keys.rs` extension | every `prosystem_*` key slot sets is declared |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin adds HSC support | Revisit: it would be a core-written save file, the NGP flash problem (issue 75) |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
None.

## References
- ADR 0095; docs/research/atari-plan.md
