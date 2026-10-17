# Labels by name (`tools/fetch-labels.py --by-name`)

On the maintainer's card (2026-10-17) 1,378 of about 7,600 games had no label: GoodTools bad dumps, hacks,
pirates, betas and translations whose CRC is in no dat, so the CRC path ends at "unknown CRC" or "missing"
(MD 748, NES 323, GBA 136, GBC 99, GG 31, SMS 24, SNES 15, PS1 2). 534 of them have a same-title sibling
on the card that already has a label. `--by-name` (off by default) gives those games art without guessing.

Round 1 on the device took that from 1,378 to 569. Round 2 adds box fronts, cut names, a few normaliser
forms, 32X, a retry of the round 1 misses, and a reviewed alias list.

For each ROM the CRC path leaves without a label (with `--device`, also one not in `--library`), in order:

1. **Alias.** `--aliases <tsv>` lines `system<TAB>stem<TAB>ss:<game id>` or `...<TAB>sibling:<stem>` force
   that match (a `--suggest` list a human has checked; `#` lines are skipped).
2. **Sibling (no network).** `title_key` drops every `[..]` and `(..)` group, a GBA release number
   (`0468 - `), a leading `The` or a GoodTools `, The` / `. The`, accents and punctuation; `_` is a space and
   `&`, `'n`, `'n'`, `n'` and a lone `n` read as `and`. A label on the card (or written earlier in the run)
   with the same key is copied: the one sharing most regions (GoodTools `J`, `U`, `E`, `W` or No-Intro
   words), then the cleanest dump (`[!]` best, `[b]`, `[h]`, `[p]`, `[t]`, `[f]` and `[T..]` last). A name
   the card cut short (no tag, at least 30 characters of title) takes the one sibling title that starts
   with it, and none when several do. PS1 copies the `disc/` label too. The sibling's `cart_shell.txt`
   line comes along when the regions agree. With `--device` the PNG comes from the run's stage, the label
   cache, or an `adb pull` into the cache, and only the new labels are pushed.
3. **CRC box.** A CRC the dat knows whose game has no label scan takes that game's front box (`box-2D`).
4. **ScreenScraper by name.** `jeuRecherche.php` with the system id and the bare title, without a trailing
   `by <author>` and, for a cut name, without its last (cut) word. A Mega Drive name with `32X` is asked
   first under ScreenScraper's 32X id 19 (Skyscraper `platforms_idmap.csv`, row `sega32x,19,21,33`) with
   `32X` removed. A reply is taken only when exactly one game id (of that system) has a name, in any
   region, with the same key (a cut name: a name starting with it); otherwise `no confident match` and
   nothing is written.

Media: the CRC path's (`support-texture`, SMS `box-2D`, PS1 `box-2D` and `support-2D`). When a game has no
label scan the front box is taken (the ROM's region, then `wor`, `us`, `eu`, `jp`); a wheel or logo never.
slot fits any PNG into the label box. Replies are cached by system and query (media URLs without the
login), so a rerun asks nothing and a later rule change judges the same replies offline; round 1's
cached "no match" markers are ignored, its matches kept. `--limit N` caps the ROMs that ask per system.
A dry run uses cached answers only.

Each ROM prints one line (`matched by alias`, `matched by sibling`, `matched by CRC, box front`, `matched
by name`, `matched by name, no art`, `no confident match`, `not searched by name`, `error`) and the summary
counts them. `--report <file>` writes a TSV: system, stem, outcome, source (sibling stem, `crc:<crc>` or
`ss:<game id>`), media. `--suggest <file>` writes, for every ROM still without a label, the nearest
candidate (`ss:<id>` and its name, or `sibling:<stem>`) and why it was not taken (`hack or bad dump`,
`subtitle differs`, `name differs`, `several ids (..)`, `other system`, `no results`). Its first three
columns are the `--aliases` format: keep the good rows and pass the file back. Homebrew, PD, test carts,
BIOS and cheat devices are expected to stay without art.

```sh
task labels:fetch -- --device --library ~/ROMS --by-name --dry-run --report by-name-dry.tsv
task labels:fetch -- --device --library ~/ROMS --by-name --report by-name.tsv --suggest suggest.tsv
task labels:fetch -- --device --library ~/ROMS --by-name --aliases approved.tsv --report by-name-aliases.tsv
```
