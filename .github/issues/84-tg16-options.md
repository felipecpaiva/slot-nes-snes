---
title: "Set the TG16 core options, the scanline window first"
phase: 10
area: cores
type: feature
size: S
depends_on: [83-platform-tg16]
---

## Why
Step 5. slot does not answer a core's declared defaults, and PCE Fast starts at scanlines 0 to 242 when unanswered: 243 lines, which the 240-line canvas halves to 121 rows (pinned by `tg16_core.rs`, `unanswered_scanline_options_draw_243_lines_which_the_240_line_canvas_halves`).

## Scope
- [x] Answer, in the core options policy: `pce_fast_initial_scanline=3`, `pce_fast_last_scanline=242` (mandatory), `pce_fast_hoverscan=352`, `pce_fast_default_joypad_type_p1=2 Buttons`, `pce_fast_disable_softreset=disabled` (issue 87 decides), `pce_fast_turbo_toggling=disabled`, `pce_fast_nospritelimit=disabled`, `pce_fast_ocmultiplier=1`, `pce_fast_frameskip=disabled`, `pce_fast_palette=RGB`.
- [x] Option prefix `pce_fast_` in `option_prefix()`; every key in the declared set (patch 0003's check).
- [x] CD keys (`pce_fast_cdbios`, `pce_fast_cdimagecache`, `pce_fast_cdspeed`, volumes) left unanswered: unreachable from a HuCard.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `core_option_keys.rs` | every TG16 key is declared by the pinned core |
| (new) | `tg16_canvas.rs` (issue 85) | through slot's open path the picture is 256x240, not 121 rows |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin renames a key | The declared-key test fails |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
None beyond issue 90.

## References
- ADR 0064 (answering declared defaults), 0091; docs/research/tg16-plan.md sections 2 and 4

## Outcome (2026-10-19)
Patch `0059-tg16-options`. Every key of the list is answered except `pce_fast_frameskip`, which keeps slot's generic `auto` (it skips only frames slot does not show, ADR 0091). Tests: `slot/tests/tg16_options.rs` (each value answered, each key and value declared by the pin, the CD keys unanswered, frameskip `auto`, no declared-default sweep) and `slot/tests/tg16_canvas.rs` (every canvas pixel through slot's open path; it fails with `pce_fast_initial_scanline` unanswered).
