# Forks of BrandonKowalski/slot: what people built

Date: 2026-10-15 (upstream v1.7.0 was released today, 05:50 UTC)

Upstream: https://github.com/BrandonKowalski/slot (169 stars, GPL-3.0-or-later since 2026-09-17, MIT before that)

## Method

1. Listed every fork with `gh api repos/BrandonKowalski/slot/forks --paginate`, then the forks of any fork whose `forks_count` was above zero.
2. Listed every branch of every fork and compared it with upstream `main` using `gh api repos/BrandonKowalski/slot/compare/main...OWNER:BRANCH` (ahead_by, behind_by, commits, files).
3. Read the commit subjects of every branch that is ahead. Read the full diffs where a fork touches NES, SNES or other new platforms: gmaster1998, savethefails (ezGBA) and bently0602.
4. Matched forks against upstream PRs (`gh pr list -R BrandonKowalski/slot --state all`), the upstream issues, and the v1.7.0 and v1.6.0 release notes.
5. Checked LICENSE in every fork whose licence differs from upstream, and the upstream LICENSE history.

Note on upstream status: Brandon lands contributions by hand and closes the PR. Only #85 shows as MERGED on GitHub. #74, #77, #81, #83, #88, #89, #56, #54 and #51 show as CLOSED, but the release notes credit them, so this document counts them as **merged upstream**. There are **no open PRs upstream** today. The "PR 33" in jgraving's branch name is a PR inside jgraving's own fork. Upstream #33 is an issue (the Smootheststep shader).

Status buckets used below:
- **merged upstream**: shipped in an upstream release, credited in the release notes or the README.
- **superseded by v1.7.0**: fork-only, but upstream now ships its own version of the same feature.
- **closed PR**: a PR was made and closed without the work landing.
- **fork-only**: never offered upstream.

## Counts

| | Count |
|---|---|
| Direct forks (API listing) | 47 |
| Forks of forks | 6 (trdpatrick and Goku039 from ygordreyer, bphenriques from pvaibhav, savethefails from bossman-CT, HugePaint and EsunR from RetroGame66) |
| Total repos checked | 53 (matches upstream `forks_count` and `network_count`, both 53) |
| Repos with at least one branch ahead of upstream | 40 (including felipecpaiva/slot, ours) |
| Repos with no changes | 13 |
| Forks with work merged upstream | 6 (MarkusMaribu, diluno, 454135431515, paulocoe-creator, flo333, GamerAnim) |
| Distinct lineages among the 40 | 33 (Slop family is 5 repos, RetroGame66 family is 3, ezGBA family is 2) |
| Open upstream PRs | 0 |

## Licence

Every fork published since 2026-09-17 keeps GPL-3.0. Four repos report MIT and two report NOASSERTION. None of them changed the licence: each one's merge base with upstream is older than the move from MIT to GPL-3.0-or-later on 2026-09-17 (commit 4061086; checked with the compare API for bossman-CT, Scorbust, RetroGame66 and ryanmsartor), and their LICENSE file is still Brandon's original MIT text.

- MIT: bossman-CT/ezGBA, savethefails/ezGBA-640x480, Scorbust/slot, ryanmsartor/slot.
- NOASSERTION (the file is the MIT text): RetroGame66/slot, EsunR/slot. HugePaint/slot reports GPL-3.0.

One caveat: **savethefails/ezGBA-640x480 declares MIT but has merged later upstream code** ("Bring over slot 1.5.0's frame-loop performance fixes", "Bring over slot's cart plastics and moulding"). That code was GPL-3.0 by then. Treat anything borrowed from ezGBA as GPL-3.0 and credit it. Its `cores/snes9x2005/runahead-audio.patch` is a patch to snes9x2005, so it also carries snes9x's non-commercial licence and the GPL-2.0 of the CATSFC parts, which is the same licence situation slot-nes-snes already ships with.

## Fork table

Ahead/behind is for the branch shown. Forks with many branches show the default branch and the branch furthest ahead.

| Fork | Branch | Ahead/behind | Last push | Summary | Upstream status | Link |
|---|---|---|---|---|---|---|
| Baggio94/slot-konkr | develop/konkr; 59 branches ahead, max 1004 on feat/konkr-upstream-1.7-visual-u1 | 437/109 | 10-15 | Android port for the KONKR KPA handheld: APK, SAF storage, native RetroAchievements (GBA, GB, GBC), gpSP and mGBA link multiplayer over LAN, run-ahead diagnostics, Mac AVD tooling | fork-only | [repo](https://github.com/Baggio94/slot-konkr) |
| stevolarn/slot | main (5 branches) | 177/81 | 10-15 | Rewritten as "Shelf", then renamed back to Slot: a game picker pak for NextUI on the TrimUI Brick. Emulation removed. NES, SNES, Mega Drive, GG, SMS, N64, PCE, NGP, Sega CD, PS1 shelves with real cart photos, LaunchBox art fetch, video-store theme, blow on carts | fork-only | [repo](https://github.com/stevolarn/slot) |
| Skipper07-coder-sys/slotHub | main; 20 branches, max 164 on main | 164/76 | 10-13 | Bluetooth headphones, Wi-Fi join and browser file drop, OTA updater, box art and label fetch (by ROM checksum, SteamGridDB), RetroAchievements, LCD1x, Retro, Bevel and CRT shaders, letter rail, CPU and GPU clock hold, run-ahead on gpSP, flashable RG34XXSP image | fork-only | [repo](https://github.com/Skipper07-coder-sys/slotHub) |
| savethefails/ezGBA-640x480 | main; 11 branches, max 133 on claude/loving-fermat-mi6kc5 | 80/279 | 10-15 | Kid-focused fork of ezGBA: **SNES shelf on snes9x and snes9x2005_plus**, SNES run-ahead with an audio patch, SNES over the link cable, SELECT without the 600 ms delay, 640x480 native layout, sharp-shimmerless port, LCD grid, PICO-8, input latency tracing | fork-only | [repo](https://github.com/savethefails/ezGBA-640x480) |
| bossman-CT/ezGBA | main | 36/279 | 09-27 | ezGBA: simplified GBA-only build for kids, L2/R2 as brightness, per-cart backdrop, 12h clock, first-boot greeting video | fork-only | [repo](https://github.com/bossman-CT/ezGBA) |
| jgraving/slot | main; 36 branches, max 81 on favorite-start-confirm | 67/81 | 10-15 | Bluetooth audio, Wi-Fi with an encrypted credential vault, OTA staging (later removed), parent controls (approved games, daily play limits, Kids carousel), SP power switch art, tactile sounds, favourites with a confirm-to-remove | fork-only; bluetooth-upstream-minimal (4/0) looks like an upcoming upstream PR | [repo](https://github.com/jgraving/slot) |
| ygordreyer/slot ("Slop") | Slop | 80/147 | 10-09 | Background RetroAchievements, home Wi-Fi, link over home network, multi-pass shader presets with parameter screen, crt-lite, VBA-Color LCD presets, cheats, label fetch, FPS overlay, on-screen keyboard, slopctl | fork-only | [repo](https://github.com/ygordreyer/slot) |
| trdpatrick/slot-pot | Slop | 84/147 | 10-13 | Slop plus a release workflow | fork-only | [repo](https://github.com/trdpatrick/slot-pot) |
| Goku039/slot | Slop | 80/147 | 10-09 | Unchanged copy of Slop | fork-only | [repo](https://github.com/Goku039/slot) |
| pvaibhav/slot | pvaibhav-improvements | 36/0 | 10-15 | Slop's base (RetroAchievements, home Wi-Fi, label fetch, panel colour calibration LUT, schedutil governor) rebased on v1.7.0, plus 120 Hz with native game pacing | fork-only | [repo](https://github.com/pvaibhav/slot) |
| bphenriques/slot | pvaibhav-improvements | 32/76 | 10-13 | Older copy of pvaibhav | fork-only | [repo](https://github.com/bphenriques/slot) |
| suprsomething/slot.advance | main (14 branches) | 79/90 | 10-15 | "slot advance", GBA focused: suspend-to-RAM sleep with lid wake, per-game profiles, save-state ring of five, battery banners, own website | fork-only; favourites, recents, last cart and titles superseded by v1.7.0 | [repo](https://github.com/suprsomething/slot.advance) |
| nelynes/slotPlus | main (4 branches) | 52/0 | 10-15 | **WonderSwan (Beetle Cygne), Atari Lynx (Beetle Lynx), Game Gear (Gearsystem)** shelves with rotation, own carts and own shaders; Transparent GB shader; rebased on v1.7.0 | fork-only | [repo](https://github.com/nelynes/slotPlus) |
| marghost/slot_modded | main | 49/14 | 10-15 | Button cheat sheet, battery banners, standby while lid shut, scrolling settings, keep FF pitch, startup screen, faster boot and faster long-shelf scrolling, RG35XXSP bezels | fork-only; favourites, recents, bezels superseded by v1.7.0 | [repo](https://github.com/marghost/slot_modded) |
| machomano11/slot | claude/project-thread-mtm719 (5 branches) | 25/0 | 10-15 | TrimUI Brick port imported from LordNordyx/Slot-Brick, RetroAchievements (softcore), WebDAV cloud sync of saves and states | fork-only | [repo](https://github.com/machomano11/slot) |
| alejandrolm96/slot-retroachievements | main (11 branches) | 21/109 | 10-10 | Home Wi-Fi from the frontend, libretro memory maps, rcheevos transport (work in progress) | fork-only | [repo](https://github.com/alejandrolm96/slot-retroachievements) |
| nickclyde/slot-plus | main | 12/76 | 10-13 | RetroAchievements over home Wi-Fi with banners, Recently Played, Favorites, list and search shelves, adb screenshot tasks | fork-only; favourites and recents superseded | [repo](https://github.com/nickclyde/slot-plus) |
| gmaster1998/slot.ps1 | main | 16/80 | 10-13 | **PS1 (PCSX ReARMed) and SNES (snes9x)**, experimental, plus a Platform::Psp stub; hi-res frame path; L2/R2 handed to the game | closed PR #76 | [repo](https://github.com/gmaster1998/slot.ps1) |
| bently0602/slot | main | 9/95 | 10-14 | **PS1 and SNES**, HDMI out with docking, music player, Bluetooth headphones, Cover Flow shelf, screen-off music mode, SNES cart renderer for Cart Studio | fork-only | [repo](https://github.com/bently0602/slot) |
| RetroGame66/slot | 66-mods | 30/409 | 10-02 | Chinese UI, linear colour correction, cheats, GB/GBC art, light and dark modes, palette browser, favourites | fork-only | [repo](https://github.com/RetroGame66/slot) |
| HugePaint/slot | 66-mods | 31/81 | 10-14 | Copy of RetroGame66 | fork-only | [repo](https://github.com/HugePaint/slot) |
| EsunR/slot | 66-mods | 31/409 | 10-11 | RetroGame66 plus RG35XXSP support and per-game button remapping | fork-only | [repo](https://github.com/EsunR/slot) |
| chiyuki0325/snowslots | main | 15/214 | 09-28 | Chinese UI and filenames, library sorting, X/Y turbo for A/B, keep FF pitch, low-latency display pacing | fork-only | [repo](https://github.com/chiyuki0325/snowslots) |
| pawndev/slot-blow | dry-battery (4 branches) | 12/0 | 10-15 | Gameplay > Experimental: dusty carts you blow on, label wear from play time, cart batteries that run dry | fork-only | [repo](https://github.com/pawndev/slot-blow) |
| 454135431515/slot | runahead | 13/81 | 10-11 | Run-ahead for GBA on mGBA | merged upstream (#56, v1.7.0) | [repo](https://github.com/454135431515/slot) |
| brianeo0210-art/slot | main (3 branches) | 8/109 | 10-09 | Syncthing save sync over home Wi-Fi, protection for saves edited outside slot | fork-only | [repo](https://github.com/brianeo0210-art/slot) |
| radiylon/slot | sp-latest (3 branches) | 9/14 | 10-15 | Bluetooth headphones with an Audio page, louder insert and eject sounds | fork-only | [repo](https://github.com/radiylon/slot) |
| markbruno/slot-plus | main | 6/214 | 09-30 | RetroArch-style shader loader (retroshader.rs) and cheats; later absorbed into Slop | fork-only | [repo](https://github.com/markbruno/slot-plus) |
| MarkusMaribu/slot_skeuomorphic | ui-redesign, game-bezels | 6/76, 2/76 | 10-13 | Skeuomorphic UI, themes, wallpapers; GB and GBC bezels | merged upstream (#74, #77) | [repo](https://github.com/MarkusMaribu/slot_skeuomorphic) |
| diluno/slot | rg28xx, favorites, panel-640 | 5/0 | 10-15 | Favorites and 640x480 canvas (merged); new: per-console Scaling row (Fit, Integer, Aspect Fill), RG28XX rotation, star sticker | merged upstream (#89, #81); rg28xx branch fork-only, likely next PR | [repo](https://github.com/diluno/slot) |
| paulocoe-creator/slot | main (5 branches) | 5/0 | 10-15 | GBC correction and LCD3x for GB (merged), RG34XX chords (merged); new: Game Boy fit without integer scaling, BaseOS target export | merged upstream (#83, #85, #88); main fork-only | [repo](https://github.com/paulocoe-creator/slot) |
| flo333/slot | fix/runahead-audio | 5/71 | 10-15 | Backlight curve and muted-play pacing (merged); new: mGBA PSG save-state patch for run-ahead audio, idle loop option for FireRed and LeafGreen | merged upstream (#54, #51); #90 closed, superseded by #53; branch fork-only | [repo](https://github.com/flo333/slot) |
| GamerAnim/slot | main | 5/109 | 10-09 | RG28XX portrait panel rotation | merged upstream (issue #35, credited in README) | [repo](https://github.com/GamerAnim/slot) |
| athroughza/slot | add-keybinds | 3/80 | 10-13 | Per-shelf button rebinding from a Controls page in the quick menu; X clears a binding | fork-only | [repo](https://github.com/athroughza/slot) |
| zognic/slot | main, square-display | 3/0 | 10-15 | Square panel support (1:1 frontend, Game Boy fills the square) | fork-only, likely next PR | [repo](https://github.com/zognic/slot) |
| Scorbust/slot | main | 3/384 | 09-16 | Small shell.rs and taskfile tweak | fork-only | [repo](https://github.com/Scorbust/slot) |
| yangch291-pixel/slot_zh | main | 3/0 | 10-15 | Chinese label font and a build workflow | fork-only | [repo](https://github.com/yangch291-pixel/slot_zh) |
| roygravy/slot | rg35xx-plus-640 | 1/81 | 10-11 | Native 640x480 grid for RG35XX Plus | superseded by v1.7.0 (#81) | [repo](https://github.com/roygravy/slot) |
| nosai-ka/slot | sharp-shader | 1/109 | 10-09 | Sharp screen shader; fix for lost pixels on small panels | fork-only | [repo](https://github.com/nosai-ka/slot) |
| felipecpaiva/slot (ours) | lazy-shelf-gb | 1/76 | 10-13 | Class a Game Boy cart shell when drawn, not when the shelf is built | closed PR #75; marghost carries it (72f468d) | [repo](https://github.com/felipecpaiva/slot) |

## Notable forks

### savethefails/ezGBA-640x480 (most relevant to us)

A fork of bossman-CT's kid-friendly ezGBA, rebuilt for the RG35XXSP 640x480 panel. It has its own SNES support built in parallel with ours:
- [10316a7](https://github.com/savethefails/ezGBA-640x480/commit/10316a7f3a009bd0f0602d4ed1c771ada40532dd) SNES shelf on snes9x, picture placed at 4:3, no LCD grid, X and Y handed to the game for SNES only, L and R kept by the game. Own SNES Game Pak drawing.
- [b2685af](https://github.com/savethefails/ezGBA-640x480/commit/b2685affb4274cf83d416066a3efd076284c9d91) Switches SNES to snes9x2005_plus because full snes9x costs about 6.5 ms a frame on the SP, too much for a frame of run-ahead.
- [20e2eee](https://github.com/savethefails/ezGBA-640x480/commit/20e2eee863e634669e5cbbde56c7717941738f16) `cores/snes9x2005/runahead-audio.patch`: snes9x2005 resets the sound chip's output buffers on every state load, so run-ahead crackles and slowly underruns (826 missing samples in their test). The patch saves and restores that output side. Comes with a sample-exact comparison example.
- [b420419](https://github.com/savethefails/ezGBA-640x480/commit/b420419b4bd729e47ce1e60147f98c5751c71cf6) (branch claude/loving-fermat-mi6kc5 only, not on main) SELECT reaches the game on the press, not 600 ms later. Chords still arm off the same hold.
- 3787664 SNES rows drawn at a whole multiple; 6c5504c "SNES Picture" setting (sharp rows or the whole 4:3).
- [ac6f2e4](https://github.com/savethefails/ezGBA-640x480/commit/ac6f2e485bfe37319b7b1616f6951e23b67aef5c) (branch claude/loving-fermat-mi6kc5 only) Two-player SNES over the emulated link cable (host is pad 1, joiner pad 2).
- 81c50d6, 3564816 SNES cart shells after the North American cart.
- Also: input latency trace, 10 ms button scan read late in the refresh, PICO-8 shelf (pico8 branch).

### gmaster1998/slot.ps1 (closed PR #76)

Experimental PS1 (PCSX ReARMed) and SNES (snes9x). It adds `Platform::{Ps1, Snes, Psp}` and `Core::{Pcsx, Snes9x, Ppsspp}` straight into upstream enums, a global hi-res frame mutex for frames larger than 240x160, and an option that hands L2 and R2 to the game. The diff leaves the turbo path alone (`ButtonMask::without_turbo` and `App::turbo` are unchanged; only PS1 gets L2 and R2), so as far as the diff shows, X and Y are still stripped on SNES. slot-nes-snes fixes that with `TurboMode::PassThrough`. Brandon closed the PR, and since then upstream has stayed GB, GBC and GBA only. [PR #76](https://github.com/BrandonKowalski/slot/pull/76)

### bently0602/slot

A large drop (203 files) of PS1 and SNES (cores/pcsx, cores/snes9x build scripts, SNES test harness, tasks/023 "SNES run-ahead audio research"), HDMI out with docking and safe area, a music player, Bluetooth, Cover Flow, and an SNES cart renderer exported for Cart Studio ([ae0ac6d](https://github.com/bently0602/slot/commit/ae0ac6d)). Its SNES cart renderer and its Cart Studio work overlap our cart art and our Cart Studio fork.

### nelynes/slotPlus

"Taking Slot and adding support for a few more 3:2-ish systems": WonderSwan and WonderSwan Color (Beetle Cygne, vertical games with a remapped pad), Atari Lynx (Beetle Lynx, rotation, audio rate fix), and Game Gear (Gearsystem) on slotPlusUltra. Each system has its own cart shape and screen shader. It is rebased on v1.7.0 (0 behind). Same approach as ours (a multi-system patch on top of upstream), with the same rebase pain. Key commits: [65e0508](https://github.com/nelynes/slotPlus/commit/65e0508), [749523c](https://github.com/nelynes/slotPlus/commit/749523c), [f0e9318](https://github.com/nelynes/slotPlus/commit/f0e9318), Transparent shader [9201b8a](https://github.com/nelynes/slotPlus/commit/9201b8a).

### stevolarn/slot (Shelf / Slot pak for TrimUI Brick)

The emulator was stripped out and the shelf became a game picker for NextUI. It has the most work on NES and SNES visuals of any fork: real cart photos for NES, SNES and Mega Drive (6531356, e34fbfb), labels cut from the top of box art (6eaa78d), Satellaview filtered off the SNES shelf (f3405a0), a bottom bar drawn as each console's own top (2cbf555), and `tools/fetch_art.py` plus on-device "Get Artwork" from the LaunchBox Games Database (box fronts, backs, cart photos). Also a video-store theme, blowing on carts, an arcade-style name search, and N64, PCE, NGP, Sega CD and PS1 shelves.

### Skipper07-coder-sys/slotHub and the Slop family (ygordreyer, pvaibhav)

These are the "everything" forks. Both have RetroAchievements, home Wi-Fi, background label fetch, multi-pass shader presets (Slop), crt-lite, LCD1x, Retro, Bevel and CRT shaders (Skipper07), on-screen keyboards and Bluetooth. Skipper07's label fetch tries the real cart label by ROM checksum first ([ccbb29a](https://github.com/Skipper07-coder-sys/slotHub/commit/ccbb29a)), then SteamGridDB logos with name matching, and finds romhacks by GBA game code. pvaibhav is rebased on v1.7.0 and adds 120 Hz with native game pacing (e8ff757).

### RetroAchievements forks

Six independent RetroAchievements efforts exist: nickclyde, alejandrolm96, machomano11, Slop and pvaibhav, Skipper07, and Baggio94 (the most complete, with GB and GBC memory coverage and an offline cache). None was offered upstream. rcheevos supports NES and SNES, so whichever one upstream adopts decides how we would extend it.

### Bluetooth audio forks

jgraving (`bluetooth-upstream-minimal`, 0 behind, "capability-gated Bluetooth audio to upstream SLOT", pushed today), radiylon, Skipper07 and bently0602. jgraving's branch looks like the next upstream PR.

### Display forks likely to become upstream PRs soon (0 behind, pushed today)

- diluno/rg28xx [4bebab2](https://github.com/diluno/slot/commit/4bebab2): a Scaling row (Fit, Integer, Aspect Fill) on each console's Screen page and in game. Touches `slot-gfx/src/game_fit.rs`, `fbo.rs`, `slot_state.rs`.
- paulocoe-creator/main [0e4b8a5](https://github.com/paulocoe-creator/slot/commit/0e4b8a5): Game Boy fit without integer scaling; touches `fbo.rs`, `pipeline.rs`, `video_mode.rs`, `app.rs`, `frontend.rs`.
- zognic/square-display: a square-panel layout path in `fbo.rs`, `layout.rs` and `square.rs`.

All three touch the files our canvas and stretch patches touch (ADR 0004 fixed 2x canvas, ADR 0016 set game canvas every frame, ADR 0018 source rect takes canvas, ADR 0022 NES/SNES default stretch). Expect rebase work if any of them lands.

## Ideas for slot-nes-snes

Ranked by value for NES and SNES players compared with effort and risk. Every item is fork-only, since upstream has no open PRs. Licence: every source is GPL-3.0 unless noted, which is compatible with slot-nes-snes. Credit the author in the commit and in LICENSING.md.

1. **SNES run-ahead on snes9x2005_plus, with the audio patch**
   - What: extend v1.7.0's run-ahead (GBA on mGBA only, #56) to SNES on snes9x2005_plus. Apply `runahead-audio.patch` so state loads do not crackle.
   - Source: savethefails b2685af, 20e2eee. bently0602 has a related research note (tasks/023).
   - Value: high. SNES platformers and action games gain a frame of input response, which is the most noticeable latency fix on this hardware.
   - Effort: M. Upstream's run-ahead is gated to mGBA in `emu.rs`/`session.rs`, so this adds a touch point. The patch slots into our `cores/` build.
   - Risk: full snes9x is too slow for it (about 6.5 ms a frame), so offer it on snes9x2005_plus only. Rewind and FF interplay must follow upstream's rules.
   - Licence: the patch modifies snes9x2005 (snes9x non-commercial licence plus GPL-2.0 parts), so ship the patched source tarball the way ezGBA does. ezGBA labels itself MIT, but treat the code as GPL-3.0.
2. **Per-shelf button remapping**
   - What: a Controls page that rebinds each shelf's buttons, so NES players can choose A/B on A/B or on B/Y and SNES players can swap face buttons.
   - Source: athroughza ec0ad11, 2ce23bf. EsunR's per-game remapping (ae7f2f0) is a second reference.
   - Value: medium to high. Upstream issues #23 and #29 ask for it.
   - Effort: M.
   - Risk: it interacts with our `TurboMode` and `ButtonMask::apply`. ADR 0008 rules out new quick-menu rows, so it would need a settings page instead, or an ADR change.
3. **SELECT without the 600 ms hold-back**
   - What: send SELECT to the game on the press. Chords still arm off the same hold.
   - Source: savethefails b420419 (branch claude/loving-fermat-mi6kc5).
   - Value: high. NES and SNES games use SELECT for menus and maps much more than GBA games do, so the delay hurts more here.
   - Conflict: the commit's own cost is that the game sees SELECT pressed under every chord. That works in ezGBA only because it has no SELECT gesture. Our ADR 0007 uses SELECT+X for the SNES picture mode, so an SNES game would see a stray SELECT on every mode switch. It needs a design answer before it fits.
   - Effort: S.
   - Risk: it lives in upstream `slot-input/src/gesture.rs`. Confirm v1.7.0 still holds SELECT back (the commit cites upstream c2a27a6), and treat it as an upstream PR candidate, not a patch of ours.
4. **Better label matching in our label fetcher**
   - What: match by ROM checksum (CRC32 against the libretro-thumbnails or No-Intro name) before name matching. Use the region fallback and alias handling from Slop.
   - Source: Skipper07 ccbb29a and 4a2ad76; Slop 1854dda. stevolarn's `tools/fetch_art.py` (LaunchBox: cart photos, box fronts and backs) is another source for NES and SNES cart photos.
   - Value: medium. Fewer blank carts with hacks, translations and odd filenames.
   - Effort: S.
   - Risk: low. LaunchBox and SteamGridDB terms of use need checking before shipping a fetcher that uses them.
5. **Keep FF pitch**
   - What: fast-forward audio at normal pitch.
   - Source: marghost 6dd84fd, chiyuki0325 f0f482d.
   - Value: low to medium. It fits our audio fixes.
   - Effort: S.
   - Risk: it is platform-wide, so it is better as an upstream PR.
6. **A crt-lite or "TV" shader for SNES and NES**
   - What: the NES and SNES were played on a television. A light CRT shader sized for the H700 GPU would fit our retro shader set.
   - Source: Slop cde8727 (crt-lite), Skipper07 a7b8e45 (CRT, Bevel, Retro, LCD1x), nosai-ka 6ca2587 (Sharp), savethefails cf0f31f (sharp-shimmerless, also upstream issue #99).
   - Value: medium.
   - Effort: S to M. It fits ADR 0026 to 0028 (own GL program, pay once, warm at boot).
   - Risk: low. It overlaps our Line and Pixel shaders.
7. **Experimental "blow on the cart" for NES**
   - What: one cart in N refuses to boot until you blow on it. Label wear grows with play time.
   - Source: pawndev 2a93203, a76e478 (under Gameplay > Experimental); stevolarn 81470ba, 94df6f1 (blow animation).
   - Value: fun. The blow is the NES ritual more than any other console's.
   - Effort: S to M.
   - Risk: purely cosmetic, but it needs a setting row (ADR 0008). Only worth it as an opt-in.
8. **Two-player SNES over the link cable**
   - What: host plays pad 1, joiner pad 2, over upstream's link transport.
   - Source: savethefails ac6f2e4 (branch claude/loving-fermat-mi6kc5).
   - Value: niche but unique.
   - Effort: L.
   - Risk: touches the link session code. Both SNES ports must be declared as joypads.
9. **RetroAchievements for NES and SNES**
   - Source: wait to see which of the six RetroAchievements forks (Baggio94 is the most complete) upstream adopts, then add the NES and SNES memory maps and console IDs.
   - Value: high for some players.
   - Effort: L.
   - Risk: depends on upstream Wi-Fi work. Do not build it ahead of upstream.
10. **Bluetooth audio**
    - Source: jgraving bluetooth-upstream-minimal.
    - Platform-agnostic, so no NES or SNES work. Track it for rebase impact on `audio/alsa.rs`, which we patch (ADR 0030 keeps ALSA open while fed).

Out of scope by our own PLAN.md non-goals (RetroArch breadth): cheats (markbruno, Slop, RetroGame66), zip ROMs (issue #55), per-game profiles (suprsomething), netplay, and save sync (brianeo0210-art, machomano11).

### Forks that add other platforms or cores (conflict or collaboration)

| Fork | Platforms and cores | Relationship to slot-nes-snes |
|---|---|---|
| savethefails/ezGBA-640x480 | SNES (snes9x, snes9x2005_plus), PICO-8 | Same SNES cores as ours. Best source of SNES fixes (run-ahead audio, SELECT). Worth contacting to share the SNES patches. |
| gmaster1998/slot.ps1 | PS1 (pcsx_rearmed), SNES (snes9x), PSP stub | Adds `Platform::Snes` and `Core::Snes9x` straight into upstream enums. Conflicts with ours if it ever lands. PR #76 was closed, so the risk is low. |
| bently0602/slot | PS1, SNES | Same collision as gmaster1998. Its Cart Studio SNES renderer overlaps our Cart Studio fork and cart art: a possible collaboration on a shared SNES cart drawing. |
| nelynes/slotPlus | WonderSwan, Lynx, Game Gear | No overlap in systems. Same patch-on-upstream model. Good partner for a shared "platform trait" seam proposal to upstream (our `Platform` methods `owns_shoulders`, `turbo_mode`, `canvas`, and so on). |
| stevolarn/slot (Brick) | NES, SNES, MD, GG, SMS, N64, PCE, NGP, Sega CD, PS1 (picker only, NextUI runs the games) | No code conflict (a different product). Source of NES and SNES cart photos and an art pipeline. |
| machomano11/slot, Baggio94/slot-konkr | TrimUI Brick, Android KONKR KPA | Device ports, no new systems. |

### Already shipped upstream (do not build)

v1.7.0 now ships favourites and recents, last-cart memory, game titles, per-platform bezels, the in-game menu, a 640x480 canvas, GBA run-ahead, and the backlight curve. The fork versions of these features (nickclyde, jgraving, marghost, suprsomething, Slop, roygravy, flo333 #90) are superseded. Check that our patches still apply on v1.7.0, especially shelf memory (ADR 0025) against upstream's last-cart memory (#53), and our canvas against #81.

## No changes

These 13 forks have 0 commits ahead on every branch: anders-kaffia/slot, dvydra/slot, jorubyp/rgsp-slot, lucascanero/slot, pmp174/slot, robert-harbison/slot, ryanmsartor/slot, saitamasahil/slot, siramok/slot, SourCreamCulture/slot, taylorling/slot, TheRealVivi/slot, therealwizywig/slot_n.

## How to refresh this document

On this Mac, `gh` needs to run outside the Claude Code sandbox (the sandbox proxy fails the TLS check for api.github.com).

```bash
# 1. All forks, then forks of forks
gh api repos/BrandonKowalski/slot/forks --paginate --jq '.[].full_name' > list.txt
for f in $(cat list.txt); do
  [ "$(gh api repos/$f --jq .forks_count)" != "0" ] && gh api repos/$f/forks --jq '.[].full_name'
done >> list.txt

# 2. Every branch of every fork against upstream main
for f in $(cat list.txt); do
  for b in $(gh api repos/$f/branches --paginate --jq '.[].name'); do
    eb=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$b")
    echo -e "$f\t$b\t$(gh api "repos/BrandonKowalski/slot/compare/main...${f%%/*}:$eb" --jq '[.ahead_by,.behind_by]|@tsv')"
  done
done > compare.tsv
awk -F'\t' '$3!="0"' compare.tsv          # branches with changes

# 3. Commit subjects for one fork branch
gh api "repos/BrandonKowalski/slot/compare/main...OWNER:BRANCH" --jq '.commits[]|.sha[0:7]+" "+(.commit.message|split("\n")[0])'

# 4. Upstream PRs, issues and release credits
gh pr list -R BrandonKowalski/slot --state all --limit 300 --json number,state,author,headRefName,title
gh api "repos/BrandonKowalski/slot/issues?state=all&per_page=100" --paginate --jq '.[]|select(.pull_request==null)|[.number,.state,.user.login,.title]|@tsv'
gh release view v1.7.0 -R BrandonKowalski/slot --json body --jq .body

# 5. Licences
gh api repos/BrandonKowalski/slot/forks --paginate --jq '.[]|[.full_name,(.license.spdx_id//"-")]|@tsv' | grep -v GPL-3.0
```

Remember that a CLOSED upstream PR can still be merged by hand. Check the release notes for credits before calling a PR rejected.
