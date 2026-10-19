---
title: "Keep NGP cart flash safe: core save dir, atomic publish, flush by reload"
phase: 9
area: platform
type: feature
size: M
depends_on: [72-platform-ngp]
---

## Why
Step 7, and the one new problem NGP brings (ADR 0090). NeoPop gives slot no `SAVE_RAM`. It writes its own `<name>.flash` only in `retro_unload_game`, truncating the file in place, into whatever save dir slot hands it (today `Saves/`). slot's `.sav` path, ADR 0072's no-state path and `save_ram_trusted` never see the flash. The facts are pinned by `ngp_core.rs` (patch 0080).

## Scope
- [ ] Core save dir for NGP is `Saves/NGP/` (a policy answer read by `open_named`), so the flash sits beside the platform's `.sav` files and follows ADR 0082's hack updates.
- [ ] Atomic publish: the core writes into a staging dir; before load slot copies `Saves/NGP/<stem>.flash` in, after unload slot publishes it with `persist`'s temp, fsync and rename.
- [ ] Flush by reload on `flush_resume` (lid close, POWER, battery critical, power menu), eject and the 60 s autosave: serialize, unload, publish, load, unserialize, and the game carries on. Measure its cost on the host and the device first; target under one frame.
- [ ] An ADR for the chosen design (plan section 3 lists the options; answering `GET_VFS_INTERFACE` is rejected because every `filestream` core would go through it).
- [ ] The resume state stays the power-cut backstop (it carries the flash, already tested).

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `ngp_core.rs` `the_cart_flash_survives_a_restart_through_slots_save_dir` | the core reads the flash back at load |
| (done) | `ngp_core.rs` `a_state_carries_the_cart_flash_with_no_flash_file` | a state alone restores the flash |
| (new) | `ngp_flash.rs` `a_lid_close_mid_game_puts_the_flash_in_saves_ngp` | real `Session`, flash marker in `Saves/NGP/<stem>.flash` after `flush_resume`, game still running |
| (new) | `ngp_flash.rs` `an_eject_publishes_the_flash_atomically` | no partial file at the final path at any point (staging then rename) |
| (new) | `ngp_flash.rs` `a_torn_flash_file_is_not_published_over_a_good_one` | a failed or short write leaves the old file |

## Edge cases
| Case | Expected handling |
|---|---|
| Game never wrote flash | No file written, no error (the core writes nothing) |
| Old `Saves/<stem>.flash` from a build before this patch | Moved into `Saves/NGP/` once, logged |
| Reload fails mid-flush | The state is already written; log, and resume from it |
| A torn `.flash` at the final path (copied in from elsewhere, or from a build before this patch) | Checked before it is staged for the core: the id is 0x0076, `total_file_length` equals the file size, and every block header fits. A file that fails is moved aside and logged, never loaded, because NeoPop's reader trusts the lengths (plan section 2) |

## Acceptance
- [ ] `task check` green; the three new tests were red with their part of the fix removed.

## Device check (RG34XXSP)
Save in-game, close the lid, pull the battery, boot: the save is there, both resuming and starting fresh. Time the flush by reload under `SLOT_TRACE`.

## References
- ADR 0012, 0034, 0072, 0082, 0090; docs/research/ngp-plan.md section 3
