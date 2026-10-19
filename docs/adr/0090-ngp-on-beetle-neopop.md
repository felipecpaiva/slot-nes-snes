# 0090. Bring NeoGeo Pocket and Pocket Color into scope on pinned Beetle NeoPop, built the NES and SNES way

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [NGP plan](../research/ngp-plan.md), [fork review](../research/fork-review-2026-10-18.md) tier 4, [nelynes survey](../research/fork-nelynes.md) section 1, [ADR 0053](0081-genesis-plus-gx-for-sega.md), [ADR 0063](0068-ps1-in-scope-on-pcsx-rearmed.md), [ADR 0072](0077-write-sav-when-the-core-gives-no-state.md), [issue 70](../../.github/issues/70-ngp-tracking.md), [issue 71](../../.github/issues/71-ngp-core-build.md), patch `patches/0075-ngp-core-tests.patch`

## Context

The 2026-10-18 fork review approved NeoGeo Pocket and Pocket Color as the first new system after
PS1. The 160x152 screen at 3x is 480x456, so it fills the 480-line panel with no scaling and no
rotation. No BIOS is needed. nelynes/slotPlus (`slotPlusUltra`, a8eae4c) runs it on
libretro/beetle-ngp-libretro, but it edits `Host`, upstream tests and `Platform::ALL`, which
ADRs 0009, 0013 and 0015 forbid, so we reimplement and credit.

There are two libretro NGP cores:

- **Beetle NeoPop** (libretro/beetle-ngp-libretro). It is Mednafen's NeoPop, plain C with five C++
  files, and GPL-2.0-or-later. nelynes uses it.
- **RACE** (libretro/RACE, checked shallow at c7810dd, 2026-06-29). It is a different NeoPop
  descendant, also GPL-2.0, and has the same save shape: flash written at shutdown, with
  `retro_get_memory_data` returning NULL for every type. It bundles a binary BIOS replacement,
  `koyote.bin`, whose source and provenance the tree does not document, and ARM32 DrZ80 assembly
  that an aarch64 build does not use. No slot fork runs it. We did not build or measure it.

## Decision

- NGP is in scope as Phase 9, one shelf `Games/NGP` for `.ngp`, `.ngc` and `.ngpc`. The platform
  is `Platform::Ngp`, appended to `SHELVES`; the core is `Core::MednafenNgp`, appended to
  `EVERY`. Upstream's `ALL` stays untouched and every policy method is answered explicitly, as for
  PS1 (ADR 0063).
- Core: libretro/beetle-ngp-libretro, pinned at `a50d5ac288a81f2104ddf43195a4efdd15c72227` (its
  HEAD on 2026-10-18, the same commit nelynes pins). Archive sha256
  `ffeabf2a357548f3a55423d542c31bb1e08571d81d7104f8213df3bfa2eb9c9f`, checked against GitHub by
  `build.sh fetch`.
  - It builds through `cores/lib.sh` with the root `Makefile`: `platform=unix` and
    `-mcpu=cortex-a53` on the device, `platform=osx` on the host.
  - It links `-static-libstdc++ -static-libgcc` because of its C++ files, like snes9x and
    nestopia. The device `.so` needs only `libc.so.6` at GLIBC_2.17, and
    `task core:device:mednafen_ngp` fails otherwise.
  - The output is `mednafen_ngp_libretro.<ext>`, so the core name is `mednafen_ngp` in `SLOT_PIN`
    keys, in `vendor/` and in `Core::as_str()`.
- One core, no picker, the same rule as Genesis Plus GX and pcsx_rearmed. RACE is not taken
  because of the undocumented BIOS blob and because it has no fork precedent. It offers nothing
  on save durability that Beetle lacks.
- Licence: we treat the combined core as GPL-3.0-or-later. The counts and the headerless list are
  in LICENSING.md. No file is GPL-2.0-only. The licence files stay in `cores/mednafen_ngp/` until
  the core ships with the platform patch, because `scripts/dist-device.sh` copies all of
  `licenses/` into the release (the Genesis Plus GX precedent, ADR 0053).
- Saves follow the core's own flash file. Durability is its own issue
  ([75](../../.github/issues/75-ngp-flash-saves.md)), not a side effect of the platform patch. The
  core shows these facts, each pinned by a test in `ngp_core.rs`:
  - NeoPop exposes no `SAVE_RAM`.
  - It writes `<name>.flash` into the frontend's save dir only in `retro_unload_game`, and only
    when the game wrote flash. The write truncates the file in place, so it is not atomic.
  - It reads the file back at load.
  - A save state carries the flash (`FLASH_StateAction`).
- Credit: the build recipe and the synthetic cart header come from nelynes/slotPlus (a8eae4c),
  credited in the patch commit and in LICENSING.md.

- Cart shells (decided by the maintainer on 2026-10-19, issue 78): mono NGP and Pocket Color carts
  both take the NGP pak in the dark grey `0x24 0x25 0x29`. The value is cited from nelynes/slotPlus
  a8eae4c (`NGP_SHELL` in `slot-ui/src/shell.rs`); using it for the Color shell too is the
  maintainer's choice, since no source for a Color shell colour was found. The header byte 0x23 still
  picks the ScreenScraper id for the label (25 or 82).

## Consequences

- About 8 patches (issues 71 to 79). NGP work does not touch GBA, GB or GBC, so the GBA harness
  compare stays at 0 diffs.
- **This is the first core whose save slot never sees.** ADR 0072's no-state path and the
  `save_ram_trusted` filter do nothing for NGP, and the flash only reaches the card when the core
  unloads. Lid close, POWER, battery critical and eject must unload the game, or slot must take
  the flash some other way (issue 75). Until then the resume state is the only power-cut copy.
- The core is in `task core:host`, `task core:device`, `task check` and `SLOT_REQUIRE_CORES`
  from now on. It joins `dist:device` and `zip-check.sh` only with the platform patch (issue 72),
  so no release ships an unused core. This is the issue 57 rule.
- On a rebase, check that the pin still builds and that the flash tests in `ngp_core.rs` still
  pass. Those tests are the contract that issue 75 builds on.
