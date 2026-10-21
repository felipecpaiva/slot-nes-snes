# Famicom Disk System disk art (issue 201)

Same rules as [VARIANTS.md](VARIANTS.md): every value cites its source, or says it is the
maintainer's choice. Nothing is guessed.

## The Disk Card

One disk for every Disk System game, `RetroShell::Fds` (patch 0126).

| Value | Ours | Source |
|---|---|---|
| One disk for every game | one shell, no variants | Wikipedia, [Quick Disk](https://en.wikipedia.org/wiki/Quick_Disk), checked 2026-10-21: "Nintendo packaged the 2.8-inch magnetic media in a 3x4-inch housing" |
| No shutter | none drawn | same page: "Most FDS disks did not have cover protection to prevent media contamination, but a later special series of five games did include a protective shutter" (the blue disks) |
| NINTENDO moulding | block letters recessed along the bottom band | Wikipedia, [Family Computer Disk System](https://en.wikipedia.org/wiki/Family_Computer_Disk_System), checked 2026-10-21: "the 'NINTENDO' moulding along the bottom of each Disk Card"; letter shapes are ours |
| Size | seated 240 x 282, drawn 312 x 367 | measured on the Zelda photo below: 960 x 1127 px, 1127 / 960 x 240 = 281.75, rounded up |
| Outline | top edge stepping up at both corners (x 1 to 22, 217 to 239) and round the centre tab (x 95 to 140), 7 units lower between; small bottom corners (r 3) | both photos below; positions measured on the Zelda photo, rounded |
| Relief | the raised U panel (x 76 to 160, round bottom at y 165), the head window (x 108.5 to 128.5, y 12.5 to 92.5, dark), the hub (r 24, lighter), write-protect holes (dark) and side notches, the label recess and the NINTENDO band frame, the "A" arrow | the Zelda photo below; positions measured, rounded |
| Label well | permille 154, 610, 839, 856 (214 x 90 px drawn) | measured on the Zelda photo (the side A sticker) |

Reference photos (proportions only, not shipped):

- Wikimedia Commons [Famicom Zelda Disk.png](https://commons.wikimedia.org/wiki/File:Famicom_Zelda_Disk.png)
  (Poirier273, CC BY 2.5), 1336 x 1568 px, read at 960 x 1127.
- Wikimedia Commons [Nintendo-Famicom-Disk-System-Floppy.jpg](https://commons.wikimedia.org/wiki/File:Nintendo-Famicom-Disk-System-Floppy.jpg)
  (Evan-Amos, public domain), 2936 x 2936 px, read at 960 x 960.

Drawn by us as `crates/slot-ui/assets/fds_cart.svg` (outline) and `fds_cart_detail.svg` (relief, the dark
head window and holes, the lighter hub), lit into `assets/retro/fds_neutral.png` by
`examples/retro_neutrals.rs`. Every other neutral regenerates byte for byte (sha256 compared before and
after).

## Shell colour

| Disks | Colour | Source |
|---|---|---|
| Every disk | `ff c4 00`, solid | the median of 20 x 20 px patches of the blank disk's plastic in Evan-Amos' photo (five patches, `ffc400` to `ffc600`), 2026-10-21. The photo is lit for a white background, so a real disk may be a little darker; to be checked against one |

A colour in `Config/cart_shell.txt` still overrides it. The blue Disk Writer disks are not drawn.

## Labels

`tools/fetch-labels.py`, system `FDS`: dat `Nintendo - Family Computer Disk System` (libretro-database
`metadat/no-intro`, CRCs of the disk without the 16-byte fwNES header, so a headered dump is hashed without
it first); ScreenScraper `fds` 106 (Skyscraper `platforms_idmap.csv` at c253bfe, row `fds,106,22,4936`).
libretro-thumbnails has no `Nintendo - Family Computer Disk System` Named_Logos (404, checked 2026-10-21),
so `--logo-fallback` takes the ScreenScraper wheel.
