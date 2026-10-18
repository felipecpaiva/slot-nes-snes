---
title: "Master System region override: a Region row in the Master System Screen section"
phase: 8
area: video
type: feature
size: M
depends_on: [66-pal-pacing]
---

## Why
Genesis Plus GX picks a Master System cart's region from its own database (`core/cart_hw/sms_cart.c`
at the pinned 393f70c), and only about 23 SMS titles there are marked `REGION_EUROPE`. Every other
European SMS cart runs as NTSC at 60 fps, so PAL pacing (issue 66, ADR 0071) never engages for it
and it runs about 20% fast. Many SMS games were released only in Europe. The maintainer approved a
manual override on 2026-10-18.

## Scope
- [x] An ADR first (ADR 0076, patch 0047): a fourth row in the Master System Screen section, a per-system setting outside
  `slot.state` (ADR 0051, 0061 pattern), and the option mapping below.
- [x] A **Region** row in `QuickRow::SCREEN_SMS`: Auto / Japan / USA / Europe, Auto by default. Stored
  per system in its own `Config/` file (for example `Config/region.txt`, `sms = europe`) through
  upstream's `ini::write`; a missing or unknown value is Auto (unknown values logged).
- [x] Map it to Genesis Plus GX's declared option `genesis_plus_gx_region_detect`
  (`libretro/libretro_core_options.h:120` at the pin): Auto = `auto`, Japan = `ntsc-j`,
  USA = `ntsc-u`, Europe = `pal`. Answer it only when the platform is Master System, so Game Gear
  and Mega Drive on the same core keep `auto`.
- [x] Changing the row applies from the next game start, like PAL Speed (a live change would need
  the core reloaded; the AV change itself is already followed by issue 66's pacing).
- [x] Credit nothing new unless a fork is used as reference.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/sms_region.rs` | a generated SMS cart the core does not know reports 59.92 fps on Auto, 49.70 with Europe, 59.92 with USA (real Genesis Plus GX) |
| (new) | `slot/tests/sms_region.rs` | with `sms = europe`, a Mega Drive `JUE` cart and a Game Gear cart stay at 59.92; a Mega Drive cart opened after a Europe SMS session is back on Auto |
| (new) | `slot/tests/sms_region.rs` | the Region row is the last row of the Master System section only and starts on Auto; Right walks Japan, USA, Europe, Auto and writes `sms = europe`; an unknown line reads as Auto |

## Edge cases
| Case | Expected handling |
|---|---|
| Region Europe and PAL Speed Panel | the core runs PAL timing, slot paces it at 60 Hz (Panel), as for any PAL game |
| Japan region on an export-only cart that checks the region | the game may refuse to boot, as on hardware; Auto restores it |
| Game Gear cart | no row, option untouched (Game Gear is 60 Hz everywhere) |

## Acceptance
- [x] ADR recorded; harness compare at 0 diffs; `task check` green; named test sites unchanged.

## Device check (RG34XXSP)
Steps in docs/DEVICE-GATE.md, "Master System region".

- [x] Passed 2026-10-18 (build df8a717): Streets of Rage (Europe, Brazil) runs at 60 Hz on Auto (no `pacing at` line) and at 49.701 fps with Region Europe; starved 0, dropped 0, present p50 16.79 ms, no panics.

## References
- issue 66 (#129), ADR 0071; Genesis Plus GX `core/loadrom.c:1148` (`sms_cart_region_detect`),
  `core/loadrom.c:1161` (the `region_detect` override)
