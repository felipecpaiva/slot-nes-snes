---
title: "Set the Lynx core options: lynx_rot_screen always set, lynx_force_60hz off, RGB565"
phase: 12
area: cores
type: feature
size: S
depends_on: [103-platform-lynx]
---

## Why
Step 6. Beetle Lynx declares three options. Two of them change behaviour slot owns, so slot answers all three explicitly (ADR 0093), never the declared defaults.

## Scope
- [ ] `lynx_rot_screen`: always set by slot per game, `0` or `180` (issue 109). Never `auto` (its declared default, which turns the pad 90 or 270 and asks for `SET_ROTATION`), never `manual` (SELECT would turn the screen, and SELECT is slot's).
- [ ] `lynx_force_60hz`: `disabled`. It only changes the reported fps (pinned by `force_60hz_only_changes_the_reported_fps_not_the_game_speed`); pacing is issue 107.
- [ ] `lynx_pix_format`: `16` (RGB565, the declared default; the canvas copy handles it).
- [ ] The declared-key check (patch 0003, `core_option_keys.rs`) covers the `lynx` prefix.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `core_option_keys.rs` | every `lynx_*` key slot sets is declared by the pinned core |
| (exists) | `lynx_core.rs` `the_core_turns_the_pad_for_a_rotated_cart_only_when_lynx_rot_screen_asks_it_to` | what each `lynx_rot_screen` value does |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin renames an option | The declared-key test fails |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
None beyond issue 112.

## References
- ADR 0093; `libretro_core_options.h` at `fcdefcf`
