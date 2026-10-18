# jgraving/slot: quality-of-life changes vs slot-nes-snes

Read-only survey, 2026-10-18. Clone of all 63 branches (`~/.cache/forks/jgraving`), compared against
slot-nes-snes ADRs 0001 to 0069, docs/PLAN.md, patches 0001 to 0041 and the patched tree
`~/.cache/ps1test/slot-nes-snes/work/slot` (`af0a23b ps1-tests`), plus upstream BrandonKowalski/slot
v1.7.0 and `origin/main` (24 unreleased commits after v1.7.0, newest 1b20432, 2026-10-18).

Link prefixes: jgraving `https://github.com/jgraving/slot/commit/<sha>`, upstream
`https://github.com/BrandonKowalski/slot/commit/<sha>`.

## Summary

- The fork is GBA SP centred (RG SP and RG35XXSP tested, never the RG34XXSP). Its `main` is 136 ahead and
  9 behind upstream, based on v1.7.0-15 (`e5b12ad`). Nothing touches NES, SNES, Sega or PS1.
- **`main` was re-baselined** in [abd245f](https://github.com/jgraving/slot/commit/abd245f) ("Adopt the
  tested sound integration as the main baseline", a two-parent merge). The v1.6.0-era history is still
  reachable from `main`, so `git cherry` reports it as merged, but the tree dropped much of it. Verdicts
  below are taken from the `main` tree (symbol greps), not from history.
- **Bluetooth is not heading upstream.** jgraving asked on upstream issue #109 ("Sound menu with Bluetooth
  and USB audio support"); Brandon closed it: "I watched the lead developer of NextUI bash his head against
  Bluetooth audio to know I don't want to touch this with a 10-foot pole." `bluetooth-upstream-minimal` is
  a squash of the fork's own PR 33, not an upcoming upstream PR. docs/research/slot-forks.md is stale on
  this point and on the branch count (it says 36; there are 63).
- **Biggest finding is in our own tree, prompted by the fork's menu scrolling:** our Screen list overflows
  the panel on a card that has every system (section 4, recommendation 1).

Licence: GPL-3.0 (LICENSE is upstream's GPL-3.0 text; GitHub reports GPL-3.0). Sole author of all 136
commits: Jake Graving. The README states development is AI-assisted. The backlight curve he imported in
d832ddc is upstream PR #54 by flo333 (already in v1.7.0). Anything we port: keep GPL-3.0, credit
"jgraving/slot (Jake Graving)" with commit links in the patch header and LICENSING.md.

## 1. Branch map

| Group | Branches | State | Verdict |
|---|---|---|---|
| Live baseline | `main` (136/9) | Sound (BT, USB, wired), day/night presets, power page with deep sleep, favourite confirm, carousel ticks, SP shell finishes, larger carts, 6-row scrolling menus | Reviewed in sections 2 to 6 |
| Sound / Bluetooth | `bluetooth-audio` (v1.6), `bluetooth-upstream-minimal` (1 commit, a0d7ef7), `sound-pr-33-visuals` (36 dev commits squashed into a0d7ef7; only 2 files differ from main), `sound-main-integration`, `adopt-sound-main`, `fix/bluetooth-connection-guards` (6b00130) | All in `main` | Superseded by main |
| Favourites | `favorites-recents`, `favorites-y-star` (v1.6), `favorite-gold-foil`, `favorite-remove-confirm-upstream` | In `main` | See 2 |
| Parent controls | `kid-play-rules` < `kid-review-base` < `kid-controls`, `kid-timers`, `cartridge-flip`, `favorite-removal`, `upright-cartridge-marks`, `favorite-start-confirm` (tip, 14 not in main) | v1.6.0 base, **never merged** | Skip (product choice for a kids' build; not our audience) |
| Wi-Fi / network | `encrypted-wifi-vault`, `wifi-network-menu` (unmerged); `saved-wifi-storage`, `wifi-settings`, `optional-network-lock`, `wifi-polish`, `simplify-wifi-menu`, `simplify-button-lock` | Merged, then **removed by the author** in [4f4f34f](https://github.com/jgraving/slot/commit/4f4f34f) "Remove home networking and OTA" | Skip |
| OTA / CI | `automatic-system-builds`, `ota-package-staging`, `ota-release-downloads`, `usb-local-updates` (doc only) | Removed by 4f4f34f; release workflow kept | Skip (ADR 0010 CI, no network) |
| Power / SP art | `tactile-sounds`, `faithful-sp-power-switch`, `feat/skeuomorphic-power-switch`, `feat/power-off-click`, `feat/power-sleep-options`, `fix/shutdown-switch-feedback` | In `main` (some v1.6 bits dropped, see 3) | See 3 |
| Display | `night-display`, `feat/restore-warm-display`, `feat/restore-night-brightness`, `feat/restore-night-shortcut` | Dropped at re-baseline, restored into `main` | See 3 |
| Carousel / shell | `grab-and-go`, `feat/continuous-slot`, `feat/cartridge-ticks`, `feat/larger-carousel-cartridges`, `rgsp-shell-finishes` | In `main` | See 5 |
| Menus | `scroll-options`, `start-closes-options` | Scroll: re-done in main (ad49e5c). Start-to-close: **dropped** at re-baseline | See 2 and 4 |
| Packaging / snapshots | `build-bluetooth-pr33`, `build-favorite-remove-confirm`, `build-favorite-remove-system`, `build-gold-pr34`, `build-power-pr35`, `build-rgsp-shell-finishes`, `preview-favorite-gold-foil`, `test-gold-smooth`, `test-main-before-sound-2026-10-16`, `sync-upstream`, `upstream-oct15-source`, `upstream-oct16-favorites-source`, `upstream-oct16-sound-source` | Build artefacts, review GIFs, mirrors of upstream (0 ahead) | No source changes; ignore |

Tree check of `origin/main`: parent controls 0 hits, Wi-Fi vault 0, OTA staging 0 (only upstream's
`slotlink.sh` uses wpa_supplicant), `display_settings` live, `QUICK_VISIBLE_ROWS` live, `suspend(` live,
Start-closes-picker (`Btn::B | Btn::Start`) 0, background shutdown sync (`prepare_poweroff`) 0.

## 2. Shelf and menu comforts

| Change | Commits | What it does | Ours | Verdict | Value / effort / risk | Patch conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|
| Confirm favourite removal | [e2dc0cb](https://github.com/jgraving/slot/commit/e2dc0cb), [37f230c](https://github.com/jgraving/slot/commit/37f230c), [a83c345](https://github.com/jgraving/slot/commit/a83c345); test `crates/slot/tests/favorites.rs` | Y on a starred cart shows "Y Again to remove" above it for 3 s (`FAVORITE_REMOVE_MS`); a distinct second Y press (key-up required) removes. Any other input cancels. The removal is saved at once; on the Favorites shelf the cart lifts away and the next one slides in | v1.7.0 favourites (diluno #89): one Y toggles, no confirm | **Adapt** (confirm only; animation optional) | M / S (confirm) or M (with departure animation) / L | `toggle_favorite`/`restock_favorites` hunks sit beside our 0021 shelf-cart-memory, 0027, 0032 | **Yes.** Generic, all devices |
| Start also closes the core picker | [e047d17](https://github.com/jgraving/slot/commit/e047d17) | `core_picker_input`: `Btn::B \| Btn::Start => Press::Back`, so START toggles the picker it opened | START opens, B closes (upstream; our 0009 adds NES/SNES pairs). Dropped from jgraving `main` at the re-baseline | **Adopt** | L-M / S / L | One-line hunk next to 0009 | **Yes** |
| Six-row scrolling menus with a thumb | [19f1196](https://github.com/jgraving/slot/commit/19f1196) (scroll-options), [ad49e5c](https://github.com/jgraving/slot/commit/ad49e5c) (main) | Every page shows at most 6 rows, window centred on the selection, scrollbar thumb; `QUICK_PITCH` 52 to 48 | None. See section 4: our Screen page overflows | **Superseded upstream** by [e1bfb2b](https://github.com/BrandonKowalski/slot/commit/e1bfb2b) (`QUICK_VISIBLE = 6`, `quick_window`), but upstream scrolls only CONTROLS, SHORTCUTS, GENERAL | H (for us) / see 4 | 0016, 0022, 0039 own the Screen rows | The thumb is a generic nicety, upstream idea only |
| Volume HUD when a game starts silent | [12f7b3a](https://github.com/jgraving/slot/commit/12f7b3a), in main via [a0d7ef7](https://github.com/jgraving/slot/commit/a0d7ef7) | On the phase change into `Playing` (once, not per frame), if `output_volume() == 0`, show the volume HUD so muted or zero volume is not mistaken for a broken core | None | **Adopt** | M / S / L | `update()` phase-change block, no patch of ours there | **Yes** |
| Browsing memory | [79a73eb](https://github.com/jgraving/slot/commit/79a73eb) | Remember shelf and cart | Upstream #53 shelf memory plus our 0049 per-shelf cart | Already have | n/a | n/a | n/a |
| Favorites and Recents shelves, Y star | [9954937](https://github.com/jgraving/slot/commit/9954937), [c1668f1](https://github.com/jgraving/slot/commit/c1668f1) | v1.6-era shelves | v1.7.0 ships both | Superseded upstream | n/a | n/a | n/a |
| Gold foil star sticker | [7558caf](https://github.com/jgraving/slot/commit/7558caf), favorite-gold-foil | Smooth SVG gold star replaces the bitmap star | v1.7.0 star | Skip (cosmetic) | L / S / L | `frontend.rs` star upload | Taste; Brandon's call |
| Status bar moved to the top, menu hint height 32 | [b2793fa](https://github.com/jgraving/slot/commit/b2793fa), [ad49e5c](https://github.com/jgraving/slot/commit/ad49e5c) | Clock, battery, connection in the top corners; footer removed | Upstream footer (MarkusMaribu #102) | Skip | L / M / M (moves every legend Y) | Touches every legend constant we rely on | No |

## 3. Display, power and audio

| Change | Commits | What it does | Ours | Verdict | Value / effort / risk | Patch conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|
| Day/night display presets | [d832ddc](https://github.com/jgraving/slot/commit/d832ddc), [f7d5064](https://github.com/jgraving/slot/commit/f7d5064), `display_settings.rs` | SELECT+X swaps saved (brightness, warmth) pairs; day defaults to current, night 2/9; adjusting either preset remembers it in `Config/display.txt` | None | **Adapt with another trigger.** SELECT+X is `Btn::X => (8192, NightToggle)`, the **same chord and bit** as our `VideoModeToggle` (ADR 0007 SNES, ADR 0068 PS1, Picture rows ADR 0061) | M / M / M | `slot-input/src/gesture.rs` chord table (our 0007, 0038) | Idea yes; after upstream's remappable shortcuts (e1bfb2b) it fits as an unbound-by-default shortcut |
| Warmer warmest step | [5586124](https://github.com/jgraving/slot/commit/5586124) | `WARMEST` [1.0, 0.82, 0.62] to [1.0, 0.60, 0.20] | Upstream value | Skip (taste) | L / S / L | none | Brandon's call |
| Lower backlight floor | [2c318fa](https://github.com/jgraving/slot/commit/2c318fa) | `BACKLIGHT_FLOOR` back to raw 1 | **Our tree has `BACKLIGHT_FLOOR = 1.0`** (v1.7.0), which is upstream issue #100 (RG34XX: first step up from off stays black) | **Skip jgraving; take upstream [3b6349c](https://github.com/BrandonKowalski/slot/commit/3b6349c)** (floor 8/255 of max, at least 1) | M-H / S / L | none (`slot-power/src/device.rs` unpatched) | Already upstream, unreleased |
| Deep sleep on lid close, "Shut Down After" with Never | [f2aa20d](https://github.com/jgraving/slot/commit/f2aa20d), [5958250](https://github.com/jgraving/slot/commit/5958250); `power_settings.rs`, `slot-power` `suspend()` | New Power page: Lid Close (Light Sleep, Deep Sleep, Power Off), Shut Down After (3, 15, 30 min, Never), Sleep Now, Power Off. Deep sleep: pause the core, mute the ring, set `axp2202-battery/os_sleep` to 16, arm `rtc0/wakealarm` for the timer, `alsactl store`, write `mem` to `/sys/power/state`, restore everything; power off if the alarm woke it. Only POWER wakes (the lid does not); a 750 ms guard eats the waking press | ADR 0033 keeps upstream's light doze and power off after 3 min. Upstream main adds a lid power-off timer 1/3/5/10/15/30 min ([2c82294](https://github.com/BrandonKowalski/slot/commit/2c82294)) and a lid watcher `lid.sh` that powers off regardless ([ad5ce8a](https://github.com/BrandonKowalski/slot/commit/ad5ce8a)) | **Adapt later** (deep sleep only; the timer is superseded upstream). Needs an ADR amending 0033 and a device gate | H (standby for days instead of power off at 3 min) / M-L / M-H (resume of GL, ALSA and threaded cores; "Never" fights upstream's lid watcher after a rebase) | `doze`/`wake` (our 0038 touches lid paths for PS1), ALSA reopen (0018) | **Yes, as an issue first.** Generic H700 feature |
| Background sync during the shutdown animation | [8df36f7](https://github.com/jgraving/slot/commit/8df36f7) | `prepare_poweroff()` starts `sync` on a thread when the switch animation starts; the final frame is presented before the blocking sync | None; dropped from jgraving `main` | Adapt (optional) | L-M (PS1 states are 4.4 MB) / S / L | none | Yes |
| Restart choice removed | 8df36f7 | Drops Restart from the power menu | Upstream moved Restart to About on X ([0ba5370](https://github.com/BrandonKowalski/slot/commit/0ba5370)) | Superseded upstream | n/a | n/a | n/a |
| ALSA: retry instead of giving up | inside [a0d7ef7](https://github.com/jgraving/slot/commit/a0d7ef7) (first in [6aaa938](https://github.com/jgraving/slot/commit/6aaa938)) | `run()`: when `write()` fails unrecoverably, `release()` and sleep 200 ms instead of `return` (which ends the playback thread, so sound is gone until restart). `write()`: count zero-frame writes, give up after 5 and sleep 1 ms on 0 instead of spinning | Our 0018 (ADR 0030, 0041) keeps ALSA open and reopens; the `return` is still there (ours and upstream main `alsa.rs:253`) | **Adopt** (these ~15 lines only, not the route code; defensive, no known trigger on our speaker and jack) | L / S / L | Same `run()` loop as 0018, small rebase | **Yes** |
| Sound menu: Bluetooth, USB, wired | [a0d7ef7](https://github.com/jgraving/slot/commit/a0d7ef7), [6b00130](https://github.com/jgraving/slot/commit/6b00130); `bluetooth.rs` (1,899 lines), `bluetooth_volume.rs`, `usb_audio.rs`, `card/System/bluetooth.sh` (670) | BlueZ agent plus BlueALSA through `/run/slot-audio-device`; ALSA opens `plug:SLAVE='bluealsa:...'` or a USB `plughw` route and never falls back to the speaker; per-output volume and mute; AVRCP volume sync; auto reconnect | None | **Skip (non-goal for now).** Declined upstream (#109). About 3k lines; rewrites the `alsa.rs` open and run loop that 0018 owns; A2DP adds latency our device gate (zero underruns, PLAN success 4) would have to re-prove; tested only on RG SP and RG35XXSP | H for BT users / L / H | 0018, `session.rs`, `frontend.rs`, quick menu | No (declined) |
| Quiet landing on unplug | [6861eac](https://github.com/jgraving/slot/commit/6861eac), in a0d7ef7 | When wired headphones (or BT, USB) go away, set the speaker to a "disconnect volume" (default 0) | Upstream keeps separate speaker and headphone levels, so unplug returns to the speaker's own level | Skip (needs the Sound menu for its setting; upstream behaviour already avoids a blast if the speaker level is low) | L / S / L | none | No |
| Synthesised cartridge ticks while scrolling | [6da0c7d](https://github.com/jgraving/slot/commit/6da0c7d), [4da83e4](https://github.com/jgraving/slot/commit/4da83e4) | `Sfx::Cartridge(n)`: a 28 ms noise-plus-resonance click per shelf step, 5 pitch variants, 35 ms throttle | None | Skip for now (taste) | L / S / M (each tick wakes the released PCM; with our 0018 hold logic the first tick after 3 s of silence may arrive late or reopen ALSA on every browse) | 0018 | Taste; Brandon's call |
| Power switch art and click | [1bdbd3b](https://github.com/jgraving/slot/commit/1bdbd3b), [1c60e07](https://github.com/jgraving/slot/commit/1c60e07), [a7073be](https://github.com/jgraving/slot/commit/a7073be), [bf85ae6](https://github.com/jgraving/slot/commit/bf85ae6) | GBA SP power switch slides off during shutdown with a click | Upstream shutdown lines | Skip (SP-specific art) | L / M / L | none | No |

## 4. Our Screen list overflows (found while reviewing the scroll work)

Our `QuickRow::SCREEN` has 9 rows (GBA, GBC, GB, NES, SNES, GG, SMS, MD, PlayStation). `quick_row_top`
in `crates/slot-ui/src/quick_menu.rs:809` centres the page with no window:
`top = (LEGEND_Y - QUICK_PITCH * rows) / 2 = (427 - 52 * 9) / 2 = -20.5`. The first row (Game Boy
Advance) starts 20 px above the panel and the last ends at about 447, under the legend at 427. Eight rows
fit (top 5.5), so it only shows on a card with every system: `retro_quick::hidden_on_shelf` returns
`None` for `[true; 5]` and nothing in SCREEN is hidden. No test catches it: `render_quick_menu.rs` casts
`quick_row_top(..) as usize`, which saturates a negative top to 0, and it only walks `QuickRow::MAIN`.

jgraving's 6-row window and upstream's `quick_window` (e1bfb2b) both solve this kind of page, but
upstream's `scrolls()` allowlist is CONTROLS, SHORTCUTS and GENERAL only, so even after a rebase onto
upstream main SCREEN will not scroll unless we add it. This is **ours**, not upstream-first.

## 5. Shell, carts and art

| Change | Commits | What it does | Ours | Verdict | Value / effort / risk | Patch conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|
| Shell colours (Graphite, Platinum, Pearl Blue, Pearl Pink), SVG slot housing, EXT.1 port | [35cc5a8](https://github.com/jgraving/slot/commit/35cc5a8) and about 20 follow-ups in rgsp-shell-finishes | New General row "Shell Color", `ShellColour` in `slot_state`, painted SVG slot and port | Upstream light/dark slot | Skip (RG SP look) | L / L / M | New `slot_state` key (PLAN gotcha 9, `format!` line), General page rows, `frontend.rs` slot faces | No |
| Larger carousel carts | [1780b2c](https://github.com/jgraving/slot/commit/1780b2c) | Carts drawn bigger on the shelf, shrink to insert size | Our NES, SNES, Sega boxes and PS1 jewel cases are sized to the v1.7.0 shelf (ADRs 0054, 0056, 0057, 0069) | Skip | L / L / H | Every cart and case patch (0012, 0013, 0023, 0028, 0029, 0039) | No |
| Play emblem removed | [7a293e3](https://github.com/jgraving/slot/commit/7a293e3) | Cosmetic | n/a | Skip | L / S / L | none | No |

## 6. How the candidates extend to our systems

| Candidate | NES / SNES | GG / SMS / MD | PS1 | Per-system Screen section? |
|---|---|---|---|---|
| Screen scrolling (ours) | The NES and SNES rows are what push SCREEN past 6 | Three Sega rows | PlayStation row is the 9th | No new section; it is the Screen list itself. Each system keeps its own row and section (maintainer rule) |
| Favourite confirm | Works as is: keyed on `(platform, stem)`, hint placed from `cart_box(platform)` and `foot_y`, which cover every platform in our tree (`cart.rs:188`) | Check placement over the tall SMS box well (ADR 0057); the hint clamps to y >= 6 and may sit on the shelf name | Check over the jewel case and the double case (ADR 0069) | No (global) |
| Start closes picker | NES (fceumm/nestopia) and SNES (snes9x/snes9x2005_plus) pickers from 0009 | No picker (one core, ADR 0053) | No picker (ADR 0063) | No |
| Silent-start HUD | All | All | All (shows after the disc loads, since it fires on entering `Playing`) | No |
| ALSA retry | All cores share the ring | All | All | No |
| Day/night presets | Warmth is applied in the final `BLIT_FRAG` (`u_gain`, `fbo.rs:444`) after every game program, so it reaches our retro shader output (ADR 0028) too | Same | Same | No (global), but needs a trigger other than SELECT+X, which is Picture on SNES and PS1 |
| Deep sleep | Core paused before suspend | Same | pcsx_rearmed threaded renderer (ADR 0064) must survive resume: gate it | No |
| Backlight floor (upstream) | Global | Global | Global | No |

## Recommended to adopt (ranked)

1. **Make the Screen list scroll (ours).** Port upstream's `quick_window` shape (e1bfb2b: window of 6
   centred on the selection, clamped to the end) into our Screen patch, apply it to `quick_row_top` and
   the draw loop, and enable it for `SCREEN` only, so a rebase onto upstream main reduces to adding
   `&QuickRow::SCREEN` to `scrolls()`. Optional: jgraving's scrollbar thumb (ad49e5c). Add a test that
   `quick_row_top(QuickRow::ScreenGba, &[]) >= 0.0` and that the last shown row ends above `LEGEND_Y`,
   evaluated as `f32` with no `as usize`. Why: on a full card the GBA row is off screen today. Effort S-M.
   Ours (upstream will not scroll SCREEN; amend ADR 0048). Device check: card with GB, GBA, NES, SNES, GG,
   SMS, MD and a PS1 disc; open Menu, Screen, every row label fully visible and none under
   the legend; scroll to PlayStation and back to Game Boy Advance.
2. **Carry upstream 3b6349c (backlight floor, #100) now.** Two lines in `slot-power/src/device.rs`; drop on
   the next rebase. Ignore jgraving's 2c318fa, which reverts it. Why: #100 was reported on the RG34XX
   family on v1.7.0, our pin. Effort S. Upstream already. Device check: brightness all the way down to off
   (the brightness Down chord, MENU or SELECT per device), then one step up: the panel lights at a dim but visible level.
3. **Confirm favourite removal (second Y).** Port the `FavoriteRemoval` state, the key-up requirement and
   the floating "Y Again to remove" face (e2dc0cb); the departure animation (37f230c, a83c345) is
   optional. Upstream-first as one PR; carry until it ships. Credit GPL-3.0 jgraving. Effort S (M with
   animation). Device check: on the Favorites shelf press Y on an SMS box and on a PS1 double case: the
   hint appears above the cart and clear of the shelf name; any other key cancels; a second Y removes it
   and it stays removed after a reboot.
4. **Silent-start volume HUD (12f7b3a).** Four lines in the phase-change block. Upstream first. Effort S.
   Device check: mute the device, insert a PS1 disc and a NES cart: the muted volume HUD shows once as
   gameplay starts, not during loading, and not again until the next insert.
5. **START closes the core picker (e047d17).** One match arm. Upstream first. Effort S. Device check: on a
   SNES cart press START to open the picker, START again closes it without changing the core; same on NES.
6. **ALSA retry instead of thread exit (defensive).** Take the `release(); sleep(200 ms)` on write failure
   and the zero-frame stall guard from a0d7ef7, nothing else from the Bluetooth work. Fold into 0018 and
   send to Brandon as a small PR (ADR 0047). Why: the `return` only fires when `snd_pcm_recover` itself
   fails (xrun and suspend, `-EPIPE` and `-ESTRPIPE`, normally recover), which jgraving hit because BT and
   USB sinks vanish mid-write; on our speaker plus jack we know of no trigger. Value L, effort S. Upstream
   first. Verification: code review plus the existing audio tests staying green; no on-device trigger.
7. **Deep sleep on lid close (f2aa20d), later and gated.** Only the suspend path (`supports_deep_sleep`,
   `suspend` with the RTC alarm and `os_sleep` restore), with upstream's `lid_off_min` as the timer instead
   of jgraving's 3/15/30/Never. Open an upstream issue first; needs an ADR amending 0033. Effort M-L, risk
   M-H. Device check: Deep Sleep selected, close the lid mid-game on SNES, MD and PS1, wait 10 minutes,
   POWER wakes into the same frame with sound; battery percentage drop overnight is a few percent, and the
   timer powers off with a resume save intact.
8. **Day/night presets, after the rebase onto upstream's remappable shortcuts.** Keep `display_settings.rs`
   as is but bind the toggle to an unbound-by-default shortcut (or a General row, which needs an ADR
   against 0008/0023), never SELECT+X. Effort M. Upstream idea first. Device check: toggle on the shelf and
   in a SNES game with crt-pi on: brightness and warmth swap, SELECT+X still flips the SNES picture.

## Skip

- **Bluetooth, USB and Sound menu (a0d7ef7):** declined upstream (#109), about 3k lines, owns the ALSA
  loop that 0018 owns, untested on the RG34XXSP, A2DP latency would have to re-pass our underrun gate.
  Revisit only on user demand, as a credited port.
- **Parent controls (kid-* chain), Wi-Fi vault, OTA:** never merged or removed by the author; out of our
  scope (no networking, no kids' build).
- **SP shell finishes, larger carts, power switch art, status bar on top, gold foil star, warmer WARMEST,
  carousel ticks:** taste or RG SP specific; the larger carts would re-fit every box we drew.
- **2c318fa backlight floor:** regresses upstream #100; take upstream 3b6349c instead.
- **Scroll-options, Restart removal, Favorites/Recents, browsing memory, lid timer:** superseded by
  upstream (e1bfb2b, 0ba5370, v1.7.0, #53, 2c82294).
- **Packaging and snapshot branches** (build-*, preview-*, test-*, upstream-oct*, sync-upstream): no
  source changes.
