# Sega cart variant research (Game Gear, Master System, Mega Drive)

Research only, same rules as [VARIANTS.md](VARIANTS.md): every value cites a page opened on 2026-10-16, or is marked "measured from refs/<file>". Where no source gave a value, the cell says so; nothing is guessed. Reference images and licences: [refs/SOURCES.md](refs/SOURCES.md).

Sega Retro (segaretro.org) sits behind a bot check that blocks scripted fetches. Its pages were read in a browser where cited.

## 1. Outlines

ConsoleMods lists Height, Width, Thickness in that order. Aspect is width / height of the front face.

| Variant | Shell (W x H x D, mm) | Aspect (W/H) | Outline notes | Source |
|---|---|---|---|---|
| `gg` (Game Gear) | 66 x 68 x 10 | 0.971 | Near-square, portrait by 2 mm. See section 2 for the measured face | [ConsoleMods: Dimensions for Game Cartridges](https://consolemods.org/wiki/Dimensions_for_Game_Cartridges) ("Sega Game Gear", confirmed by Reddit user gsx115) |
| `gg` Japan vs West | no mm source | n/a | A Japanese cart (Madou Monogatari I, link-only in SOURCES.md) shows the same shell as `refs/gg.jpg`: grooves at the top, U-shaped channel, embossed SEGA oval. Observation only; no page states the two shells are identical | link-only photo |
| `sms_cart` (Western Master System cartridge) | 108 x 69 x 16 | 1.565 | Landscape, square corners. The label strip runs across the top of the face; the rest is a flat panel | ConsoleMods ("Sega Master System Cartridge", confirmed by Bomb Bloke) |
| `sms_card` (Sega Card / My Card) | 54 x 85.5 x 2 | 0.632 | Credit-card-sized, portrait, rounded corners, exposed contacts on the bottom edge (observed in `refs/sms_card.jpg`) | [Wikipedia: Sega Card](https://en.wikipedia.org/wiki/Sega_Card) |
| Japanese Mark III / Master System cart | not found | n/a | Sega Retro says first-party Japanese releases came in "Gold Cartridges" and the two third-party ones in "Silver Cartridges". ConsoleMods has "?" for Mark III and for the Japanese Master System. No dimensions and no free photo, so no outline | [Sega Retro: Master System cartridges](https://segaretro.org/Master_System_cartridges); ConsoleMods |
| `md_jp` (Japanese Mega Drive) | 93 x 67 x 17 | 1.388 | Per the source: rectangular footprint "with rounded edges; the top and sides of the cart are also rounded", plus an indentation on the left side for the console's cart lock | ConsoleMods ("Standard Sega Mega Drive Japanese Cartridges", confirmed by NagaTen) |
| `md_west` (US Genesis and PAL Mega Drive) | 109 x 70 x 17 (table) | 1.557 | The source says "Genesis and PAL Mega Drive carts share the same mold". Its note gives a footprint that is 95 mm wide and widens to 108 mm "with rounded sides, 67 mm tall", chamfered edges, a flat top and no lock indentation. The table (70 x 109) and the note (67, 108) disagree by 3 mm and 1 mm; this file uses the table values | ConsoleMods ("Standard PAL Sega Mega Drive Cartridges" and "Standard NTSC Sega Genesis Cartridges", one row) |
| EA cart (note only) | 95 x 88 x 17 | 1.080 | Taller shell with a large indentation holding "a yellow plastic section with the EA logo molded onto it"; flat bottom edge, flat top, chamfered or slightly rounded sides. Note only, not a v1 variant | ConsoleMods ("Sega Genesis EA (Electronic Arts) Cartridges") |

The brief expected separate US and PAL outlines. The only dimension source says they share one mould, so there is one Western outline (`md_west`). The labels seen differ: the Genesis label in `refs/genesis.jpg` has a red "GENESIS" band down the left edge, and the three PAL labels in `refs/md_eu.jpg` have a "MEGA DRIVE" band down the left or across the bottom. That is label art, not shell.

Suggested seated boxes at width 240, with the body spanning x 6.5 to 233.5 like VARIANTS.md section 7 (height = 227 / cited aspect, rounded): `gg` 240 x 234, `sms_cart` 240 x 145, `sms_card` 240 x 359, `md_jp` 240 x 164, `md_west` 240 x 146, EA 240 x 210.

Open question for the renderer: VARIANTS.md section 7 notes that `seated_box` and `cart_box` take a platform, not a cart, so every variant of a platform shares one box (Famicom was drawn at the NES width, bottom aligned). Here the Master System card (359) and cart (145) differ by a factor of 2.5, and `md_jp` (164) vs `md_west` (146) by 12 percent. This file does not pick the rule.

## 2. Values measured from the photos

Rectangles are x, y, width, height in pixels of the committed 800 px files. Fractions are of the shell bounding box. Photo colour depends on camera and light; these are the colours of the photos, not a colorimetric standard.

Shell bounding boxes and the photo aspect as a cross-check of section 1:

| File | Shell box in the photo | Photo aspect | Cited aspect | Method |
|---|---|---|---|---|
| `refs/gg.jpg` (800 x 778) | x 19 to 787, y 18 to 771 | 1.020 | 0.971 | threshold edges; the top edge is about 15 px narrower each side than the bottom (camera tilt) |
| `refs/sms_cart.jpg` (800 x 533) | rotated -14.2 degrees, 521.7 x 338.3 | 1.542 | 1.565 | minimum-area box around the shell mask |
| `refs/sms_card.jpg` (768 x 800) | rotated 24.2 degrees, 475.6 x 692.5 | 0.687 | 0.632 | same; the photo is oblique, so this is the weakest row |
| `refs/md_jp.jpg` (800 x 571) | x 120 to 682, y 104 to 478 | 1.503 | 1.388 | threshold edges; mismatch of 8 percent, cause not established |
| `refs/genesis.jpg` (800 x 800) | x 163 to 605, y 102 to 387 (top cart) | 1.551 | 1.557 | traced by eye (black cart on a black background, about 3 px) |

Label windows and details (measured from refs/<file>; the `md_jp` and `md_west` label edges were traced by eye, about 3 px):

| Variant | Label window (fractions) | Other features | From |
|---|---|---|---|
| `gg` | x 0.092 to 0.915, y 0.173 to 0.754, rounded corners | Three horizontal grooves at x 0.26 to 0.74, y 0.10 to 0.14. A recessed U-shaped channel wraps the top of the label from y 0.08 and runs down both sides to about 0.40. Embossed "SEGA" oval at x 0.31 to 0.70, y 0.81 to 0.92. Small top-corner radius, square bottom | `refs/gg.jpg` |
| `sms_cart` | full width (x 0.02 to 0.96), y 0.01 to 0.22: a red grid strip with the title | Four grooves across the face at y 0.22 to 0.31; a flat textured panel from 0.31 to the bottom with a thin raised rim; open card-edge slot at the bottom (seen in the Evan-Amos photo, link-only) | `refs/sms_cart.jpg` |
| `sms_card` | x 0.10 to 0.93, y 0.07 to 0.59 (approximate, oblique photo) | Black lower face with printed product codes; two rows of gold contacts at y 0.83 to 0.93; rounded corners | `refs/sms_card.jpg` |
| `md_jp` | x 0.103 to 0.902, y 0.00 to 0.872 (the label wraps over the top edge) | Ribbed grips on both sides at y 0.18 to 0.72, each about 0.05 of the width; lock notch on the left side at y 0.76 to 0.83; the lower body steps in about 0.045 per side from y 0.94; top corners rounded (about 0.045 of the width) | `refs/md_jp.jpg` |
| `md_west` | x 0.147 to 0.855, y 0.00 to 0.898 (wraps over the top) | Glossy ribbed side bands between the shell edge and the label (left band x 0.00 to 0.10); small corner radius; flat top | `refs/genesis.jpg` |

Both Master System cart photos opened (Casino Games and Sonic the Hedgehog, both Matthew Paul Argall) use the grid-strip layout. Whether some carts carry a full-face picture label instead was not checked; the fractions above describe the strip layout only.

Plastic colours (mean RGB, stdlib Python over the BMP from `sips -s format bmp`):

| Plastic | Sampled from | Pixel area (x, y, w, h) | Mean RGB | Std dev (luma) | Note |
|---|---|---|---|---|---|
| Game Gear black | `refs/gg.jpg` | 40, 605, 180, 30 | #242129 | 1.7 | below the label, left of the SEGA oval |
| Master System cart black | `refs/sms_cart.jpg` | 330, 260, 150, 80 | #48484a | 8.2 | the textured panel reads lighter than smooth plastic |
| Sega Card black | `refs/sms_card.jpg` | 300, 500, 60, 25 | #2e3236 | 3.9 | lower face; may be printed surface, not bare plastic |
| Mega Drive (Japan) black | `refs/md_jp.jpg` | 200, 440, 400, 25 | #26242a | 4.9 | strip below the label |
| Genesis black | `refs/genesis.jpg` | 250, 363, 270, 16 | #403036 | 7.6 | strip below the label; warm indoor light gives a red cast |

No value was taken from `refs/md_eu.jpg`: the carts are oblique, partly hidden by the console and lit orange. It is kept for the PAL label layout only. No free photo of an EA cart was found, so the yellow tab has no sampled colour.

## 3. Region and shell selection

### Master System and Game Gear header

From [SMS Power: ROM header](https://www.smspower.org/Development/ROMHeader): the header "can be at offset $1ff0, $3ff0 or $7ff0 in the ROM, although only the last of these seems to be used in known software". It starts with `TMR SEGA`. "The high 4 bits of the 16th byte of the header give the region and system", so the byte is at 0x7FFF (or 0x1FFF, 0x3FFF). Codes: `$3` SMS Japan, `$4` SMS Export, `$5` GG Japan, `$6` GG Export, `$7` GG International. The low 4 bits give the ROM size used by the BIOS checksum. The page adds that Game Gear and Japanese releases "tend not to have a correct checksum". Genesis Plus GX probes the same three offsets, 0x1FF0 first and 0x7FF0 last (`core/loadrom.c:302-313`), and maps the same five codes (`core/loadrom.c:327-345`).

Card or cart: the header says region and system, not media. [Wikipedia: Sega Card](https://en.wikipedia.org/wiki/Sega_Card) gives "4 to 32 KB of ROM versus 16 to 512 KB of ROM" for cards and cartridges, and says the Master System II has no card slot. So a ROM under 16 KB can only be a card, a ROM over 32 KB can only be a cart, and 16 to 32 KB is ambiguous. The libretro No-Intro Master System dat does not mark cards (no entry name says "card"); it has 17 entries under 16 KB and 251 at or under 32 KB.

Proposed rule (this project's rule, not a cited one):

Applied in order, first match wins:

| Step | Signal | Shell |
|---|---|---|
| 1 | Game Gear platform folder (the GG dat lists `gg\|sms`, so a `.sms` there stays `gg`), or nibble `5`, `6`, `7` | `gg` (one shell for every region) |
| 2 | Master System file under 16 KB | `sms_card` |
| 3 | everything else, including nibble `3` (SMS Japan) and no header | `sms_cart` (the Japanese gold/silver cart has no sourced outline) |

The 16 to 32 KB band (for example Super Tennis) defaults to the cart. A `Config/cart_shell.txt` line remains the override.

### Mega Drive header

From [Plutiedev: ROM header](https://plutiedev.com/rom-header): `$100` 16 bytes system type ("SEGA" must be there or "systems with TMSS will refuse to boot the game"), `$120` 48 bytes domestic title, `$150` 48 bytes overseas title, `$190` 16 bytes device support (`J` 3-button, `6` 6-button, `A` analogue, `4` multitap, `G` light gun, `M` mouse), `$1F0` 3 bytes region support. Old style: letters `J` (Japan), `U` (Americas), `E` (Europe). New style: one ASCII hex digit, bit 0 Japan 60 Hz, bit 1 domestic 50 Hz, bit 2 Americas 60 Hz, bit 3 Europe 50 Hz.

Genesis Plus GX parses the field as a set (`core/loadrom.c:1084-1124`): it accepts `EUR`, `USA` and `JAP` strings, then letters `U`, `J`, `E` and `K` (Korea, counted as Japan), then hex digits. A letter `E` is read as Europe before the hex check, so hex `E` (Americas plus Europe plus domestic 50 Hz) is never seen as hex; both readings include a Western region, so the shell is the same.

Proposed map (this project's rule): any Americas or Europe bit, letter or string gives `md_west`; only Japan bits (bit 0, bit 1, `J`, `K`, `JAP`) give `md_jp`; an empty or unreadable field gives `md_west`. Mixed fields such as `JUE`, `JU` and `UEJ` give `md_west`, like the NES rule in VARIANTS.md section 8: a western release existed, so the western shell is drawn. Korean carts get `md_jp` by this rule; their real shell is not verified. Titles for the label fetcher: overseas title at 0x150 for `md_west`, domestic at 0x120 for `md_jp`.

### SMD interleaved dumps

[Sega Retro: SMD](https://segaretro.org/SMD) (read in a browser): an interleaved format made by the Super Magic Drive copier, in 16 KB blocks, "with the first 8K being the even bytes and the remaining 8K being the odd bytes". The 512-byte header comes from Genesis Plus GX, which drops 512 bytes before de-interleaving (`core/loadrom.c:673-689`, `size -= 512`); the file(1) magic ([console magic](https://kernelsources.org/source/more/freebsd/contrib/file/magic/Magdir/console?full=0x10e)) matches `0xAABB` at offset 8 and `EAGN` or `EAMG` at 0x280, offsets that presuppose that header.

Conflict: Genesis Plus GX `deinterleave_block` (`core/loadrom.c:221-230`) writes the first 8 KB of each block to odd output offsets (`src[i*2+1] = block[i]`) and the second 8 KB to even ones. The magic agrees with the code: `EAGN` at 0x280 is the odd bytes of "SEGA GEN" at 0x100. The code is taken as authoritative; the Sega Retro sentence counts bytes another way or is wrong.

Detection as Genesis Plus GX does it (`core/loadrom.c:673-689`): "SEGA" is absent at 0x100, `size % 512 == 0` and `(size / 512)` is odd; then it drops 512 bytes and, for Mega Drive only, de-interleaves each 16 KB block. It does not check `0xAABB`. Size alone is not enough: the No-Intro dat has an entry of 2 MB + 512 bytes (Waterworld, Sega Channel), which a size test alone would misread.

Can a `.md` or `.bin` be interleaved? The loader checks content, not the extension, so any extension is handled. One scraper author (sselph, [RetroPie forum](https://www.petrockblock.com/?p=82062)) noted `.md` is sometimes documented as a Multi Game Doctor format but chose to treat it as raw binary, because the emulators in use only support raw and SMD. The library sample in section 4 found no interleaved file.

## 4. What the library holds

Read-only header checks over zips in `/Volumes/MuOs/ROMS` (first 0x8000 bytes, random sample with seed 1; no ROM data copied):

| Set | Sample | Result |
|---|---|---|
| `megadrive` (2146 zips: 1249 `.md`, 896 `.bin`, one misplaced `.gg`) | 30 (23 `.md`, 7 `.bin`) | 29 raw with "SEGA" at 0x100; 0 headered or interleaved; 1 Taiwanese unlicensed `.md` with no header (0xFF at 0x100). 3 of 29 list `6` in device support. Region fields: J 7, U 7, E 3, JU 2, JUE 2, UEJ 2, UJE 1, EUR 1, B 1, F 1, 4 1, blank 1 |
| `megadrive` loose files | 10 | 9 raw with "SEGA" at 0x100; 1 beta with no header; none interleaved |
| `mastersystem` (418 zips, all `.sms`) | 10 | 10 of 10 have `TMR SEGA` at 0x7FF0, all nibble `4` (SMS Export) |
| `gamegear` (586 zips, all `.gg`) | 10 | 10 of 10 have `TMR SEGA` at 0x7FF0; nibble `7` (GG International) 6, nibble `6` (GG Export) 4 |

24 of the 30 Mega Drive samples match a CRC in the libretro No-Intro dat when hashed raw.

## 5. Not found (dropped, not guessed)

- Japanese Mark III / Master System cart shell: no dimensions and no free photo.
- Free front-view photo of an EA cart, so no yellow tab colour.
- A page stating that No-Intro Mega Drive CRCs are of raw, non-interleaved ROMs (the CRC match above is evidence, not a citation).
- Shell of Korean Mega Drive carts.
- The cause of the 8 percent gap between the cited `md_jp` aspect and its photo.

## 6. Shipped rules (patch 0028, `sega-carts`)

Where the research above landed. Box rule, as for the Famicom in VARIANTS.md section 7: `seated_box`
and `cart_box` take a platform, so each platform has one box and every variant is drawn inside it.

| Platform | Seated box | Variants and how they sit in the box | Label well (permille of the cart box: x0, y0, x1, y1) |
|---|---|---|---|
| Game Gear | 240 x 234 (section 1) | `gg`, body x 6.5 to 233.5, full height | 114, 173, 893, 754 |
| Master System | 240 x 145 (the `sms_cart` box) | `sms` fills the box; `segacard` is drawn at the box height, 91.7 wide (the cited 0.632 aspect), centred | `sms` 46, 10, 935, 220; `segacard` 347, 70, 664, 590 |
| Mega Drive | 240 x 164 (the `md_jp` box, the taller one) | `megadrive` fills the box; `genesis` is drawn 146 high (the cited 1.557 aspect), bottom aligned, like the Famicom in the NES box | `megadrive` 125, 0, 880, 872; `genesis` 166, 110, 836, 909 |

Every well is section 2's measured fraction mapped into the box (x = 6.5 + f x 227, or the card's
own span). Details drawn in the detail SVGs: the three Game Gear grooves, the U channel and the SEGA
oval; the four Master System grooves and the panel rim; eight Sega Card contact cuts; the Mega Drive
side ribs, left lock notch and stepped lower body; the Genesis ribbed side bands. All other surface
detail (texture, printed text) is left out.

Plastic defaults, all Solid, from section 2: Game Gear #242129, Master System cart #48484a, Sega
Card #2e3236, Mega Drive #26242a, Genesis #403036 (the warm cast of that photo is kept, not
corrected; a `Config/cart_shell.txt` line changes it). No per-title colour rows exist yet; the EA
yellow tab has no sampled colour and no outline.

Selection, first match wins:

- A `Config/cart_shell.txt` or `Labels/cart_shell.txt` word for the cart's own platform: `gg`;
  `sms` or `segacard`; `megadrive` or `genesis`. A word for another platform is ignored.
- Game Gear: always `gg`.
- Master System: a file under 16 KB is `segacard`, anything else `sms` (section 3). The 16 to 32 KB
  band defaults to the cart.
- Mega Drive: the header region set (`crates/slot-store/src/sega.rs`, read as Genesis Plus GX reads
  it): Japan only gives `megadrive`; any Americas or Europe region, a blank field or no header gives
  `genesis`.
