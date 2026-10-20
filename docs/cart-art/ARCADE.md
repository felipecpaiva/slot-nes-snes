# Neo Geo, CPS1 and CPS2 shelf objects (issue 192)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, says it is an estimate from a
named photo, or says it is the maintainer's choice. Sources opened 2026-10-20. Arcade boards have no
cart, so each shelf gets the object the board's games came in that best carries a game's art face-on
(ADR 0099). Patch 0116.

## Neo Geo: the AES home cart

| Value | Ours | Source |
|---|---|---|
| Object | the AES cart, not the MVS | The MVS cart's game is named only on a strip along its top edge: a white label about 165 x 20 mm ("dimensions are 165*20mm", Rom1, arcade-projects.com, MVS labels thread, 2022-07-09; the top-edge placement from the Wikimedia Commons photo `Neo_Geo_cartridge_stack.jpg`). Its big face is bare ribbed plastic, so a face-on shelf could not show the game. The AES cart carries its label on the face |
| Size | 190 x 140 mm face: seated 240 x 177, drawn 360 x 266 | Wikipedia "Neo Geo", caption of the AES cart photo: "The game cartridges measure 19 cm by 14 cm by 2.5 cm" |
| Outline | rounded rectangle, corner radius 4 of 240 | estimate from Evan-Amos, Wikimedia Commons `Neo-Geo-AES-Cartridge-Bottom.jpg` (small radii) |
| Label well | permille 270, 0, 730, 470: centred, from the top edge, about 46% of the width and 47% of the height | estimate from the same photo (the well starts at the top edge and wraps over it) |
| Relief | the seam above the connector band, two bands of eight ribs either side of a centre seam, the shoulder steps beside the well | estimate from the same photo |
| Colour | `2a 2a 2d`, solid black | maintainer's choice: AES carts are black plastic (nostos.market AES vs MVS guide; the photo); the value is our dark black, like the Mega Drive's measured `26 24 2a` |

## CPS2: the B-board top cover

| Value | Ours | Source |
|---|---|---|
| Size | 270 x 400 mm, standing: seated 162 x 240, drawn 222 x 329 | Wikipedia "CP System II", "Dimensions (A+B board pair): 40 x 27 x 8 cm". The drawn size is our choice, as tall as the NES cart, so the shelf keeps its height |
| Outline | chamfered corners at the screw end (12 of 162 across, 17 of 240 down) | estimate from the Flickr photo 19081668@N00/10481320 (Mars Matrix, Japan), the cover spanning pixels 38 to 972 by 85 to 697 taken as 400 x 270 mm |
| Label well | permille 158, 107, 572, 489 (about 112 x 153 mm, portrait) | same photo, label at pixels 138 to 495 by 347 to 600, turned upright |
| Serial sticker | permille 629, 393, 869, 495, in label paper | same photo, the "CAPCOM CP システム II SER. No" sticker at pixels 405 to 500 by 165 to 312 |
| Relief | two grilles of ten slanted vents, the screw at the chamfered end, moulded CAPCOM along the far end | same photo ("two groups of 9 to 11 slanted slots", the screw near the chamfered corner, a raised "CAPCOM" about 120 x 15 mm) |
| Colour by region | Japan green `21 90 59`; USA, Europe, World, Oceania blue `1f 5f ae`; Asia grey `8a 8d 90`; Hispanic and Brazil orange `e0 7a 2a`; rental yellow `e6 c2 29` | the region table of Wikipedia "CP System II" (Japan Green, USA Blue, Euro/Etc./World Blue, Asia Grey, Hispanic Orange, Brazil Orange, Oceania Blue, Rental Yellow), confirmed for green, blue, grey and yellow by the BEEP blog (quiet-village.hatenadiary.org, 2014-12-12). Green is sampled from the Mars Matrix photo; the other values are estimates. The region is read from the set's title (`(Japan 960206)`, `(USA 940323)`, a title with "rent") |

arcade-history.com (game 69578) says pink for Brazil; we follow Wikipedia's table and note the conflict.

## CPS1: the CPS Changer and CPS 1.5 case

| Value | Ours | Source |
|---|---|---|
| Object | the grey case, seen from above | nfgworld.com on the CPS Changer: "Each game was a full-on arcade board, packaged in a large grey case, the same used in several Capcom arcade releases". Most CPS1 boards are bare PCBs; the case is the CPS1 object that carries a game label |
| Size | seated 240 x 200, drawn 360 x 300 | estimate, no dimension found; about the CPS2 cover's footprint, squarer as in the photos |
| Label | on a raised plinth, permille 300, 40, 780, 470 | estimate from Wikimedia Commons `CP_System_Changer_Capcom.jpg` and Wikipedia `CPS_1.5_board.gif` (full-colour art on the plinth, about 40% of the width) |
| Relief | the plinth's edge, a speaker grille of eleven slots, two front bosses, moulded CAPCOM above the JAMMA edge, the serial sticker | same photos |
| Colour | `48 47 4a`, dark charcoal grey | estimate from `CPS_1.5_board.gif` |

## Labels

`tools/fetch-labels.py` systems `NEOGEO`, `CPS1`, `CPS2`. A set is asked from ScreenScraper by its file
name (`romnom=mslug.zip`, how ScreenScraper identifies arcade sets) under 142 (Neo Geo, Skyscraper
`platforms_idmap.csv` row `neogeo,142,36,24` at c253bfe), 6 (Capcom Play System) or 7 (Capcom Play
System 2) (ScreenScraper's own system pages; Skyscraper has no CPS rows). It takes the cart label scan
(`support-texture`) when there is one, else the flyer (what Skyscraper takes as an arcade cover), else
the box front. A name search (`--by-name`) and the logo fallback go by the set's full title from slot's set
table. libretro-thumbnails `FBNeo - Arcade Games` has Named_Boxarts, Snaps and Titles but no Named_Logos,
so the Logo Only fallback uses the ScreenScraper wheel. Which media each set has is not verified per
game: the ScreenScraper search needs a login.

Art is placed whole inside the well, centred on its own edge colour (the Master System rule, ADR 0057),
since a flyer is portrait and the wells are not.

## Check

Rendered with libretro-thumbnails box art beside the Genesis cart (the review sheet in the PR):
`Metal Slug - Super Vehicle-001`, `Final Fight (World, set 1)`, `Dungeons & Dragons - shadow over mystara
(960206 Japan)`. Every other neutral regenerates byte for byte (sha256 compared before and after).
