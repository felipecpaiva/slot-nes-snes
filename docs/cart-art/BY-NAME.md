# Labels by name (`tools/fetch-labels.py --by-name`)

On the maintainer's card (2026-10-17) 1,378 of about 7,600 games had no label: GoodTools bad dumps, hacks,
pirates, betas and translations whose CRC is in no dat, so the CRC path ends at "unknown CRC" or "missing"
(MD 748, NES 323, GBA 136, GBC 99, GG 31, SMS 24, SNES 15, PS1 2). 534 of them have a same-title sibling
on the card that already has a label. `--by-name` (off by default) gives those games art without guessing.

For each ROM the CRC path leaves without a label (with `--device`, also one not in `--library`):

1. **Sibling (no network).** `title_key` drops every `[..]` and `(..)` group, a GBA release number
   (`0468 - `), a leading `The` or a GoodTools `, The`, accents and punctuation. A label on the card (or
   written earlier in the run) with the same key is copied: the one sharing most regions (GoodTools `J`,
   `U`, `E`, `W` or No-Intro words), then the cleanest dump (`[!]` best, `[b]`, `[h]`, `[p]`, `[t]`, `[f]`
   and `[T..]` last). PS1 copies the `disc/` label too. The sibling's `cart_shell.txt` line comes along
   when the regions agree. With `--device` the PNG comes from the run's stage, the label cache, or an
   `adb pull` into the cache, and only the new labels are pushed.
2. **ScreenScraper by name.** `jeuRecherche.php` with the system id and the bare title. A reply is taken
   only when exactly one game id (of the same system) has a name, in any region, with the same key;
   otherwise the run prints `no confident match` and writes nothing. The media are the CRC path's
   (`support-texture`, SMS `box-2D`, PS1 `box-2D` and `support-2D`). Answers are cached by title, media by
   game id, and `--limit N` caps the searches per system. A dry run uses cached answers only.

Each ROM prints one line (`matched by sibling`, `matched by name`, `no confident match`, `not searched by
name`), the summary counts them, and `--report <file>` writes a TSV (system, stem, outcome, source: the
sibling stem or `ss:<game id>`). The report is written in a dry run too.

```sh
task labels:fetch -- --device --library ~/ROMS --by-name --dry-run --report by-name-dry.tsv
task labels:fetch -- --device --library ~/ROMS --by-name --report by-name.tsv
```
