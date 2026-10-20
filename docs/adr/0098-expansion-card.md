# 0098. An Expansion Card in TF2 lends whole Games folders to the main card through bind mounts

- Status: Accepted
- Date: 2026-10-20
- Deciders: maintainer (Felipe Paiva)
- Related: patches/0098-expansion-card.patch, tools/expansion-card.py, docs/upstream/baseos-frontend-card-issue.md

## Context

The RG34XXSP has two TF slots. PlayStation discs (and later Sega CD and PC Engine CD) outgrow the OS
card, so the maintainer wants a second card that holds whole systems' game folders while everything
else (carts, `Saves/`, `States/`, `Config/`, `Labels/`, `BIOS/`, `System/`) stays on the OS card.

BaseOS 1.3.0 decides the frontend card in `/etc/init.d/rcS`: it tries `/dev/mmcblk1p1` (TF2 p1) first
with `-t vfat`, then `-t exfat`, then runs `fsck.fat -a` and tries `-t vfat` and `-t auto`, and only
then falls back to `/dev/mmcblk0p7` (TF1 p7). `frontend-session` repeats the same order. `baseos.conf`
has no setting to change it. So any mountable TF2 p1 becomes `/mnt/sdcard`. BaseOS runs slot as
root and its busybox `mount` supports `-o bind`.

## Decision

The Expansion Card is GPT with p1 16 MiB of zeros (type Linux reserved, no filesystem), so rcS and
frontend-session fall through to TF1 p7, and p2 exFAT `EXPANSION` holding `Games/<SYS>/`. A new
`System/expansion.sh`, run by `launch_frontend.sh` before slot starts, mounts p2 at `/mnt/expansion`
(exFAT, then vfat) and binds each folder `Config/expansion.txt` lists onto `/mnt/sdcard/Games/<SYS>`.
Slot itself is unchanged: it sees one `Games/` tree. `repair.sh` unmounts anything mounted below the
card, deepest first, before it unmounts the card.

Why zeros and not a small FAT partition holding nothing: a mountable p1 would become the main card.
Why bind mounts and not a second content root in slot: no slot code changes, every path (scan,
prefetch, disc loading, the tools over adb) stays the same, and the shelf degrades to the base card's
folders when the card is out. Why `diskutil partitionDisk` is not used: with GPT it puts a 200 MiB
FAT32 EFI partition first (seen on a disk image on 2026-10-20), which would become TF2 p1.

## Consequences

- Positive: no Rust change, no new upstream test site, two upstream script hunks
  (`launch_frontend.sh` one line, `repair.sh` three lines). The repair fix is upstream-worthy on its
  own (anything mounted below the card made `umount` fail busy) and goes upstream under ADR 0047.
- Positive: saves, states and labels of moved systems stay on the main card, so they survive a card
  swap, and an empty or missing Expansion Card leaves the shelf as it was.
- Negative: files left in a moved folder on the base card are hidden under the bind (the session log
  says so). The launch waits up to one second for a late TF2 when `Config/expansion.txt` lists a
  system. A seated game of a moved system is not resumed while the card is out (slot clears the seat).
- Negative: BaseOS USB storage mode exports TF2 whenever it is present, so the main card is reachable
  over USB only with the Expansion Card out. Card repair never checks the Expansion Card.
- Negative: shutdown relies on rcK's `umount -a -r` (binds first, in reverse mount order); `axp-off`
  refuses a power cut while any persistent filesystem is writable, as it already does for the main
  card, and the kernel shutdown takes over.
- If BaseOS gains a setting to choose the frontend card (draft issue in
  `docs/upstream/baseos-frontend-card-issue.md`), p1 may become an ordinary partition; the bind
  mounts stay as they are.
- On each upstream rebase: re-check the `launch_frontend.sh` and `repair.sh` hunks
  (`docs/UPSTREAM-TOUCHPOINTS.md`) and run `card/test-expansion.sh`.
