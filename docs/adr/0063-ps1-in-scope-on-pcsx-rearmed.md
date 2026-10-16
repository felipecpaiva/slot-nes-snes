# 0063. Bring PlayStation into scope, built the NES and SNES way, on pinned pcsx_rearmed

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [PS1 plan](../research/ps1-plan.md), [PS1 spike](../research/ps1-spike.md), [ADR 0047](0047-upstream-first-fixes.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [ADR 0059](0059-need-fullpath-load.md), [issue 56](../../.github/issues/56-ps1-tracking.md)

## Context

docs/PLAN.md lists more systems as something this patch set is not for, and the Sega phase was a
deliberate exception. The PS1 plan (2026-10-15) said go with limits after a device spike. The
spike (2026-10-16) passed every bar: SotN at 4.27 ms a frame and Spyro at 3.61 with threads off,
conversion at most 0.80 ms, analog sticks. Two forks (gmaster1998/slot.ps1, bently0602/slot) and two
derivatives that are not GitHub forks (AaronC1990/tray, oauramos/omega-zero) already run PS1 on
slot. None of
them can be merged as it is: they edit upstream enums and tests, or they are hard forks.

## Decision

- PS1 is in scope as Phase 8, one shelf `Games/PS1` (with `Labels/`, `Saves/` and `States/` PS1
  folders), `Platform::Ps1` appended to `SHELVES` and `Core::PcsxRearmed` to `EVERY`, upstream's
  `ALL` untouched, every policy method answered explicitly. It ships as patches like every other
  system, numbered from 0034.
- Core: libretro/pcsx_rearmed pinned at `c8816799b50388e61cfe237fe2cdbb7d8175f20a`, archive
  sha256 `edeb21fdeef8815521cb9d4488d2cd35746607c968ca9b26cce4e42c09f2dc99`, built through
  `cores/lib.sh` with `HAVE_PHYSICAL_CDROM=0 BUILTIN_GPU=neon` and `-mcpu=cortex-a53` on the
  device, CHD on (`HAVE_CHD=1`, the core default). It fits ADR 0002's build rule with no
  exception. GPL-2.0-or-later, so it combines with our GPL-3.0-or-later directly.
- One core, no picker, the same rule as Genesis Plus GX (ADR 0053) until a second core runs at
  speed.
- BIOS: user-supplied `scph*.bin` in `BIOS/`, never shipped and never in CI.
  `pcsx_rearmed_bios=auto` falls back to HLE when none is found. Every test forces
  `pcsx_rearmed_bios=HLE` with discs generated in the test.
- Where we reuse an idea or a function, the patch commit and LICENSING.md credit its author:
  - bently0602: the fullpath load, the `DiskControl` FFI, the swap rollback, the option set and
    the synthetic EXE and ISO fixture;
  - gmaster1998: the trigger hand-off shape;
  - AaronC1990 (tray): the EXT disk interface, the remembered disc and the threaded-rendering
    finding;
  - oauramos (omega-zero): the build flags, the declared-defaults answer, PAL pacing and the
    crash guard.

## Consequences

- About 9 patches for v1 (issues 57 to 64), analog later (issue 65). PS1 work does not touch
  GBA, GB or GBC: the GBA harness compare stays at 0 diffs for every PS1 patch.
- Upstream reality is unchanged: slot#30 says no more systems, so nothing PS1-specific goes
  upstream. Generic seams follow ADR 0047.
- The README and docs/PLAN.md say PS1 is planned, not shipped, until issue 56 closes.
- On a rebase, check the pin still builds and the option keys still exist at the pin.
