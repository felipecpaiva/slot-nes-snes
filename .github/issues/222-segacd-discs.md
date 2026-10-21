---
title: "Swap Sega CD discs, remember the disc, record it in states"
phase: 21
area: platform
type: feature
size: S
depends_on: [217-platform-segacd]
---

## Why
Step 8. Night Trap and Prize Fighter are two-disc games in the library. ADR 0067's machinery (swap, rollback, remembered disc, state trailer) applies, with two differences pinned in the core source: Genesis Plus GX registers only the legacy disk-control interface (13, `retro_init`), so there is no `set_initial_image`, and it holds 4 discs at most.

## Scope
- [x] Swap on SELECT+L2 as on PS1 (L2 is unused on the Mega Drive pad), with ADR 0067's rollback and banners.
- [x] `Saves/SEGACD/<stem>.disc` written on every swap; restored by a swap right after load (eject, set index, close), since the core has no initial-image call.
- [x] The state trailer of ADR 0067 for a game with more than one disc, the PS1 trailer itself (`SLOTPSX` and version 1, the disc index little-endian u32): the magic names the format, and a state never leaves `States/SEGACD`.
- [x] The flush by reload of issue 221 reloads the playlist and swaps back before unserialize.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `segacd_core.rs` `an_m3u_names_its_discs_relative_to_itself_and_names_the_backup_ram` | relative playlist lines load, absolute ones do not |
| (done, 0139) | `segacd_discs.rs` | swap to disc 2 of a synthetic two-disc playlist (dummy BIOS), rollback of an out-of-range index, the `.disc` file, restore after load, the trailer round trip |

## Edge cases
| Case | Expected handling |
|---|---|
| `.disc` says 3 for a two-disc game | Disc 1, logged |
| A state with no trailer | Loads on the current disc |

## Acceptance
- [x] `task check` green.

## Device check (RG34XXSP)
Night Trap: swap to disc 2, eject, reinsert: disc 2 is in.

## References
- ADR 0067, 0104; `libretro/libretro.c` lines 2762 and 3835 at `393f70c`
