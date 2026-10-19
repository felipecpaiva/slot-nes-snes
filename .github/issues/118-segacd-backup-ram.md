---
title: "Keep Sega CD backup RAM safe: core save dir, atomic publish, check, flush by reload"
phase: 13
area: platform
type: feature
size: M
depends_on: [116-segacd-options]
---

## Why
Step 7, the one new problem (ADR 0094). Genesis Plus GX gives slot no `SAVE_RAM` for a CD and does not expose the backup RAM in its memory maps. It writes `<stem>.brm` itself, only in `retro_unload_game`, truncating the file in place, into whatever save dir slot hands it (today `Saves/`). **Unlike NGP, the state does not carry it**, so a resume state is no backstop: a power cut loses everything since the last clean eject, resume or not. The facts are pinned by `segacd_core.rs` (patch 0057).

## Scope
- [ ] Core save dir `Saves/SEGACD/` through the per-platform policy answer of NGP issue 75 (reuse it; land 75 first).
- [ ] Atomic publish: the core writes into `Saves/SEGACD/.core/`; before load slot copies `Saves/SEGACD/<stem>.brm` in, after unload it publishes with `persist`'s temp, fsync and rename.
- [ ] Check before staging: a `.brm` that is not 8192 bytes or lacks the format footer (`SEGA_CD_ROM` at 0x1fe0, `RAM_CARTRIDGE___` at 0x1ff0) is moved aside and logged, never handed to the core (which would format over it silently).
- [ ] Flush by reload on `flush_resume` (lid close, POWER, battery critical, power menu), eject and the 60 s autosave: serialize, reload the disc, publish, unserialize; the game carries on.
- [ ] Measure the reload on the device first (plan section 3): `core_bench --reload N` or a device test, on Final Fight CD, Sonic CD and Lunar `.chd`, cold and warm, under `SLOT_TRACE`. Bars: under 100 ms warm at lid close, under 250 ms at eject, one frame (16.6 ms) or a hidden frame at autosave. Host baseline: 0.8 ms synthetic CHD, 2.0 ms median Final Fight CD (M5 Max).
- [ ] If the lid-close bar fails: flush by reload only at eject, autosave and quick menu open, record the loss window in the ADR. A core patch exposing `scd.bram` as `SAVE_RAM` is the last resort, upstream first (ADR 0047), because ADR 0002 builds cores unpatched.
- [ ] The publish skips the write when the bytes equal the published file (the core already skips an unchanged RAM, but its first unload always writes a formatted file).

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `segacd_core.rs` `a_state_does_not_carry_the_backup_ram` | why the state is no backstop |
| (done) | `segacd_core.rs` `the_backup_ram_is_read_at_load_and_not_rewritten_when_unchanged` | the core reads the staged file |
| (done) | `segacd_core.rs` `a_flush_by_reload_writes_the_backup_ram_and_the_game_carries_on_from_its_state` | the reload contract and its host time |
| (done) | `segacd_core.rs` `a_flush_by_reload_of_an_owned_disc_is_timed` | host timing on a real disc (`SLOT_SEGACD_DISC`) |
| (new) | `segacd_bram.rs` `a_lid_close_mid_game_puts_the_backup_ram_in_saves_segacd` | real `Session`, file in `Saves/SEGACD/<stem>.brm` after `flush_resume`, game still running |
| (new) | `segacd_bram.rs` `an_eject_publishes_the_backup_ram_atomically` | never a partial file at the final path |
| (new) | `segacd_bram.rs` `a_short_or_unformatted_brm_is_moved_aside_not_loaded` | the check |

## Edge cases
| Case | Expected handling |
|---|---|
| Game never saved | The first unload still writes a formatted 8 KB file (pinned); publishing it is harmless |
| Reload fails mid-flush (disc removed from the card) | The state is written; log, toast, and resume from the state on the next launch |
| A disc swapped mid-game | The reload loads the playlist, then swaps back to the disc in play (issue 119) before unserialize |
| A `.brm` copied in from RetroArch or muOS (`scd_U.brm`, per region) | Not imported automatically; README says to rename it `<stem>.brm` for the game it belongs to |

## Acceptance
- [ ] `task check` green; the three new tests were red with their part of the fix removed.

## Device check (RG34XXSP)
Save in Lunar, close the lid, pull the battery, boot: the save is there, resuming and starting fresh. The reload times recorded in docs/PERFORMANCE.md.

## References
- ADR 0012, 0034, 0072, 0082, 0094; NGP issue 75 and docs/research/ngp-plan.md section 3 (ngp branch); docs/research/segacd-plan.md sections 2 and 3
