---
title: "Set the Sega CD core options: per-game backup RAM, no RAM cart, no precache"
phase: 13
area: cores
type: feature
size: S
depends_on: [114-platform-segacd]
---

## Why
Step 5. Three Genesis Plus GX options decide where Sega CD saves go and what a reload costs. slot answers no option it was not given, so today the core reads them as unset (pinned by `segacd_core.rs`). They must be explicit (ADR 0094).

## Scope
- [ ] `genesis_plus_gx_system_bram = per game`: `<stem>.brm` per game instead of one `scd_U.brm` per region, so one game cannot fill or clobber another's 8 KB and a torn write loses one game.
- [ ] `genesis_plus_gx_cart_size = disabled`: no RAM cart, as today by accident. RetroArch's default (`4meg`, one 512 KB `4Mbit_cart.brm` shared by every game, rewritten whole at every flush) is not wanted. A game that needs the RAM cart is a device-gate finding; then `per game` with the smallest size it needs.
- [ ] `genesis_plus_gx_cd_precache = disabled`: a reload must not read the whole CHD.
- [ ] `genesis_plus_gx_cd_latency` left at the core default (enabled; a few games need it).
- [ ] These go in `core_options_policy.rs`'s fixed Genesis Plus GX list; they are harmless for the cart shelves (the core reads them only for a CD).

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `segacd_core.rs` `by_default_the_core_writes_only_scd_u_brm_into_slots_save_dir_and_only_at_unload` | the unset baseline |
| (exists) | `segacd_core.rs` `per_game_backup_ram_is_named_after_the_disc_stem` | the per-game name |
| (new) | `segacd_options.rs` | slot's open path sets the three values; a load writes only `<stem>.brm` |

## Edge cases
| Case | Expected handling |
|---|---|
| A playlist game | `<m3u stem>.brm`, the same file for every disc (pinned) |
| A ROM hack renamed by ADR 0082 | The `.brm` moves with the stem like a `.sav` |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
Save in two different games; two `.brm` files, each with its own saves.

## References
- ADR 0053, 0064, 0094; `libretro/libretro.c` lines 1385 to 1500 and 1765 at `393f70c`
