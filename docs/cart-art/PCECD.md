# PC Engine CD jewel case (ADR 0104)

Same rules as [PS1.md](PS1.md): every value cites a page opened on 2026-10-21, or says that nothing was
found. The PC Engine CD shelf draws the PlayStation's jewel case and disc unchanged; this page records why
that is the right object and what was looked for.

## 1. The case

| Item | Value | Source |
|---|---|---|
| Case | the standard three-piece jewel case, 142 x 125 x 10 mm | [Wikipedia: Optical disc packaging](https://en.wikipedia.org/wiki/Optical_disc_packaging) ("a three-piece plastic case, measuring 142 by 125 by 10 millimetres"); the same row as PS1.md |
| Front insert | 120 x 120 mm | same page |
| Japanese spine strip (obi) | "folded over the left side of music CDs, video games, LaserDiscs, or DVDs" | [Wikipedia: Obi (publishing)](https://en.wikipedia.org/wiki/Obi_(publishing)) |
| Disc | 120 mm, 15 mm centre hole | [Wikipedia: Compact disc](https://en.wikipedia.org/wiki/Compact_disc); PS1.md section 1 |

Not found: a cited page that shows a CD-ROM², Super CD-ROM² or TurboGrafx-CD case differing from the
standard jewel case on its front. The format logos (CD-ROM², SUPER CD-ROM², ARCADE CD-ROM², TurboGrafx-CD)
are printed on each game's own cover and disc, so the cover art carries them. The "larger jewel cases ...
around the size of VHS keep cases" that page names are Sega CD, Saturn and early PlayStation North
American releases, not this system. So no variant shells are drawn.

## 2. What slot draws

| Shell | When | Notes |
|---|---|---|
| `jewel_jp` | the file name carries a `Japan` tag (`ps1_case::tag_region`) | the PS1 case with the spine strip over x 0 to 169 permille; width an estimate, as in PS1.md |
| `jewel_us` | any other disc (`USA`, no tag) | the plain case |
| disc | every disc, on insert | the PS1 disc: printed from radius 51 to 177 px, hub and hole generated |

The region comes from the name tags only. A PC Engine disc has no `SYSTEM.CNF` serial, and slot never
groups PC Engine discs, so there is no double case.

## 3. Images

- Cover: ScreenScraper `box-2D`, at `Labels/PCECD/<stem>.png`, fitted whole in the square well.
- Disc: ScreenScraper `support-2D`, at `Labels/PCECD/disc/<stem>.png`, printed on the disc's print area.
- Both from one jeuInfos call under system id 114 (`tools/fetch-labels.py`, `PCECD`).
