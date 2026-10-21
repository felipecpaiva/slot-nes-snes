# 0101. Bring the Famicom Disk System into scope on the shipped fceumm, a disk shelf of its own

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems; closes [issue 33](../../.github/issues/33-deferred-fds.md)
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0067](0067-ps1-disk-control-and-disc-in-states.md) (the disc chord), [ADR 0093](0093-lynx-on-beetle-lynx.md) (the BIOS check), [ADR 0072](0072-write-sav-when-the-core-gives-no-state.md), [ADR 0100](0100-shelf-order-option.md), [issue 194](../../.github/issues/194-fds-tracking.md), patches `0120-platform-fds` to `0126-fds-carts`, [docs/research/next-systems-2026-10-20.md](../research/next-systems-2026-10-20.md) (FDS, rank 6)

## Context

The maintainer asked for the Famicom Disk System as a full platform. It was deferred in v1 because it
needs a BIOS and a different save model (issue 33). The 2026-10-20 research ranked it sixth and "a small
job": about 268 titles left over in the unified backup's `ES-DE/Roms/nes`, on fceumm, which slot already
ships for the NES.

What fceumm does with a disk at the pin `ac0d00a` (read in the source, `src/fds.c` and
`src/drivers/libretro/libretro.c`, and pinned by `fds_core.rs`):

- **BIOS.** `FDSLoad` opens `<system dir>/disksys.rom` and reads 8192 bytes. Without it the load fails
  ("FDS BIOS image (disksys.rom) missing"); there is no high-level boot.
- **Files.** `.fds` with the 16-byte fwNES header (`FDS\x1a`, side count at byte 4) or the raw image
  (`*NINTENDO-HVC*` at byte 1, side count from the length), 65,500 bytes a side, up to 8 sides.
- **Saves.** `RETRO_MEMORY_SAVE_RAM` is the live disk itself (`FDSROM`, every side, no header). A game
  that writes to the disk writes there. fceumm keeps the original sides apart only to make states
  smaller (`diskdatao`, XORed in `PreSave` and `PostSave`).
- **Disk control.** No libretro disk-control interface is registered (no `SET_DISK_CONTROL_INTERFACE`
  in the core at this pin). `retro_run` reads the pad: a press of **R** ejects or inserts the disk
  (`FCEU_FDSInsert`), a press of **L** selects the next side (`FCEU_FDSSelect`, refused while the disk
  is in). The disk starts inserted on side A (`FDSInit`, `InDisk = 0`). The selected side (`SELD`) and
  the drive (`INDI`, 255 when empty) are in the state.
- **Region.** `FDSLoad` calls `FCEUI_SetVidSystem(0)`: every disk runs NTSC. The Disk System was never
  sold outside Japan.

BIOS: libretro-database `dat/System.dat`, comment "Nintendo - Famicom Disk System", row
`disksys.rom size 8192 crc 5E607DCF md5 ca30b50f880eb660a320674ed365ef7a` (fetched 2026-10-21). The
maintainer's `Bios/disksys.rom` in the unified backup has that md5 (checked 2026-10-21), so the
research doc's "unverified" note is resolved.

## Decision

- The Disk System is in scope as Phase 18. One shelf `Games/FDS` for `.fds`. The platform is
  `Platform::Fds`, appended to `SHELVES` after CPS2. **No new core**: it runs on `Core::Fceumm`, so
  `Core::EVERY`, the core builds, `SLOT_PIN`, the zip's core list and LICENSING.md are unchanged.
  `Core::runs` gives the disk to fceumm alone (Nestopia also emulates the Disk System, but the NES
  picker does not reach this shelf, and one core keeps the save model single). No picker.
- **Policy: the NES's.** L1 and R1 stay slot's, L2 and R2 are rewind and fast-forward, the NES
  overscan crop, rewind on, the retro shader list, fceumm's 360x240 canvas, Crop by default.
- **BIOS: never shipped, never fetched.** Before launch slot checks `BIOS/disksys.rom`: present, 8192
  bytes, crc32 `0x5e607dcf`. Missing or the wrong size: refuse with "FDS needs BIOS/disksys.rom" (the
  Lynx shape, ADR 0093). Another 8 KB file: launch, toast "disksys.rom is not the known dump" once a
  session. The check is crc32 because slot already has one (`slot_store::lynx::crc32`) and md5 would
  be new code for the same answer; both values are cited above.
- **Disk control: the PlayStation disc chord, SELECT+L2, on this shelf too.** It walks the sides of
  every disk and back: Disk 1 Side A, Disk 1 Side B, Disk 2 Side A, and so on. Because the core takes
  the pad and not a disk interface, slot presses the core's own buttons in the emu thread
  (`slot::fds_disk`): R (eject) on the first frame, L (next side) two frames later, R (insert) 60
  frames after the eject, so a game polling the drive sees the disk out for a second, as when a
  player swaps it. L1 and R1 never reach the core on this shelf, so the player cannot press them by
  accident. After the insert slot reads the side back from the core's state (`SELD`) and shows it as
  a banner; it never counts sides itself, so a state load or a rewind cannot put the banner out of
  step. A one-sided disk is not flipped. `swaps_discs` stays false for the Disk System: the PS1 disc
  path (index file, state trailer) is not used. The PS1 chord was free here: SELECT+L2 is the GB
  palette step back, which the Disk System has no use for.
- **Saves: the ordinary `.sav`.** `Saves/FDS/<stem>.sav` is the disk as the game left it, every side
  without the fwNES header (131,000 bytes for a two-sided disk), written and read by the save path
  every other system uses. The `.fds` on the shelf is only ever read, so deleting the `.sav` gives
  the disk back as dumped, and a RetroArch `.srm` of the same disk loads the same way. A `.sav` whose
  size is not the disk's (another dump under the same name, a different side count) is not loaded half
  over the disk: it is renamed `<stem>.sav.mismatch`, kept, logged, and the game starts from the disk
  as it is (`slot::fds_save`). A disk that is never written still gets a `.sav`, a copy of the disk.
- **Screen section** after CPS2: Shader (the retro list, `Config/fds_shader.txt`) and Picture (the
  NES's: Crop by default, then Stretch, Actual, 4:3; `fds` in `Config/picture.txt`). No PAL Speed row:
  fceumm forces NTSC for every disk. Neither row touches the NES choices.
- **Release order.** `RELEASED` gets `(Platform::Fds, 1986, 2, 21)` (Wikipedia, "Family Computer Disk
  System": "released in Japan on February 21, 1986"), between the Master System and the Atari 7800.
- **Shelf object: the yellow Disk Card.** Wikipedia ("Quick Disk"): "Nintendo packaged the 2.8-inch
  magnetic media in a 3x4-inch housing" and "Most FDS disks did not have cover protection ... but a
  later special series of five games did include a protective shutter"; ("Family Computer Disk
  System"): "the 'NINTENDO' moulding along the bottom of each Disk Card". So the shelf draws the
  yellow card without a shutter: the stepped top edge and centre tab, the raised U panel with the
  head window and the hub, write-protect holes and side notches, a wide label well low on the card
  and the NINTENDO moulding. The values are in [docs/cart-art/FDS.md](../cart-art/FDS.md).
- **Labels.** `tools/fetch-labels.py` system `FDS`: dat `Nintendo - Family Computer Disk System`
  (libretro-database `metadat/no-intro`, headerless CRCs: Adian no Tsue (Japan).fds is 131,000
  bytes), a headered dump hashed without its 16 bytes first; ScreenScraper id 106 (Skyscraper
  `platforms_idmap.csv` at c253bfe, row `fds,106,22,4936`). libretro-thumbnails has no Family
  Computer Disk System Named_Logos (404, 2026-10-21), so the logo fallback takes the ScreenScraper
  wheel.
- **Upstream test sites**, by the standing rule: (b) gains `| Platform::Fds` after `| Platform::Cps2`,
  (g) gains `, "FDS"` after `"CPS2"`, (h) gains `, QuickRow::ScreenFds` after `QuickRow::ScreenCps2`.
  (e) is unchanged: no new core.

## Consequences

- Seven patches, 0120 to 0126. No GBA, GB or GBC path changes, so the harness compare stays at 0 diffs.
  The emu loop gains one atomic load a frame (`fds_disk::press`), no allocation.
- **CI cannot boot a game.** The core tests use a generated disk and an 8 KB placeholder BIOS of
  zeros, under which fceumm loads the disk, exposes it as save RAM and runs the drive. The tests that
  boot the real BIOS read it from `SLOT_FDS_BIOS` and print a BIOS skip otherwise.
- Known gaps: rewinding into the second the disk is out of the drive can leave it out (SELECT+L2
  again puts the next side in); the Disk Writer kiosk and the blue shuttered disks are not drawn; a
  disk that is never written still leaves a full-size `.sav`.
- On a rebase or a fceumm pin bump, re-check that fceumm still drives the disk from L and R and still
  exposes the disk as save RAM (`fds_core.rs`); if it ever registers a disk-control interface, the
  chord should move to it and this ADR be amended.
