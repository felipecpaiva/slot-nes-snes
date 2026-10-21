# Sega CD jewel case (issue 225, ADR 0104)

Same rules as [VARIANTS.md](VARIANTS.md) and [PS1.md](PS1.md): every value cites its source, or says it is
the maintainer's choice. Nothing is guessed.

## What slot draws

A Sega CD game is the PlayStation jewel case of ADR 0069, unchanged: `RetroShell::Ps1(Ps1Case)` with the
same outlines, neutrals, cover well, black tray, disc and insert animation (patch 0142). No new bitmap; a
Sega CD case and a PS1 case with the same cover are the same pixels (`slot-ui/tests/segacd_case.rs`).

| Value | Ours | Source |
|---|---|---|
| Jewel case | 142 x 125 x 10 mm, the PS1 geometry | [Wikipedia: Optical disc packaging](https://en.wikipedia.org/wiki/Optical_disc_packaging), as in PS1.md |
| Disc | 120 mm, printed outside the hub | [Wikipedia: Compact disc](https://en.wikipedia.org/wiki/Compact_disc), as in PS1.md |
| Japanese style | the PS1 obi strip over the hinge | Optical disc packaging (obi "wound around the left side of the case"); Japanese Mega-CD releases are Japanese CD releases. The width is the PS1 estimate |
| Style by region | file name tag, then the disc's region byte at 0x20b (`.cue`, `.iso`), then US | Genesis Plus GX `get_region` at `393f70c` (0x64 Europe, 0xa1 Japan); the BIOS check uses the same rule |
| Double case | a playlist of two or more discs (Night Trap, Prize Fighter) | the PS1 rule |
| US large case | not drawn in v1: the cover is fitted whole in the square well on its edge colour (`box_contain`) | Optical disc packaging, read 2026-10-21: "larger jewel cases that were around the size of VHS keep cases were used for North American releases of games for the Sega CD". A deferred style, like the PS1 disc stack (issue 68) |

## Art

- Cover: ScreenScraper `box-2D` to `Labels/SEGACD/<stem>.png`; disc scan: `support-2D` to
  `Labels/SEGACD/disc/<stem>.png` (the PS1 media pair).
- System id 20: Skyscraper `platforms_idmap.csv` row `segacd,20,20,21` (Gemba/skyscraper `290d2c0`).
- By name only (`--by-name`): a `.chd` has no CRC that a dat or ScreenScraper indexes (Redump "Sega - Mega CD &
  Sega CD" lists track CRCs), so `tools/fetch-labels.py` never hashes a Sega CD disc.
- Logo fallback (`--logo-fallback`): libretro-thumbnails "Sega - Mega-CD - Sega CD" Named_Logos (451 PNGs,
  checked 2026-10-21).
