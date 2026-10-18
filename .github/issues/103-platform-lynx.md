---
title: "Add Platform::Lynx with its own shelf, scan, LNX header reader and explicit policy"
phase: 12
area: platform
type: feature
size: M
depends_on: [102-lynx-core-build]
---

## Why
Step 4. The shelf and the policy answers, built on the 1.8.0 base (ADR 0086).

## Scope
- [ ] `Platform::Lynx` in `SHELVES` (not `ALL`), `Core::MednafenLynx` in `EVERY` with `as_str() == "mednafen_lynx"` and option prefix `lynx`. Folders `Games/Lynx`, `Labels/Lynx`, `Saves/Lynx`, `States/Lynx`.
- [ ] Scan `.lnx` and `.lyx`. Not `.o` or `.bll` (homebrew loaders the core accepts; no dat). A `.lyx` that is not exactly 128, 256 or 512 KB still lists, with a one-line log, because the core will refuse it silently (it goes "illegal" and shows the undrawn fill).
- [ ] Header reader in our own `slot_store::lynx` module: `LYNX` magic, version 1, title at 0x0a (32 bytes, NUL or space padded), rotation byte at 0x3a (1 left, 2 right, anything else none). Title falls back to the stem for `.lyx`, a short file or a blank title. Never panics.
- [ ] Every policy method answers explicitly: `owns_shoulders` false (L and R are Option 1 and 2), `passes_xy_through` false, `select_x_toggles_picture` true, `picker_cores` None, `stretch_crops_height` false, `overscan` (0, 0), `follows_frame_width` false, `has_gb_palettes` false, `rewinds` true, `Core::canvas(MednafenLynx, Lynx) = (240, 160)`.
- [ ] Placeholder cart until issue 111.
- [ ] Named test sites (b) and (e) take `Platform::Lynx` and `Core::MednafenLynx` (ADR 0055).
- [ ] Release: move both licence files to `licenses/`; add the core to `scripts/dist-device.sh` and every list in `scripts/zip-check.sh` (cores, `req`, `ok`, licence and srcmeta checks, the strings pair `mednafen_lynx:Beetle Lynx`), and `Lynx` to its `games` list. README row "planned, not shipped".
- [ ] Credit nelynes/slotPlus 749523c for the shelf shape.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `lynx_platform.rs` `an_lnx_cart_lands_on_the_lynx_shelf_with_its_header_title` | scan, folders, title from 0x0a |
| (new) | `lynx_platform.rs` `the_header_rotation_byte_reads_left_right_or_none` | 1, 2, 0 and junk |
| (new) | `lynx_platform.rs` `a_headerless_lyx_lists_under_its_stem` | `.lyx`, short file, odd size |
| (new) | `lynx_seat.rs` `an_lnx_cart_seats_on_beetle_lynx_through_a_real_session` | BIOS-gated (`SLOT_LYNX_BIOS`), picture 160x102 in 240x160 |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.lnx` with a non-1 version | Treated as headerless by the core; we list it with the stem |
| A title with high-bit bytes | Lossy to UTF-8, trimmed |

## Acceptance
- [ ] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
A Lynx cart boots from the shelf with the BIOS in place. Full gate in issue 112.

## References
- ADR 0050, 0055, 0086; patch 0034 for the shape; docs/research/lynx-plan.md section 6
