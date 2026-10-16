# 0053. Use Genesis Plus GX as the one core for Game Gear, Master System and Mega Drive

- Status: Accepted. Amends [0002](0002-cores.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 50](../../.github/issues/50-sega-tracking.md), [issue 51](../../.github/issues/51-platform-gg.md), [issue 52](../../.github/issues/52-platform-sms.md), [issue 53](../../.github/issues/53-platform-md.md), [ADR 0050](0050-canvas-per-core-and-platform.md), [ADR 0051](0051-sega-shaders-outside-slot-state.md), [ADR 0052](0052-md-stretch-follows-frame-width.md), [PERFORMANCE.md](../PERFORMANCE.md), [LICENSING.md](../../LICENSING.md)

## Context

The maintainer wants Game Gear, Master System and Mega Drive. The candidates were Genesis Plus
GX (all three, non-commercial licence), PicoDrive (all three, the same non-commercial terms,
lighter), Gearsystem (SMS and GG only, GPL-3.0) and BlastEm (MD, GPL-3.0, interpreted on ARM).
slotPlus (nelynes) adds Game Gear as a fork that edits upstream tests and `Host`, which our rules
forbid, so we take nothing from its code.

## Decision

Genesis Plus GX (libretro/Genesis-Plus-GX, pinned in `SLOT_PIN`) serves all three systems. Each
system is its own `Platform` and shelf. There is no core picker for them until a second core is
added (PicoDrive for MD, Gearsystem for SMS and GG are the candidates). Order: core build and
measurement, then Game Gear, Master System, Mega Drive, then cart art. The core is built with the
same rule as the others (ADR 0002): pinned commit and tarball sha256, `make -f Makefile.libretro
platform=unix` with `-mcpu=cortex-a53`, `.meta` stamp, source tarball beside the core. The FM
option stays at its default, `mame (ym2612)`.

## Measured on the RG34XXSP (2026-10-15, performance governor, light test carts)

| Pair | ms/frame | x real time at 59.92 Hz | State size |
|---|---|---|---|
| MD, 240p Test Suite 1.32 | 3.305 | 5.05 | 1,036,288 bytes |
| MD, same, FM set to `nuked (ym2612)` | 11.760 | 1.42 | same |
| SMS, River Strike 0.10 (title) | 1.302 | 12.8 | 1,036,288 bytes |
| GG, Tunnel 1.0 (title) | 1.013 | 16.5 | 1,036,288 bytes |
| SNES on snes9x2005_plus, 240p Test Suite 1.10 | 2.696 | 6.2 (at 60.10 Hz) | 564,544 bytes |

## Consequences

- One build script, one licence stance (the snes9x one: separate program across the libretro C
  ABI, full licence and source shipped, never sold), one set of option and save tests for three
  shelves. Release terms do not change, they are already non-commercial because of snes9x.
- Go for Mega Drive on Genesis Plus GX, provisionally: 5x headroom on a light cart is comparable
  to snes9x2005_plus. The DEVICE-GATE heavy MD titles (Virtua Racing on SVP, Sonic 3D, Street
  Fighter II SCE, Thunder Force IV) still have to run on the device before MD ships; PicoDrive
  is the fallback if one misses. Nuked FM is too slow for fast-forward and stays off.
- The state is about 1 MB on every system, so rewind costs the same per push on GG and SMS as
  on MD, about twice snes9x2005_plus. Serialize is still under 0.5 ms (p95) on the device.
- Licence file: `cores/genesis_plus_gx/LICENSE.txt` until the core shipped, because
  `scripts/dist-device.sh` copies every file in `licenses/` into the release. It moved to
  `licenses/genesis_plus_gx-LICENSE.txt` when the core joined the release (2026-10-16), where
  `zip-check.sh` requires it and compares it with the repo copy.
