# marghost/slot_modded vs slot-nes-snes: what to adopt

Read-only review, 2026-10-18. Fork cloned to `~/.cache/forks/marghost` (one branch, `main`, at
1660894 = tag v1.7.0-mod.6.0; seven `v1.x-mod.*` tags). Upstream cloned to `~/.cache/forks/brandon-slot`
(main at 1b20432). Our side: slot-nes-snes at da67dd2 (patches 0001 to 0041, ADRs 0001 to 0069), patched
tree `~/.cache/pal/slot-nes-snes/work/slot`. Line numbers and quotes from our tree are from its committed HEAD
97b2881 (`ps1-tests`, all 41 patches); that work tree also had uncommitted edits in progress (10 files,
none adding menu scrolling), which this review ignores.

## Base and method

- The fork merges upstream instead of rebasing. Its last merge is upstream **e5b12ad** (main after
  v1.7.0, unreleased: 48 kHz sinc resampler, hold POWER powers off, RG35XX-H, brighter lowest backlight
  step, save clock fix). So `git diff e5b12ad origin/main` is exactly the fork's own work: 79 files,
  +4931 / -397, 72 commits since v1.7.0 counting merges and README work.
- Upstream main has moved 9 more commits past e5b12ad (lid watcher #117, core opened off the frame loop
  #119, button remapping e1bfb2b, lid power-off timer and scrolling settings pages 2c82294, left stick).
- Our tree is v1.7.0. So "superseded" below has two kinds: **in v1.7.0** (we already have it) and
  **upstream main, unreleased** (arrives on our next rebase, ADR 0038 / REBASE.md).
- Every feature commit was read as a diff, and the final state was re-read against e5b12ad, because
  several features were reshaped or removed by later merges (scrolling settings, own bezels, own
  favourites storage).
- Panel: the fork targets the **RG35XXSP (640x480, 4:3)**. About a third of its code is gated on
  `slot_gfx::framed(panel)`, which is false on our RG34XXSP 720x480 (ADR 0021). On 720x480 a Game Boy
  frame is already drawn at a whole 3x (480x432), so nothing in that group helps us.

Commit link prefix: `https://github.com/marghost/slot_modded/commit/<sha>`. Verdict column:
verdict, value (H/M/L), effort (S/M/L), risk (L/M/H).

## 1. Shelf, carts, favourites and recents

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Verdict (V/E/R) | Patch interaction | Per-system section? | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Stale cart face dropped after a restock** | [88af60a](https://github.com/marghost/slot_modded/commit/88af60a) (`cart_faces.rs`, `slot-store/collections.rs` `CartKey`) | The face worker now returns `(key, CartKey, face)`. `place()` drops a face when the cart at `(shelf, index)` is no longer the cart it was built for | **Bug present in our tree and in upstream main.** `cart_faces.rs:113` places by `(shelf, index)` only; `requeue` skips keys already `pending`, so an in-flight build is never re-requested after `Shelf::restock` reshuffles Favorites or Recents. The old cart's face stays on the new cart at that index until the next restock | Fork fixes a real race. Matters more for us: 9 platforms mix in Favorites/Recents and our faces (bitmap retro carts, PS1 jewel case with cover decode) take longer to build, so the in-flight window is wider | none | **adopt**, M, S, L | none of our patches touch `cart_faces.rs` | no | **Yes, generic.** Upstream PR first, carry until it lands (ADR 0047) |
| Restock keeps textures and selection | 88af60a (`Shelf::replace_carts`) | Restock maps old faces by `(platform, stem)` onto the new list, frees only the rest, and keeps the selected cart selected | v1.7.0 `Shelf::restock` frees every face and `select(0)`; `restock_favorites` restores the old index number, not the cart. ADR 0049 lists "a restock of Recents or Favorites in a session still starts at upstream's index" as an open consequence | Fork better. Toggling a favourite no longer rebuilds every face on the shelf (expensive for PS1 covers) and answers ADR 0049's open point | none | **adopt** together with the row above, M, S, L | `shelf.rs` is touched by 0012, 0021, 0039; small, separate hunk | no | Yes, same PR as above |
| Lookups prefer the selected index | 88af60a, [72f468d](https://github.com/marghost/slot_modded/commit/72f468d) (`shelf_cart`, `Shelf::find`, `Shelf::behind`, `selected_cart`) | Checks `carts[index]` before a linear `stem` search | Our tree still searches by stem only (`behind`, `find`, `auto_link`). A stem that exists on two platforms (same file name in Games/NES and Games/GB, or Recents mixing them) resolves to the first match | Fork better, and it is a correctness fix for us (more platforms, more same-name stems), plus a small per-frame saving on long shelves | none | **adopt**, L to M, S, L | app.rs touch points (ADR 0024 map) | no | Yes, fold into the same PR |
| Header shared across shelves on insert | 88af60a (`share_header`) | After `read_header` on insert, copies title and code to the same cart on other shelves (Favorites, Recents) | Not present | Small consistency fix (link detection, titles) | none | adapt, L, S, L | app.rs | no | Yes, optional in the same PR |
| `seat_of` skips Recents/Favorites at boot | 88af60a | Resume seating only searches platform shelves | v1.7.0 lets a platform-less rack match | Behaviour choice of upstream's #53, not clearly a bug | none | skip, L | n/a | n/a | Ask upstream if wanted |
| Letter jump off on Recents | 88af60a (`jump_letter`) | Up/Down does nothing on Recents, which is not alphabetical | v1.7.0 jumps letters on Recents | Small UX fix | none | adapt, L, S, L | app.rs one line | no | Yes, tiny PR |
| Favorite Added / Removed toast | 88af60a (`Toast::FavoriteAdded/Removed`) | Toast on Y | v1.7.0 gives no feedback except the star | Nice, generic | none | skip for us, offer upstream, L, S | toast list is upstream's | no | Yes, if Brandon wants it |
| Heart badge from `System/favorite.png`, per-shell position | 88af60a, later commits (`favorite.rs`, `badge_centre`) | Replaces upstream's star with a heart PNG placed per shell (GBA, GB, GBC) | We use upstream's star. Its position comes from `label_rect(shell)`, which only knows GBA and GB shells | Cosmetic. Would need a position for every one of our shapes (NES, Famicom, SNES, SFC, GG, SMS, MD/Genesis, PS1 case) | none | skip, L | 0012, 0023, 0039 draw our carts | **yes**, one position per system | no |
| Favorites Show/Hide row | [227234c](https://github.com/marghost/slot_modded/commit/227234c) | General page toggle, keeps the list | v1.7.0 shows Favorites when non-empty | New SlotState field and row | ADR 0013 site (f), row policy | skip, L | slot_state.rs (0002, 0014, 0017, 0021) | no | Upstream's call |
| Startup Screen (Last Used, GBA, GB, GBC, Favorites, Recents) | [88af60a](https://github.com/marghost/slot_modded/commit/88af60a), reshaped in [77f2e1e](https://github.com/marghost/slot_modded/commit/77f2e1e) | Fixed shelf at boot, default Last Used | v1.7.0 boots on the last shelf (#53, ADR 0039) and our 0021 adds per-shelf carts | Little gain over Last Used; enum hard-codes GBA/GB/GBC | new SlotState field (site f) | skip, L | slot_state.rs | **yes**, would need NES, SNES, GG, SMS, MD, PS1 choices | no |
| Per-shelf cart memory | [cbbe4d6](https://github.com/marghost/slot_modded/commit/cbbe4d6) (`shelf_marks` in slot.state) | Remembers GBA, GB, GBC, Favorites carts; written on leaving a shelf, menu, insert, lid, power off | **Have, better:** ADR 0049 / patch 0021, `Config/shelf_carts.txt`, every shelf incl. Recents, written at rest through the state writer, no SlotState field | Ours better (crash-safe at rest, no `durability.rs` change, all shelves) | theirs would break site (f) | ours better | n/a | n/a | Ours is already the upstream candidate (branch `per-shelf-cart-memory`) |
| Favourites and Recents themselves | [88af60a](https://github.com/marghost/slot_modded/commit/88af60a), migrated in [eb04111](https://github.com/marghost/slot_modded/commit/eb04111), [7931365](https://github.com/marghost/slot_modded/commit/7931365) | Own storage, later moved onto upstream's `favorites.txt` and `recents.txt` with a one-time import | v1.7.0 ships both | n/a | none | superseded upstream (in v1.7.0) | n/a | n/a | n/a |
| Lazy Game Boy shell read ("faster boot") | [72f468d](https://github.com/marghost/slot_modded/commit/72f468d) | Adapted from our slot#75 | v1.7.0 `Shelf::new` is lazy (`OnceLock` shells), ADR 0040 dropped our patch | Same thing. Survives in the fork only as merge residue | none | superseded upstream (in v1.7.0) | n/a | n/a | n/a |
| **Fast scroll on long shelves** | [efe32cd](https://github.com/marghost/slot_modded/commit/efe32cd) (from stevolarn) | After 30 repeats (about 2 s held) on a shelf of 60+ carts, each repeat moves 3 carts | Not present. v1.7.0 repeat gaps 110, 85, 65, 50 ms, one cart each, so about 20 carts/s at best. Our Up/Down letter jump covers coarse moves | Better for big libraries (a full NES or SNES set is 700+ carts), but needs the lag fix below and a face-load check | none | **adapt**, M, S, M (see interaction) | `shelf.rs` (0012, 0021, 0039) | no | **Yes, generic** |
| Draw the carts where the shelf actually is | [0fce212](https://github.com/marghost/slot_modded/commit/0fce212) (`Shelf::lag`, `on_screen`, `draw`) | At stride 3 the sliding scroll falls more than `SLOTS` behind the index, so the screen went blank. Face requests and drawing now centre on the scroll position | n/a without fast scroll | Required with fast scroll. Risk for us: `CartFaces::sync` **blocks the frame** on every `on_screen` face (`built.recv()` loop), so at 60 carts/s on the PS1 or SNES shelf, slow cover builds turn into frame hitches | none | adopt with fast scroll, M, S, M | as above | no | Yes, same PR |

## 2. Settings pages and menus

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Verdict (V/E/R) | Patch interaction | Per-system section? | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Scrolling settings pages** | [3751a4a](https://github.com/marghost/slot_modded/commit/3751a4a), removed by the merge [7931365](https://github.com/marghost/slot_modded/commit/7931365) (mod.3.1: "every page now fits") | Six rows visible, list follows the bar, up/down marks | **Finding for our tree:** our `QuickRow::SCREEN` has 9 rows (GBA, GBC, GB, NES, SNES, GG, SMS, MD, PS1, ADR 0048/0055/0065). `QUICK_PITCH` 52 x 9 = 468 px against `LEGEND_Y` 427, so `quick_row_top` puts the first row at y = -20.5 and the last row runs to about 447, over the legend. No patch changes pitch; rows hide only when a system has no carts (`retro_quick::hidden_on_shelf`). A card with all six of our systems overflows (computed from code, confirm with a screenshot). Upstream main (e1bfb2b, 2c82294) now has `quick_window` / `QUICK_VISIBLE = 6`, but `scrolls()` is a whitelist: CONTROLS, SHORTCUTS, GENERAL only | Fork's code is on v1.6.0 menus and gone; upstream's is the base to use | ADR 0048 test sites (g), (h) | **superseded upstream (unreleased)**, but we must act: H, S, L | 0016, 0017, 0022, 0027, 0032 to 0034 all touch `quick_menu.rs` | yes: it is the platform list itself | Upstream-first variant: "any page longer than `QUICK_VISIBLE` scrolls" instead of a whitelist; otherwise add SCREEN to `scrolls()` in our patch on the rebase. Until the rebase, either a minimal own scroll on SCREEN or accept overlap |
| Button Cheat Sheet (settings, in-game menu, START in the state switcher) | [defe26b](https://github.com/marghost/slot_modded/commit/defe26b), [081236f](https://github.com/marghost/slot_modded/commit/081236f), [1754135](https://github.com/marghost/slot_modded/commit/1754135), [bc4e29a](https://github.com/marghost/slot_modded/commit/bc4e29a) | Four static pages of button strings (carousel, in game, screen and sound, state switcher) | Nothing. Our controls differ per system: SELECT+X picture on SNES and PS1 (ADR 0007, 0068), shoulders and triggers to the game on PS1, no rewind or FF on PS1 (ADR 0066), shaders via SELECT+B/A | Useful idea, but the strings are hard-coded and already wrong for us. Upstream main now has remappable Controls and Shortcuts pages (e1bfb2b) that list every binding live, so a static sheet goes stale on the next release | adds main-menu and in-game rows (ADR 0023/0043 row policy) | skip now; revisit after the rebase, M, M, L | `quick_menu.rs` (7 patches), app.rs | **yes**, per-system pages | Better upstream as a read-only help page generated from the bindings |
| Polaroid dots centred in the free gap | 081236f (`polaroids.rs draw_dots`) | When a 4th hint is added the dots move between the hint groups | Only needed if we add a hint there | n/a | none | skip, L | none | no | Only with the cheat sheet |
| In-game hidden rows as a bit table | [a78747c](https://github.com/marghost/slot_modded/commit/a78747c) (`IN_GAME_HIDDEN`) | Replaces the 8-arm match with a 16-entry table | We already use the same table trick in `retro_quick.rs` | Internal | none | skip | n/a | n/a | no |
| Menus fullscreen on 4:3 | [bc4e29a](https://github.com/marghost/slot_modded/commit/bc4e29a) | Settings and About fill a 640x480 panel | 720x480 has no strip; upstream #91 did the shelves | n/a | none | skip (not our panel) | n/a | n/a | n/a |
| About `_modded` badge, version text, avatar | [2981f45](https://github.com/marghost/slot_modded/commit/2981f45), [c19a201](https://github.com/marghost/slot_modded/commit/c19a201) | Branding | n/a | n/a | none | skip | n/a | n/a | no |

## 3. Power, lid, battery

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Verdict (V/E/R) | Patch interaction | Per-system section? | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Standby: stop drawing while dozing** | [b1f9e24](https://github.com/marghost/slot_modded/commit/b1f9e24) (from slot.advance; `standby.rs`, `device_app.rs`) | In `Phase::Doze` (lid shut or POWER tap), after 2 dark frames the device loop sleeps 50 ms per turn, still calls `advance` (input, power off, restart) but skips `step_emulator`, render and swap | Not present. v1.7.0 and upstream main keep composing and swapping black frames at 60 Hz with the backlight off for the whole doze. Upstream main makes doze longer (Lid Off 1 to 30 min, 2c82294), so the waste grows | Better. Wake costs at most 50 ms. Keeps ADR 0033 (doze, then power off) intact | none (ADR 0033 is about the timeout, not the loop) | **adopt**, M, S, M | `device_app.rs` is touched by 0015 (frame trace): the rest branch must sit before the trace and not count as a missed latch | no | **Yes, generic, upstream first.** Check first: with a link session active, doze does not expire (`doze_expired`) and standby skips `step_emulator`; confirm a peer is not stalled |
| **Battery Low banners at 15% and 10%** | [1706a16](https://github.com/marghost/slot_modded/commit/1706a16) (from slot.advance; `warn_battery`) | One toast per threshold per discharge, reset by charging, silent in doze or during shutdown, above the 5% critical power-off | v1.7.0 only lights the LED at 20% and powers off at 5% | Better, tiny, no state | none | **adopt**, M, S, L | app.rs `on_battery`, toast list (no patch touches either) | no | **Yes, generic.** Upstream PR first |
| Battery badge in game on 4:3 | [f323b5e](https://github.com/marghost/slot_modded/commit/f323b5e), [7e49ace](https://github.com/marghost/slot_modded/commit/7e49ace), [d7aab9e](https://github.com/marghost/slot_modded/commit/d7aab9e) (`battery_badge_face`, compositor overlay) | Draws a gauge plus percent in the bezel area beside the game | 720x480: the game fills the panel, no bezel area; the overlay is only drawn on framed paths | n/a | ADR 0021 | skip (not our panel) | n/a | n/a | n/a |
| Hold POWER powers off, Restart on About | merged upstream [0ba5370](https://github.com/BrandonKowalski/slot/commit/0ba5370) | Upstream change | arrives on rebase | n/a | none | superseded upstream (unreleased) | n/a | n/a | n/a |

## 4. Audio

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Verdict (V/E/R) | Patch interaction | Per-system section? | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Keep FF Pitch** | [6dd84fd](https://github.com/marghost/slot_modded/commit/6dd84fd) (from snowslots f0f482d; `pitch.rs`, `emu.rs`) | With FF sound on, a WSOLA time-stretch (256-frame hop, ±64 search, crossfade) shortens the audio by the FF factor before the resampler, so pitch stays normal; the resampler ratio then drops the squeeze. Resets on toggle | Not present. v1.7.0 plays FF sound sped up | Better for FF-sound users. Cheap (about 4k multiply-adds per 256 frames) | as our patch: new SlotState `ff_pitch` + a Game row = site (f) and row policy | adapt, M, S as upstream PR / M as our patch, M (audio) | `emu.rs` is touched by 7 of our patches incl. 0018 audio hold; the fork applies it on e5b12ad's sinc resampler, not v1.7.0's | no (PS1 has no FF, ADR 0066) | **Yes, upstream only.** Port against upstream main; we get it on rebase. Not worth carrying |

## 5. Video, bezels, boot logo

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Verdict (V/E/R) | Patch interaction | Per-system section? | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| Integer Scale for GB/GBC | [a78747c](https://github.com/marghost/slot_modded/commit/a78747c) (`integer_rect`, `GamePass::set_integer`, compositor viewport) | 3x (480x432) instead of 2.67x on 640x480 | 720x480 already gives GB a whole 3x; our NES/SNES Actual is a whole 2x (ADR 0004/0050) | n/a | ADR 0021 | skip (not our panel) | n/a | n/a | It answers upstream #115 for 4:3 panels |
| Classic GB/GBC bezels, panel-fitted bezels, filled bars | [cf8b449](https://github.com/marghost/slot_modded/commit/cf8b449), [c19a201](https://github.com/marghost/slot_modded/commit/c19a201), [7e49ace](https://github.com/marghost/slot_modded/commit/7e49ace) (`panel_bezel.rs`, `draw_panel_art`, CC BY-SA 4.0 art) | RG35XXSP bezel art and placement | Upstream v1.7.0 bezels (#77) replaced the fork's own; rest is 4:3 | n/a | ADR 0021 | skip; own bezels superseded upstream (in v1.7.0) | n/a | n/a | n/a |
| GB/GBC bezel stays until the menu shows | [4b755c6](https://github.com/marghost/slot_modded/commit/4b755c6) | No SP-frame flash on menu tap | 4:3 path only | n/a | none | skip | n/a | n/a | n/a |
| Built-in boot logo | [ba588eb](https://github.com/marghost/slot_modded/commit/ba588eb), [ad2e6d7](https://github.com/marghost/slot_modded/commit/ad2e6d7) (`include_bytes!` 216 KB bmp) | `System/bootlogo.bmp` no longer read; `Config/bootlogo.bmp` still wins | Branding only; not a boot-time change (the logo is written on a background thread) | n/a | none | skip | n/a | n/a | no |

## 6. Upstream code the fork merged (not the fork's work)

5dc5b83 sinc resampler, 0ba5370 hold POWER, 3b6349c backlight step, 894201d save clock, 656ce7e mGBA
state size, f6b9ef8 baseos-release fallback, e5b12ad RG35XX-H, plus the carousel-footer PR #102. Take
these by rebasing on the next upstream release, never from the fork.

## 7. Speed claims and the device measurement plan

Our scripts (`boot-compare.sh`, `bench-device.sh`, `auto-play.sh`) all drive the device over adb
themselves (`ADB=adb`). This review used no adb. Run the steps below yourself; each one also has an
SD-card-only fallback.

**What to expect.** "Faster boot" is our own #75, already in v1.7.0 (ADR 0040), so marghost should boot
the same as upstream v1.7.0, give or take noise. "Faster scrolling" is arithmetic: 50 ms repeat at
stride 3 is about 60 carts/s against 20 carts/s now. What actually needs measuring is the cost: frame
time and blank carts while scrolling on our heavier shelves.

### 7.1 Boot (also closes ADR 0040's open re-measure)

1. Build three device binaries: ours (`task` dist as usual), upstream v1.7.0 (the command in the
   `boot-compare.sh` header), and marghost:
   `DEVICE_ROOT=1 sh scripts/device-sh.sh 'cargo build --profile device --target-dir build/marghost/target-device --manifest-path <marghost clone copied under build/>/Cargo.toml -p slot --no-default-features --features device'`
   (device-sh mounts the repo at /src, so copy the clone under `build/` first).
   Caution: the marghost binary writes its built-in `_modded` boot logo to the boot partition when
   `Config/bootlogo.bmp` is absent. After the runs, boot ours normally once so its own refresh puts the
   card's logo back.
2. `RUNS=5 COLD=1 sh scripts/boot-compare.sh ours=<ours> upstream=<v1.7.0> marghost=<marghost>`.
   Read `slot: boot: first frame at N ms` (and `ui faces`) per run. Report median and worst.
   upstream and marghost ignore NES, SNES, Sega and PS1 folders, so the ours minus upstream gap is the
   cost of our six platforms, and the marghost minus upstream gap is the fork's.
3. Pass mark: marghost within ±5% of upstream (claim already in v1.7.0). If marghost is faster by
   more than that, bisect its commits with the same command.
4. Fallback without adb: install one binary as `System/slot`, power-cycle 5 times, copy
   `Logs/slot.log*` off the card, `grep 'boot: first frame'`.

### 7.2 Fast scroll (only after the port is built)

1. Card with a long shelf on three platforms: GBA (cheap faces), SNES (bitmap carts, ADR 0054), PS1
   (jewel case with cover decode, ADR 0069). At least 200 carts each.
2. Put `System/trace-latency.on` on the card (enables `slot: frametime: 600 presents, p50 p99 max`
   from patch 0015 and the `slot: pace:` line).
3. Input: reuse `auto-play.sh`'s injector (`node_for`, `hat()` writes ABS_HAT0X=1 to the hat node). Hold
   Right for 10 s, release, wait 2 s, repeat 5 times per shelf. No new script: a small `MODE=scroll`
   branch, or the same `printf` event files pushed and `cat` on the device.
4. Read: frametime p99 and max during the holds (gate: p99 under 17.5 ms and max under 33 ms on GBA;
   report SNES and PS1 as numbers, then decide), `slot: pace: ... missed a latch`, and carts moved: the
   shelf's line in `Config/shelf_carts.txt` once the cursor rests (patch 0021 writes it at rest), turned
   into an index from the sorted card list.
5. Visual: film the screen with a phone for one hold per shelf; count frames with an empty board or
   blank carts. Baseline is the same run on ours without the port.
6. Fallback without adb: hold Right by hand for 10 s with the trace flag on, then read slot.log off the
   card.

### 7.3 Standby battery

1. Charger off, battery above 50%, game loaded, lid shut for 2.5 min (under the 3 min power-off).
2. Sample `/sys/class/power_supply/axp2202-battery/current_now` (or `power_now`) every 5 s from a
   device shell, and `top -b -n 1` for slot's CPU, with and without the standby port. 5 runs each.
3. Pass mark: lower mean current with standby; wake to picture on lid open under 100 ms (film it).
4. Fallback without adb: a one-line loop in `System/launch_frontend.sh` that appends `current_now` to
   `Logs/current.log` every 5 s for the run, then read the card.

## 8. Licence and credit

- Fork: **GPL-3.0-or-later** (LICENSE is GPL-3.0; README: "Same license, GPL-3.0-or-later"), same as
  upstream since 2026-09-17 and same as our patch set. Compatible.
- Author: marghost. README and CHANGELOG say the code was written with an AI model; that does not
  change the licence. When porting, do not copy the fork's `Co-Authored-By` trailers (workspace rule).
- Credit chain to carry in the patch header, the upstream PR body and our LICENSING/credits notes:
  - Standby and battery banners: marghost (b1f9e24, 1706a16), adapted from **suprsomething/slot.advance**
    (GPL-3.0).
  - Fast scroll: marghost (efe32cd, 0fce212), adapted from **stevolarn/slot** (GPL-3.0).
  - Keep FF Pitch: marghost (6dd84fd), adapted from **chiyuki0325/snowslots** f0f482d (GitHub reports
    GPL-3.0).
  - Cart face and restock fixes: marghost (88af60a).
- Not adopted, but note if ever taken: Classic bezels are mugwomp93 art via chrizzo-hb/knulli-bezels,
  **CC BY-SA 4.0** (`licenses/bezel-CC-BY-SA-4.0.txt`); the boot logo and avatar are the fork's own art.

## Skipped

Skip: the cheat sheet (static strings, wrong for our per-system controls, overtaken by upstream's
remappable Controls/Shortcuts pages), Startup Screen, Favorites Show/Hide, heart badge, everything
gated on 4:3 panels (Integer Scale, Classic and panel bezels, in-game battery badge, fullscreen menus),
branding (boot logo, About badge), and the fork's own favourites, recents and lazy shell (in v1.7.0).

## Recommended to adopt (ranked)

1. **Let the Screen page scroll (9 rows overflow).** Why: on a card with all our systems, the Screen
   page is 468 px tall against a 427 px legend line, so the top row is cut and the bottom row sits on
   the legend. The fork showed the need and then dropped it; upstream main now has `quick_window`, but
   only for three pages. Effort S. Upstream first: propose "any page longer than `QUICK_VISIBLE`
   scrolls" (no whitelist); on our rebase, add SCREEN if the whitelist stays. Before the rebase: a
   screenshot on a full card decides whether we need an interim patch. Verify: screenshot of Screen
   with GBA, GB, GBC, NES, SNES, GG, SMS, MD and PS1 carts present; every row visible as you move the bar
   from top to bottom. Touches ADR 0048 sites (g)/(h).
2. **Cart face and restock fixes** (CartKey check in `place`, `replace_carts` keeping faces and
   selection, selected-index lookups). Why: a real race in our tree and in upstream main (stale face
   on the wrong cart after a favourite toggle), a full face rebuild on every restock (PS1 covers), and
   stem-only lookups that can pick the wrong platform's cart. Also closes ADR 0049's open
   consequence. Effort S to M. Upstream first (generic, no NES code), carry until it lands (ADR 0047).
   Verify: the fork's `slot-ui/tests/shelf.rs` (`a_restocked_shelf_keeps_each_carts_face_and_interior_and_hands_back_the_rest`) and `slot/tests/favourites.rs` (`y_on_the_favorites_shelf_removes_the_game_and_keeps_the_others`), plus a new test for the stale face (the fork has none: build in flight, restock, assert the face is dropped), then on the device toggle
   Y quickly on the Favorites shelf while carts are still loading; no cart shows another's art.
3. **Standby while dozing.** Why: stops 60 Hz GPU work with the backlight off for the whole doze,
   which gets longer with upstream's Lid Off timer. Effort S. Upstream first. Check the link-session
   case first. Verify: plan 7.3 (lower current, wake under 100 ms), plus a lid-close save and resume
   on NES, SNES and PS1 (ADR 0033 behaviour unchanged).
4. **Battery Low banners.** Why: a 5% hard power-off with no warning except an LED is a bad surprise
   mid-game. Effort S, no state. Upstream first. Verify: unit test like the fork's
   `battery_warnings.rs`; on the device, run down past 15% and 10% once in a game and once on the shelf.
5. **Fast scroll with the lag-aware draw.** Why: large NES and SNES libraries. Effort S, but risk
   medium because `CartFaces::sync` blocks the frame on visible faces. Upstream first. Verify: plan
   7.2; adopt only if SNES and PS1 frametime p99 stays within the gate and no blank board shows.
6. **Keep FF Pitch, upstream only.** Why: nicer FF sound, but as our patch it costs a SlotState field
   (site f), a row and a hunk in an `emu.rs` that 7 patches touch. Effort S as an upstream PR against
   main (where the fork already rebased it onto the sinc resampler). Verify upstream: the fork's
   `tests/pitch.rs`; on the device, FF with sound on a GBA and an SNES game, pitch normal at 2x and 4x.
