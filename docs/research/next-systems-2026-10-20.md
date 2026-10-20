# slot-nes-snes: which systems next (2026-10-20)

Read-only research. No repo file other than this one was written, and nothing was committed. This
report builds on the 2026-10-18 review (`/tmp/claude-501/research/next-systems.md`, not in the repo).
That review already covers the zip non-goal, the canvas width problem (384-wide boards), ADR 0071
pacing, the Genesis Plus GX backup RAM problem and the FBNeo licence. Those points are referenced here,
not repeated.

Markers, as in the house style:
- **verified**: read today in source, a local file, or a page opened today.
- **unverified**: recalled or inferred. Check it before it goes into an ADR.
- **Estimate**: a number nobody has measured.

## The short answer

| Rank | System | Owned (unique games) | In his genres | Core (already shipped?) | Effort | One best copy on the card | Score /10 |
|---|---|---|---|---|---|---|---|
| 1 | Sega CD | 59 titles (61 discs) | 25 | Genesis Plus GX (**shipped**) | M | about 13.5 GB (5.1 GB for his genres) | 8.6 |
| 2 | PC Engine CD | 27 | 10 | Beetle PCE Fast (**shipped**) | S | about 7.8 GB (3.0 GB) | 8.4 |
| 3 | Neo Geo | 153 parent games | 16 (platform/run and gun) | FBNeo (new) | L | about 3.1 GB (0.4 GB) | 6.5 |
| 4 | Atari 2600 | 597 | 68 | Stella 2014 (groundwork built) | M (with 7800) | about 3 MB | 6.3 |
| 5 | CPS1 and CPS2 | 32 + 38 | 7 | FBNeo (same build as Neo Geo) | M after Neo Geo | about 0.95 GB | 6.0 |
| 6 | Famicom Disk System | 268 | about 15 that matter | fceumm (**shipped**) | S to M | about 12 MB | 5.6 |
| 7 | Virtual Boy | 28 | 4 | Beetle VB (new) | M | about 31 MB | 5.0 |
| 8 | Atari 7800 | 71 (66 games) | 7 | ProSystem (groundwork built) | rides on 2600 | about 2 MB | 4.8 |
| 9 | CPS3 | 6 | 0 | FBNeo | S after CPS2, plus a device gate | about 0.3 GB | 3.5 |
| 10 | Atari 5200 | 105 | 2 | atari800 (new) | M | about 1 MB | 3.0 |
| not now | Atari Jaguar | 74 | 12 | Virtual Jaguar | | | |

The score weights genre fit 40%, library size and quality 20%, effort 20% (inverted) and performance
risk 20% (inverted). It is a ranking aid, not a measurement.

**Proposed order:** Sega CD, then PC Engine CD, then the Neo Geo shelf on FBNeo with CPS1 and CPS2
straight after, then the Atari 2600 and 7800 pair, then Virtual Boy. FDS can slot in anywhere as a
small job. The two CD systems do not fit on the card today (see "Device space").

## Corrections to the brief

- **The panel is 720x480 (3:2), not 640x480 (4:3).** `docs/DEVICE-GATE.md` line 4 says "RG34XXSP
  (H700, 720x480, BaseOS)" (verified). A 384x224 frame (CPS, Virtual Boy) is 1.875x across
  (720x420). A vertical arcade game (224x384) scaled to 480 high is 280 wide.
- **The RG34XXSP has two analog sticks.** ADR 0068 says "The spike proved the RG34XXSP sticks are
  analog. They are four axes on event1", and `input/sticks.rs` maps both (verified). So the right
  stick can be the Virtual Boy's second D-pad, and the 5200's analog joystick has a real stick.

## What changed since the 2026-10-18 review

- **Shipped since then:** NGP, TG16 (PCE HuCard), WonderSwan, Lynx and Sega 32X (ADRs 0090 to 0093
  and 0096, verified in `docs/adr/`). So Beetle PCE Fast is on the device, and PC Engine CD drops from
  "S to M after HuCard" to **S**.
- **The NGP flash design is on main** (ADR 0094, staged, checked, published). Sega CD's backup RAM
  plan reuses it, so its prerequisite is done.
- **Groundwork branches exist but are stale.** `origin/segacd-groundwork` (8306dd7) and
  `origin/atari-groundwork` (a5d838a) both branch from 6f3aa4f, far behind main (verified).
  - **ADR number clash:** main's 0094 is the NGP flash ADR, and the Sega CD branch also has a 0094.
    Main has 0096 (32X) and no 0095, so the Atari 0095 can keep its number. Sega CD needs a new number.
  - The branches' test patches (0057 Sega CD, 0060 Atari) clash with main's numbering, which now runs
    to 0097. Integration includes a rebase and a renumber. This is counted in the effort.
- **The unified backup found far more Atari.** The old review saw 103 Atari 2600 dumps (card only).
  `Roms/atari2600` now holds 605 files (597 titles), and there are 72 for the 7800, 104 for the 5200
  and 81 for the Jaguar (`unified-backup/RESULT.md`, verified).
- **Felipe's decisions:** N64 is out (the H700 cannot run the whole library well, so it cannot be
  fully tested). Atari ST was rejected. The same "can the whole library be tested at full speed" bar
  is applied to the heavy systems below.

## How the counts were made

- **Sources.** Every candidate folder in `Roms/`, `ES-DE/Roms/`, `RG34XXSP/originalcard/Roms` and
  `RG34XXSP/MuOsBackup/ROMS`, listed once (depth 3), art, xml, txt and saves excluded. Titles are
  deduplicated by name with region and tags stripped, so one game in three regions counts once.
- **Arcade.** Zip stems from every arcade folder (1,262 stems) were matched to the FBNeo 1.0.0.03
  Arcade and Neo Geo dats (libretro/FBNeo `dats/`, fetched today). 966 stems are FBNeo sets. Each set
  maps to its board through `sourcefile` and to its parent through `cloneof`. Genre comes from the
  MAME 2003-Plus `catver.ini`, and orientation from `mame2003-plus.xml` (both fetched today).
  **Name match only**: no romset was hashed, so the FBNeo version of his zips is unknown.
- **Atari, Virtual Boy, Jaguar.** Genre from libretro-database `metadat/genre` (fetched today).
- **Sega CD and PC Engine CD.** No fetchable genre dat covers them, so these are **hand-classified by
  title**. No ScreenScraper requests were made.
- **"His genres"** means RPG, strategy and tactics, adventure, platformer and metroidvania. Catver's
  "Platform" tag is generous: it puts Metal Slug (run and gun) and Ghouls'n Ghosts and Strider
  (action platformers) there, and the arcade beat-em-ups (D&D, Knights of the Round) are not counted
  at all. Sports and racing are counted separately because he ranks them last.
- **Sizes** come from directory listings. For CD systems the smallest CHD per disc is kept, minus about
  9% for the repack with `cdlz,cdzl,cdfl` at hunk 489600 (the PS1 result). That 9% is an estimate for
  these discs. For arcade, the parent zip is kept when present, else the largest clone.

## Per system

### 1. Sega CD / Mega-CD

- **Owned.** 59 titles on 61 discs (Night Trap and Prize Fighter are multi-disc). Most come from the
  muOS backup (62 CHDs, 15.2 GB) and `Roms/SegaCd` (27 CHDs), all CHD.
- **In his genres: 25** (hand-classified).
  - RPG and tactics: Lunar The Silver Star, Lunar Eternal Blue, Vay, Shining Force CD, Dark Wizard,
    Popful Mail, Dungeon Explorer, Eye of the Beholder, Dungeon Master II, Heimdall.
  - Strategy and adventure: Dune, Third World War, Snatcher, Rise of the Dragon, The Secret of Monkey
    Island, The Adventures of Willy Beamish.
  - Platformers: Sonic CD (plus the Sonic CD++ hack), Flink, Earthworm Jim Special Edition, Mickey
    Mania, Pitfall The Mayan Adventure, Flashback, Heart of the Alien, Spider-Man vs The Kingpin,
    Wonder Dog.
  - Sports and racing: 7 (NBA Jam, NHL 94, Championship Soccer 94, F1 Beyond the Limit, Road Rash,
    Prize Fighter, WWF Rage in the Cage).
- **Core.** Genesis Plus GX at the existing pin (393f70c), CHD on. Nothing new to build.
- **Performance.** RetroPie recommends lr-genesis-plus-gx for Sega CD "for the Pi 2/3" (RetroPie-Docs
  `Sega-CD.md`, verified). The Pi 3 has the same Cortex-A53 at 1.2 to 1.4 GHz, so it is the closest
  honest proxy for the H700 at 1.5 GHz. Our own MD number is 3.3 ms a frame (PERFORMANCE.md).
  Estimate for Sega CD: 4 to 6 ms, unmeasured on the device.
- **BIOS.** Required, one per region. `Bios/bios_CD_U.bin` md5 `854b9150...`, `bios_CD_E.bin`
  `e66fa1dc...` and `bios_CD_J.bin` `278a9397...` all match the Genesis Plus GX doc (md5 re-run today).
- **Input.** The shipped Mega Drive 6-button policy. Nothing new.
- **Licence.** Unchanged, Genesis Plus GX already ships (non-commercial, separate program stance).
- **Effort M.** The groundwork (ADR "0094" on the branch, core tests, issues 113 to 122) is done.
  Left: rebase and renumber, the shelf with the jewel case, the BIOS check, backup RAM durability on
  the NGP flash design, disc control from PS1, and the device gate. The one real risk is the flush by
  reload at lid close, which the plan gates on a device measurement (under 100 ms).
- **Device space.** About 14.8 GB as stored, **about 13.5 GB** after a repack. His genres alone are
  about 5.1 GB.

### 2. PC Engine CD / TurboGrafx-CD

- **Owned.** 27 discs (`Roms/NEC - TurboGrafx CD`, `Roms/PCECD`, the stock card), all CHD.
- **In his genres: 10** (hand-classified): Akumajou Dracula X Chi no Rondo (Rondo of Blood), Ys Book I
  and II, Ys III, Ys IV (fan translation), Dungeon Explorer II, Dungeon Master Theron's Quest, Beyond
  Shadowgate, Kaze Kiri, Prince of Persia, Shadow of the Beast. Shooters are 12 (Gate of Thunder, Lords
  of Thunder, R-Type Complete CD, Spriggan, NEXZR and others). Sports and racing: 0.
- **Core.** Beetle PCE Fast, already shipped for the TG16 shelf (ADR 0091). It takes `.cue`, `.ccd`
  and `.chd` (RetroPie doc, verified). CD backup RAM goes through `SAVE_RAM`, so the normal `.sav` path
  works and there is no backup RAM problem (2026-10-18 review, verified in source).
- **Performance.** PCE Fast is a light core and already runs HuCards on the device. CD adds ADPCM and
  CD-DA streaming from the CHD. Estimate: well under budget, unmeasured for CD.
- **BIOS.** `syscard3.pce` md5 `38179df8f4ac870017db21ebcbf53114` is required. The correct copy is
  `Bios/RetroPieBIOS-master/BIOS/syscard3.pce` (md5 re-run today). The top-level `Bios/syscard3.pce`
  is headered (`ff1a6742...`), so it is the wrong file to point him at.
- **Input.** The shipped 2-button TG16 pad.
- **Licence.** As TG16 (GPL-2.0-or-later Mednafen, combined under GPL-3.0-or-later).
- **Effort S.** A disc medium on the TG16 path (or a second shelf), scan, BIOS check, jewel case
  variants (JP CD-ROM2, Super CD-ROM2, US TurboGrafx-CD), disc tests gated on the BIOS, device gate on
  Rondo of Blood, Ys Book I and II, Gate of Thunder.
- **Device space.** About 8.6 GB stored, **about 7.8 GB** repacked, his genres about 3.0 GB.

### 3. Neo Geo on FinalBurn Neo

- **Owned.** 179 FBNeo Neo Geo sets, **153 parent games** (the unified-backup `Roms/neogeo` folder
  plus the ES-DE, card and muOS copies).
- **In his genres: 16** by catver: Metal Slug 1, 2, 3, 4, 5 and X, Magician Lord, Cyber-Lip, Blue's
  Journey, Top Hunter, Nightmare in the Dark, Zupapa!, Spin Master, Ganryu, Eight Man, Bang Bang
  Busters. Most of the rest is fighters (KOF 94 to 2003, Samurai Shodown I to V, Garou, Last Blade 1
  and 2) and shooters. **Sports and racing: 28** (the largest such share of any candidate).
- **Core.** FBNeo, as planned the snes9x way. FBNeo's own README says the core "will already run
  really well on low-end devices (rpi3, ...)" (libretro/FBNeo `src/burner/libretro/README.md`,
  verified). On aarch64 there is no Cyclone, so 68K is the C core. Estimate: 3 to 6 ms a frame.
- **BIOS.** `Bios/neogeo/neogeo.zip` (1,760,976 B) holds `sp-s2.sp1`, `000-lo.lo`, `sfix.sfix` and
  `sm1.sm1` (listed today), and was CRC-checked against the FBNeo dat on 2026-10-18. Use that one, not
  the 2009 top-level `Bios/neogeo.zip` (1.26 MB). Note the path may move with the `Bios/<system>`
  consolidation.
- **Input.** A, B, C and D on the face buttons, coin on a SELECT tap. All 153 games are horizontal,
  and 320x224 fits the 360x240 canvas at 2x.
- **Licence.** Non-commercial, changes published, full text shipped, and **no donation requests on any
  project using FBNeo code** (FBNeo licence, verified on 2026-10-18; the libretro README repeats the
  clause today). The release zip already has no donation link. Record a standing "no donation links"
  rule in the arcade ADR.
- **Effort L.** New core build (large), an ADR amending the zip non-goal, a name table from the FBNeo
  dat with clones and BIOS sets hidden, the coin input, the BIOS check, an MVS cart mould, and a romset
  rebuild against the pinned dat on his side.
- **Device space.** About **3.1 GB** for 153 games, 0.4 GB for his 16.

### 4. Atari 2600

- **Owned.** 597 titles (605 files, No-Intro zipped, `Roms/atari2600`).
- **In his genres: 68** by libretro genre: Pitfall!, Pitfall II, Adventure, Haunted House, Raiders of
  the Lost Ark, Dragonstomper and The Entity (RPGs), platformers (Mountain King,
  Jungle Hunt, Donkey Kong, Mario Bros.), Quest for Quintana Roo, Riddle of the Sphinx, Star Raiders.
  Sports and racing: 70. The rest is mostly "Action" (284).
- **Core.** Stella 2014 pinned at 7d1361e (ADR 0095 on the branch, built and tested). Trivial cost on
  an A53.
- **BIOS.** None.
- **Input.** Joystick and one button. The console switches (difficulty, colour, Select, Reset) are
  Screen rows that slot applies (ADR 0095). Paddle games could use a stick (unverified that Stella
  2014 reads the analog axis as a paddle).
- **Licence.** GPL-2.0-or-later through Stella's own `Copyright.txt` (ADR 0095).
- **Effort M** for the pair with the 7800: about 16 patches (issues 126 to 140) plus the rebase.
- **Device space.** About 3 MB for all of it.

### 5. CPS1 and CPS2 on the same FBNeo build

- **Owned.** CPS1: 89 sets, 32 games. CPS2: 55 sets, 38 games.
- **In his genres: 7.** CPS1: Ghouls'n Ghosts, Strider, Magic Sword, Willow, Nemo, Mega Twins. CPS2:
  Armored Warriors. Close to his taste but tagged as beat-em-ups: Dungeons & Dragons Tower of Doom and
  Shadow over Mystara, King of Dragons, Knights of the Round, Warriors of Fate. The rest is mostly
  fighters (SF2, Alpha, Darkstalkers, Marvel). Sports: 4 (wrestling and Capcom Sports Club).
- **Performance.** Part of FBNeo's "runs really well on rpi3" claim. Estimate 3 to 6 ms.
- **BIOS.** None. The FBNeo dat lists `sfa3` and `ssf2t` with no `romof` and has no `qsound` set at all
  (grep today), so CPS2 needs no BIOS zip on FBNeo. This settles the 2026-10-18 "unverified" line.
- **Input.** Six-button fighters need L1 and R1 for the game (`owns_shoulders` false, as PS1 and MD).
  Coin on SELECT. 384x224 rides the PS1 640x480 resample canvas. Vertical sets: 3 CPS1 (1941, Mercs,
  Varth) and 2 CPS2 (19XX, Dimahoo); keep them off until a rotation ADR.
- **Effort M** after Neo Geo (the build, licence and name table are reused).
- **Device space.** About 0.38 GB (CPS1) plus 0.57 GB (CPS2).

### 6. Virtual Boy

- **Owned.** 28 titles (23 in `Roms/VB` plus zips in ES-DE; 19 on the stock card).
- **In his genres: 4.** Virtual Boy Wario Land, Jack Bros., Mario Clash, SD Gundam Dimension War
  (strategy, translated). Others worth having: Vertical Force, Red Alarm, Teleroboxer, Panic Bomber,
  Galactic Pinball. **Sports: 9** (golf, bowling, baseball, tennis, fishing).
- **Core.** Beetle VB. Licence **GPL-2.0-or-later** (`mednafen/vb/vip.c` header says "either version
  2 of the License, or (at your option) any later version", verified today). It has a `vb_cpu_emulation`
  option, default `fast` (verified). V810 cost on the A53 is unmeasured; Estimate 2 to 4 ms.
- **BIOS.** None.
- **How it would look.** The real thing is red on black, 384x224 per eye, stereoscopic. On this
  screen:
  - **2D mode** (`vb_3dmode = anaglyph` with `vb_anaglyph_preset = disabled`): one image in the chosen
    palette. That is the mode to ship. Whether "disabled" draws the left eye only or both eyes merged is
    **unverified**; the code path reads `vb.anaglyph.preset` and `vb.default_color` (libretro.cpp
    lines 443 to 447). Check on the device.
  - **Palette** (`vb_color_mode`): black and red (default), black and white, black and blue, black and
    cyan, black and electric cyan, black and green, black and magenta, black and yellow (verified).
    This is a natural Screen row.
  - Anaglyph presets (red and blue, red and cyan, and so on) need glasses. Side by side puts two
    384-wide eyes on a 720 panel, so it is useless here. Cyberscope, VLI and HLI need special
    displays.
  - Size: 384x224 at 1.875x is 720x420, letterboxed, non-integer. Or the PS1 640x480 resample canvas
    (1.67x across). A red-on-black picture with nearest scaling will shimmer; a smooth scaler suits it.
  - Pacing: 50.27 Hz, handled by ADR 0071 (one repeat in about six frames). No PAL row needed.
- **Input.** Two D-pads. The right one maps to the right analog stick read as digital
  (`vb_right_analog_to_digital`, options enabled, invert x, invert y, invert both, verified). The
  device has the stick (ADR 0068).
- **Effort M.** New core, new canvas mapping (reused from PS1), the stick-as-D-pad input, a Screen
  palette row.
- **Device space.** About 31 MB.

### 7. Atari 7800

- **Owned.** 71 files, 66 games (the rest are BIOS, monitor and test carts).
- **In his genres: 7.** Scrapyard Dog, Tower Toppler, Impossible Mission, Ikari Warriors, Mario Bros.,
  Donkey Kong, Donkey Kong Junior. Sports and racing: 19.
- **Core.** ProSystem pinned at 8a88014 (ADR 0095 on the branch). GPL-2.0-or-later plus zlib.
- **BIOS.** Optional. `Bios/7800 BIOS (U).rom` md5 `0763f1ff...` matches (re-run today). slot
  defaults to BIOS off (ADR 0095).
- **Input.** Joystick and two buttons; switches as Screen rows.
- **Effort.** Rides with the 2600 batch. **Device space** about 2 MB.

### 8. Atari 5200 (brief)

- 105 titles, about 1 MB. Only 2 in his genres (Kangaroo, Looney Tunes Hotel). The 5200 has an analog
  joystick and a 12-key keypad, so the stick fits but the keypad needs a mapping. Core would be
  atari800 (GPL). `Bios/5200.rom` md5 `281f20ea...` matches the atari800 doc (re-run today). Low value
  for its cost; after the 2600 and 7800.

### 9. Atari Jaguar: not now

- 74 titles, 12 in his genres (Rayman, Flashback, Pitfall, Cannon Fodder, Syndicate, Worms, Towers
  II). RetroPie says lr-virtualjaguar "is experimental and too slow for most Raspberry Pi systems";
  only an overclocked Pi 4 runs some games at full speed (RetroPie-Docs `Atari-Jaguar.md`, verified).
  The Pi 4 is an A72, much faster than the H700's A53. It fails the whole-library test.

### CPS3 (after the CPS2 shelf)

- 6 games: Street Fighter III (all three), JoJo (two), Red Earth. None in his genres. A search result
  reports all three SF III games at full speed on a Pi 3B+ with lr-fbneo, but the forum page could not
  be opened (bot check), so this is **unverified**. The BIOS is inside each set on FBNeo (`sfiii3` has
  no `romof`, verified). Gate on the device before promising it. About 0.3 GB.

## Cheap overlaps

- **Genesis Plus GX** (shipped) covers Sega CD and **SG-1000** too. He owns 121 SG-1000 files
  (`ES-DE/Roms/sg-1000`). No new core for either.
- **Beetle PCE Fast** (shipped) covers PC Engine CD.
- **FBNeo** covers Neo Geo, CPS1, CPS2 and CPS3 from one build, and its dats also list ColecoVision,
  FDS, MSX 1, SG-1000 and Channel F (FBNeo `dats/`, verified). Those console drivers are a fallback
  only; dedicated cores fit the per-system pattern better.
- **fceumm** (shipped) runs FDS with `disksys.rom`.
- **Stella 2014 and ProSystem** come as a pair on one branch with one ADR.

## Device space

The card is 117.7 GB with about 5.5 GB free, PS1 uses about 80 GB, and the rule is one copy of each
game, no duplicates.

| System | One best copy, all owned | His genres only |
|---|---|---|
| Sega CD (repacked) | about 13.5 GB | about 5.1 GB |
| PC Engine CD (repacked) | about 7.8 GB | about 3.0 GB |
| Neo Geo | about 3.1 GB | about 0.4 GB |
| CPS1 + CPS2 | about 0.95 GB | under 0.05 GB |
| CPS3 | about 0.3 GB | 0 |
| Virtual Boy | about 31 MB | under 10 MB |
| Atari 2600 + 7800 + 5200 | about 6 MB | under 1 MB |
| FDS | about 12 MB | under 1 MB |

**What fits now (5.5 GB):**
- Everything small fits with room to spare: Atari, Virtual Boy, FDS, SG-1000, CPS1 and CPS2 (under 1.1
  GB together).
- Neo Geo (3.1 GB) fits, or just its non-sports games.
- Sega CD **his genres only** (5.1 GB) barely fits on its own. PC Engine CD his genres (3.0 GB) fits on
  its own. Both at once do not.
- The full Sega CD and PC Engine CD libraries (about 21 GB) do not fit.

**Ways to make room:**
1. Trim PS1 sports and racing: about 7.2 GB back.
2. Put only the genre subset of each CD system on the card (Sega CD 5.1 GB, PC Engine CD 3.0 GB, 8.1
   GB together). With option 1 that leaves about 4.6 GB for Neo Geo and the small systems.
3. Repack the Sega CD and PC Engine CD CHDs with the PS1 settings before copying (about 2 GB saved,
   Estimate).
4. Drop the sports and racing sets from Neo Geo (28 games) and skip Virtual Boy sports.
5. A larger card (256 GB) removes the problem; everything above plus the full CD libraries needs about
   26 GB.

## Not now (heavy systems, same bar as N64)

| System | Owned | Why not |
|---|---|---|
| N64 | about 412 titles | Felipe's decision: the H700 cannot run the whole library well |
| Saturn | about 63 titles | Two SH-2s plus VDP1/2; Beetle Saturn and Yabause are far beyond an A53 (unverified, widely reported) |
| Dreamcast | about 97 titles | Flycast needs GLES3 hardware rendering, which slot lacks; reviews report drops even under RetroArch on the H700 (DroiX, 2026-10-18 review) |
| PSP | about 157 titles | PPSSPP needs GLES hardware rendering; God of War about 20 fps, Tekken 6 about 70% on the H700 (DroiX) |
| NDS | about 80 titles | Only closed DraStic is fast enough; two screens, no touch panel on this device |
| 3DO | 4 titles | Opera core is heavy for an A53 (unverified) and the library is tiny |
| Atari Jaguar | 74 titles | Too slow on a Pi 3 class CPU (RetroPie doc, verified) |

## Other light systems worth a look

- **Famicom Disk System** (rank 6): 268 titles left in `ES-DE/Roms/nes` by the unified job (12 MB) on
  the shipped fceumm. `Bios/disksys.rom` md5 `ca30b50f880eb660a320674ed365ef7a` (computed today; the
  match with the fceumm doc value is from memory, **unverified**). Disk sides need the PS1 disk control
  (ADR 0067). Caution for the no-duplicates rule: the genre highlights (Zelda 2, Metroid, Kid Icarus,
  Akumajou Dracula) are already on his NES shelf as cartridge versions. The FDS-only ones are mostly
  Japanese text: Nazo no Murasamejou, Esper Dream, Deep Dungeon, Famicom Tantei Club I and II, Dracula
  II (Japanese Simon's Quest).
- **SG-1000** on Genesis Plus GX: 121 files, nearly free to add (no BIOS). Mostly arcade-style games.
- **MSX and MSX2**: about 747 titles across ES-DE, `Roms/MSX` and the card, with real genre value
  (Knightmare I to III, King's Valley II, Metal Gear 1 and 2, Hydlide 1 to 3, Dragon Quest I and II,
  Nobunaga's Ambition). The keyboard is the problem (2026-10-18 review), so it
  stays an L.
- **ColecoVision and Intellivision**: 169 files each (ES-DE only). Keypad controllers fit poorly.
  ColecoVision BIOS: only `RetroPieBIOS-master/BIOS/colecovision.rom` (`2c66f591...`, not checked
  against a doc). Intellivision `grom.bin` at the top level is 0 bytes.
- **Game & Watch**: 48 files (the same 48 in three places). The `gw` core is tiny; LCD games suit a
  pocket device.
- **PICO-8**: 39 carts (ES-DE and muOS). The fake-08 core exists; licence unverified.
- **Super Game Boy borders**: no files needed, it is a feature of the GB shelf. His `sgb_bios.bin` and
  `Super Game Boy (World).sfc` are both 0 bytes (md5 `d41d8cd9...`, the empty file), so he owns no real
  SGB BIOS. Whether the shipped mGBA can draw SGB borders without one is **unverified**.
- **Not in the library:** Pokemon Mini, Vectrex, Satellaview, Sufami Turbo, Neo Geo CD (no ROM files
  found in any of the four trees).

## Not verified

- **Romset versions.** Arcade counts are name matches against the FBNeo 1.0.0.03 dat. No zip was
  hashed, so he will need a RomVault or ClrMamePro pass against the dat of the pinned FBNeo commit.
- **Device frame costs** for Sega CD, PC Engine CD, Neo Geo, CPS1/2, CPS3 and Virtual Boy. All are
  Pi 3 proxies or Estimates. The first step for each is `scripts/bench-device.sh` with `CORE=...` on an
  owned dump.
- **Sega CD and PC Engine CD genres** are hand-classified by title.
- **Virtual Boy 2D mode**: what `anaglyph` with preset `disabled` draws (one eye or both merged).
- **CPS3 full speed** on a Pi 3B+ (search result only).
- **SGB borders without a BIOS** on mGBA.
- **FDS BIOS md5** against the fceumm doc.
- **The 9% CHD repack saving** for Sega CD and PC Engine CD discs (measured only on PS1).
- **Virtual Boy sizes** come from the 2026-10-18 review: `Roms/VB` did not answer a listing today
  while the reorganisation job ran.

## Sources opened today

- Local: `docs/rom-library/unified-backup/RESULT.md`, `left-in-place.tsv`, `inventory.csv.gz`; the
  2026-10-18 review; `docs/DEVICE-GATE.md`; ADR 0068; `origin/segacd-groundwork` ADR 0094 and
  `segacd-plan.md`; `origin/atari-groundwork` ADR 0095 and `atari-plan.md`; BIOS md5s in
  `/Volumes/B3Tb/Emulation/Bios`.
- libretro/FBNeo `dats/` (Arcade only, Neogeo only) and `src/burner/libretro/README.md`.
- libretro/mame2003-plus-libretro `metadata/catver.ini` and `mame2003-plus.xml`.
- libretro/libretro-database `metadat/genre` (Atari 2600, 5200, 7800, Jaguar; Nintendo Virtual Boy).
- libretro/beetle-vb-libretro `libretro_core_options.h`, `libretro.cpp`, `mednafen/vb/vip.c`.
- RetroPie-Docs `Virtual-Boy.md`, `Atari-Jaguar.md`, `Neo-Geo.md`, `Sega-CD.md`, `PC-Engine.md`,
  `FinalBurn-Neo.md`.
