# 0092. Bring WonderSwan and WonderSwan Color into scope on pinned Beetle Cygne, at 60 Hz mode by default

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [WonderSwan plan](../research/wswan-plan.md), [fork review](../research/fork-review-2026-10-18.md), [nelynes survey](../research/fork-nelynes.md) section 2, [ADR 0064](0069-answer-pcsx-declared-option-defaults.md), [ADR 0071](0076-pace-off-panel-cores-at-their-own-fps.md), the NGP groundwork (the precedent, on its own branch), [issue 91](../../.github/issues/91-wswan-tracking.md), [issue 92](../../.github/issues/92-wswan-core-build.md), patch `patches/0059-wswan-core-tests.patch`

## Context

The 2026-10-18 fork review lists WonderSwan and WonderSwan Color (item 18), and the nelynes survey ranks them fourth to adopt (docs/research/fork-nelynes.md, "Recommended to adopt"). nelynes/slotPlus ships it on `main` on libretro/beetle-wswan-libretro, but it adds `Host` fields, answers `SET_ROTATION` with a CPU copy and edits upstream tests and `Platform::ALL`, which ADRs 0009, 0013 and 0015 forbid, so we reimplement and credit.

Beetle Cygne is the only libretro WonderSwan core. Three facts shape the decision, each pinned by a test in `wswan_core.rs`:

- **Speed.** The hardware runs at 75.47 fps (3.072 MHz over 159 lines of 256 cycles). The core's `wswan_60hz_mode` emulates a fifth frame every fourth `retro_run` and reports 60.38 fps. It **declares** `enabled` as the default but starts it `false`, and only a `GET_VARIABLE` answer turns it on. slot answers declared defaults for pcsx_rearmed only (ADR 0064), so unanswered, Cygne runs at 75.47 fps. In both modes the game plays at its own speed: the sound handed out per second is 44100 frames either way.
- **Rotation.** slot answers no `SET_ROTATION`, so Cygne rotates in software into its own buffer. `wswan_rotate_display=portrait` draws 144x224, `landscape` 224x144. Left unanswered it is `manual`, and every SELECT press turns the picture. The core ignores the footer's vertical flag.
- **Saves.** Cygne exposes the cart's SRAM or EEPROM as `SAVE_RAM`, sized by the footer, with no RTC block and no file of its own. That is the ordinary `.sav` path, unlike NeoPop (the NGP groundwork, on its own branch).

## Decision

- WonderSwan is in scope as Phase 11, one shelf `Games/WS` for `.ws` and `.wsc`. The platform is `Platform::Ws`, appended to `SHELVES`; the core is `Core::MednafenWswan`, appended to `EVERY`. Upstream's `ALL` stays untouched and every policy method is answered explicitly, as for PS1 (ADR 0063).
- Core: libretro/beetle-wswan-libretro, pinned at `4b01295838ea89e3f1355bbe4cb5cf98aa6108cd` (its HEAD on 2026-10-18, the same commit nelynes pins). Archive sha256 `bce15c0e2505e15b7b55fa1d51b4a12219d07a67be62bbca5c26678d0d89c659`, checked against GitHub by `build.sh fetch`.
  - It builds through `cores/lib.sh` with the root `Makefile`: `platform=unix` and `-mcpu=cortex-a53` on the device, `platform=osx` on the host.
  - It is plain C (`SOURCES_CXX` is empty, the link driver is `$(CC)`), so no static C++ runtime. The device `.so` needs only `libc.so.6` at GLIBC_2.17, and `task core:device:mednafen_wswan` fails otherwise.
  - The output is `mednafen_wswan_libretro.<ext>`, so the core name is `mednafen_wswan` in `SLOT_PIN` keys, in `vendor/` and in `Core::as_str()`. The option prefix is `wswan`, not the core name (nelynes 3ca1660 lost `cygne_frameskip` to exactly this).
- One core, no picker. No BIOS.
- **Speed: 60 Hz mode by default, Native 75 Hz as a user option.** The platform always sets `wswan_60hz_mode` itself, `enabled` unless the user picked Native in the WonderSwan Screen section. ADR 0071 made Native the PAL default because the panel rate there changes the content's speed (50 fps games run 20% fast at 60). That reason does not carry over: here both modes play the game at its own speed and both show 4 frames in 5 on a 60 Hz class panel. 60 Hz mode is the core author's declared default, not a value tuned for our panel, and at 60.38 fps it sits inside ADR 0071's 2 fps window, on the upstream path that every NTSC core uses (about 1.3% slow on the 59.6 Hz panel; NES at 60.1 fps is 0.8% slow the same way). Native goes through `av_rate::owed_frames` with ticks that run 2 frames, a path no core exercises yet (PAL only ever owes 0 or 1), so it ships with a host test of that path. The choice persists and becomes the user's default, and it applies from the next game, like PAL Speed.
- **Rotation is the core's.** slot keeps refusing `SET_ROTATION` and always sets `wswan_rotate_display` (`portrait` for a cart whose footer byte 0xfffc has bit 0 set, else `landscape`) and `wswan_rotate_keymap=disabled`, so slot is the only button mapper and SELECT never turns the picture behind slot's back. No host rotation code.
- Licence: we treat the combined core as GPL-3.0-or-later. The counts and the headerless list are in LICENSING.md. No file is GPL-2.0-only. `v30mz.c` carries Bryan McPhail's permissive notice asking for a credit, which LICENSING.md and the release notes give. The licence files stay in `cores/mednafen_wswan/` until the core ships with the platform patch (the Genesis Plus GX precedent, ADR 0053).
- Credit: the build recipe from nelynes/slotPlus (273ded9) and the reset jump of the synthetic cart from cloudwithax/unslot (00296a5), both GPL-3.0, in the patch commit and LICENSING.md. The input tables (69b8379, 0f895d3, 2ab147a) are a reference for issue 96, credited there.

## Consequences

- About 7 patches (issues 92 to 99). WonderSwan work does not touch GBA, GB or GBC, so the GBA harness compare stays at 0 diffs.
- Two declared-default traps of the same class: `wswan_60hz_mode` and `wswan_rotate_display`. The options patch (issue 94) must set both on every load, and its tests must fail if either is dropped.
- Saves need no new mechanism. ADR 0072's no-state path and `save_ram_trusted` apply as to any `.sav` core.
- The vertical library (Gunpey, Judgement Silversword and others) needs a 360x240 canvas at 2x and its own button map; the horizontal library is a 3x fit in the GBA-sized path. The input remap is the largest item (issue 96).
- The core is in `task core:host`, `task core:device`, `task check` and `SLOT_REQUIRE_CORES` from now on. It joins `dist:device` and `zip-check.sh` only with the platform patch (issue 93), so no release ships an unused core. This is the issue 57 rule.
- On a rebase, check that the pin still builds and that `wswan_core.rs` still passes, in particular the 60.38 and 75.47 fps tests and the SELECT-on-manual test.
- Numbers to settle at merge: this ADR (0092), issues 91 to 99, the test patch (0064 here, it collides with the NGP and other branches) and Phase 11 in `scripts/setup-github-project.py`.
