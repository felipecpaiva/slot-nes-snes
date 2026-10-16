# savethefails/ezGBA-640x480: SNES changes vs slot-nes-snes

Read-only survey, 2026-10-15. Clone of all 11 branches; compared against slot-nes-snes ADRs 0001 to 0046,
docs/PLAN.md, docs/DEVICE-GATE.md and the v1.7.0 port (`rebase-v1.7.0`, patched tree `work/slot`), plus
upstream BrandonKowalski/slot at 34ac380.

Base: the fork is 279 commits behind upstream and drawn for a 640x480 panel (RG35XXSP), so nothing ports as
a cherry-pick. Every item below is "reimplement or copy one file". Branches with SNES work: `main` (core,
picture, run-ahead, cores) and `claude/loving-fermat-mi6kc5` (53 ahead: carts, SELECT, link, refactors).
`claude/cores-snes`, `claude/snes9x2005-runahead`, `claude/latency`, `claude/picture-depth`,
`claude/fervent-galileo-i4mak5`, `claude/shutdown-boot-image` are 0 ahead (merged). `pico8`, `free-time`,
`handmade-gba` have no SNES work.

Licence: README says MIT, but the tree merged GPL-3.0 upstream code after 2026-09-17. Treat everything as
GPL-3.0 and credit "savethefails/ezGBA-640x480" with commit links. The snes9x2005 patch is a patch to
snes9x2005: snes9x non-commercial licence plus GPL-2.0 (CATSFC parts), the same terms we already ship
(ADR 0002, LICENSING.md). GPL-2.0 means the shipped source tarball must be the patched tree.

Link prefix: `https://github.com/savethefails/ezGBA-640x480/commit/<sha>`

## 1. Core builds and options

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| snes9x build | [6e10635](https://github.com/savethefails/ezGBA-640x480/commit/6e10635) | Pinned unpatched libretro/snes9x build in a bullseye box, licence and build record shipped beside the core | Have: `cores/snes9x/build.sh`, SLOT_PIN sha256, ship checks (ADR 0002, PLAN step 9) | Ours is stricter (tarball sha256, host and device builds, aarch64 check) | none | no (SNES only) |
| snes9x2005_plus build, made the SNES default | [b2685af](https://github.com/savethefails/ezGBA-640x480/commit/b2685af) | Same pin as ours (`a79dfe9047e7`), `USE_BLARGG_APU=1`. Default SNES core is snes9x2005_plus because snes9x costs ~6.5 ms/frame on the SP, too much for run-ahead | Have the build (`cores/snes9x2005_plus/build.sh`) and the per-game picker pair (patch 0009). Our default is snes9x (ADR 0002) | Different policy. Their default buys run-ahead headroom; ours buys accuracy. Our gate log already shows Super Mario RPG (SA-1) on snes9x failing p99 (19.24 ms) | Changing the default contradicts ADR 0002; needs a new ADR | no |
| snes9x2005 frameskip key | b2685af (`core.rs`) | Sets `snes9x_2005_frameskip` (the core's real prefix), not `snes9x2005_plus_frameskip` | Have: patch 0003 `option_prefix()` plus a declared-key check, test `core_option_keys.rs` | Ours better (checks the core declares it) | none | no |
| "SNES Emulator" quick-menu row | [78438fe](https://github.com/savethefails/ezGBA-640x480/commit/78438fe), fixed in [84a5706](https://github.com/savethefails/ezGBA-640x480/commit/84a5706) | A global default SNES core in theme.txt; a per-game `selected_core.ini` line still wins | Have the per-game picker (START on the cart, patch 0009) | Ours covers it per game; theirs is a global default only | A new row runs against ADRs 0023/0043 (only the shader rows we chose) | no |
| Colour Depth | 78438fe | Saturation, contrast and gamma pass in the game shader (Off, Rich, Deep, Custom), all consoles | None | Generic, not SNES specific. Our retro shaders cover look; no colour pass | none | Generic: if anyone wants it, it is an upstream PR, not ours |

## 2. Input mapping

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| X/Y to the game on SNES, L/R kept by the game | [10316a7](https://github.com/savethefails/ezGBA-640x480/commit/10316a7) | Turbo stripping off for SNES; shoulders only taken on GB carts | Have: patch 0007 `TurboMode::PassThrough`, `owns_shoulders()` policy, tests T22/T22b | Equal in effect; ours is tested in both trees | none | no |
| SELECT on the press, no 600 ms hold | [b420419](https://github.com/savethefails/ezGBA-640x480/commit/b420419) (loving-fermat only) | Game sees SELECT at once; chords arm behind it, so every chord also sends SELECT to the game | Not taken. Upstream did exactly this in 4d77a8b (2026-09-17) and **reverted it** in c2a27a6 (2026-09-30, "hold SELECT back from the game until it cannot be a chord") | Worse for us. SNES games use SELECT (maps, menus); SELECT+X (ADR 0007), SELECT+B/A shaders, SELECT+L1/R1 states would all leak a SELECT press into the game | **Conflicts with ADR 0007 and T22** (SELECT chords must not reach the core) | Already rejected upstream |
| Both pads declared | [ac6f2e4](https://github.com/savethefails/ezGBA-640x480/commit/ac6f2e4) (`libretro.rs`) | `set_controller_port_device(1, JOYPAD)` so full snes9x sets up port 2 | Not present (v1.7.0 tree only declares port 0) | Only matters if we do SNES link (section 7) | none | Yes, alongside any two-pad feature |

## 3. Audio and run-ahead (the valuable part)

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| Run-ahead (generic) | [b240d57](https://github.com/savethefails/ezGBA-640x480/commit/b240d57), [e6e4aee](https://github.com/savethefails/ezGBA-640x480/commit/e6e4aee), [9857af6](https://github.com/savethefails/ezGBA-640x480/commit/9857af6), [8931dca](https://github.com/savethefails/ezGBA-640x480/commit/8931dca) | RetroArch-style 1 or 2 frames; off in netplay, FF and rewind; plays the real frame's audio; rewind reuses the saved state | Superseded: v1.7.0 ships run-ahead (4a4ba92, from #56), 0 or 1 frame, and `runahead_for()` (app.rs:4478) enables it **only for (Mgba, Gba)**. Our port inherits that, so NES and SNES have no run-ahead | Upstream's is the base we use. The fork's version is longer but adds one thing upstream lacks: the budget guard below | none | n/a |
| Run-ahead budget guard | b240d57 (`RUNAHEAD_BUDGET` 12 ms, `RUNAHEAD_STRIKES` 8) | Run-ahead switches itself off for the session after 8 presents in a row over 12 ms, with a log line | Missing. Upstream only switches off when serialize or unserialize fails (`refused`) | Better than upstream: without it, a heavy SNES chip game (SA-1, SuperFX) under run-ahead slows down instead of falling back | none | **Yes, generic**: belongs as a PR to slot (it protects any core upstream later admits) |
| snes9x2005 run-ahead audio patch | [20e2eee](https://github.com/savethefails/ezGBA-640x480/commit/20e2eee) (`cores/snes9x2005/runahead-audio.patch`, 126 lines; build.sh applies `*.patch` and archives the patched tree) | `S9xAPULoadState` resets the blargg APU output side (landing buffer, extra buffers, resampler ring and history), so every load inserts silence: crackle plus ~0.1% short output (826 missing samples in their test). The patch snapshots the output side on save and restores it on load, if buffers are unchanged | Missing. Our `cores/lib.sh` has no patch step and we do not run SNES run-ahead | Needed for SNES run-ahead on snes9x2005_plus under the fork's audio order; unverified under upstream's (see Adopt 1 caveat). Same pin as ours, so it should apply as-is. Side effect: a manual state load or rewind after a save restores output state too (benign: avoids the same click) | none, but a patched core needs the patched source tarball (GPL-2.0 parts) | Belongs **upstream at libretro/snes9x2005**, not slot. Offering it there needs the maintainer's ok (public action) |
| Run-ahead audio comparison tool | 20e2eee (`crates/slot-retro/examples/runahead_audio.rs`, 95 lines) | Runs N frames straight and through save/frame/load, compares samples exactly; exit 1 on any difference | Missing | Cheap proof for each of our 4 NES/SNES cores before enabling run-ahead on any | none | Possibly generic (works for any core); low priority |
| Latency trace, 10 ms polling, late button read, display-locked worker | [598e5e3](https://github.com/savethefails/ezGBA-640x480/commit/598e5e3), [5f57568](https://github.com/savethefails/ezGBA-640x480/commit/5f57568), [c67a44e](https://github.com/savethefails/ezGBA-640x480/commit/c67a44e), [5f627cd](https://github.com/savethefails/ezGBA-640x480/commit/5f627cd) | Generic latency work | Superseded: upstream dea6756 ("faster polling, late pacing and a clock lock") and v1.7.0's latency lines that DEVICE-GATE.md already uses | n/a | none | already upstream |

## 4. Video, canvas, hi-res

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| Frames at the core's own size | [f2fe72e](https://github.com/savethefails/ezGBA-640x480/commit/f2fe72e) (20 files) | Drops the 240x160 buffer; texture reallocated on size change; per-console `Fit` | We use Option A: fixed 360x240 canvas, hi-res blended 2:1 (ADR 0004, patch 0004). Their design is our deferred Option B (issue 36) | Theirs keeps true 512x448 hi-res detail; ours is a much smaller patch and keeps GBA byte-identical | Conflicts with ADR 0004 unless issue 36 is picked up | Only if upstream itself wants variable frames (it was 279 commits ago; upstream has not taken it) |
| SNES at 4:3, no LCD grid | 10316a7 | 256x224 and 512x448 both placed at 4:3 | Ours: Stretch (fills 720x480 at 3:2, crops both axes, ADR 0022/0046) or Actual (2x of the canvas, 8:7 square pixels) via SELECT+X | Different defaults. 4:3 is the "TV aspect" many players want; we have no 4:3 mode | A third mode would extend ADR 0007's two-way toggle | no |
| Whole-multiple rows ("Sharp") and SNES Picture setting | [3787664](https://github.com/savethefails/ezGBA-640x480/commit/3787664), [6c5504c](https://github.com/savethefails/ezGBA-640x480/commit/6c5504c) | Full width, rows at the largest whole multiple (224 at 2x and 448 at 1x = 448 rows, 16 px bars) so one-pixel lines never thin | Partly: our Actual is already 2x rows (448); Stretch is 2.14 rows per line, and our Sharp, Line and Pixel shaders (ADRs 0026, 0036) soften the thinning instead | On 720x480 their "full width, 448 rows" would be a 720x448 stretch; a 4:3 at 448 rows would be ~597x448. Either is a new mode | Adds a picture mode (ADR 0007, 0022) | no |
| 720x720 panel | [a998035](https://github.com/savethefails/ezGBA-640x480/commit/a998035) | SNES at 8:7 across 720 wide on a square panel | No square-panel support | Device we do not target (ADR 0021: RG34XXSP) | none | Generic; zognic/slot has a square-panel branch heading upstream |

## 5. Save handling

No SNES-specific save change found. SRAM goes through the generic libretro path; states are filed per core
(b2685af notes snes9x2005 states are kept apart from snes9x's, which slot already does per core).
b68bed9 / 45fd8ff are generic persist and Game Boy fixes. Nothing to take.

## 6. Shelf and cart art

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| SNES Game Pak drawing, shelf mark | 10316a7 | Own SVG cart, ridges, label panel, d-pad/diamond mark | Have: patches 0012, 0013, procedural renderer (ADR 0042), NES/Famicom/SNES/SFC variants (ADR 0006) | Ours covers four shells and region pick; theirs one | none | no |
| Two SNES moulds by header region, then dropped | [81c50d6](https://github.com/savethefails/ezGBA-640x480/commit/81c50d6), [3564816](https://github.com/savethefails/ezGBA-640x480/commit/3564816), [79fcc12](https://github.com/savethefails/ezGBA-640x480/commit/79fcc12) | NA boxy and SFC rounded by region; later NA only. Killer Instinct black | Have: region pick (patch 0013, probe of region byte at 0x7fc0/0xffc0), `RETRO_BLACK` for Killer Instinct (patch 0012), `cart_shell.txt` override | Ours equal or better | none | no |
| Generated SNES label fallback | 3564816 | No art: draws a black label with title, badge, purple arrow, publisher bar and "SUPER NINTENDO" in red | Ours: Logo Only on a generated ground (ADR 0014) | Theirs imitates Nintendo's label trade dress | Conflicts with ADR 0014's fallback; trade-dress risk | no |
| SNES header title | `slot-store/src/snes.rs` | LoROM/HiROM by checksum complement, copier header skip, ASCII title | Have, plus region (patch 0005 `PROBES`) | Ours better | none | no |
| One shelf for all consoles | [1e12620](https://github.com/savethefails/ezGBA-640x480/commit/1e12620) | Single name-sorted shelf | Upstream v1.7.0 has per-platform shelves and shelf memory (ADR 0039) | Product choice for a kids' fork | none | no |
| Cart refactors | [c3ca97b](https://github.com/savethefails/ezGBA-640x480/commit/c3ca97b) | One mould table per shape | Our retro renderer is already separate (ADR 0042) | n/a | none | no |

## 7. Two-player SNES over the emulated link

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|
| SNES link, pad 1 host, pad 2 joiner | ac6f2e4 (+ [9ecbf26](https://github.com/savethefails/ezGBA-640x480/commit/9ecbf26) BIOS check only in GBA link mode) | Uses the existing cable route (`run_frame_linked(p1, p2)`, lockstep from the host's state) for SNES on snes9x or snes9x2005; ~30 lines of app.rs plus a real-core test `snes_cable.rs` | None. PLAN.md records "link cable stays GBA only by design" (app.rs:2701) | v1.7.0 upstream already has `run_frame_linked` and `cable.rs`, so the port is small. Real 2P SNES on two devices is a big feature for SNES users | Contradicts the PLAN decision; needs an ADR. Also check upstream's `link_state::same_bios` on a non-GBA state | The two-pad port declaration and "BIOS check only in GBA link mode" are generic; the SNES gate is ours |

## Adopt (ranked)

1. **SNES run-ahead on snes9x2005_plus + the audio patch.** Add `(Snes9x2005Plus, Snes) => frames` to
   `runahead_for`, apply `runahead-audio.patch` in `cores/snes9x2005_plus` (add a patch step to
   `cores/lib.sh`, ship the patched source tarball, record the patch sha256 in the stamp). Value: high, one
   frame less input lag on the faster SNES core, crackle-free. Effort M. Risk: medium (SA-1 or SuperFX on
   2005 may not fit the budget; needs a device gate run). Licence: patch is snes9x non-commercial + GPL-2.0;
   credit savethefails (20e2eee) in LICENSING.md and the patch header. Needs an ADR.
   **Caveat, audio order:** the 826-missing-samples proof was measured under the fork's order (play the real
   frame's audio). Upstream v1.7.0 `RunAhead::run` (emu.rs:1155) does the reverse: it discards the real
   frame's audio (the one right after each load) and plays the ahead frame's. That discarded frame may soak up
   most of the reset, so the patch is proven for the fork and **unverified for v1.7.0**. First step: run the
   comparison example rewritten to `RunAhead::run`'s order (or upstream's run-ahead test against the real
   vendored core), unpatched. If clean, the patch drops to optional and effort falls to S.
   Checked: the `(Mgba, Gba)`-only gate in `runahead_for` is upstream's (upstream app.rs:4455), not ours, so
   enabling SNES is a new hunk on an upstream function (record in the touch-point map, ADR 0024).
   Checked: `RunAhead.video` copies `video_xrgb8888()`, which in our tree is already the 360x240 canvas
   with the hi-res 2:1 blend (patches 0004/0006 size `Frames` from `core.canvas()`), so no new video path.
2. **Run-ahead budget guard (12 ms x 8 strikes).** Value: high once item 1 lands (stops slowdown on heavy
   chips). Effort S. Risk: low. Generic: send as a PR to BrandonKowalski/slot, carry it in our patch set
   until it lands. Credit: GPL-3.0 by savethefails (b240d57).
3. **Run-ahead audio comparison example.** Run it against snes9x, snes9x2005_plus, fceumm and nestopia
   before enabling run-ahead anywhere (it also answers whether NES run-ahead is safe). Value: medium
   (proof, not a feature). Effort S. Risk: none (never ships). Credit: GPL-3.0 (20e2eee).
4. **Two-player SNES link** (port-2 declaration + SNES gate + BIOS check scoped to GBA). Value: high for
   two-device owners. Effort M (app.rs touch points, ADR, real-core test like `snes_cable.rs`, device test
   with two units). Risk: medium (lockstep desync on snes9x is untested by us). Reverses the PLAN "GBA only"
   decision. Port declaration and BIOS-scope fix go upstream. Credit: GPL-3.0 (ac6f2e4, 9ecbf26).
5. **A 4:3 SNES picture (rows at a whole multiple).** Value: medium (correct TV aspect, no thinned lines).
   Effort M. Risk: low, but it adds a third mode to the SELECT+X toggle (amend ADR 0007/0022). Idea only;
   their code is built on Option B frames and the 640 panel, so write it fresh. Credit as inspiration.

## Skip

- **Immediate SELECT (b420419):** upstream already tried and reverted it (c2a27a6); breaks ADR 0007 and
  T22 because every SNES chord would leak SELECT into the game.
- **snes9x2005_plus as the SNES default (b2685af):** contradicts ADR 0002; revisit only if item 1 proves
  out on the device gate. The picker already lets a user pick it per game.
- **SNES Emulator row (78438fe):** per-game picker covers it; ADR 0023/0043 keep quick-menu rows minimal.
- **Frames at own size (f2fe72e):** that is our deferred issue 36 (Option B); a 20-file rework of a base
  279 commits behind. Use it as a design reference if issue 36 is ever picked up.
- **Generated SNES label (3564816):** imitates Nintendo trade dress; ADR 0014 uses Logo Only.
- **Cart drawings, two moulds, header parser (10316a7, 81c50d6, 79fcc12):** ours already does more.
- **Colour Depth, 720x720 panel, one shelf, PICO-8, latency trace and pacing:** not SNES specific,
  superseded upstream (dea6756), or a product choice for their kids' build.
