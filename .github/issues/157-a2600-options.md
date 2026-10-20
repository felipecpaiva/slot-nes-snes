---
title: "Set the Stella 2014 core options slot relies on"
phase: 14
area: cores
type: feature
size: S
depends_on: [156-platform-a2600]
---

## Why
Stella has no TV type, difficulty or region option (atari-plan section 2): those are input. The options it has must be answered so a user's RetroArch habit or a core default change cannot move the picture.

## Scope
- [ ] `stella2014_palette=standard`, `stella2014_mix_frames=disabled`, `stella2014_color_depth=24bit`, low-pass off. Paddle options untouched (issue 172).
- [ ] Every declared option answered (core_option_keys test pattern).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `core_option_keys.rs` extension | every `stella2014_*` key slot sets is one the pinned core declares |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin renames an option | The key test fails |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
None.

## References
- ADR 0095; docs/research/atari-plan.md
