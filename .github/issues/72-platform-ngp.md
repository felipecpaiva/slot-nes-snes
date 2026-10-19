---
title: "Add Platform::Ngp with its own shelf, scan and explicit policy"
phase: 9
area: platform
type: feature
size: M
depends_on: [71-ngp-core-build]
---

## Why
Step 4. The shelf and the policy answers, built on the 1.8.0 base (ADR 0090).

## Scope
- [ ] `Platform::Ngp` in `SHELVES` (not `ALL`), `Core::MednafenNgp` in `EVERY` with `as_str() == "mednafen_ngp"` (the dylib name) and option prefix `ngp`. Folders `Games/NGP`, `Labels/NGP`, `Saves/NGP`, `States/NGP`.
- [ ] Scan `.ngp`, `.ngc`, `.ngpc` (not `.npc`, in no No-Intro dat); `._` files skipped; title from the stem.
- [ ] Header reader in our own `slot_store::ngp` module: colour flag at 0x23 (0x10 Color, 0x00 mono), title at 0x24 (12 bytes), the `COPYRIGHT BY SNK CORPORATION` or ` LICENSED BY SNK CORPORATION` signature. A short or unsigned file still lists, as mono.
- [ ] Every policy method answers explicitly, like PS1 (patch 0034): `owns_shoulders` true, `passes_xy_through` false (X and Y turbo), `select_x_toggles_picture` true, `picker_cores` None, `stretch_crops_height` false, `overscan` (0, 0), `follows_frame_width` false, `has_gb_palettes` false, `rewinds` true, `Core::canvas(MednafenNgp, Ngp) = (240, 160)`.
- [x] Placeholder cart until issue 78 (replaced by the pak in patch 0064).
- [ ] Named test sites (b) and (e) take `Platform::Ngp` and `Core::MednafenNgp` (ADR 0055).
- [ ] Release: move `cores/mednafen_ngp/mednafen_ngp-GPL-2.0.txt` to `licenses/`; add the core to `scripts/dist-device.sh` and every list in `scripts/zip-check.sh` (cores, `req`, `ok`, the licence and srcmeta checks, the strings pair), and `NGP` to its `games` list. README row "planned, not shipped".
- [ ] Credit nelynes/slotPlus a8eae4c for the shelf shape in the patch commit.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ngp_platform.rs` `an_ngc_cart_lands_on_the_ngp_shelf` | scan, folders, title from the stem |
| (new) | `ngp_platform.rs` `the_header_colour_byte_picks_color_or_mono` | 0x10 and 0x00, and a short file falls back to mono |
| (new) | `ngp_seat.rs` `an_ngp_cart_seats_on_neopop_through_a_real_session` | `require_core("mednafen_ngp")`, picture 160x152 in 240x160 |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.ngp` file that is a Color cart | Shell follows the header byte, not the extension |
| A file under 0x30 bytes | Lists with the stem as title, mono, never panics |

## Acceptance
- [ ] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
An NGP cart boots from the shelf. Full gate in issue 79.

## References
- ADR 0050, 0055, 0090; patch 0034 for the shape; docs/research/ngp-plan.md section 6
