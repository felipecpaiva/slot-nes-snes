# bently0602's Cart Studio work vs our fork (felipecpaiva/slot-cart-studio, branch nes-snes)

Read-only survey, 2026-10-15. Clones: bently0602/slot-cart-studio (main) and bently0602/slot.

## Where the work lives

- **bently0602/slot-cart-studio** (fork of BrandonKowalski/slot-cart-studio), branch `main`, 5 commits
  ahead of upstream `38189ca` (the same base as our nes-snes branch), 341 files, +66k lines (most of it
  vendored HorizonJS, tasks/ notes and a 10k-line crop catalog). Commit messages say nothing
  ("next", "next revisions"), so the features are mapped to commits by `git log -S`:
  - [d422c91](https://github.com/bently0602/slot-cart-studio/commit/d422c91) "add psx": PSX platform, `Dat::named`
  - [d078afd](https://github.com/bently0602/slot-cart-studio/commit/d078afd) "cleaup"
  - [06618d1](https://github.com/bently0602/slot-cart-studio/commit/06618d1): SNES platform, raw+headerless CRC (`web/snes.js`), music albums
  - [6370aef](https://github.com/bently0602/slot-cart-studio/commit/6370aef): HorizonJS UI rewrite, Near SNES labels, Named_Logos fallback
  - [74c0881](https://github.com/bently0602/slot-cart-studio/commit/74c0881): desktop app art download/cache, Download Assets, SNES shown without a shell
- **bently0602/slot** [ae0ac6d](https://github.com/bently0602/slot/commit/ae0ac6d) "Publish SNES renderer and music
  scanner dependencies for Cart Studio": `snes_face` in `slot-ui/src/cart.rs`, a 360x225 rectangle in the
  shell colour with darkened border, rib stripes and a seam line, and a 240x146 label pasted at the top. The studio pins
  this slot (`slot.ref`, checkout `../slot-b`). In the end the studio **does not draw it for SNES**: its `face.rs`
  draws only the label, with no cart around it (task 027, "Show SNES artwork without the cartridge shell").
- No other repos of his touch slot (the rest are 2015 to 2024 projects).
- Licence: the fork keeps GPL-3.0 (LICENSE unchanged). HorizonJS is ExtJS 2-era code under LGPL-3.0, and its
  CSS/images carry the old ExtJS "Assets only with the Component" clause.

## Change-by-change

| # | Change | What it does | Commit | We have it? | Better/worse than ours | Licence | Effort to pull |
|---|---|---|---|---|---|---|---|
| 1 | SNES cart rendering (slot `snes_face` + studio `face.rs`) | Slot: a flat rectangle with ribs. Studio: draws no cart for SNES, only the label at 240x146 (or a title placeholder in a hash colour) | ae0ac6d (slot), 06618d1/74c0881 | Yes, better | **Worse.** We draw slot-nes-snes's real SNES/SFC and NES/Famicom silhouettes with variant wells, Outline row, cart_shell words, and face parity tests against slot | GPL-3 | n/a, skip |
| 2 | SNES label size | 960x584 export (4x a 240x146 well), letterboxed with black padding | 06618d1 | Yes | Ours is made at the shape of the slot-nes-snes well for each variant (snes/sfc/nes/famicom), with the top kept. His fixed 240x146 well is not ours | GPL-3 | skip |
| 3 | SNES ROM identification | CRC of the whole file first, then the CRC with a 512-byte copier header removed when `size % 32768 == 512` (`web/snes.js` `romChecksums`, `copierHeaderSize`); `artKey` tries both | 06618d1 | Mostly (ours: `src/rom.rs` skips the header when `len % 1024 == 512` and hashes the headerless CRC only) | Slightly more forgiving: a file that is 512 past a KiB but not headered still matches on the raw CRC. In practice No-Intro SNES is headerless, so the gain is small | GPL-3 | Small (fall back to the raw CRC when the headerless one misses, ~10 lines + test) |
| 4 | harvest.py SNES raw/bare CRC | ScreenScraper `jeuInfos` retried with the headerless CRC and size-512; the index files art under both CRCs; skips `look` for SNES | 06618d1 | Partly (we harvest NES/SNES with the bare CRC) | Equivalent for --dat runs; his helps `--card` runs with headered dumps | GPL-3 | Small, optional |
| 5 | **libretro Named_Logos fallback** | When the checksum art set has no logo (or an unreadable one), fetch `Named_Logos/<thumbnail_name>.png` from libretro-thumbnails, using the existing stub/alias resolution (`studio.js` `dress()`) | 6370aef/74c0881 | **No.** Our `dress()` fetches only `Named_Boxarts`, for colour; a miss in our art set falls back to slot's generated label | **Better coverage.** libretro has `Named_Logos` for both NES and SNES (checked), so carts outside our ~1630 NES / ~755 SNES published set would get a logo label | Code GPL-3; images are libretro-thumbnails (same source we already use for box art) | **Small**: ~10 lines in `dress()`, extend the platform list to NES/SNES, plus a test |
| 6 | **Near SNES label catalog** | `tools/harvest-near.py` + `tools/near-labels.json` (716 USA SNES labels, each with a hand-reviewed crop box and the scan's SHA-1/size) + `near-title-aliases.json` (84 name fixes); maps them to 800 USA retail No-Intro CRCs; downloads scans from archive.org `near-snes-scans-png` (about 12.7 GB), rotates them and pads to 960x584 | 6370aef/74c0881 | No (our SNES labels are ScreenScraper `support-texture`, reduced to 256 colours) | **Better source for USA SNES**: real high-res scans with reviewed crops. USA only, 716 titles; no SFC/PAL | Script and catalog GPL-3. **The scans have no redistribution licence** (his README says so and keeps them out of releases) | Medium: adapt the output to our art-set layout (`SNES/<media>/<CRC>.png` + index.json) and to our well shape instead of 960x584 letterboxing; quantise like the rest. Publishing them in slot-nes-snes-art is a rights decision |
| 7 | `Dat::named` | Case-insensitive lookup by name, for discs | d422c91 | No | Only PSX uses it | GPL-3 | skip (no PSX) |
| 8 | PSX carts | PSX folder, `.chd/.cue/.pbp/.iso/.exe/.m3u`, m3u disc hiding, 536x536 square cover, Redump dat | d422c91 | No | n/a: slot-nes-snes has no PSX. His own task 016 notes his slot's PSX well is now 296, while the studio still exports for 268 | GPL-3 | skip |
| 9 | Music album covers | Scans `Games/Music`, reads MP3/FLAC tags (music-metadata), MusicBrainz/Cover Art Archive search through a Cloudflare Worker or the desktop server, writes `cover.jpg` | 06618d1 | No | Needs his slot's music player | GPL-3 + npm deps | skip |
| 10 | HorizonJS UI rewrite | Whole UI moved to ExtJS-style Viewport, TabPanel, DataView and modal editors; `editor.js` rewritten (+445/-~400), new `ui.js` | 6370aef | No | A different UI, not an improvement on the problems we have. It conflicts with every editor change we made (Outline row, ART badge, picker) | LGPL-3 runtime; the ExtJS asset clause is awkward for a GPL web app | Very large, skip |
| 11 | Real Label preview polish | Keeps the old preview under a loading overlay with a spinner while a real label downloads; retry on failure without an extra undo step; a late download cannot replace a newer choice | 74c0881 (tasks 028/029) | Partly: upstream's tile already has "Couldn't load. Click to try again" | The idea is nice, but the code is HorizonJS-bound | GPL-3 | Medium (reimplement in our DOM editor); low priority |
| 12 | Desktop app + local art library | Rust `desktop/` local server (cargo-zigbuild, Win/macOS), `library.json` offline art, `cache-art.py`/`pack-art.py`, Download Assets button, release.yml | 74c0881 | No | Out of scope: we ship a Pages web app | GPL-3 | Large, skip |
| 13 | `fetchDat` path generalised (`metadat/<set>/`) | Lets PSX use Redump | d422c91 | n/a | Only PSX needs it | GPL-3 | skip |
| 14 | Tests | Playwright `tools/browser.test.mjs` (1043 lines), `web/snes.test.mjs` | various | We have `tools/verify.py` + node unit tests | Tied to HorizonJS DOM | GPL-3 | skip (copy only the `snes.test.mjs` cases with #3) |

## Pull (ranked)

1. **Named_Logos fallback for NES and SNES (#5).** Small diff in `dress()`; it covers every cart outside our
   published art set. Libretro already serves our box art, so it adds no new source. Keep our set first.
2. **Near SNES label catalog (#6), as a harvest input, not as hosted art yet.** Take `near-labels.json`
   (reviewed crops plus SHA-1) and `near-title-aliases.json`, and adapt `harvest-near.py` to write into our art-set layout
   at our SNES well shape. Better USA labels than the ScreenScraper textures. Credit bently0602 (GPL-3, compatible).
   Before publishing the images in slot-nes-snes-art, decide on the rights question: the archive.org item has no licence.
3. **Raw CRC fallback for SNES (#3/#4).** Keep the headerless CRC first, then try the raw CRC (and file harvested art
   under both). A few lines; covers oddly sized dumps.
4. *(optional)* **Real Label "keep the previous preview while loading" (#11)**, reimplemented in our DOM editor if the
   flicker bothers us.

## Skip

- SNES cart renderer (#1) and the 960x584 SNES label (#2): ours is more faithful (real silhouettes, SFC/Famicom
  variants, wells that match slot-nes-snes, parity tests). His studio no longer draws a SNES cart at all.
- PSX (#7, #8, #13): slot-nes-snes has no PSX, and his own PSX well and export disagree (268 vs 296).
- Music covers (#9): depends on his slot's music player, MusicBrainz and a Cloudflare Worker.
- HorizonJS rewrite (#10): an unrelated UI framework, a merge-conflict magnet, and ExtJS asset licence terms.
- Desktop app, local library, Download Assets, release workflow (#12): a different distribution model from our Pages site.
- His Playwright suite (#14): bound to the HorizonJS DOM.
