# PlayStation jewel case research (ADR 0069)

Same rules as [VARIANTS.md](VARIANTS.md) and [SEGA.md](SEGA.md): every value cites a page opened on
2026-10-17, or is marked "measured from refs/<file>". Where nothing gave a value, the cell says so.
Reference images and licences: [refs/SOURCES.md](refs/SOURCES.md).

## 1. Dimensions

| Item | Value | Source |
|---|---|---|
| Jewel case | 142 x 125 x 10 mm, aspect 1.136 | [Wikipedia: Optical disc packaging](https://en.wikipedia.org/wiki/Optical_disc_packaging) ("a three-piece plastic case, measuring 142 by 125 by 10 millimetres") |
| Front insert (the cover) | 120 x 120 mm, square | same page ("a 120 by 120 millimetres ... booklet") |
| Double (multi-disc) case | no front size given; "slightly thicker than two normal jewel cases stacked on top of each other" | same page (chubby jewel cases) |
| Obi (Japan) | "a J-card-esque paperboard slip wound around the left side of the case"; no width given | same page |
| Disc | 120 mm across, 15 mm centre hole, a clamping area (stacking ring), program area from radius 25 mm | [Wikipedia: Compact disc](https://en.wikipedia.org/wiki/Compact_disc) |

## 2. Measured from the photo

`refs/jewel_case.jpg` (800 x 636) is an empty jewel case with a black tray, front on. That is the
case PS1 games shipped in; the photo itself is not of a PS1 game.

| Feature | Value | Method |
|---|---|---|
| Black tray seen through the lid | #1f1f1f, luma std dev 7.4 | mean RGB of x 500, y 100, 100 x 100 px (stdlib Python over `sips -s format bmp`) |
| Hinge band (ribbed black spine on the left) | about 0.11 to 0.12 of the case width | traced by eye, about 5 px; ADR geometry uses 17 mm of 142 (0.120), the space left of a 120 mm cover with a 5 mm right margin |
| Lid | clear, with a light rim where the plastic is thick | observation |

The photo's case box measures 1.2 where the cited aspect is 1.136 (camera angle or lens, not
established), so outlines use the cited millimetres, not the photo.

## 3. What slot draws

Geometry in the 240 x 211 seated box (142 x 125 mm at 1.69 px per mm), cart box 360 x 317.

| Shell | Outline | Cover well (permille of the box) | Notes |
|---|---|---|---|
| `jewel_us` | one case, x 1 to 239, corner radius 2 | x 120 to 965, y 20 to 980 (304 x 305 px, square) | hinge ribs left of the well |
| `jewel_eu` | same as `jewel_us` | same | no front-visible difference was found: both regions used the same black-tray jewel case, and the PAL and NTSC-U differences named in docs/research/ps1-plan.md are on the spine, the back and the printed insert. The bitmap is a separate file (its own grain) so a hand-painted replacement can differ |
| `jewel_jp` | same as `jewel_us` | same | the obi strip over x 0 to 169 permille (24 mm), paper over the hinge and 7 mm of the cover. The width is an estimate: no source gave one |
| `jewel_double` | two cases: the front one at 0.96 scale, bottom left, the back one 5.7 mm up and to the right | x 115 to 926, y 59 to 981 | draws the extra thickness the source describes as a second case behind; a real chubby case is one thicker case seen from the front |
| disc | 360 x 360, round | print from radius 51 to 177 px (17 to 59 mm) | 15 mm hole, a clear hub to radius 49.5 px (16.5 mm) with a darker stacking ring, a light rim. The print start radius is chosen, not cited: it sits outside the stacking ring |

Colours:

| Name | Value | Source |
|---|---|---|
| `JEWEL_TRAY_BLACK` (case plastic, Overlay colour) | #1f1f1f | section 2 |
| `OBI_PAPER` (strip ground) | #ece9e2 | placeholder off-white, not sampled; every real obi is printed per game |
| Plain disc ground | the title colour (`label_colour`) | as the plain cart label |

## 4. Region and multi-disc picks

- Region: the file name tags first (`USA`, `Europe`, `Japan` and the country names in
  `ps1_case::tag_region`), then the serial in `SYSTEM.CNF` (patch 0034: SLUS and SCUS US, SLES and
  SCES EU, SLPS, SCPS and SLPM JP). Tags first because they cost nothing; the serial needs the disc
  opened, and `.chd` and `.pbp` have none slot can read. No tag and no serial means US, the default
  case.
- Double: an `.m3u` (the user's own, or the one slot writes for `(Disc N)` files) naming two or
  more discs. A double case has no region style.

## 5. Images

- Cover: ScreenScraper `box-2D` ("Boitier : Avant", [webapi2.php](https://www.screenscraper.fr/webapi2.php)
  media table), at `Labels/PS1/<stem>.png`, fitted whole in the well on its own edge colour (ADR 0057).
- Disc: ScreenScraper `support-2D`, at `Labels/PS1/disc/<stem>.png`, cover-fitted to 360 x 360 and
  drawn on the print area only, so the hub and hole stay the generated disc. A `disc/` folder next
  to the covers keeps the stem the only key, the same as every other label, and slot's label
  listing ignores the folder entry.
- Neither is ever a screenshot (`ss`), a back (`box-2D-back`) or a texture scan.

## 6. Open

- Blind render check against reference photos (issue 64 acceptance), including the obi width.
- The 3D disc or disc stack alternative stays deferred (issue 68).
