# Cart variant research (issue #25)

Research only. Every row below cites a page that was opened while writing this file. Where a source gave no value, the cell says so: an uncited colour or measurement is dropped, never guessed. Issue 26 (cart art) builds the SVGs from this; `evals/eval-colour-sources.sh` later checks every table row against it.

Reference images: [refs/SOURCES.md](refs/SOURCES.md) (files, authors, licences, link-only entries).

## 1. How slot draws carts today (geometry baseline for issue 26)

Read from the pinned upstream tree, `work/slot/crates/slot-ui/src/cart.rs` and `assets/`:

| Item | Value | Where |
|---|---|---|
| GBA/GB/GBC shell colour | per-game table in `shell.rs` (`EXACT`, `FAMILY`, `GB_CODES`); NES placeholder `[0x8c,0x8c,0x8c]`, SNES placeholder `[0xb4,0xb4,0xbc]`, both Solid | `shell.rs` `shell_for` |
| Placeholder colours | Not research-backed. They are Phase 1 stand-ins and must be replaced by cited values or removed | `shell.rs` |
| Outline selector | `Outline::{Auto, Notched, Rounded}` parsed from `Labels/cart_shell.txt` as `<outline> <rrggbb> <solid\|clear\|glitter>` | `slot-store/src/cart_shell.rs` |
| Silhouette | One SVG per shell, rasterised to an alpha mask plus a depth mask; `cart.svg` viewBox `0 0 240 141` | `assets/cart.svg`, `silhouette.rs` |
| GBA body | x from 6.5 to 233.5 of 240 (body is 94.6% of the box); two 28.89-high shoulders step out to the full width at the top | `cart.svg` path |
| GBA label window | fractions of the cart box: x 0.135 to 0.875, y 0.231 to 0.882 (`label_panel`) | `cart.rs` |
| GB (notched) | viewBox `0 0 240 259`; body x 6.5 to 233.5; a 11.5 high step on the right: top edge runs to x 213.1, drops to y 11.5, continues to 233.5; corner radii about 4 to 5 | `gb_cart.svg` |
| GBC (rounded) | same box; top corners radius 18, bottom corners about 4.3 by 3.4 | `gbc_cart.svg` |
| GB label window | x 0.147 to 0.854, y 0.291 to 0.868 | `gb_label_panel` |
| Ridges and cuts | `cart_detail.svg` holds `ridge` and `cut` groups drawn into a detail mask | `assets/cart_detail.svg` |
| Seated box | width 240 for every platform; height 141 (GBA) or 259 (GB, GBC) | `SEATED_W`, `SEATED_H`, `GB_SEATED_H` |
| Cart box on shelf | width 360 (GBA), 312 (GB) | `CART_W`, `GB_CART_W` |
| Platform dispatch today | `Platform::Nes` and `Platform::Snes` both fall into `Shape::Gba` in `shape_of`, `seated_box` and `cart_box` | `cart.rs` |

Takeaway for issue 26: the box width is fixed at 240 and the height varies per shape. Pick the seated height from the real aspect ratios in section 2 (NES is portrait like the GB box, SNES is landscape like the GBA box).

## 2. Outlines

Aspect is width : height of the plastic shell front when known. All mm values are from the cited page.

| Variant | Shell size (W x H x D, mm) | Aspect (W/H) | Outline notes | Source |
|---|---|---|---|---|
| `nes` (NES Game Pak, 72-pin, US NTSC and PAL/EU) | 120 x 133 x 20 (cited as 13.3 cm tall, 12 cm wide, 2 cm thick; "all officially licensed NTSC-U and PAL region cartridges") | 0.902 | Portrait, near-square. Squared body with a narrower lower part where the card edge enters (see the stepped bottom in the photo `refs/nes.jpg`). Ribbed finger-grip band down the left; a recessed label field in the upper right and a small triangle arrow mark below it (observed in `refs/nes.jpg`, no mm source for those). Early carts use five slotted screws, post-1987 carts use two moulded clips. | [iFixit NES Cartridge](https://www.ifixit.com/Device/NES_Cartridge) |
| `nes` label | 55 x 97 mm label, "with the top 7 mm of that in the fold-over", so the visible label face is about 48 x 97 | 97 : 55 landscape within a portrait shell | Label is wider than tall, sits in the upper part of the shell. Label window fraction of shell: 97/120 = 0.81 wide, 55/133 = 0.41 tall (computed from the two cited numbers; position within the shell not given by this source) | [nesdev: NES cartridge dimensions](https://www.nesdev.org/wiki/NES_cartrige_dimensions) |
| `nes` 72-pin cart body (PCB inside) | PCB 100 wide x 1.2 thick; card edge 93.5 wide, 14.5 deep, pads 12 high x 3 wide; notches 97 mm, 90 mm and 3.5 mm wide, notch heights 6 mm and 2.5 mm; cutout heights 25.5, 40.5, 44.5, 65.5, 95.5 depending on board | n/a | This is the board, not the shell. It bounds the shell lower step: shell is 120 wide, the card edge 93.5 wide. Use for the bottom opening width (93.5 of 120 = 0.78 of shell width, computed) | [nesdev: NES cartridge dimensions](https://www.nesdev.org/wiki/NES_cartrige_dimensions) |
| 72-pin vs 60-pin connector | NES connector 72 pins at 2.50 mm pitch; Famicom 60 pins at 2.54 mm pitch | n/a | Famicom parts are on the side opposite the label, NES parts on the label side | [nesdev: Cartridge connector](https://www.nesdev.org/wiki/Cartridge_connector) |
| `famicom` (HVC cassette, 60-pin) | Shell size: not found in any page opened. A search snippet quoted 108 x 71 x 17 mm but the page behind it was not opened, so it is dropped | not sourced; the photo `refs/famicom.jpg` shows a wide, short shell (visibly wider than tall) | "Short, wide": a rounded-corner rectangle with a narrower, stepped lower section where the connector enters. Label is a flat silver-white rectangle across the upper two thirds. Original design plan was a cassette-tape-size cartridge that "ended up being twice as large" | [Wikipedia: NES](https://en.wikipedia.org/wiki/Nintendo_Entertainment_System) (cassette remark); photo description at [Commons HVC-SM](https://commons.wikimedia.org/wiki/File:HVC-SM_cassette_face_20090828.jpg) |
| `famicom` board | PCB 90 wide x 46.1 high x 1.2 thick; card edge 78.4 wide; notched width 81 (HVC-TxROM, MMC1-4) or 68 (HVC-N/Cx/Gx/UxROM discrete boards) | 1.95 for the board | Shell outline on that page is marked "TODO: measure and publish dimensions" by the wiki itself, so no shell mm exists in a citable page yet | [nesdev: Famicom cartridge dimensions](http://www.nesdev.org/wiki/Famicom_cartridge_dimensions) |
| `snes` (NTSC North America) | 136 x 88 x 20 (5.35 x 3.45 x 0.78 in) | 1.545 | Landscape with a raised ridged top band and grooved sides, a recessed centre notch where the connector is, and small corner screw bosses (observed in the top cart of `refs/snes.jpg`). iFixit calls the family "curved rectangular" with "a unique grooved shape" | [Wikipedia: SNES Game Pak](https://en.wikipedia.org/wiki/Super_Nintendo_Entertainment_System_Game_Pak) (dimensions); [iFixit Nintendo Game Cartridge](https://www.ifixit.com/Device/Nintendo_Game_Cartridge) (shape words) |
| `sfc` (Super Famicom, PAL) | 130 x 86 x 20 (5 x 3.39 x 0.79 in), given for "PAL/Japanese" | 1.512 | Rounded, smooth lower cart (the bottom cart in `refs/snes.jpg`, and `refs/snes_pal.jpg` shows the PAL edge). The same page says the PAL Game Pak and Japanese Cassette cases are nearly identical | [Wikipedia: SNES Game Pak](https://en.wikipedia.org/wiki/Super_Nintendo_Entertainment_System_Game_Pak) |
| SNES connector | 62 pins (two rows of 31) | n/a | Orientation drawing only, no shell dimensions | [snes.nesdev.org: Cartridge connector](https://snes.nesdev.org/wiki/Cartridge_connector) |

Not found: label window position for `snes`, `sfc` and `famicom` in mm. Issue 26 must measure it from the CC0/public-domain photos in `refs/` and record the measured fractions in its own table, marked "measured from refs/<file>", not as a cited source.

Suggested seated boxes for issue 26 at width 240 (computed from the aspects above, not cited): `nes` about 240 x 266; `snes` about 240 x 155; `sfc` about 240 x 159; `famicom` unknown until a shell width and height are measured.

## 3. SNES region byte

Verified offset (two sources: the snes.nesdev.org ROM header page, and snes9x's own loader at the pinned commit `fae2fea`, `memmap.cpp:2091` `RomHeader = ROM + 0x7FB0` and `:2047` `ROMRegion = RomHeader[0x29]`, which is file offset 0x7FD9 before mapping): the country (destination) code is header byte `$FFD9` in cartridge address space. The header block starts at `$FFC0` (HiROM) or `$7FC0` (LoROM), so the byte sits 0x19 into the header.

| Layout | Header start | Region byte, file offset (no copier header) | With 512-byte copier header |
|---|---|---|---|
| LoROM | `$7FC0` | `0x7FD9` | `0x81D9` (0x7FD9 + 0x200) |
| HiROM | `$FFC0` | `0xFFD9` | `0x101D9` (0xFFD9 + 0x200) |
| ExHiROM | `$40FFC0` | `0x40FFD9` | `0x4101D9` (0x40FFD9 + 0x200) |

Copier header detection: file size modulo 1024 equals 512; the header then adds 0x200 to every offset, and the ROM checksum excludes it.

Sources opened:
- [snes.nesdev.org: ROM header](https://snes.nesdev.org/wiki/ROM_header): table row `$FFD9 | 1 | Country code (implies NTSC/PAL)`; header placed at `$007Fxx` (LoROM), `$00FFxx` (HiROM), `$40FFxx` (ExHiROM); notes the 512-byte copier header is separate.
- [snes.nesdev.org: ROM file formats](https://snes.nesdev.org/wiki/ROM_file_formats): "A simple way of detecting a header is by checking if the file size modulo 1024 is equal to 512"; header offsets shift by 512 in headered files.

Cross-check caveat: the Wikibooks page [SNES memory map](https://en.wikibooks.org/wiki/Super_NES_Programming/SNES_memory_map) was also opened. It confirms `$7FC0` / `$FFC0` as header starts but labels `$xFD9` as "Developer ID", which conflicts with the nesdev table. The nesdev wiki table was taken as authoritative (it matches the usual `$FFD9` = destination code layout); the Wikibooks row is treated as an error. snes9x agrees with nesdev: its loader reads the region from that byte and treats codes 2 to 12 and 18 as PAL (`memmap.cpp:2373`), so 13 (Korea), 15 (Canada) and 16 (Brazil) run as NTSC in snes9x. NTSC timing does not settle which shell those regions used; the shell rows for them stay open below. fullsnes (problemkaputt.de) was fetched but the returned excerpt did not include the cartridge section, so it is not cited.

Country code to variant map (codes and regions from the nesdev table; the variant column is this project's rule):

| Code | Region (source) | Game code letter | NTSC/PAL (source) | Variant |
|---|---|---|---|---|
| `$00` | Japan | J | NTSC | `sfc` |
| `$01` | North America | E | NTSC | `snes` |
| `$02` | Europe | P | PAL | `sfc` |
| `$03` | Scandinavia | W | PAL | `sfc` |
| `$04`, `$05` | Finland, Denmark | none | PAL | `sfc` |
| `$06` | Europe (French only) | F | PAL | `sfc` |
| `$07` | Dutch | H | PAL | `sfc` |
| `$08` | Spanish | S | PAL | `sfc` |
| `$09` | German | D | PAL | `sfc` |
| `$0A` | Italian | I | PAL | `sfc` |
| `$0B` | Chinese | C | PAL | `sfc` |
| `$0C` | Indonesia | none | PAL | `sfc` |
| `$0D` | South Korea | K | PAL | `sfc` (shell shape of Korean carts not verified) |
| `$0E` | Common | A | PAL | `sfc` |
| `$0F` | Canada | N | PAL per the page's "most other regions" rule | `sfc` by rule; open: Canadian carts physically match North America, no source opened, so issue 26 may special-case `$0F` to `snes` if a source is found |
| `$10` | Brazil / Nintendo Gateway System | B / G | PAL | `sfc` (shape of Brazilian carts not verified) |
| `$11` | Australia | U | PAL | `sfc` |
| `$12` to `$14` | Other variation | X, Y, Z | PAL | `sfc` |
| other or unreadable | none | none | none | `snes` (default, matches the placeholder platform shape today) |

Source for the table and the rule "Codes `$00` and `$01` are always considered NTSC, while most other regions are considered PAL": [snes.nesdev.org: ROM header](https://snes.nesdev.org/wiki/ROM_header).

Honest limit: the byte says region, not shell shape. Mapping `$00` Japan to `sfc` and `$02`+ to `sfc` rests on the Wikipedia statement that the PAL Game Pak and the Japanese Cassette cases are nearly identical ([SNES Game Pak](https://en.wikipedia.org/wiki/Super_Nintendo_Entertainment_System_Game_Pak)). The user override line in `cart_shell.txt` stays the escape hatch (PLAN step 24).

## 4. NES has no region byte

The original iNES header and NES 2.0 carry TV-system bits, not a Famicom vs NES shell flag. So a variant has to be inferred.

| Signal | Detail | Reliability | Source |
|---|---|---|---|
| iNES flags 9, bit 0 | `0: NTSC; 1: PAL` | Rarely set by dumpers | [nesdev: iNES](https://www.nesdev.org/wiki/INES) |
| iNES flags 10, bits 0-1 | `0: NTSC; 2: PAL; 1/3: dual compatible` (unofficial) | Rarely set | [nesdev: iNES](https://www.nesdev.org/wiki/INES) |
| NES 2.0 byte 12, bits 0-1 | `0` RP2C02 (NTSC NES), `1` RP2C07 (licensed PAL NES), `2` multiple-region, `3` UA6538 (Dendy) | Reliable when the header is NES 2.0 (byte 7 bits 2-3 equal binary `10`) | [nesdev: NES 2.0](https://www.nesdev.org/wiki/NES_2.0) |
| Filename tag | No-Intro: `(USA)` (includes Canada), `(Europe)` (includes Australia), `(Japan)`, `(World)`, multi-region as `(Japan, USA)` | Best signal for Famicom vs NES in practice | [No-Intro naming convention](https://wiki.no-intro.org/index.php?title=Naming_Convention) |
| Database lookup | NESCartDB records region, PCB and scans per cart profile | Needs a CRC match | [NesCartDB](https://nescartdb.com/) |

Proposed rule (the PLAN step 24 default, now with sources): `(Japan)` only gives `famicom`; `(USA)`, `(Europe)`, `(World)`, `(Japan, USA)` and mixed tags give `nes`; NES 2.0 timing values `0`, `1`, `2` give `nes`; untagged gives `nes`. The iNES region bits only decide NTSC vs PAL timing and never select a Famicom shell. `(Japan, ...)` mixed tags should prefer `nes` because a western release existed.

## 5. Notable carts

Colour values: none of the opened sources gives a hex or RGB value, so no hex value from an external source is recorded in this file (the two hex values in section 1 are slot's own current placeholders, read from the repo). Colour names below are the sources' own words. Numeric values for issue 26 must come from sampling the free images in `refs/` (noting the file) or from a new cited source.

| Cart | Platform and variant | Shell colour per source | Outline note | Source |
|---|---|---|---|---|
| The Legend of Zelda (NA) | NES, `nes` | "gold-colored" cartridge, shown through a die-cut window in the box; battery save | Standard `nes` body | [Wikipedia: The Legend of Zelda](https://en.wikipedia.org/wiki/The_Legend_of_Zelda_(video_game)); photo [Commons Golden Cartridge](https://commons.wikimedia.org/wiki/File:The_Legend_of_Zelda_-_Golden_Catridge.jpg) (`refs/nes_gold_zelda.jpg`) |
| Zelda II: The Adventure of Link (NA) | NES, `nes` | gold: "the shield insignia at the top-left is a cutout that shows the gold cartridge inside" | Standard `nes` body | [Wikipedia: Zelda II](https://en.wikipedia.org/wiki/Zelda_II:_The_Adventure_of_Link) |
| Tengen unlicensed NES games | NES, own outline | "rounded and matte-black", not "the gray, semi-square shape" of licensed carts; "resemble the original Atari cartridges" | Distinct rounded Atari-like shell, not the `nes` outline. This needs its own outline in issue 26 or is dropped from v1 (see below) | [Wikipedia: Tengen](https://en.wikipedia.org/wiki/Tengen_(company)) |
| Killer Instinct (SNES; EU, AU, CA and US) | SNES, `snes` (US) / `sfc` (PAL) | "black cartridge casing, instead of the standard grey shell" | Same outline as the region's normal cart | [Wikipedia: Killer Instinct (1994)](https://en.wikipedia.org/wiki/Killer_Instinct_(1994_video_game)) |
| Bomberman (Hudson, Famicom) | Famicom, `famicom` | black; shell was "originally being chosen between blue, yellow, and black", black chosen as it "matched the game atmosphere" per Takahashi Meijin | Standard `famicom` body | [Techbang article](https://www.techbang.com/posts/125880-takahashi-meijin-famicom-cartridge-color-secret) (Chinese; secondary reporting, treat as weak) |
| Super Mario Bros. (HVC-SM, Famicom) | Famicom, `famicom` | Commons description gives only the label name. The photo in `refs/famicom.jpg` shows a yellow-orange shell with a silver-white label (an observation of that photo, not a measured value) | Standard `famicom` body | [Commons HVC-SM](https://commons.wikimedia.org/wiki/File:HVC-SM_cassette_face_20090828.jpg) |
| Mario Bros. (Famicom) | Famicom, `famicom` | Commons categories: "Silver, white, yellow" and "Orange, silver, white" | Standard `famicom` body | [Commons Famicom Mario Bros](https://commons.wikimedia.org/wiki/File:Famicom_%27Mario_Bros%27_(5099954300).jpg) |
| Devil World (Famicom) | Famicom, `famicom` | Commons categories: "Black, blue, red, white" and "Salmon (color)" | Standard `famicom` body | [Commons Famicom Devil World](https://commons.wikimedia.org/wiki/File:Famicom_%27Devil_World%27_cartridge_(5158740395).jpg) |

Famicom per-game colour policy: the only source that speaks to who chose colours says a Nintendo manager picked them by impression, with no publisher system ([Techbang](https://www.techbang.com/posts/125880-takahashi-meijin-famicom-cartridge-color-secret)). So there is no rule to derive colour from publisher or game. A table can only list individually cited games. Everything else falls back to one neutral Famicom default, and that default has no cited value yet. Until one is found, issue 26 should render uncatalogued Famicom carts in the neutral platform colour used today and flag it in the PR, or sample a cited photo.

Uncertain or not found (dropped, not guessed):
- Famicom shell width, height and depth in mm (only the board is documented).
- Label window position for `snes`, `sfc`, `famicom` in mm.
- Standard licensed NES grey, SNES grey and Super Famicom light grey as numeric values.
- Black NES Tengen: which specific games, and an exact shell shape in mm. The Wikipedia text covers the look only. A link-only photo reference is in `refs/SOURCES.md`.
- Whether Canadian (`$0F`), Korean (`$0D`) and Brazilian (`$10`) carts use the NTSC-US or the PAL shell.

## 6. Disposition for the next issue

- Build `nes`, `famicom`, `snes`, `sfc` outlines first; add Tengen black and Killer Instinct black only as `cart_shell.txt` colour entries (same outlines) plus, for Tengen, a rounded outline if time allows.
- Colour table rows must reference a row above. The sourced colours today are Zelda gold, Zelda II gold, Killer Instinct black, Tengen matte black, Bomberman black, all by name only; numeric values still need sampling.
- Carts show real label art, never screenshots (docs/DECISIONS.md, 2026-10-12). The photos in `refs/` are for likeness comparison only and ship in no asset.

## 7. Values measured and sampled for issue 26

Method: each photo in `refs/` was converted to BMP with `sips` and the mean RGB of the pixel rectangle below was taken (stdlib Python). Rectangles are x, y, width, height in pixels of the committed file (800 px on the long side, `nes.jpg` is 724 x 800). Photo colour depends on the camera and the light, so these are the colours of the photos, not a colorimetric standard. `evals/eval-colour-sources.sh` fails if a plastic colour in `retro_shell.rs` has no row here.

| Plastic | Sampled from | Pixel area (x, y, w, h) | Mean RGB | Used for |
|---|---|---|---|---|
| NES grey | `refs/nes.jpg` | 40, 200, 70, 300 | #7a7a7a | Platform default for `nes` and uncatalogued Famicom carts |
| SNES grey | `refs/snes.jpg` | 300, 45, 310, 35 | #9f9ca2 | Platform default for `snes` (top cart, flat label face) |
| Super Famicom grey | `refs/sfc.jpg` | 200, 400, 400, 80 | #949696 | Default for `sfc` (lower panel below the label) |
| Gold | `refs/nes_gold_zelda.jpg` | 250, 160, 100, 25 | #aa9451 | The Legend of Zelda and Zelda II |
| Famicom yellow-orange | `refs/famicom.jpg` | 150, 395, 500, 35 | #ac8642 | Super Mario Bros. (Famicom) |

Colours with no sampleable photo (stated, not guessed):
- Black (Killer Instinct, Bomberman, Tengen): `refs/` has no free photo of a black cart (see `refs/SOURCES.md`, link-only). The numeric value reuses slot's own black Game Boy plastic, `DUAL_MODE_SHELL` #333031 in `shell.rs`. The sources give only the word "black"; the value is slot's existing black, not a measurement of these carts.
- Zelda II gold: no photo of that cart in `refs/`. It reuses the Zelda gold sample, because the source says the shell is gold like the first game.
- Famicom uncatalogued default: no cited value, so uncatalogued Famicom carts use NES grey. Flagged for the PR.
- Mario Bros. and Devil World (Famicom): Commons category words only, no photo downloaded. No table row.
- Tengen: no game title is cited in section 5, so no title row. Section 5 allows Tengen only as an outline plus colour, which needs a title list from a new source.

Geometry measured from the photos (trace of the shell edge, fractions of the shell bounding box unless noted):

| Item | Measured | From |
|---|---|---|
| `nes` label field | x 0.41 to 0.85, y 0.00 to 0.67 of the shell, portrait (about 53 x 86 mm at the cited 120 x 133). Section 2's 0.81 x 0.41 reads the cited 55 x 97 mm label with width and height swapped: the photo shows the label taller than wide and open at the top (the fold-over). | `refs/nes.jpg` |
| `nes` body | Full width down to 0.80 of the height, then a stepped lower part 0.09 to 0.92 of the width (left step larger than right, drawn 0.09 and 0.078). Ribbed grip band x 0.18 to 0.38 with 20 grooves, a recessed pocket with 5 ridges at its top (y 0.03 to 0.15), a plain rounded tab at its bottom, a triangle mark and a round dot inside the label recess (hidden by the label art). No moulded text on the face. | `refs/nes.jpg` |
| `famicom` outline | Wider than tall, aspect about 1.8 (781 x 435 px). Near-rectangular front with only slightly rounded top shoulders (the apparent taper in the photo is the top face seen obliquely), a stepped lower section about 5 percent narrower each side starting at 0.83 of the height, no side marks. Label x 0.07 to 0.92, y 0.05 to 0.68, drawn at x 0.06 to 0.94 with a thin rim. | `refs/famicom.jpg` |
| `sfc` label | x 0.12 to 0.89, y 0.02 to 0.42, wide and short. Top corners only slightly rounded (small radius, no chamfer), side ribs on the shoulders, two screws in the lower corners, a finger recess centred at about 0.60 of the height spanning x 0.22 to 0.78, and two grooves that start under the label edge (about 0.43) and run to about 0.95. | `refs/sfc.jpg` |
| `snes` label and outline | No front view of a Super NES shell exists in `refs/` (`snes.jpg` is an oblique stack). The label window reuses the `sfc` measurement and the outline follows the iFixit and Wikipedia words in section 2 plus the oblique photo: ridged sides, connector notch, corner screws. This is the weakest row of the set. | `refs/sfc.jpg`, `refs/snes.jpg` |

Seated boxes used (width 240, the body spans 6.5 to 233.5 like the GB and GBA shells, so the height is the body width divided by the cited aspect): `nes` 240 x 252 (0.902), `snes` and `sfc` 240 x 150 (1.545 and 1.512, one shared platform box). The suggestions in section 2 treated the whole box as the shell and gave 266, 155 and 159. `famicom` is drawn at the width of the `nes` box, bottom aligned, because `seated_box` and `cart_box` take a platform, not a cart, so every variant of a platform shares one box.
