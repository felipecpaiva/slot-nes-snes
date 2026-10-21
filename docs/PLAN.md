# slot NES/SNES: patch set over pinned slot main 1b20432, phased build plan (RG34XXSP reference)

> Built against slot v1.6.0 (`9d7c795`), rebased onto v1.7.0 (`34ac380`) on 2026-10-15 (ADR 0038) and
> onto upstream main `1b20432` (no 1.8.0 tag yet) on 2026-10-18 (ADR 0083).
> Version numbers below follow `SLOT_PIN`; the phase history is unchanged.

## Plan changelog

Each row is one editing round. Read only the rows you haven't seen.

| Round | Sections touched | What changed |
|---|---|---|
| 1 (initial) | All sections | First cut. Five phases: NES boot slice, SNES, parity, real cart art with variants, release/CI/rebase. Bezel decided. Cart art expanded to full variant parity. |
| 2 | Approach, Phased rollout, Signature impact, Critical files, Test plan, Gotchas, Open questions, Evaluation | Review fixes: Host side-state, pair-relative picker, macOS-primary CI, deterministic harness, licensing tarball |
| 3 | Open questions | User resolved OQ2 (no quick menu shader rows) and OQ4 (SELECT+X SNES video mode) |
| 4 | Phased rollout | Phase 7 (Sega on Genesis Plus GX, patches 0024 to 0028) added |
| 5 | Spec, Phased rollout | PS1 brought into scope as Phase 8 (ADRs 0063 to 0069, issues 56 to 68), planned, not shipped; PAL pacing moved from deferred to issue 66 |
| 6 | Spec (Out of scope), Phase 6+ | PAL 50 Hz pacing leaves the out-of-scope and deferred lists: issue 66, patch 0043, ADR 0071 |
| 7 | Header, Phase 8 | PS1 shipped (patches 0034 to 0041, device gate rows in docs/DEVICE-GATE.md); base is upstream main 1b20432 (ADR 0083) |
| 8 | Spec (Who it's NOT for), Phase 11 | WonderSwan and Color in the patch set (patches 0064 to 0069, ADR 0092), device gate (issue 99) pending |
| 9 | Spec (Who it's NOT for), Phase 15 | Sega 32X in the patch set on PicoDrive (patches 0090 to 0097, ADR 0096), device gate (issue 152) pending |
| 10 | Spec (Who it's NOT for), Phase 16 | Virtual Boy in the patch set on Beetle VB (patches 0102 to 0109, ADR 0097), device gate (issue 182) pending |
| 11 | Spec (Who it's NOT for), Phase 17 | Neo Geo, CPS1 and CPS2 in the patch set on FinalBurn Neo (patches 0110 to 0116, ADR 0099), the zip as the romset on those three shelves only, device gate (issue 193) pending |
| 12 | Spec (Who it's NOT for, Out of scope), Phase 18, Phase 6+ | Famicom Disk System in the patch set on the shipped fceumm (patches 0120 to 0126, ADR 0101), out of the deferred list, device gate (issue 202) pending |
| 13 | Spec (Who it's NOT for), Phase 19 | PICO-8 carts in the patch set on FAKE-08 (patches 0127 to 0130, ADR 0102), no states, device gate (issue 208) pending |
| 14 | Spec (Who it's NOT for), Phase 20 | PC Engine SuperGrafx in the patch set on Beetle SuperGrafx (patches 0131 to 0134, ADR 0103), device gate (issue 214) pending |
| 15 | Spec (Who it's NOT for), Phase 21 | PC Engine CD in the patch set on the shipped Beetle PCE Fast built with CHD (patches 0135 to 0138, ADR 0104), device gate (issue 221) pending |
| 16 | Spec (Who it's NOT for), Phase 22 | Sega CD / Mega-CD in the patch set on the shipped Genesis Plus GX (patches 0139 to 0146, ADR 0105), device gate (issue 232) pending |
| 17 | Spec (Who it's NOT for), Phase 23 | Neo Geo CD in the patch set on NeoCD (patches 0147 to 0150, ADR 0106), device gate (issue 238) pending |

From now on, every edit round adds one row above and posts the same diff in chat.

## Context

The request was a plan "using all the details we gathered", with the work broken into phases, "adding the tests and everything else using same approach slot did on baseOs (we will use my rg35xxsp as a reference / test device."

Slot's own approach has three parts:
- it pins an upstream (mGBA at `MGBA_COMMIT`, gpSP at `GPSP_COMMIT`);
- it applies `cores/<core>/*.patch` in glob order, writes a `.meta` stamp and ships GPL corresponding source in `System/licenses/`;
- it builds natively for aarch64 in `rust:1-bullseye` and ships a zip whose `System/` replaces the previous one, which BaseOS boots through `System/launch_frontend.sh`.

This repo does the same thing one level up: it pins slot itself and patches it.

Binding constraints:
- **Upstreaming is closed.** The owner wrote on slot#30: *"slot will not be adding support for more systems."*
- **Bezel (decided by the user during planning).** NES and SNES keep the GBA SP bezel on the RG35XXSP exactly like GBA, with the same 640x427 window.
- **Cart art (decided by the user during planning).** It must match slot's nostalgia depth, including real cartridge variants. The user's words: *"A lot of the experience around this project is based on some of the nostalgia. That's why you have all of those options on the cards for the GBA, GBC, and the GB. I would like to have the same experience for the NES and SNES because there are different versions of the cartridges as well so it should account for those."*

Conflict found in the audit:
- RESEARCH.md says to "edit asserts" in `slot-store/tests/platform.rs` and `tests/core.rs`.
- The confirmed bar (QUALITY-BAR.md) says "every upstream test passes, unmodified".

This plan sides with the bar. Upstream constants, struct field lists and in-source test helpers stay as they are, and new parallel constants and side structs are added instead. Two places cannot hold literally, and both go to Open Questions with defaults:
- the quick menu SCREEN page, which upstream tests pin to exactly four rows;
- SNES video mode, which upstream reaches only through L1/R1.

## Spec

- **What it does:** adds `Platform::Nes` and `Platform::Snes` to slot v1.7.0 as first-class shelves:
  - `Games/NES`, `Games/SNES` and the matching `Labels/`, `Saves/` and `States/` folders;
  - a per-platform core pair in the picker: fceumm/nestopia for NES, snes9x/snes9x2005_plus for SNES;
  - per-platform shaders;
  - real NES/Famicom and SNES/Super Famicom cart shapes with colour and finish variants.

  It ships as `patches/*.patch` over a pinned slot commit, built into `slot-nes-snes-vX-h700.zip` laid out exactly like slot's release zip. A GPL-3 corresponding-source tarball goes with every release.
- **Who it's for:** slot users on Anbernic H700 handhelds who want NES and SNES with slot's feel. The reference and test device is the user's RG34XXSP.
- **Who it's NOT for:**
  - upstream slot (no PR, no issues filed there);
  - owners of non-H700 devices (no builds, no testing);
  - people who want RetroArch breadth: netplay, cheats, per-game overrides, more systems, zip ROMs. Systems are added one at a time by ADR: Sega (Phase 7), PlayStation (Phase 8, ADR 0063), TurboGrafx-16 (Phase 10, ADR 0091), WonderSwan (Phase 11, ADR 0092), Atari Lynx (Phase 12, ADR 0093), NeoGeo Pocket (Phase 9, ADR 0090), Sega 32X (Phase 15, ADR 0096), Atari 2600 and 7800 (Phase 14, ADR 0095), Virtual Boy (Phase 16, ADR 0097), Neo Geo, CPS1 and CPS2 (Phase 17, ADR 0099, the only shelves where the zip is the romset), the Famicom Disk System (Phase 18, ADR 0101), PICO-8 carts (Phase 19, ADR 0102, on FAKE-08; PICO-8 itself is never shipped), the PC Engine SuperGrafx (Phase 20, ADR 0103), PC Engine CD discs (Phase 21, ADR 0104; the System Card is never shipped) Sega CD (Phase 22, ADR 0105) and Neo Geo CD discs (Phase 23, ADR 0106, on NeoCD; the BIOS is never shipped) so far;
  - anyone redistributing commercially (snes9x is licensed for non-commercial use only).
- **Success looks like:**
  1. **GBA, GB and GBC are byte-identical to unpatched slot v1.7.0.** A blind frame-hash compare of the same legal test carts and scripted inputs matches 100%, after a control run proves the harness is deterministic. All ~1,400 upstream tests pass with zero hunks in upstream test code, meaning both `crates/*/tests/` and the `#[cfg(test)]` modules of every patched source file. GBA `core_bench` median frame cost is within 2% (5 repeats, same ROMs).
  2. **Every parity row works on NES and SNES:** carousel, letter jump, cart art and labels, core picker, insert and eject, resume on boot, saves and autosave, save states and polaroids, rewind, fast-forward, turbo, shaders, video mode, quick menu, settings, volume, sleep and lid-close save.
  3. **Frontend cost stays inside the GBA budget.** Pixel conversion, publish and upload per frame on NES/SNES stay within the GBA budget measured on the same host.
  4. **Manual device gate on the RG34XXSP:** full speed and zero audio underruns, read from `SLOT_TRACE`/`slot.log` over 10 minutes of play each. The ROMs are dumps the user owns and are never committed.
     - SNES: Star Fox, Yoshi's Island, Kirby Super Star, Super Mario RPG, Seiken Densetsu 3.
     - NES: Super Mario Bros. 3 (MMC3), Kirby's Adventure (MMC3, heavy scenes), Castlevania III (MMC5), Akumajou Densetsu (VRC6 expansion audio), Mega Man 2 (MMC1), Battletoads (AxROM, timing-sensitive).
  5. **Install and update work like slot.** A user installs by unzipping, copying the top folder's contents to the SD root and booting. An update deletes `System/` and copies the new one, and `Config/` survives.
- **Out of scope:**
  - upstreaming;
  - zip ROMs;
  - the stem-key collision in `selected_core.txt`, `video_mode.txt` and `cart_shell.txt` (documented only);
  - Option B variable frame size and true hi-res SNES detail;
  - colour correction on NES/SNES;
  - teaching the external Cart Studio the new outline words.

## Quality bar

- **Goal type:** code (emulator frontend patch set), with a visual half for cart art.
- **Bar:** unpatched slot v1.7.0 at `34ac380` (v1.6.0 at `9d7c795` until 2026-10-15) (github.com/BrandonKowalski/slot), built from the same tarball the patch set uses, with the same shared `vendor/` cores. For cart art, the depth bar is slot's own GB/GBC/GBA cart system in `crates/slot-ui`.
- **Measurable half:**
  - frame-hash equality on GBA/GB/GBC (`harness/frame_dump`, control run first);
  - the upstream suite passes with upstream test code unmodified (`scripts/check-upstream-tests.sh`);
  - `core_bench` GBA frame cost within 2%;
  - NES/SNES frontend cost at or below the GBA budget;
  - the parity checklist 100% green through T1 to T47.
- **Critic:** a separate reviewer who runs the real build (`task check` on macOS) and the blind compare. Cart art is judged against reference photos of real carts, side by side with labels stripped. The device gate is manual (the user on the RG34XXSP), not the critic's call.
- **Bar fetch method:** `task upstream:build` builds `build/slot-upstream` from the pinned tarball with no patches. The critic diffs `harness/frame_dump` output from both trees (both linked to the same `vendor/`) and runs the upstream suite on the patched tree. Cart reference images live in `docs/cart-art/refs/` with source URLs. Gauntlet prompt: `docs/gauntlet-prompt.md`.

## Approach

- **Patch set rendered from a working branch.**
  - Code is written in a working clone `work/slot` (gitignored) on branch `nes-snes`, cut from the pinned commit, one commit per concern.
  - `scripts/export-patches.sh` runs `git format-patch --binary` into `patches/NNNN-<concern>.patch`.
  - The build applies them in glob order onto the fetched tarball, mirroring `cores/mgba/build.sh`: `git apply`, then a `.meta` stamp with `slot_commit=`, `source=` and `patch=<f> sha256:<hex>`.
  - Rebase is `git rebase --onto <new-tag>` in the working clone, re-export, run the suite, bump the pin.
  - Rejected: a long-lived fork (rebase cost with no stamp or provenance, per EVAL.md) and the dispatcher shim (240x160 squeeze, games on the GBA shelf).
- **Upstream test code stays literally unmodified.** Nothing it touches changes shape:
  - `Platform::ALL` (3), `Core::ALL` (2), `QuickRow::SCREEN` (4), `CorePicker::open(seat, now)` and the `Host` struct field list (`libretro.rs:25-41`) are left alone. That last one matters because the in-source test helper `host_with()` at `libretro.rs:701-718` builds `Host` with every field listed.
  - New `Platform::SHELVES` and `Core::EVERY` are added. Only the source consumers switch over: `scan.rs:65`, `app.rs:365`, `slot_state.rs:240` and `frontend.rs:602,606`.
  - New libretro state (canvas, av change, av enable) lives in a side struct `HostExtra`, owned by `LibretroCore`, with its own thread-local pointer bound next to every `Active::bind` call. `Active::bind`'s signature is unchanged.
  - When `HostExtra` is unbound (the in-source tests), `video_refresh` and `environment` behave exactly like upstream.
  - New test helpers go in new files only.
- **Video: Option A, a fixed canvas per core.**
  - Mgba and Gpsp keep 240x160 at SCALE 3. Fceumm, Nestopia, Snes9x and Snes9x2005Plus use 360x240, which is 2x into the same 720x480 logical space.
  - Canvas truth is `Core::canvas()`, so `open_core`'s signature does not change.
  - The new public `Compositor::set_game_canvas(w, h)` (in `fbo.rs`, which owns the private `GamePass`) is called every frame from `Frontend::compose` and does nothing when the canvas is unchanged, so every core, GBA included, is covered. GBA always gets (240, 160).
  - Byte-identity is proven, not assumed, by a harness leg that runs NES, ejects, plays GBA, and compares the result to a GBA-only run.
  - On the RG35XXSP the canvas maps into the same 640x427 window and bezel as GBA (decided). NES shows about 455x427 and SNES about 455x398, both non-integer, the same treatment GBA gets.
  - Rejected: Option B (variable frames up to 512x480, a much bigger patch).
- **Policy lives in new files as `Platform`/`Core` methods; `app.rs` hunks are one token.**
  - New files: `slot-store/src/platform_policy.rs`, `core_policy.rs` and `slot-retro/src/canvas.rs` (second `impl` blocks).
  - Methods: `owns_shoulders`, `turbo_mode`, `shader_choices`, `has_gb_palettes`, `has_colour_correction`, `picker_cores`, `option_prefix`, `canvas`.
  - Enums are append-only.
  - New `slot.state` keys are written by a second `push_str` after the upstream `format!` (`slot_state.rs:130`) and parsed with `unwrap_or(fallback)`, never `?`.
- **Core picker is pair-relative.**
  - Socket faces and chip faces are both built from `Core::EVERY` (6 each) and indexed by `core.index()`. `socket_face` inks the core name (`board.rs:282-293`), so a NES picker must show FCEUmm/Nestopia sockets.
  - The draw loop at `app.rs:2243-2244` walks the seated platform's `(left, right)` pair, with position 0/1 into `SOCKET_U` (still `[f32; 2]`, `board.rs:164`).
  - `core_picker.rs:115-116` (Left/Right), `:151` (`rightward = hop.from == pair.0`) and `:163` (`across = pos(seat)`) become pair-relative.
  - The upstream `render_shelf.rs:49-62` builds 2-entry face vectors from `Core::ALL`, which still index correctly for the GBA pair (indices 0 and 1), so it stays green.
- **Cart art in two steps.**
  - Phase 1 ships a placeholder: the GBA Spec with flat NES grey (`#8c8c8c`) and, from Phase 2, SNES grey (`#b4b4bc`).
  - Phase 4 replaces it with real silhouettes, variants, verified colour tables, region auto-pick and the extended `cart_shell.txt` grammar. A research sub-step comes first and verifies every colour against a cited reference.
- **CI is macOS-primary.** Slot's host core tasks are macOS-only: `taskfile.yml:83-127` asserts `Mach-O` and uses the apple buildbot. slot-retro tests hardcode `vendor/mgba_libretro.dylib` (e.g. `slot-retro/tests/rumble.rs:9`). `HeadlessSurface` is `#[cfg(target_os = "macos")]` (`slot-gfx/src/lib.rs:7,23`). So:
  - a `macos-14` job runs every test, the harness and the benches;
  - a Linux arm job only builds device artefacts, the zip and the ship checks.

### Build steps → decisions → defaults

| Step | Key decision | Default chosen | When to override |
|---|---|---|---|
| 1. Repo infra | How to get slot source | Tarball of pinned commit `9d7c795` (file `SLOT_PIN`: tag, commit, tarball sha256), `git init` + `git apply` per patch | Git clone if the tarball endpoint changes |
| 2. Working clone | Where code is written | `work/slot` branch `nes-snes`; `scripts/export-patches.sh` regenerates `patches/` | Never hand-edit `.patch` files |
| 3. Shared cores | Where host and device cores live | One repo-level `vendor/`; `build/slot/vendor` and `build/slot-upstream/vendor` are symlinks to it | none |
| 4. Docker wrapper | Device builds | Own `scripts/device-sh.sh`, a copy of slot's internal `device:sh` (`taskfile.yml:278`, which is `internal: true` and cannot be called from outside) | Native when already Linux aarch64 |
| 5. Step-0 patch | Silent fallthroughs | Exhaustive `match` via `Platform` methods; behaviour-identical for GBA/GB/GBC | none |
| 6. Platform variants | Constants | Append `Nes` (Phase 1), `Snes` (Phase 2); `SHELVES` grows per phase; `ALL` unchanged | User prefers amending 3 asserts (OQ1) |
| 7. Extensions | File types | NES `nes`; SNES `sfc`, `smc` (copier header when `len % 1024 == 512`) | Add `fig`/`swc` on request |
| 8. Core variants | Naming | `Fceumm`, `Nestopia`, `Snes9x`, `Snes9x2005Plus`; `as_str` = dylib stem; `text` = "FCEUmm", "Nestopia", "Snes9x", "Snes9x 2005+" | Fix the build if an output name differs |
| 9. Device core builds | Make flags | `make platform=unix CFLAGS/CXXFLAGS=-mcpu=cortex-a53`; fceumm `-f Makefile.libretro`; nestopia and snes9x in `libretro/`; snes9x2005 with `USE_BLARGG_APU=1` | Never `platform=arm64` (yields `.dll`) |
| 10. Host core builds | Pinned or nightly | NES/SNES host dylibs built from the same pinned commits with `platform=osx`; mgba via slot's `core:mgba:host`; gpsp via slot's buildbot fetch, with the dylib sha256 recorded as `gpsp_host_sha256_<arch>` in `SLOT_PIN` (one key per architecture, arm64 now, x86_64 added by whoever first builds there) and `task core:host` failing if it differs | Buildbot fallback if a core will not build on macOS, recording date and sha256 in `.meta` |
| 11. Canvas | Size | 360x240 for NES/SNES cores, 240x160 for Mgba/Gpsp | none in v1 |
| 12. Hi-res | 512-wide / 448-tall frames | Average 2:1 horizontally when `width > 360` and vertically when `height > 240` | Option B later |
| 13. Pixel format | RGB565 path | Keep per-pixel conversion; measure first; add a 64K-entry LUT only if NES/SNES frontend cost exceeds budget (bit-identical, so gpSP stays identical) | Measured overrun |
| 14. Env calls | Which to add | `SET_GEOMETRY` true; `SET_SYSTEM_AV_INFO` stores av in `HostExtra`, the emu rebuilds the resampler; `GET_AUDIO_VIDEO_ENABLE` returns 3, with the video bit clear on FF-skipped frames. All return false when `HostExtra` is unbound | none |
| 15. Turbo | SNES X/Y | `TurboMode::{Turbo, Off, PassThrough}`; SNES is PassThrough always; NES keeps slot's X/Y turbo; the Turbo quick row is a documented no-op on SNES | none |
| 16. Shoulders | L1/R1 in game | GBA game; GB/GBC slot; NES slot (picture toggle like GB); SNES game | none |
| 17. SNES video mode | How to toggle Stretch/Actual | New SELECT+X chord (X is unused in `gesture.rs:409-424` chords), acting on SNES only | OQ4 |
| 18. Core picker | Pair per platform | `CorePicker::open_pair(seat, pair, now)`; `open` delegates with (Mgba, Gpsp); faces from `Core::EVERY`; positions 0/1 | none |
| 19. Shaders | NES/SNES list and storage | Phase 1: NES shares `shader_gb` and `Shader::GB` (provisional). Phase 3: `Shader::RETRO = [Off, Grid, Dot]` with keys `shader_nes`, `shader_snes`, default Off, changed via SELECT+B/A | OQ2 decides quick menu rows |
| 20. Colour toggle on NES/SNES | SELECT+Y | Suppressed (no state change, no toast) when `has_colour_correction()` is false | none |
| 21. Thumbnails | Crop | No crop: the full 360x240 canvas, same 3:2 aspect as GBA's 240x160, so the polaroid layout is unchanged; `emu.rs:884` calls `png_sized` with `core.canvas()` | Crop to `picture()` if the borders look wrong on device |
| 22. Cart art v1 | Phase 1 shape | GBA Spec + flat grey per platform | none; replaced in Phase 4 |
| 23. Cart variants | Outlines | NES: `nes` (front-loader), `famicom`; SNES: `snes` (NTSC-US ridged), `sfc` (Super Famicom/PAL rounded); `auto` uses the region pick | FDS: one yellow Disk Card shell (ADR 0101) |
| 24. Region auto-pick | Source | SNES header region byte (offset verified in research; candidates 0x7FD9 LoROM / 0xFFD9 HiROM, +0x200 with copier header); NES No-Intro tags: `(Japan)` gives Famicom, `(USA)`/`(Europe)` give NES, default NES | User override line in `cart_shell.txt` |
| 25. Colour tables | Content | Only research-verified entries, with a cited source per row | none |
| 26. Harness | Determinism | Fresh temp copy of a pre-warmed root per run, driven emu (`set_driven`), settle-point hashing, mandatory control run | none |
| 27. Licensing | GPL-3 source | `slot-nes-snes-src-<tag>.tar.gz` (git archive of patched `build/slot` + this repo) attached to the release and copied into `System/licenses/`; `LICENSING.md` | none |
| 28. Release | Name | Tag `v1.7.0-ns.N`, zip `slot-nes-snes-v1.7.0-ns.N-h700.zip` with a top folder of the same name | none |
| 29. CI | Split | `macos-14` job (tests, harness, benches) is required; Linux arm job (device build, zip, ship checks); `release.yml` needs both | none |

## Working process

- Each phase deliverable is built, then checked by a separate reviewer who runs `task check` on macOS against the quality bar and says pass or fail. Work loops until it passes.
- Binding decisions (bezel kept, unmodified-test strategy, HostExtra side struct, canvas per core, placeholder art in Phase 1, macOS-primary CI, SELECT+X for SNES video mode) are recorded as ADRs in `docs/adr/` (indexed in `docs/DECISIONS.md`) as they are confirmed.
- One project-level env flag, `SLOT_REQUIRE_CORES=1`, is read only by this repo's tests.
- Device-gate results per title (fps, underrun count, CPU governor) are recorded in `docs/DEVICE-GATE.md`.

## Edge cases by layer

| Layer | Failure mode | Handling |
|---|---|---|
| Patch infra | A patch fails `git apply` on a new slot release | `scripts/apply-patches.sh` stops at the first failure, prints the patch name and the rejected hunk, and exits non-zero. Fix by rebasing `nes-snes` in `work/slot` and re-exporting. Never `--reject` |
| Patch infra | Binary assets (lettering PNGs) dropped from a text patch | `git format-patch --binary`; `task patches:check` re-applies onto a clean tarball and diffs the tree against `work/slot` HEAD |
| Core build | `platform=arm64` yields `.dll`, so no `.so` exists | Each `cores/<c>/build.sh` asserts `file $out \| grep -q 'ELF 64-bit.*aarch64'` on device and `Mach-O` on host before writing `.meta` |
| Core build | snes9x2005_plus output name is not `snes9x2005_plus_libretro.*` | build.sh copies the produced file to the `dylib_name` form; T31 opens it via `Core::Snes9x2005Plus` |
| Core build | gpSP host dylib from the nightly buildbot changes between runs and shifts upstream test results | Its sha256 is recorded on first fetch; `task check` fails with "gpsp host dylib changed" until someone re-baselines on purpose |
| Tests | Real-core tests skip silently because the dylib is missing | `require_core(name)` panics under `SLOT_REQUIRE_CORES=1` (set in CI and `task check`); `task check` builds all 6 host cores first |
| Tests | Upstream suite passes vacuously because mgba/gpsp aren't in `vendor/` | `task check` runs slot's `core` tasks into the shared `vendor/` and asserts `vendor/mgba_libretro.dylib` and `vendor/gpsp_libretro.dylib` exist before `cargo test` |
| Tests | A patch touches an in-source `#[cfg(test)]` module (e.g. `host_with()` in `libretro.rs`) | `scripts/check-upstream-tests.sh` extracts every `#[cfg(test)] mod` block from each patched src file in both trees and fails if any differ |
| Harness | Two runs of the same tree differ (label cache, wall clock, background label check) | Fresh temp copy of the pre-warmed root per run, driven emu, wait for `rebuilding_labels() == false` plus settle, mandatory control run. Any frame that differs in the control run fails the harness itself before the cross-tree compare |
| Runtime | Third Core reaches `SOCKET_U[2]` (`app.rs:2244`) and panics, or a chip draws off board (`core_picker.rs:163`) | Draw loop walks the platform pair with positions 0/1; `across` and `rightward` are pair-relative; T23 renders a NES picker frame |
| Runtime | NES ROM with no selected core goes through `core_for` (`app.rs:2646`) and defaults to Mgba | Replaced with `core_for_platform(root, stem, cart.platform)` |
| Runtime | NES dylib missing on device: MockCore (240x160 buffer) is uploaded into a 360x240 game texture | `MockCore::sized(core.canvas())` in the fallback in `slot/src/core.rs`; the upload guard requires an exact length (`len == w*h*4`), so a mismatch is skipped rather than drawn wrong |
| Runtime | After NES, GBA plays with a stale 360x240 texture | `set_game_canvas` runs every frame from compose and does nothing when unchanged, GBA included; harness leg H3 (NES, eject, GBA) must equal the GBA-only run |
| Runtime | fceumm region option or snes9x changes av mid-game; the resampler stays at the old rate and audio drifts | `HostExtra.av_change`; the emu loop calls `take_av_change()` after `run_frame` and rebuilds `Resampler::new` |
| Input | SELECT+X chord added for SNES video mode changes GBA input behaviour | T22b runs the same SELECT+X sequence on a GBA cart in both trees and asserts identical core input masks |
| Input | SELECT+Y on SNES flips `colour_correction` and toasts with no effect | Guard in `app.rs` near 1445: when `!core.has_colour_correction()`, return true with no state change and no toast |
| State | Downgrade to unpatched slot with `cart_platform=nes` | Upstream `platform_value` returns None, so it boots to the shelf. T30b runs this on the upstream tree and asserts no panic. Documented |
| State | `slot.state` written by unpatched slot (no `shader_nes`) | Parsed with `unwrap_or`; T25 asserts Off defaults with the other fields intact |
| Cart art | `cart_shell.txt` line `nes ...` read by unpatched slot | Upstream `ShellChoice::parse` returns None on an unknown outline word (`cart_shell.rs:32-36`), so the line is dropped and the cart falls back to auto |
| Cart art | Cart Studio may drop `nes`/`snes` lines when rewriting `Labels/cart_shell.txt` | Unverified. Phase 4 round-trip check. Until then, document "keep NES/SNES overrides in `Config/cart_shell.txt`" |
| Device | SA-1 titles pop on the default governor | Measure first. If underruns appear, test the `interactive` governor (one muOS RG40XXH report) via a `launch_frontend.sh` line, gated on the measurement |
| Release | snes9x licence or GPL source tarball missing from the zip | Ship checks in `release.yml` fail the build |

## Phased rollout

### Phase 1: NES boots on the RG34XXSP from a release-shaped zip (blocking)

Smallest end-to-end slice: patch infra, `Platform::Nes`, fceumm, the 2x canvas, the Step-0 fixes and the GBA-unchanged harness. `Platform::Snes` does not exist until Phase 2.

Deliverables:
- [ ] `SLOT_PIN`, `taskfile.yml`, `scripts/fetch-slot.sh`, `scripts/apply-patches.sh` (glob order, `.meta` stamp), `scripts/export-patches.sh`, `scripts/device-sh.sh` (docker `rust:1-bullseye` wrapper), `scripts/check-upstream-tests.sh`, `.gitignore` (`work/`, `build/`, `vendor/`).
- [ ] `task upstream:build` → `build/slot-upstream`, `task build` → `build/slot`. Both `vendor/` dirs symlink to the repo `vendor/`.
- [ ] `task core:host`: slot's `core:mgba:host` and `core:gpsp:host` (gpSP sha recorded), plus `cores/fceumm/build.sh build ... vendor/fceumm_libretro.dylib` from the pinned commit with `platform=osx`.
- [ ] `patches/0001-step0-exhaustive-matches.patch` (behaviour-identical):
  - `scan.rs:21-32` `read_header`;
  - `slot/src/core.rs:128` `palette_for` (`has_gb_palettes()`);
  - `app.rs:855` (`owns_shoulders()`), `app.rs:2643` (`picker_cores().is_none()` early return), `app.rs:2646` (`core_for_platform`), `app.rs:2701` (upstream `!= Platform::Gba` kept, link cable stays GBA only);
  - `slot-store/src/core.rs:46` `Core::runs`;
  - `slot-ui/src/cart.rs` `gb_shell_of` Outline `_ =>`.

  Policy goes in new file `slot-store/src/platform_policy.rs`.
- [ ] `patches/0002-platform-nes.patch`:
  - `Platform::Nes` appended; `SHELVES = [Gba, Gb, Gbc, Nes]`; `scan.rs:65`, `app.rs:365`, `slot_state.rs:240` switched to it;
  - `dir_name` "NES", extensions `["nes"]`, `picture` (256, 240);
  - DIRS: `Games/NES`, `Labels/NES`, `Saves/NES`, `States/NES`;
  - title from the stem;
  - provisional arms: `app.rs:1044-1047` and `1407-1410` map Nes to `shader_gb` / `Shader::GB`;
  - placeholder cart arms in `shell.rs:92`, `cart.rs:91,157,164` (GBA Spec, `#8c8c8c` solid).
- [ ] `patches/0003-core-fceumm.patch`:
  - `Core::Fceumm` appended; `Core::EVERY`; `text` "FCEUmm";
  - `parse`, `runs`, `default_for(Nes) = Fceumm`;
  - `colour_option(Fceumm) = None` (`slot/src/core.rs:151`);
  - `option_prefix()`; `apply_core_options` sets `{prefix}_frameskip` only when the core declares it, and sets fceumm's overscan options so the full 256x240 is shown (key names taken from the T32 dump).
- [ ] `patches/0004-canvas.patch`:
  - `slot-retro/src/canvas.rs` (centring copy, RGB565 conversion, hi-res blend);
  - `HostExtra { canvas }` (issue 14 adds `av_change` and `av_enable`) owned by `LibretroCore`, with a thread-local `EXTRA` pointer set by a new `ExtraGuard` next to each `Active::bind` call site in `LibretroCore`. `Host` fields and `Active::bind` are unchanged. `Host.video` is sized `canvas.w * canvas.h * 4` at open, and when `EXTRA` is unbound `video_refresh` uses 240x160 exactly like upstream;
  - `LibretroCore::set_canvas`; `RetroCore::canvas()` defaults to `(GBA_W, GBA_H)`;
  - `emu.rs:151` `Frames::new` sized from `core.canvas()`; `emu.rs:884` uses `thumb::png_sized`;
  - `MockCore::sized`;
  - `GamePass::set_canvas` (re-allocates the texture, re-sets `u_src`, scale = `OUT_W / w`); upload guard becomes `len == w*h*4`; `whole_scale_source` uses the pass's canvas;
  - `fbo.rs` `Compositor::set_game_canvas`, exported in `slot-gfx/src/lib.rs`;
  - `frontend.rs` calls it every frame from `compose`, a no-op when unchanged;
  - `video_mode::source_rect` and `app.rs:930` `picture_rect` take the canvas.
- [ ] `cores/fceumm/build.sh` (mirrors `cores/gpsp/build.sh`: `stamp COMMIT` and `build COMMIT SRC_TGZ WORKDIR OUT`; ships the source tarball as GPL-2 corresponding source).
- [ ] `licenses/fceumm-GPL-2.0.txt`, with **licence gate:** fceumm's GPL-2.0-or-later status is verified from its `COPYING` and source headers at the pinned commit and recorded in `LICENSING.md`.
- [ ] `LICENSING.md`: slot GPL-3.0-or-later and this patch set, fceumm (verified), plus a placeholder section for snes9x/nestopia filled in later phases.
- [ ] `harness/` (macOS only):
  - `frame_dump.rs` is copied into `crates/slot/examples/` of both trees (not a patch).
  - `harness/roms/` holds legal homebrew or public-domain GBA/GB/GBC carts with their licence files. Candidates are the 240p Test Suite ports and Yerrick's GB/GBA homebrew; each licence is verified before commit.
  - `harness/root-template/` contains the ROMs, `Config/slot.state` with `clock_set=1` and no `cart=`, and a label cache pre-built by `task harness:warm`.
  - Legs:
    - H1: shelf, insert GBA, 600 driven frames with scripted input, quick menu, eject.
    - H2: the same for GB and GBC.
    - H3: insert NES, eject, then H1 (patched tree only, compared to the patched H1).
  - Each run copies the template into a fresh temp dir, boots with the emu in driven mode, and waits until `rebuilding_labels()` is false and 120 settle frames have passed. It hashes every core frame published plus composited frames at settle points (shelf idle, in-game steady, quick menu steady, after eject).
  - Scripts: `task harness:control` (same tree twice, must be 0 diffs) and `task harness:compare` (upstream vs patched, needs the control to pass first).
- [ ] `task bench:compare`: `core_bench` on `harness/roms/` carts for mgba and gpsp, both trees.
- [ ] `task dist:device` runs `task -d build/slot dist:device`, then copies `fceumm_libretro.so`, `.meta`, the source tarball and licences into `System/` and `System/licenses/`. `task zip` (runs `dist:device` and `src-tarball` first), `task src-tarball`, `task deploy:device` (adb push of the extra cores, chmod, reboot).
- [ ] New tests T1 to T14 and T45.

Acceptance:
- T1 to T14 and T45 green under `SLOT_REQUIRE_CORES=1` on macOS;
- `scripts/check-upstream-tests.sh` reports 0 changed test blocks;
- `harness:control` 0 diffs; `harness:compare` 0 diffs on H1/H2; H3 equals H1;
- `bench:compare` within 2%;
- device check passes.

Device check (RG34XXSP):
- unzip, copy to the SD root, boot;
- the NES shelf appears after GBC;
- Super Mario Bros. 3 and Mega Man 2 (user-owned dumps) are playable at full speed, save on eject and resume on reboot;
- a GBA cart still plays;
- `slot.log` shows `slot: core .../fceumm_libretro.so` and no mock-core line.

### Phase 2: SNES (blocking)

Deliverables:
- [ ] `patches/0005-platform-snes.patch`:
  - `Platform::Snes` appended to the enum and `SHELVES`; `dir_name` "SNES"; extensions `["sfc", "smc"]`; `picture` (256, 224); DIRS;
  - title from the SNES internal header: LoROM/HiROM probe by checksum complement, skipping the 512-byte copier header, with a fallback to the stem when the bytes are not printable ASCII (JIS X 0201 titles);
  - provisional shader and cart arms like NES (cart `#b4b4bc`).
- [ ] `Core::Snes9x` appended; `default_for(Snes) = Snes9x`; `text`, `colour_option` None.
- [ ] `patches/0006-libretro-env.patch`: `SET_GEOMETRY`, `SET_SYSTEM_AV_INFO`, `GET_AUDIO_VIDEO_ENABLE` through `HostExtra` (this patch adds its `av_change` and `av_enable` fields), plus trait `take_av_change()` (default None) and resampler rebuild in the emu loop. Unit tests go in new file `slot-retro/src/libretro/env_tests.rs` (one `#[cfg(test)] mod env_tests;` line in `libretro.rs`). Beyond the original text: `slot/src/av_rate.rs` (core and device rate maths, shared by both resampler sites), its `pub mod av_rate;` line in `slot/src/lib.rs`, and `slot/tests/nes_av.rs`, `slot/tests/emu_av_change.rs`. Known: the rebuild gives one click at the change, because `resample.rs` has no setter to keep the phase.
- [ ] Hi-res blend active for width > 360 and height > 240.
- [ ] `patches/0007-input.patch`:
  - `TurboMode` and `ButtonMask::apply(mode, frame)` delegating to the existing `turbo`/`without_turbo`;
  - `Shared.turbo` stays an AtomicBool, and a new `Shared.pass_through: AtomicBool` is checked first at `emu.rs:662`;
  - `owns_shoulders(Snes) = false`;
  - SELECT+X chord (`gesture.rs` chord bit 8192, `Action::VideoModeToggle`), handled only when the platform is Snes;
  - SELECT+Y suppressed when `!has_colour_correction()`.
- [ ] `cores/snes9x/build.sh`; `licenses/snes9x-LICENSE.txt` verbatim from the pinned source; `LICENSING.md` records the libretro plugin-boundary stance for snes9x (a separately loaded `.so` across the libretro C ABI, as shipped by RetroArch, ROCKNIX and Knulli) and the non-commercial terms; README and release notes carry the notice.
- [ ] New tests T15 to T22b.

Acceptance:
- T1 to T22b green;
- harness control and compare still 0 diffs;
- SNES frontend cost passes `eval-frontend-cost.sh`.

Device check:
- Super Mario World and Super Metroid at full speed;
- X, Y, L and R reach the game;
- a SELECT tap reaches the game; SELECT+R1 saves a state without sending R; SELECT+Y sends no Y and does nothing; SELECT+X toggles Stretch/Actual;
- first pass over the five gate titles, recorded as a `feedback` drawer. A gate failure here informs Phase 3 and does not block.

### Phase 3: full parity (blocking)

Deliverables:
- [ ] `patches/0008-core-picker-pairs.patch`:
  - `Core::Nestopia`, `Core::Snes9x2005Plus` appended;
  - `Platform::picker_cores()`: GBA (Mgba, Gpsp), NES (Fceumm, Nestopia), SNES (Snes9x, Snes9x2005Plus), GB/GBC None;
  - `CorePicker::open_pair`, with `open` delegating;
  - pair-relative `core_picker.rs:115,116,151,163`;
  - `frontend.rs:602,606` sockets and chips from `Core::EVERY`;
  - `app.rs:2243-2244` loop walks the pair: `SOCKET_U[pos]`, `sockets[core.index()]`.
- [ ] `cores/nestopia/build.sh` and `cores/snes9x2005_plus/build.sh`, host and device builds; licences. **Licence gate:** nestopia GPL-2.0-or-later verified at the pinned commit; snes9x2005 licence recorded in `LICENSING.md`.
- [ ] `patches/0009-shaders.patch`:
  - `Shader::RETRO`;
  - `SlotState.shader_nes` and `shader_snes` (default Off), written by a `push_str` after the line-130 `format!` and parsed with `unwrap_or`;
  - `app.rs:1044-1047` and `1407-1410` Nes/Snes arms move off `shader_gb`.
- [ ] FF: each core's frameskip key verified by T32 and set via `option_prefix()`; video-off on skipped frames through `GET_AUDIO_VIDEO_ENABLE`.
- [ ] Rewind: measure snes9x serialize time and size against the 2-frame cadence and the blocking `sync_channel(4)` (`rewind.rs:98`). Add a `Platform::rewind_every()` method (default 2) only if a measurement exceeds budget. The channel stays as it is.
- [ ] Polaroids: full 360x240 canvas thumbnails (no crop, decided).
- [ ] Quick menu works on NES/SNES with the existing rows; the Turbo row is a documented no-op on SNES. Shader rows follow OQ2.
- [ ] New tests T23 to T33.

Acceptance:
- every row of the AC coverage table ticked with a passing test;
- harness 0 diffs;
- all 6 cores open on the device.

Device check:
- picker swaps fceumm↔nestopia and snes9x↔snes9x2005_plus with the correct socket names, and the choice survives a reboot;
- rewind (L2) and FF (R2) on Super Mario RPG with zero underruns in `SLOT_TRACE`;
- lid close saves; sleep and wake; volume; brightness;
- all 11 titles recorded in `docs/DEVICE-GATE.md`.

### Phase 4: real NES and SNES cart art with variants (blocking for the v1 release)

Deliverables:
- [ ] **Research sub-step first (no code).** `docs/cart-art/VARIANTS.md` covers:
  - outline references: NES front-loader (US/EU), Famicom (short, wide), SNES NTSC-US (ridged top, grooved sides), Super Famicom/PAL (rounded);
  - the verified SNES region byte offset and the region code to variant map;
  - notable carts, each with a source URL: gold The Legend of Zelda and Zelda II (NES), black unlicensed Tengen NES carts, black Killer Instinct SNES cart, Famicom per-game colours.

  No row ships without a cited reference.
- [ ] Assets: `nes_cart.svg`, `nes_cart_detail.svg`, `famicom_cart.svg`, `famicom_cart_detail.svg`, `snes_cart.svg`, `snes_cart_detail.svg`, `sfc_cart.svg`, `sfc_cart_detail.svg`, `lettering_nes.png`, `lettering_snes.png` (generated by extending `slot-ui/examples/lettering.rs`).
- [ ] `patches/0010-cart-art.patch`:
  - `Shape::{Nes(NesShell), Snes(SnesShell)}` and their `spec()` arms (label box, mask, depth, detail, max_px, rim, board) in `cart.rs`;
  - `seated_box`/`cart_box` arms;
  - `silhouette.rs` silhouettes and lettering;
  - shelf shadows per new shape (the `frontend.rs:197-204` pattern, plus new setters);
  - label cache size per variant;
  - `shell.rs` tables `NES_TITLES`/`SNES_TITLES`, keyed by No-Intro title with tags stripped;
  - `shell_presets()` entries appended after the upstream ones.
- [ ] `patches/0011-cart-shell-grammar.patch`:
  - `Outline::{Nes, Famicom, Snes, Sfc}` appended, with parse and `to_value` words;
  - a word that doesn't match the cart's platform is treated as `auto`;
  - README section on hand-editing `Config/cart_shell.txt`.
- [ ] Region auto-pick: SNES from the header byte, NES from stem tags.
- [ ] Cart Studio round-trip check, recorded in `VARIANTS.md`.
- [ ] New tests T34 to T40.

Acceptance:
- T34 to T40 green;
- upstream slot-ui tests untouched and green;
- harness 0 diffs;
- `eval-cart-likeness.sh` and `eval-colour-sources.sh` pass.

Device check:
- a mixed shelf of NES, Famicom, SNES and SFC carts;
- insert and seat animations land in the correct boxes;
- gold Zelda shows gold;
- shadows sit under the carts.

### Cart labels for NES and SNES (Phase 4)

Carts show the real cartridge label art, never a screenshot (maintainer goal, 2026-10-12). slot's Cart Studio (github.com/BrandonKowalski/slot-cart-studio, GPL-3.0) covers GB, GBC and GBA only. The owner was asked on slot #64 whether NES and SNES should land as a PR to Cart Studio or a credited fork (issue 40, GitHub #48). A user-side script that fetches real labels at user time is the fallback (issue 41, GitHub #49). No Nintendo art is ever committed.

### Phase 5: release, CI, rebase automation and the final device gate (blocking for the v1 release)

Deliverables:
- [ ] `.github/workflows/test.yml`:
  - **Job `host` (`macos-14`, required):** Rust toolchain, brew cmake, `task core:host` (all 6 dylibs), `task check`. That covers the upstream suite with the shared vendor, the new tests under `SLOT_REQUIRE_CORES=1`, `check-upstream-tests.sh`, `harness:control`, `harness:compare`, the render tests and `bench:compare` (informational on CI runners).
  - **Job `device` (`ubuntu-24.04-arm`, container `rust:1-bullseye`):** `task dist:device`, `task zip`, `scripts/zip-check.sh`. It runs no host tests.
- [ ] `.github/workflows/release.yml` on tag: needs both jobs; builds the zip and `slot-nes-snes-src-<tag>.tar.gz`; ship checks; gh release with both assets.
  - Ship checks: `file | grep aarch64` for `slot` and all 6 cores; `test -x System/slot`; licence, `.meta` and patch files for every core; `System/licenses/slot-nes-snes-src-<tag>.tar.gz`; `System/licenses/snes9x-LICENSE.txt` and the snes9x2005 licence; `Games/NES` and `Games/SNES`.
  - Notes include the non-commercial snes9x notice and "do not report to slot's tracker".
- [x] `scripts/rebase.sh NEW_TAG`: fetch, `git rebase --onto` in `work/slot`, re-export, `task check`, update `SLOT_PIN`.
- [x] `docs/REBASE.md`: re-apply, full suite, harness against the new upstream, device smoke, bump the pin, tag `vNEW-ns.1`.
- [x] `task diffsurface`: per-file changed lines over upstream files, and the touch-point map `docs/UPSTREAM-TOUCHPOINTS.md` (one row per hunk with a reason). The 25-line `app.rs` target was replaced on 2026-10-13 by tracking every touch point (docs/DECISIONS.md).
- [ ] Final device gate on the RG34XXSP, using the zip downloaded from GitHub.
- [ ] New tests T41 to T44.

Acceptance:
- both CI jobs green on the tag;
- the zip installs on a clean SD card;
- the device gate passes on all 11 titles.

### Cross-platform performance evaluation (Phase 5, after all implementation)

One platform experience: every platform and core (GBA on mGBA and gpSP, GB, GBC, NES on fceumm and nestopia, SNES on snes9x and snes9x2005_plus) is measured on the RG34XXSP against unpatched slot playing GBA on mGBA, in the same session. Metrics: boot and insert to first frame, frame time median and p99, audio underruns, fast-forward speed, rewind cost, save and load state time, shelf and menu frame time, input latency. Results in `docs/PERFORMANCE.md`; every miss gets a follow-up issue. Tracked in `.github/issues/39-cross-platform-performance.md` (GitHub #45). Added at the maintainer's request on 2026-10-12.

### Phase 7: Sega (Game Gear, Master System, Mega Drive)

Tracking issue 50, children 51 to 53, ADRs 0050 to 0056, research in docs/research/sega-plan.md
and docs/cart-art/SEGA.md. One core, Genesis Plus GX, serves three new platforms, each its own
shelf (`Games/GG`, `Games/SMS`, `Games/MD`), with no core picker until a second core exists.

| Patch | Content |
|---|---|
| 0024-platform-gg | `Platform::Gg`, `Core::GenesisPlusGx`, `Core::canvas(platform)` (ADR 0050: Game Gear 240x160 at 3x), core options, env answers for cores slot did not ship, `TMR SEGA` region reader |
| 0025-platform-sms | `Platform::Sms`, 360x240 at 2x, left border hidden, START is Pause |
| 0026-platform-md | `Platform::Md`, SNES input policy (X, Y, Z, MODE), Stretch follows the live frame width (ADR 0052), header title and region |
| 0027-sega-shaders | Game Gear, Master System and Mega Drive rows on the Screen page and in game, retro shader list, `Config/sega_shaders.txt` (ADR 0051), named test sites (g) and (h) widened (ADR 0055) |
| 0028-sega-carts | Five generated bitmap shells, one box per platform (ADR 0056), region and size rules |
| 0029-sms-box-art | Master System and Sega Card wells made portrait for the whole front box, contain fit (ADR 0057) |
| 0030-need-fullpath | A `need_fullpath` core (gpSP, fceumm, Genesis Plus GX, later pcsx_rearmed) gets the path with data NULL and no ROM copy (ADR 0059), upstream-first, drop when upstream lands |

Done on the host: every test with `SLOT_REQUIRE_CORES=1`, real-core boot, canvas, save RAM round
trip, input, Stretch and shader tests per system. Open: the device gate (heavy Mega Drive titles,
`task perf:play` rows), a second core per system, a harness leg for a Sega cart then GBA.

### Phase 8: PlayStation (shipped)

Tracking issue 56, children 57 to 65, ADRs 0063 to 0069, research in docs/research/ps1-plan.md
and docs/research/ps1-spike.md (device spike passed on 2026-10-16). One core, pcsx_rearmed pinned
at `c8816799`, one shelf `Games/PS1`, no core picker. Patches start at 0034.

| Step | Issue | Content |
|---|---|---|
| 1 | done | `need_fullpath` load, patch 0030 (ADR 0059) |
| 2 | done | Device spike: SotN 4.27 ms a frame threads off, Spyro 3.61, GT2 3.08; conversion at most 0.80 ms; sticks analog |
| 3 | done | ADRs 0063 to 0069 |
| 4 | 57 | Core build, pin and licence |
| 5 | 58 | `Platform::Ps1`, shelf, disc scan, explicit policy |
| 6 | 59 | Core options and pcsx's declared defaults (ADR 0064); rewind and run-ahead off (ADR 0066) |
| 7 | 60 | 640x480 canvas, PS1 budget line, PS1 Screen section with Shader and Picture rows (ADR 0065) |
| 8 | 61 | Disk control, remembered disc, disc index in states (ADR 0067) |
| 9 | 62 | L2/R2 to the game, PlayStation face mapping (ADR 0068) |
| 10 | 63 | Generated EXE and ISO tests on HLE BIOS |
| 11 | 64 | Jewel cases with cover art and region styles (ADR 0069) |
| 12 | 65 | Analog sticks and DualShock (v2, not blocking) |

Also queued after step 2, not blocking PS1: PAL pacing at 50 Hz (issue 66, patch 0043, ADR 0071) and a crash guard on
resume (issue 67, upstream-first).

### Phase 10: TurboGrafx-16 (device gate pending)

Tracking issue 81, children 82 to 90, ADR 0091, plan in docs/research/tg16-plan.md. One core, Beetle
PCE Fast (`mednafen_pce_fast`) pinned at `3f946f2`, one shelf `Games/TG16` for HuCards, no BIOS, no core
picker, no CD and no SuperGrafx. The platform patches (0058 to 0063) are on the main-1b20432 base (ADR 0083).

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0091 and the issues |
| 2 | 82, done | Core build, pin and licence (`powf` bound to GLIBC_2.17) |
| 3 | 88, done | Generated-HuCard tests: boot, 256x240 on the 360x240 canvas, the scanline-option contract, states, BRAM (patch 0057); a test file per platform step and a GBA-after-TG16 eject test (patch 0063) |
| 4 | 83, done | `Platform::Tg16`, shelf, `.pce` scan, explicit policy; joins dist and zip-check (patch 0058) |
| 5 | 84, done | Core options, the scanline window (3 to 242) first (patch 0059) |
| 6 | 85, done | SNES 360x240 canvas at 2x, TG16 Screen section with Shader and Picture rows, Crop by default (no PAL Speed) (patch 0058) |
| 7 | 86, done | Backup RAM through the standard `.sav`, a 2 KB `.sav` per game accepted; TurboCD out of scope (patch 0060) |
| 8 | 87, done | II, I, Select, Run, X and Y turbo; Select+Run soft reset kept (patch 0061) |
| 9 | 89, done | HuCard art, labels for ScreenScraper id 31 (patch 0062, tools/fetch-labels.py) |
| 10 | 90 | Device gate |
### Phase 11: WonderSwan (device gate pending)

Tracking issue 91, children 92 to 99, ADR 0092, plan in docs/research/wswan-plan.md. One core, Beetle
Cygne (`mednafen_wswan`) pinned at `4b01295`, one shelf `Games/WS` for WonderSwan and Color, no
BIOS, no core picker. Patches 0064 to 0069 on main 1b20432; the device gate is the step left.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0092 and the issues |
| 2 | 92, done | Core build, pin and licence |
| 3 | 97, done | Generated-cart tests: boot, 224x144 and 144x224 pictures, 60.38 and 75.47 fps, states, the SELECT trap, save RAM (patch 0064); platform tests in each patch below |
| 4 | 93, done | `Platform::Ws`, shelf, scan, footer reader, explicit policy, per-game canvas, Shader and Picture rows, `.sav` saves; joins dist and zip-check (patch 0065) |
| 5 | 94, done | Core options set on every load: 60 Hz mode, rotation from the footer, keymap off (patch 0066) |
| 6 | 95, done | 240x160 canvas at 3x (horizontal) or 360x240 at 2x (vertical), Refresh row (60 Hz default, Native) (patch 0067) |
| 7 | 96, done | X and Y pads: shoulder modifiers on horizontal games, turned maps and the SELECT flip on vertical ones (patch 0068) |
| 8 | 98, done | Black and clear carts, labels for ScreenScraper ids 45 and 46 (patch 0069, tools/fetch-labels.py) |
| 9 | 99 | Device gate, both Refresh values |

### Phase 12: Atari Lynx (device gate pending)

Tracking issue 101, children 102 to 112, ADR 0093, plan in docs/research/lynx-plan.md. One core,
Beetle Lynx (`mednafen_lynx`) pinned at `fcdefcf` (Handy rejected for now, ADR 0093), one shelf
`Games/Lynx`, the player's own BIOS, no core picker. Integrated on slot main 1b20432 as patches 0070
to 0079 (2026-10-19).

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0093 and the issues |
| 2 | 102, done | Core build, pin and licence (GPL text plus the Handy zlib text) |
| 3 | 110, done (0070, each patch, 0079) | Homebrew and synthetic-cart tests: picture, real rate, states, missing-BIOS signature; BIOS-gated cart boot and pad rotation (patch 0070) |
| 4 | 103, done (0071) | `Platform::Lynx`, shelf, scan, LNX header (title, rotation byte), explicit policy; joins dist and zip-check |
| 5 | 104, done (0072) | BIOS check before launch, toast |
| 6 | 105, done (0073) | Core options: `lynx_rot_screen` always set, `lynx_force_60hz` off |
| 7 | 106, done (0071, 0074) | 240x160 canvas at 4x, Lynx Screen section (Shader, Picture, Lynx Speed, Flip Right Carts) |
| 8 | 107, done (0075) | Pacing at the game's measured rate, Lynx Speed row (Native default) |
| 9 | 109, done (0077) | Buttons, turned carts through the core's own pad turn |
| 10 | 108, done (0076) | Saves: states only |
| 11 | 111, done (0078) | Cards, labels for ScreenScraper id 28 |
| 12 | 112 | Device gate with the maintainer's BIOS |

### Phase 9: NeoGeo Pocket (in the patch set, device gate pending)

Tracking issue 70, children 71 to 79, ADR 0090, plan in docs/research/ngp-plan.md. One core, Beetle
NeoPop (`mednafen_ngp`) pinned at `a50d5ac`, one shelf `Games/NGP` for Pocket and Pocket Color, no
BIOS, no core picker. Patches 0080 to 0087 on upstream main 1b20432; flash durability in ADR 0094.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0090 and the issues |
| 2 | 71, done | Core build, pin and licence |
| 3 | 77, core half done | Generated-cart tests: boot, 160x152 picture, states, flash across a restart (patch 0080) |
| 4 | 72, done (0081) | `Platform::Ngp`, shelf, scan, header colour flag, explicit policy; joins dist and zip-check |
| 5 | 73, done (0082) | Core options (`ngp_language=english`) |
| 6 | 74, done (0083) | 240x160 canvas at 3x, NGP Screen section with Shader and Picture rows (no PAL Speed) |
| 7 | 75, done (0084, ADR 0094) | Flash durability: staging save dir `Saves/NGP/.core`, check before load, atomic publish, flush by reload |
| 8 | 76, done (0085) | A, B and Option |
| 9 | 78, done (0087) | NGP pak for mono and Color carts in the nelynes dark grey (maintainer's choice, ADR 0090), labels for ScreenScraper ids 25 and 82 |
| 10 | 79 | Device gate, including a lid-close and battery-pull flash test |

### Phase 15: Sega 32X (in the patch set, device gate pending)

Tracking issue 143, children 144 to 152, ADR 0096. One core, PicoDrive (`picodrive`) pinned at
`1890c29` with its emu2413, dr_libs and libpicofe submodules as their own pinned tarballs, one shelf
`Games/32X` for `.32x` and `.bin` with a 32X header, no BIOS, no core picker. Mega Drive is untouched.
Patches 0090 to 0097 on upstream main 1b20432. (Phases 13 and 14 were the Sega CD and Atari groundwork
on their own branches; Sega CD shipped as Phase 22.)

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0096 and the issues |
| 2 | 144, done | Core build with the three submodules, the dynarec on the device, `log` and `pow` at GLIBC_2.17, licence |
| 3 | 150, core half done | Generated-cart tests: the SH-2s answer M_OK, 320x224 picture, states, save RAM (patch 0090) |
| 4 | 145, done (0091) | `Platform::S32x`, shelf with the header check, explicit policy the same as Mega Drive; joins dist and zip-check |
| 5 | 146, done (0092) | Core options: six-button pad, region Auto, dynarec on |
| 6 | 147, done (0093) | 32X Screen section: Shader, Picture, PAL Speed, Renderer, Sound Rate |
| 7 | 148, done (0094) | Saves: the ordinary `.sav`, written only for games that save |
| 8 | 149, done (0095) | The Mega Drive pad, tests only |
| 9 | 150, done (0096) | A Mega Drive game after a 32X game equals a Mega Drive only run |
| 10 | 151, done (0097) | One black 32X cart, labels for ScreenScraper id 19 |
| 11 | 152 | Device gate: dynarec active, Virtua Racing Deluxe, Star Wars Arcade, Knuckles' Chaotix |
### Phase 14: Atari 2600 and 7800 (device gate pending)

Tracking issue 153, children 154 to 171 (172 deferred), ADR 0095, plan in docs/research/atari-plan.md.
Stella 2014 (`stella2014`) pinned at `7d1361e` and ProSystem (`prosystem`) pinned at `8a88014`, one
core each, shelves `Games/A2600` and `Games/A7800`, no core picker, no BIOS needed. Atari ST is not
planned. Patches 0099 to 0101 on main 1b20432; the device gates are the step left.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0095 and the issues |
| 2 | 154, 155, done | Core builds, pins and licences |
| 3 | 171, done | Generated-cart tests (patch 0099); platform, seat, switch, Screen and cart tests (0100, 0101) |
| 4 | 156, 163, done (0100) | `Platform::A2600` and `Platform::A7800`, shelves, scan; join dist and zip-check |
| 5 | 157, 164, done (0100) | Core options; no 7800 high score cart |
| 6 | 158, 166, done (0100) | Own canvases (360x256, 360x272), 4:3 by default; own Screen sections |
| 7 | 159, 167, done (0100) | Joystick, buttons, console switch rows held every frame, paddles on the left stick |
| 8 | 165, done (0100) | 7800 BIOS row, Off by default |
| 9 | 160, 168, done (0100) | PAL pacing (ADR 0071), PAL Speed rows |
| 10 | 161, 169, done (0101) | Carts and labels (ScreenScraper 26 and 41) |
| 11 | 162, 170 | Device gates |

### Phase 16: Virtual Boy (in the patch set, device gate pending)

Tracking issue 173, children 174 to 182, ADR 0097. One core, Beetle VB (`mednafen_vb`) pinned at
`d5ae54c` with the VR view off, one shelf `Games/VB` for `.vb` and `.vboy`, no BIOS, no core picker.
Anaglyph 3D with the preset off: the left eye alone in the palette colour. Patches 0102 to 0109.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0097 and the issues |
| 2 | 174, done | Core build with `HAVE_VR=0`, the C++ runtime linked in, `pow` at GLIBC_2.17, licence |
| 3 | 180, core half done | Generated two-eye cart: the left eye alone, both eyes with a real preset, states, cart RAM (patch 0102) |
| 4 | 175, done (0103) | `Platform::Vb`, 384x256 canvas, explicit policy; joins dist and zip-check |
| 5 | 176, done (0104) | Core options: anaglyph with the preset off, right stick to digital, fast V810 |
| 6 | 177, done (0105) | Screen section: Shader, Picture, VB Speed, Palette, Right Pad |
| 7 | 179, done (0106) | Pad: the right stick as the right D-pad, the ABXY fallback with L2 and R2 to the game |
| 8 | 178, done (0107) | Saves: the 64 KB cart RAM as the ordinary `.sav`, tests only |
| 9 | 180, done (0108) | A GBA game after a Virtual Boy game equals a GBA only run; resume |
| 10 | 181, done (0109) | One grey Virtual Boy cart with its dust cap, labels for ScreenScraper id 11 |
| 11 | 182 | Device gate: Virtual Boy Wario Land, Jack Bros., Red Alarm, Teleroboxer |

### Phase 17: Neo Geo, CPS1 and CPS2 (in the patch set, device gate pending)

Tracking issue 183, children 184 to 193, ADR 0099. One core, FinalBurn Neo (`fbneo`) pinned at `2dbbac7`
with only the Neo Geo and CPS drivers built, three shelves `Games/NEOGEO`, `Games/CPS1` and `Games/CPS2`
for the board's romset zips (FBNeo 1.0.0.03 sets), the Neo Geo BIOS checked, never shipped. CPS3 is out.
Patches 0110 to 0116 and 0119 on upstream main 1b20432.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0099 and the issues |
| 2 | 184, done | Core build with FBNeo's neogeo and cps12 subsets, `log` and `pow` at GLIBC_2.17, licence and the no-donations rule |
| 3 | 191, core half done | Zero-filled sets through FBNeo's patched-romset folder: frame sizes, rates, BIOS, rotation, states, NVRAM (patch 0110) |
| 4 | 185, done (0111) | Three platforms, the set table from the pinned source, full titles, explicit policy |
| 5 | 186, done (0112) | Options: Auto frameskip, no held-Start service menu |
| 6 | 187, done (0113) | Screen sections; vertical games upright (slot's quarter turn) or turned (pad turned) |
| 7 | 188, done (0114) | `BIOS/neogeo.zip` checked by CRC before a Neo Geo set starts |
| 8 | 189, 190, 191, done (0115) | Real-session seats, NVRAM at session end, resume per board |
| 9 | 192, done (0116) | Neo Geo AES cart, CPS2 B-board cover in its region colour, CPS1 case, arcade labels by set name |
| 10 | done (0119) | The set table indexed once; a 20,000-file scan guard (boot regression found on the device) |
| 11 | 193 | Device gate |

### Phase 18: Famicom Disk System (in the patch set, device gate pending)

Tracking issue 194, children 195 to 202, ADR 0101. No new core: fceumm, already shipped for the NES,
runs the disks; one shelf `Games/FDS` for `.fds`; the player's own `BIOS/disksys.rom` checked, never
shipped. Patches 0120 to 0126.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0101 and the issues |
| 2 | 195, done (0120) | `Platform::Fds`, the NES policy, fceumm alone, `RELEASED` 1986-02-21 |
| 3 | 196, done (0121) | Screen section: Shader, Picture (no PAL Speed, fceumm forces NTSC) |
| 4 | 197, done (0122) | `BIOS/disksys.rom` checked by size and CRC before a disk starts |
| 5 | 198, done (0123) | SELECT+L2 flips the disk through fceumm's own R and L; core tests on a generated disk |
| 6 | 199, done (0124) | The live disk as the ordinary `.sav`, a wrong-size save kept aside |
| 7 | 200, done (0125) | A GBA game after a flipped disk equals a GBA only run; resume |
| 8 | 201, done (0126) | One yellow Disk Card, labels for ScreenScraper id 106 |
| 9 | 202 | Device gate |

### Phase 19: PICO-8 (in the patch set, device gate pending)

Tracking issue 203, children 204 to 208, ADR 0102. One core, FAKE-08 (`fake08`, MIT) pinned at `814991a`
with its z8lua submodule, built with `cores/fake08/slot.patch`; one shelf `Games/PICO8` for `.p8` and
`<name>.p8.png` carts; no BIOS, no states. Patches 0127 to 0130.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0102 and the issues |
| 2 | 204, done | Core build with the source patch, `owner` and `source_patch` in `cores/lib.sh`, `powf`, `exp2f` and `pow` at GLIBC_2.17, licence |
| 3 | 207, core half done | Generated text and PNG carts: picture, pad, cartdata, stderr, pause menu, runtime error, no states (patch 0127) |
| 4 | 205, done (0128) | `Platform::Pico8`, 240x160 canvas, Screen section, Saves/PICO8 save dir, no rewind, States page hidden |
| 5 | 206, done (0129) | Our grey PICO-8 cart; labels cropped from the cart by `fetch-labels.py` |
| 6 | 207, done (0130) | A GBA game after a PICO-8 game equals a GBA only run |
| 7 | 208 | Device gate |

### Phase 20: PC Engine SuperGrafx (in the patch set, device gate pending)

Tracking issue 209, children 210 to 215, ADR 0103. One core, Beetle SuperGrafx (`mednafen_supergrafx`)
pinned at `9c11dcd`, one shelf `Games/SGX` for `.sgx` and `.pce`, no BIOS, no core picker, every card run
as a SuperGrafx (`sgx_forcesgx`). The TurboGrafx-16 shelf is unchanged. Patches 0131 to 0134.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0103 and the issues |
| 2 | 210, done | Core build with `HAVE_CHD=0`, the C++ runtime linked in, `powf` at GLIBC_2.17, licence |
| 3 | 213, core half done | Generated HuCard: picture, rates, SuperGrafx mode by extension and by `sgx_forcesgx`, states, backup RAM (patch 0131) |
| 4 | 211, done (0132) | `Platform::Sgx`, options, Screen section (Shader, Picture with 4:3), saves, the TurboGrafx-16 pad |
| 5 | 212, done (0133) | The Super HuCard, labels for ScreenScraper id 105 |
| 6 | 214 | Device gate: Daimakaimura, 1941, Aldynes, Battle Ace, Granzort, Darius Plus, Darius Alpha |
| 7 | 200, done (0134) | Pad row: 2 Buttons or the 6-button Avenue Pad; a GBA game after it equals a GBA only run |

### Phase 21: PC Engine CD (in the patch set, device gate pending)

Tracking issue 216, children 217 to 221, ADR 0104. No new core: Beetle PCE Fast, now built with
`HAVE_CHD=1`; one shelf `Games/PCECD` for `.cue`, `.chd` and `.ccd`; the user's `BIOS/syscard3.pce`
checked, never shipped; no core picker, no multi-disc. Patches 0135 to 0138.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0104 and the issues |
| 2 | 217, done (0135) | Core build with `HAVE_CHD=1` and the CHD notices; generated cue and bin with a placeholder System Card: picture, rates, header skip, backup RAM, states |
| 3 | 218, done (0136) | `Platform::Pcecd`, CD options, Screen section (Shader, Picture with 4:3), saves, the TurboGrafx-16 pad, release date |
| 4 | 219, done (0137) | The System Card check and its toasts |
| 5 | 220, done (0138) | The jewel case and disc, labels for ScreenScraper id 114 |
| 6 | 221 | Device gate: Rondo of Blood, Ys Book I and II, Gate of Thunder, Garou Densetsu Special (Arcade Card) |

### Phase 22: Sega CD / Mega-CD (in the patch set, device gate pending)

Tracking issue 222, children 223 to 232, ADR 0105 (the groundwork's ADR "0094", issues 113 to 122 and
patch 0057, renumbered). No new core: Genesis Plus GX, already shipped for the Mega Drive, plays the
discs; one shelf `Games/SEGACD` for `.chd`, `.cue`, `.iso` and `.m3u`; the player's own
`bios_CD_U.bin`, `bios_CD_E.bin` and `bios_CD_J.bin` checked, never shipped. Patches 0139 to 0146.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0105 and the issues |
| 2 | 230, core half done (0139) | Synthetic discs on the real core with a dummy BIOS: load, region, timing, backup RAM, m3u joining |
| 3 | 223, 225, done (0140) | `Platform::SegaCd`, the Mega Drive policy and canvas, `RELEASED` 1991-12-12; per-game backup RAM and no precache for a disc only, the RAM cart option unanswered |
| 4 | 226, done (0141) | Screen section: Shader, Picture (Stretch, Actual, 4:3), PAL Speed; no Region row |
| 5 | 224, done (0142) | The region's BIOS checked by size and crc32 before a disc starts |
| 6 | 228, done (0143) | Relative playlists, SELECT+L2 swap, the remembered disc swapped in after load, the PS1 trailer |
| 7 | 227, done (0144) | Backup RAM staged, checked and published in `Saves/SEGACD`, flushed by reload (the NGP flash design) |
| 8 | 229, 230, done (0145) | The Mega Drive pad; a GBA game after a swapped disc equals a GBA only run; resume |
| 9 | 231, done (0146) | The PS1 jewel case, labels by name for ScreenScraper id 20 |
| 10 | 232 | Device gate, including the reload time at lid close |

### Phase 23: Neo Geo CD (in the patch set, device gate pending)

Tracking issue 233, children 234 to 238, ADR 0106. A new core, NeoCD (`neocd`) pinned at `b1e04c7`, LGPL-3.0
with a non-commercial Z80 core; one shelf `Games/NEOCD` for `.cue` and `.chd`, holding the maintainer's two
CD-only games; the player's own `neocd.bin`, `front-sp1.bin` or `top-sp1.bin` in `BIOS/neocd/` checked,
never shipped. Patches 0147 to 0150.

| Step | Issue | Content |
|---|---|---|
| 1 | done | ADR 0106 and the issues |
| 2 | 234, done (0147) | The core pinned and built (`HAVE_CDROM=0 USE_LTO=0`, GLIBC_2.17), its licences; the core tests |
| 3 | 235, done (0148) | `Platform::Neocd`, `Core::Neocd`, the Neo Geo shelf's input, the options, backup RAM per game, no rewind, Shader and Picture, `RELEASED` 1994-09-09 |
| 4 | 236, done (0149) | The BIOS row (CDZ, Front Loader, Top Loader) and the model's file checked before a disc starts |
| 5 | 237, done (0150) | The jewel case and disc, labels by name for ScreenScraper id 70 |
| 6 | 238 | Device gate: Crossed Swords II and Samurai Shodown RPG |

### Phase 6+: deferred (non-blocking)

- A 3D disc or disc stack PS1 shelf style (issue 68).
- Stem-key collision (documented only).
- Option B variable frame size.

## Consumer-grep evidence (verified in `upstream slot` at `9d7c795`)

| Symbol | Consumer sites (file:line) | Verified |
|---|---|---|
| `Platform::ALL` | `slot-store/src/scan.rs:65`, `slot/src/app.rs:365`, `slot-store/src/slot_state.rs:240`; tests `slot-store/tests/platform.rs:5,11`, `durability.rs:312` | yes |
| `Core::ALL` | `slot/src/frontend.rs:602,606`; tests `slot-store/tests/core.rs:95,203`, `slot-ui/tests/board.rs:221`, `slot/tests/core_options.rs:59`, `render_shelf.rs:49,56` | yes |
| `SOCKET_U` | `slot-ui/src/board.rs:164` (`[f32; 2]`), `slot/src/app.rs:2243-2244` | yes |
| `socket_face` inks core name | `slot-ui/src/board.rs:282-293` | yes |
| Picker Mgba/Gpsp hardcode | `slot/src/core_picker.rs:115,116` (Left/Right), `:151` (`rightward = hop.from == Core::Mgba`), `:163` (`across = seat.index()`), `slot/src/app.rs:2272` (chip faces by `core.index()`) | yes |
| `Host` literal in an in-source test | `slot-retro/src/libretro.rs:701-718` `host_with()` lists every field of `Host` (`:25-41`) | yes |
| `GamePass` private in Compositor | `slot-gfx/src/fbo.rs:96` (construct), `:128-129` `upload_game` | yes |
| Upload guard | `slot-gfx/src/pipeline.rs:122` (rejects short buffers only) | yes |
| `!= / == Platform::Gba` | after patch 0001 only `slot/src/session.rs:465` and `slot/src/app.rs:2701` remain (link cable, GBA only by design); `core.rs:128`, `app.rs:855,2643`, `slot-store/src/core.rs:47` became policy methods | yes |
| `core_for` (no platform) | `slot/src/app.rs:2646` | yes |
| Gb/Gbc match arms | `slot-ui/src/shell.rs:92`, `slot-ui/src/cart.rs:91,157,164`, `slot-store/src/core.rs:53`, `slot/src/app.rs:1046,1409` | yes |
| Video mode via shoulders only | `slot/src/app.rs:1276-1281` (guarded by `slot_owns_the_shoulders`, `:854-856`) | yes |
| SELECT chords | `slot-input/src/gesture.rs:409-424` (no X; Y is colour toggle; A/B shaders) | yes |
| Colour toggle handler | `slot/src/app.rs:1445-1452` | yes |
| `GBA_W/GBA_H` | `slot-retro/src/libretro.rs:15,321-330`, `slot/src/emu.rs:151`, `slot/src/thumb.rs:1-14`, `slot-retro/src/mock.rs:33-47` | yes |
| Thumbnail call site | `slot/src/emu.rs:884` | yes |
| `SRC_W/SRC_H` | `slot-gfx/src/pipeline.rs:7-9,35,50-51,122,133-134,181-182`, `slot/src/video_mode.rs:45-54`, `slot/src/app.rs:930` | yes |
| X/Y stripped | `slot-retro/src/core.rs:27-42`, applied at `slot/src/emu.rs:662-664` | yes |
| `environment` default false | `slot-retro/src/libretro.rs:213` | yes |
| Unknown outline returns None | `slot-store/src/cart_shell.rs:32-36` | yes |
| `QuickRow::SCREEN` pinned | `slot-ui/tests/quick_menu.rs:85-91`, `slot/tests/quick_menu.rs:239-255` | yes |
| `write_slot_state` `format!` | `slot-store/src/slot_state.rs:130` | yes |
| Frameskip option key | `slot/src/core.rs:178`, `slot-retro/examples/core_bench.rs:104` (mgba/gpsp only) | yes |
| Hardcoded `.dylib` in tests | `slot-retro/tests/rumble.rs:9` (also `netpacket.rs`, `libretro.rs` tests per review) | yes (rumble.rs) |
| HeadlessSurface macOS-only | `slot-gfx/src/lib.rs:7,23` | yes |
| macOS-only host core tasks | `taskfile.yml:83-127` | yes |
| `device:sh` internal | `taskfile.yml:278` | yes |
| `dist:device` copies only mgba/gpsp | `taskfile.yml:285-319` | yes |
| Label cache dir | `slot/src/label_cache.rs:12` (`System/Cache/Labels`) | yes |
| `rebuilding_labels` | `slot/src/frontend.rs:417` | yes |

## Signature impact table

| Item | Change | Breaks upstream test code? |
|---|---|---|
| `RetroCore` trait | Append default methods `canvas(&self) -> (u32, u32)` (returns `(GBA_W, GBA_H)`) and `take_av_change(&mut self) -> Option<AvInfo>` (returns None) | No. The `Recorder` impl in `slot-retro/src/core.rs` tests and `MockCore` compile unchanged |
| `Host` (libretro) | **Unchanged field list.** New `HostExtra` struct owned by `LibretroCore`, plus thread-local `EXTRA` and `ExtraGuard` bound beside `Active::bind` | No. `host_with()` (`libretro.rs:701-718`) still compiles, and with `EXTRA` unbound the behaviour is upstream's |
| `LibretroCore` | New `pub fn set_canvas(&mut self, w, h)` | No |
| `GamePass` | New `pub fn set_canvas(&mut self, w, h)`; `new()` unchanged; upload guard becomes exact length | No (GBA buffers are always exactly 240x160x4) |
| `Compositor` (`fbo.rs`) | New `pub fn set_game_canvas(&mut self, w, h)` | No |
| `ButtonMask` | Unchanged; new `enum TurboMode` and `fn apply(self, mode, frame)` | No (`slot-retro/tests/turbo.rs` untouched) |
| `Shared` (emu) | New `pass_through: AtomicBool`; `set_turbo(bool)` unchanged | No |
| `CorePicker::open` | Unchanged; new `open_pair(seat, pair, now)` | No (`slot/tests/core_picker.rs` untouched) |
| `SlotState` | Fields `shader_nes`, `shader_snes` appended (Phase 3) | No. Test literals use `..Default::default()`. Phase 3 task: confirm all 55 `SlotState {` sites under `*/tests/` by eye (49 confirmed by grep) |
| `Platform` / `Core` / `Outline` enums | Variants appended; new `SHELVES`/`EVERY` | No, given the constants strategy |
| `thumb::png` | Unchanged; new `png_sized(buf, w, h)` | No |
| `root::DIRS` | `[&str; 20]` becomes `[&str; 28]` | No (tests iterate it: `dist.rs:11,20,45`, `bios.rs:118`, `boot.rs:254`) |
| `gesture.rs` chord table | Adds `Btn::X => (8192, Action::VideoModeToggle)` | No upstream test asserts SELECT+X; T22b proves GBA input is identical |

## Existing-test inventory

- **Counts at `9d7c795`:** slot 71 files / 773 tests; slot-ui 33 / 291; slot-store 14 / 129; slot-retro 6 / 78; slot-input 1 / 46; slot-gfx 6 / 45; slot-power 3 / 34; slot-sfxcut 1 / 5. About 1,401 `#[test]` total, across `tests/` and 10 source files that carry `#[cfg(test)]` modules.
- **Tests pinning upstream shapes (must stay green untouched):**
  - `slot-store/tests/platform.rs:5,11`;
  - `slot-store/tests/core.rs:203`;
  - `slot-ui/tests/quick_menu.rs:85`;
  - `slot/tests/quick_menu.rs:239`;
  - `slot-retro/src/libretro.rs:701-718` (`host_with`);
  - `slot/tests/render_shelf.rs:49-62`.
- **Real-core tests that skip silently without vendored cores:** `slot/tests/bios.rs`, `core.rs`, `e2e.rs`, `gb_palette_recolour.rs`, `gpsp.rs`, `mgba_link.rs`, `link_ui.rs`, `render_gb_palette.rs`, `render_colour_correction.rs`, and slot-retro's `rumble.rs`, `netpacket.rs` and in-source libretro tests (hardcoded `vendor/mgba_libretro.dylib`). Several also need ROMs under `sdcard/Games/...`. `task check` provides the cores and prints a skip report of ROM-dependent tests.
- **macOS-only tests:** CGL `HeadlessSurface` tests (`slot-gfx/tests/pipeline.rs`, all `render_*.rs`).
- **Card script tests:** `card/test-*.sh` via `task test:card`.
- **CI:** upstream has no test workflow. This repo adds `test.yml`.

## Critical files

### New files (repo `this repo`)

| Path | Purpose | Size estimate |
|---|---|---|
| `./SLOT_PIN` | Pinned slot tag, commit, tarball sha256 | 0.1 KB |
| `./taskfile.yml` | Tasks: `work:init`, `upstream:build`, `build`, `core:host`, `core:device`, `test`, `check`, `harness:warm`, `harness:control`, `harness:compare`, `bench:compare`, `bench:device`, `dist:device`, `zip`, `src-tarball`, `deploy:device`, `log:device`, `patches:export`, `patches:check`, `diffsurface` | 10 to 14 KB |
| `./scripts/fetch-slot.sh` | Fetch and verify the slot tarball into `build/<tree>`, link shared `vendor/` | 1 KB |
| `./scripts/apply-patches.sh` | `git apply` in glob order, `.meta` stamp, fail loudly | 1.5 KB |
| `./scripts/export-patches.sh` | `git format-patch --binary` from `work/slot` | 0.5 KB |
| `./scripts/device-sh.sh` | Docker `rust:1-bullseye` wrapper (native on Linux aarch64) | 0.5 KB |
| `./scripts/check-upstream-tests.sh` | Fail if any `crates/*/tests/` file or any `#[cfg(test)]` block in a patched src file differs from upstream | 1.5 KB |
| `./scripts/rebase.sh` | Rebase onto a new slot tag, re-export, check, bump pin | 1.5 KB |
| `./scripts/zip-check.sh` | Assert release zip layout, arches, licences, source tarball | 1.5 KB |
| `./cores/{fceumm,nestopia,snes9x,snes9x2005_plus}/build.sh` | Pinned host (`platform=osx`) and device (`platform=unix`, cortex-a53) builds, stamp, source tarball | 2.5 KB each |
| `./licenses/{fceumm-GPL-2.0,nestopia-GPL-2.0,snes9x-LICENSE,snes9x2005-LICENSE}.txt` | Verbatim licences from pinned sources | 20 to 40 KB |
| `./LICENSING.md` | Licence status per component, snes9x plugin-boundary stance, GPL-3 source offer | 3 KB |
| `./harness/frame_dump.rs` | Driven headless Frontend run, prints per-frame sha256 | 5 to 8 KB |
| `./harness/roms/` + `LICENSES/` | Legal homebrew GBA/GB/GBC (and NES/SNES test-suite) carts | 1 to 4 MB |
| `./harness/root-template/` | Pre-warmed content root (slot.state without `cart=`, label cache) | small, generated |
| `./patches/0001-step0-exhaustive-matches.patch` to `0011-cart-shell-grammar.patch` | One concern per patch | 2 to 60 KB each |
| `./.github/workflows/test.yml` | macOS host job (required) + Linux arm device job | 3 to 4 KB |
| `./.github/workflows/release.yml` | Tag build, ship checks, zip + source tarball, gh release | 4 KB |
| `./docs/REBASE.md` | Rebase procedure and log | 2 KB |
| `./docs/DEVICE-GATE.md` | RG34XXSP checklist and per-title results | 2 KB |
| `./docs/cart-art/VARIANTS.md` + `refs/` | Verified variant and colour research with sources | 5 KB + images |
| `./evals/{eval-frontend-cost,eval-cart-likeness,eval-colour-sources}.sh` | Qualitative evals | 1 to 2 KB each |

New files inside patches (created in `work/slot`):

| Path (slot tree) | Purpose | Size estimate |
|---|---|---|
| `crates/slot-store/src/platform_policy.rs` | `impl Platform`: `SHELVES` and policy methods | 2 KB |
| `crates/slot-store/src/core_policy.rs` | `impl Core`: `EVERY`, `canvas`, `option_prefix`, `has_colour_correction` | 1.5 KB |
| `crates/slot-store/src/snes.rs`, `nes.rs` | SNES header title/region (copier skip, ASCII check); NES stem-tag region | 3 KB |
| `crates/slot-retro/src/canvas.rs` | `HostExtra`, `ExtraGuard`, centring copy, RGB565, hi-res blend | 4 KB |
| `crates/slot-retro/src/libretro/env_tests.rs` | Env call unit tests | 3 KB |
| `crates/*/tests/nes_*.rs`, `snes_*.rs`, `tests/nes_common/mod.rs` | New tests and ROM generators (NROM/LoROM/HiROM with battery flags) | 30 to 50 KB |
| `crates/slot-ui/assets/{nes,famicom,snes,sfc}_cart{,_detail}.svg`, `lettering_{nes,snes}.png` | Cart art | 40 to 120 KB |

### Modified files (upstream, edited in `work/slot`; reference copy `upstream slot`)

| Path | Change |
|---|---|
| `upstream slot: crates/slot-store/src/platform.rs` | Append `Nes`, `Snes` and arms |
| `upstream slot: crates/slot-store/src/core.rs` | Append 4 variants, `text`/`parse`/`runs`/`default_for` arms |
| `upstream slot: crates/slot-store/src/scan.rs` | `read_header` exhaustive; line 65 uses `SHELVES` |
| `upstream slot: crates/slot-store/src/slot_state.rs` | New fields, defaults, `unwrap_or` parse arms, `push_str` after line 130, line 240 uses `SHELVES` |
| `upstream slot: crates/slot-store/src/cart_shell.rs` | Append `Outline` words |
| `upstream slot: crates/slot-store/src/lib.rs` | `mod` lines and exports |
| `upstream slot: crates/slot-retro/src/core.rs` | Trait default methods, `TurboMode`, `ButtonMask::apply` |
| `upstream slot: crates/slot-retro/src/libretro.rs` | `video_refresh` via `canvas.rs`; env arms read `EXTRA`; `ExtraGuard` beside each `Active::bind`; `set_canvas`; Host fields untouched |
| `upstream slot: crates/slot-retro/src/mock.rs` | `MockCore::sized` |
| `upstream slot: crates/slot-gfx/src/pipeline.rs` | `set_canvas`, exact-length upload guard, canvas-aware `whole_scale_source` |
| `upstream slot: crates/slot-gfx/src/fbo.rs` | `Compositor::set_game_canvas` |
| `upstream slot: crates/slot-gfx/src/lib.rs` | Export if needed |
| `upstream slot: crates/slot-input/src/gesture.rs` | SELECT+X chord and new `Action::VideoModeToggle` |
| `upstream slot: crates/slot/src/emu.rs` | Frames from canvas; `pass_through`; av change rebuilds resampler; `png_sized` at 884 |
| `upstream slot: crates/slot/src/core.rs` | `palette_for` via method; `colour_option` arms (151); `option_prefix`; sized MockCore |
| `upstream slot: crates/slot/src/app.rs` | One-token hunks at 365, 855, 930, 1044-1047, 1407-1410, 2643, 2646; colour guard near 1445; VideoModeToggle arm near 1276; picker pair loop at 2243-2244 |
| `upstream slot: crates/slot/src/core_picker.rs` | Pair field, `open_pair`, pair-relative 115, 116, 151, 163 |
| `upstream slot: crates/slot/src/frontend.rs` | Sockets and chips from `Core::EVERY` (602, 606); `set_game_canvas` on open; new shadows |
| `upstream slot: crates/slot/src/session.rs` | Turbo mode and pass-through on open |
| `upstream slot: crates/slot/src/video_mode.rs`, `thumb.rs`, `root.rs` | Canvas-aware rect, `png_sized`, DIRS |
| `upstream slot: crates/slot-ui/src/cart.rs`, `shell.rs`, `silhouette.rs`, `lib.rs` | Shape/Spec arms, tables, presets, silhouettes, exports |
| `upstream slot: crates/slot-ui/examples/lettering.rs` | NES/SNES lettering |

## Verification

All host steps run on macOS.

1. `cd this repo && task work:init`. Expect `work/slot` on branch `nes-snes` at `9d7c795`.
2. `task check`. It builds both trees, builds and fetches 6 host cores into the shared `vendor/`, then runs:
   - `cargo test --workspace` in `build/slot` with `SLOT_REQUIRE_CORES=1`;
   - `test:card`;
   - `check-upstream-tests.sh`;
   - `harness:control`, then `harness:compare`.

   Expect `test result: ok` for every crate, `upstream test code: 0 blocks changed`, `control: 0 diffs`, `compare: 0 diffs (H1, H2), H3 == H1`, and a skip report listing only ROM-dependent upstream tests.
3. `task bench:compare`. Expect patched medians within 2% of upstream for mgba and gpsp on `harness/roms/`.
4. `task zip && sh scripts/zip-check.sh slot-nes-snes-v1.7.0-ns.1-h700.zip`. Expected tree:

```
slot-nes-snes-v1.7.0-ns.1/
  System/ slot  launch_frontend.sh  coresave.sh  led.sh  slotlink.sh  bootlogo.bmp  bezels/
          mgba_libretro.so  gpsp_libretro.so  fceumm_libretro.so  nestopia_libretro.so
          snes9x_libretro.so  snes9x2005_plus_libretro.so
          licenses/ (slot's files, core licences, .meta, core source tarballs, patches,
                     slot-nes-snes-src-v1.7.0-ns.1.tar.gz)
  BIOS/ Config/ Games/{GBA,GB,GBC,NES,SNES}/ Labels/{...}/ Saves/{...}/ States/{...}/ Wallpapers/ ...
```

5. Device: `task deploy:device`, play, then `task log:device`. Expect `slot: core /mnt/sdcard/System/fceumm_libretro.so` and no `running the mock test pattern`.

Failure-injection checks:
- Delete `vendor/fceumm_libretro.dylib` and run `task test`. Expect T9 to fail with "fceumm core required (SLOT_REQUIRE_CORES=1)".
- Corrupt one byte of `patches/0004-canvas.patch` and run `task build`. Expect a stop naming `0004-canvas.patch`, exit non-zero.
- Add a field to `Host` in `work/slot` and run `task check`. Expect a compile failure in `host_with()`. That proves the side-struct rule is enforced.
- Remove the `rebuilding_labels` wait from `frame_dump` and run `task harness:control`. Expect diffs, which proves the control run catches non-determinism.
- Remove `licenses/snes9x-LICENSE.txt` and run `zip-check.sh`. Expect failure.

## Research acceptance criteria

- [ ] All plan-template sections populated.
- [ ] `## Spec` five bullets filled.
- [ ] `## Quality bar` five bullets present.
- [ ] Build steps table has a concrete default on every row.
- [ ] Success criteria only in `## Spec`.
- [ ] Consumer-grep evidence verified in source, including the review sites (`host_with`, `socket_face`, `fbo.rs`, chords, label cache, macOS-only tasks).
- [ ] Signature table covers RetroCore, GamePass, Compositor, Host, ButtonMask, CorePicker::open, SlotState.
- [ ] Existing-test inventory lists pinning tests, in-source test modules and silent-skip tests.
- [ ] AC-to-code coverage maps every parity row to a code site and a test ID.
- [ ] Every phase has checkbox deliverables, named tests, an acceptance gate and an RG34XXSP check.
- [ ] `## Gotchas` present.
- [ ] Bezel recorded as decided.
- [ ] Phase 4 starts with research and forbids uncited colours.
- [ ] Harness determinism designed (control run, pre-warmed root, driven emu).
- [ ] Licensing: GPL-3 source tarball and `LICENSING.md` gates.
- [ ] Open Questions each have a default and an owning phase.

## Outcome verification mechanisms

| Signal | Source | Target threshold |
|---|---|---|
| Audio underruns per 10-minute session on gate titles | `SLOT_TRACE` in `slot.log` / `slot-session.log` on the RG34XXSP | 0 on all 11 titles |
| Frame pacing | `SLOT_TRACE_LATENCY` (`System/trace-latency.on`) | p99 under 16.7 ms per title |
| Crash rate | `crash/` on the SD card after a week of use | 0 new files |
| Rebase cost | `scripts/rebase.sh` output plus a `docs/REBASE.md` row | Each slot release rebased in 1 session; conflicts only in `app.rs`/`frontend.rs` |
| Patch diff surface | `task diffsurface:check` | Every upstream touch point in `docs/UPSTREAM-TOUCHPOINTS.md` with a reason |
| GBA regressions reported | Issues labelled `gba-regression` on felipecpaiva/slot-nes-snes | 0 |

## Test plan

Rules:
- New tests live in new files only.
- Real-core tests call `require_core("<name>")`: they skip locally and panic under `SLOT_REQUIRE_CORES=1`.
- ROM generators in `tests/nes_common/mod.rs`:
  - `nes_rom(battery)`: NROM with iNES byte 6 bit 1 for battery, writing a fixed backdrop palette index;
  - `snes_rom(map, copier, sram_kb)`: LoROM/HiROM, map/type byte with 0x02 (ROM+RAM+battery) and SRAM size set when battery is wanted, setting CGRAM backdrop colour 0.
- No commercial ROMs in tests. Device-gate titles are the user's own dumps.
- Real-core colour asserts check that the picture area is uniform and is not the mock gradient, with each core's exact RGB recorded per core (palettes differ between fceumm and nestopia).
- Cores run with overscan options set explicitly so NES outputs 256x240.

### Unit tests

- `slot-retro/src/libretro/env_tests.rs`: env calls with `HostExtra` bound and unbound (unbound returns false, like upstream).
- `slot-retro/src/canvas.rs` `#[cfg(test)]`: centring, hi-res blend, and RGB565 conversion equal to the upstream formula for all 65,536 inputs.
- `slot-store/src/snes.rs` and `nes.rs` `#[cfg(test)]`: header and tag parsers.

### Integration / E2E tests

| Test ID | Phase | File (new unless noted) | Scenario | Asserts |
|---|---|---|---|---|
| T1 | 1 | upstream suite in `build/slot` + `scripts/check-upstream-tests.sh` | `cargo test --workspace` with mgba/gpsp vendored | 0 failures; 0 changed files under `crates/*/tests/`; 0 changed `#[cfg(test)]` blocks in any patched src file |
| T2 | 1 | `harness/frame_dump.rs` | Control run, then H1/H2 across trees | Control 0 diffs, then cross-tree 0 diffs |
| T3 | 1 | `task bench:compare` | `core_bench` mgba and gpsp, `--frames 3000 --warmup 300 --repeats 5`, `harness/roms/` | Medians within 2% |
| T4 | 1 | `slot-store/tests/nes_platform.rs` | `SHELVES` and accepts | `SHELVES == [Gba, Gb, Gbc, Nes]` (Phase 2: `+ Snes`); `ALL` unchanged; `Nes.accepts("x.nes")`, `!Nes.accepts("x.gba")` |
| T5 | 1 | `slot-store/tests/nes_scan.rs` | `Games/NES/Super Mario Bros. 3 (USA).nes` | One cart, platform Nes, title from the stem even when bytes look like a GB header |
| T6 | 1 | `slot-store/tests/nes_core.rs` | Selection | `core_for_platform(Nes)` = Fceumm; a `Mario = mgba` line is dropped; `Core::ALL.len() == 2`; `parse(as_str())` round-trips over `EVERY` |
| T7 | 1 | `slot/tests/nes_palette.rs` | `palette_for(Some(p), Nes, rom_0x143_clear, None)` | None |
| T8 | 1 | `canvas.rs` tests | 256x240 white into 360x240 | Lit at (52, 0) and (307, 239); dark at (51, 0) and (308, 0) |
| T9 | 1 | `slot/tests/nes_emu.rs` | fceumm boots `nes_rom`, 60 frames | Buffer 360x240x4; picture area uniform and equal to the recorded fceumm RGB; not the mock gradient |
| T10 | 1 | `slot-gfx/tests/nes_pipeline.rs` | HeadlessSurface: `Compositor::set_game_canvas(360, 240)`, upload, draw | Output (2x, 2y) equals source (x, y) at fbo scale 1; a 240x160 buffer after the switch is rejected |
| T11 | 1 | `slot/tests/nes_thumb.rs` | `png_sized` of 360x240 | Decoded 360x240, pixels match |
| T12 | 1 | `slot/tests/nes_dist.rs` | `--init-root` | NES dirs plus every upstream DIRS entry |
| T13 | 1 | `scripts/zip-check.sh` | Local zip | One top folder; aarch64 ELF for slot and cores; licences and source tarball present |
| T14 | 1 | `slot/tests/nes_mock.rs` | NES cart with fceumm missing (no `SLOT_REQUIRE_CORES`) | `MockCore::sized` 360x240; no panic; upload accepted |
| T45 | 1 | harness leg H3 | NES, eject, GBA in the patched tree | Hashes equal to H1 |
| T46 | 5 | `scripts/perf-eval.sh` | every platform and core on the RG34XXSP against the GBA baseline | full table for all 8 pairs, no missing run |
| T47 | 5 | `docs/PERFORMANCE.md` | thresholds against the GBA baseline | every pair within threshold or a linked follow-up issue |
| T48 | 4 | Cart Studio NES/SNES (PR or fork) | sample card with NES, Famicom, SNES, Super Famicom ROMs | labels sized per variant, valid cart_shell.txt lines, preview matches slot |
| T49 | 4 | `tools/tests/test_fetch_labels.py` | offline fixtures for the label fetcher | CRC rules, label sizes, cart_shell.txt grammar, network failures |
| T50 | 2 | `slot/tests/nes_video_mode.rs` | NES and SNES default to Stretch | unsaved NES/SNES carts read Stretch; a saved line wins; GBA, GB, GBC read Actual |
| T15 | 2 | `slot-store/tests/snes_header.rs` | LoROM/HiROM, with and without copier header, plus a JIS X 0201 title | Title parsed in the 4 ASCII cases; non-ASCII and garbage fall back to the stem |
| T16 | 2 | `slot-retro/tests/snes_turbo.rs` | `apply(PassThrough, f)` / `apply(Turbo, f)` | X/Y kept; Turbo equals upstream `turbo(f)` |
| T17 | 2 | `slot/tests/snes_shoulders.rs` | `taken_buttons()` playing | GBA `[]`, GB `[L1, R1]`, Nes `[L1, R1]`, Snes `[]` |
| T18 | 2 | `libretro/env_tests.rs` | `SET_GEOMETRY`; `SET_SYSTEM_AV_INFO` 50.0 fps / 32040 Hz | true; `take_av_change()` returns it once; unbound returns false |
| T19 | 2 | `libretro/env_tests.rs` | `GET_AUDIO_VIDEO_ENABLE` | 3 normally; video bit clear on an FF-skipped frame |
| T20 | 2 | `canvas.rs` tests | 512x224 alternating columns; 512x448 checkerboard | 256 wide mid-grey; 448 halved to 224 |
| T21 | 2 | `slot/tests/snes_emu.rs` | snes9x boots `snes_rom(Lo)` | Uniform recorded RGB, not mock; `av_info().sample_rate` about 32040 |
| T22 | 2 | `slot/tests/snes_select.rs` | SNES: SELECT tap; SELECT+R1; SELECT held then Y; SELECT+X | Tap reaches the core mask; R1 chord saves a state with the R bit never sent; Y never sent and `colour_correction` unchanged with no toast; X never sent and video mode toggles |
| T22b | 2 | `slot/tests/select_x_gba.rs` | Same SELECT+X sequence on a GBA cart, run in both trees | Identical per-frame core input masks and identical state |
| T23 | 3 | `slot/tests/nes_core_picker.rs` | NES picker: Right, then A | `<stem> = nestopia` written; no panic; positions 0/1; rendered sockets carry FCEUmm and Nestopia ink (compared to `socket_face(Core::Fceumm/Nestopia)`) |
| T24 | 3 | upstream `slot/tests/core_picker.rs`, `render_shelf.rs` (unchanged) | GBA picker | Pass untouched |
| T25 | 3 | `slot-store/tests/nes_shader_state.rs` | Round-trip `shader_nes=dot`; old file; Lcd3x in `shader_nes` | Round-trips; Off defaults with other fields intact; Lcd3x falls back |
| T26 | 3 | `slot/tests/nes_quick_menu.rs` | Quick menu on seated NES/SNES | Opens and navigates; Rewind/FF rows change state; Turbo row on SNES changes nothing at the core |
| T27 | 3 | `slot/tests/nes_states.rs` | SELECT+R1 then SELECT+L1 on NES and SNES (battery ROMs) | State files under `States/NES|SNES`; polaroid decodes at 360x240; load restores the frame |
| T28 | 3 | `slot/tests/snes_rewind.rs` | Rewind on snes9x for 300 frames | `rewind_fill` rises; L2 restores an earlier frame; serialize time logged under budget |
| T29 | 3 | `slot/tests/snes_ff.rs` | FF on snes9x and fceumm | Frameskip key declared; observed speed at least `ff_speed` minus 1 |
| T30 | 3 | `slot/tests/nes_resume.rs` | `cart=Mario`, `cart_platform=nes`, boot | Boots into the NES cart; T30b on the upstream tree shows the shelf, no panic |
| T31 | 3 | `slot/tests/alt_cores.rs` | nestopia and snes9x2005_plus boot generated ROMs | Uniform per-core recorded RGB, not mock |
| T32 | 3 | `slot/tests/core_option_keys.rs` | Dump `declared_options()` for all 6 cores | `option_prefix()` frameskip and overscan keys exist, or are documented absent |
| T33 | 3 | `slot/tests/nes_eject_save.rs` | Eject on battery `nes_rom` and `snes_rom` | `.sav` written under `Saves/NES|SNES` and reloaded |
| T34 | 4 | `slot-store/tests/nes_cart_shell.rs` | Parse `nes`, `famicom`, `snes`, `sfc`; unknown word | Round-trip; unknown returns None; GB words unchanged |
| T35 | 4 | `slot-store/tests/snes_region.rs` | Region bytes at the verified offset, LoROM/HiROM, copier | Japan gives Sfc; USA gives Snes; Europe gives Sfc |
| T36 | 4 | `slot-store/tests/nes_region.rs` | `(Japan)`, `(USA)`, `(Europe)`, no tag | Famicom, Nes, Nes, Nes |
| T37 | 4 | `slot-ui/tests/nes_shell.rs` | Notable-cart lookups | Each verified row maps; keys unique |
| T38 | 4 | `slot-ui/tests/render_nes_shelves.rs` | Render 4 variants (HeadlessSurface) | Mask inside `seated_box`/`cart_box`; shadow under the cart; label inside its box |
| T39 | 4 | `slot-ui/tests/nes_gb_outline.rs` | GB stem with `nes ...` | Treated as Auto (header class) |
| T40 | 4 | `slot-ui/tests/nes_presets.rs` | `shell_presets()` | Upstream presets are a prefix in the same order |
| T41 | 5 | `test.yml` | Push | `host` (macos-14) job green with no real-core test in the skip report; `device` job green building the zip |
| T42 | 5 | `scripts/rebase.sh --dry-run main` | Against slot main | "all patches apply", or the first failing patch named with a non-zero exit |
| T43 | 5 | `release.yml` on a test tag | Full release | Ship checks pass; zip and source tarball attached |
| T44 | 5 | `scripts/zip-check.sh` on the downloaded asset | Clean SD install | Same as T13 on the published artifact |

### Manual smoke tests

- **RG34XXSP Phase 1:** NES boot, save and resume; GBA plays.
- **RG34XXSP Phase 2:** SNES X/Y/L/R/SELECT and the SELECT+X/Y chords; first pass over the gate titles.
- **RG34XXSP Phase 3:** picker socket names and swaps; rewind; FF; shaders; lid close; sleep; volume; all 11 titles.
- **RG34XXSP Phase 4:** variant carts, animations, shadows.
- **RG34XXSP Phase 5:** clean install from the GitHub zip; update by replacing `System/` with `Config/` preserved.
- **Host:** `task run:4x3` (`SLOT_WINDOW=1280x960`) each phase, to exercise the RG35XXSP bezel path.

## AC-to-code coverage stub

| Parity row / criterion | Code site | Test |
|---|---|---|
| GBA/GB/GBC identical | all patches; `set_game_canvas(240, 160)` on GBA | T1, T2, T3, T45, T22b |
| Carousel / own shelves | `scan.rs:65`, `app.rs:365`, `SHELVES` | T4, T5 |
| Letter jump | shelf code (platform-agnostic) | T5, T38 |
| Cart art and labels | `cart.rs`, `shell.rs`, `silhouette.rs`, label cache | T37 to T40 |
| Core picker | `core_picker.rs:115,116,151,163`, `app.rs:2243-2272`, `frontend.rs:602-609` | T23, T24 |
| Insert and eject | `session.rs:438`, open path | T9, T21, T33 |
| Resume on boot | `slot_state.rs` `cart_platform` | T30 |
| Saves and autosave | persist (platform dir) | T33 |
| Save states and polaroids | `thumb.rs`, `emu.rs:884` | T11, T27 |
| Rewind | `rewind.rs`, emu loop | T28 |
| Fast-forward | `option_prefix`, `GET_AUDIO_VIDEO_ENABLE` | T19, T29, T32 |
| Turbo | `TurboMode`, `emu.rs:662` | T16, T26 |
| Shaders | `Shader::RETRO`, `app.rs:1044-1047,1407-1410` | T25 |
| Video mode | `video_mode.rs`, `app.rs:930`, `app.rs:1276-1281` (NES shoulders), SELECT+X (SNES) | T10, T17, T22 |
| Quick menu | `quick_menu.rs` (unchanged) | T26 |
| Settings / volume / sleep | platform-agnostic | T26 + device |
| SNES buttons | `turbo_mode`, `owns_shoulders`, chord guards | T16, T17, T22 |
| SNES geometry / av | env arms via `HostExtra` | T18, T21 |
| Hi-res | `canvas.rs` | T20 |
| Frontend cost | `canvas.rs`, upload | `eval-frontend-cost.sh` |
| Licensing | `LICENSING.md`, release ship checks | T13, T43 |
| Device gate | n/a | `docs/DEVICE-GATE.md` |

## Gotchas

1. **Real-core tests pass vacuously.** Upstream helpers return early when `vendor/<core>` is missing. New tests use `require_core`; `task check` and CI set `SLOT_REQUIRE_CORES=1` and build all 6 cores first. Workspace rule: never let a stub be the only thing that ran.
2. **The `platform=arm64` `.dll` trap.** Use `platform=unix` with `-mcpu=cortex-a53` on device and `platform=osx` on host, and assert the binary type in build.sh.
3. **SOCKET_U panic, wrong socket names, chip drift.** `SOCKET_U` is `[f32; 2]` (`board.rs:164`, used at `app.rs:2244`); `socket_face` inks the core name (`board.rs:282-293`); `core_picker.rs:151,163` assume Mgba is on the left. Faces are indexed by `core.index()` over `EVERY`; positions are pair-relative.
4. **`Host` cannot grow.** The in-source `host_with()` (`libretro.rs:701-718`) lists every field, so any new field breaks an upstream test. New state goes in `HostExtra`.
5. **X/Y are always stripped.** `turbo()` and `without_turbo()` both clear X/Y (`slot-retro/src/core.rs:27-42`). SNES needs pass-through.
6. **The RG35XXSP window is 640x427.** The bezel takes rows 427 to 479. NES and SNES scale non-integer like GBA (decided). Don't "fix" this to 512x480.
7. **RGB565 slow path.** The conversion is shared with gpSP on GBA. Any LUT must be bit-identical or the harness fails on gpSP carts.
8. **Rewind's blocking channel.** `rewind.rs:98` `sync_channel(4)` stalls the emu thread when the writer lags. Measure first and tune the cadence; don't redesign the channel.
9. **The `slot_state` `format!` line conflicts.** `slot_state.rs:130` changes on most upstream releases. Never edit it. Use a separate `push_str` and `unwrap_or` parsing.
10. **The snes9x licence and the GPL-3 source must ship.** Both are release-blocking ship checks. snes9x is non-commercial.
11. **Upstream tests pin enum and menu shapes.** `platform.rs:5,11`, `core.rs:203`, both `quick_menu.rs` tests and `render_shelf.rs:49-62`. Use `SHELVES`/`EVERY` and no SCREEN rows (OQ2).
12. **CI must be macOS for tests.** Host core tasks assert Mach-O (`taskfile.yml:83-127`), slot-retro tests hardcode `.dylib`, and HeadlessSurface is macOS-only. Linux runs only the device build.
13. **The harness is non-deterministic by default.** The label cache (`System/Cache/Labels`), slot.state and saves written between runs, the background label check and the wall-clock `now()` all vary. Use a fresh pre-warmed root per run, the driven emu, settle points, and the control run first.
14. **Frameskip key ≠ dylib name.** Verify through T32. `core_bench --frameskip` knows only mgba/gpsp.
15. **Binary assets in patches.** Export with `git format-patch --binary`; `patches:check` catches drops.
16. **Slot's `device:sh` is internal** (`taskfile.yml:278`) and `dist:device` copies only mgba/gpsp (`:285-319`). This repo owns its docker wrapper and the post-copy of the 4 cores, `.meta`, licences and sources.

## Evaluation criteria & evals

### Quantitative criteria

| Criterion | Metric | Target | Eval needed? |
|---|---|---|---|
| Upstream suite | failures in `cargo test --workspace` (`build/slot`, macOS) | 0 | No: `task test` exit code |
| Upstream test code unmodified | changed files under `crates/*/tests/` plus changed `#[cfg(test)]` blocks in patched src files | 0 | No: `scripts/check-upstream-tests.sh` |
| Harness determinism | control-run diffs | 0 | No: `task harness:control` |
| GBA identical | cross-tree differing hashes (H1, H2) and H3 vs H1 | 0 | No: `task harness:compare` |
| GBA frame cost | `core_bench` median delta | 2% or less | No: `task bench:compare` |
| New tests | T4 to T45 passing under `SLOT_REQUIRE_CORES=1` | 100% | No |
| Diff surface | upstream touch points | All mapped with a reason | No: `task diffsurface:check` |
| Ship checks | missing licence, source tarball or wrong arch | 0 | No: `zip-check.sh` |
| Device underruns | underrun lines per 10 minutes | 0 per title | No: `grep -c underrun slot.log` |

### Qualitative criteria

| Criterion | Why no simple metric | Eval draft |
|---|---|---|
| Frontend cost within GBA budget | Paired measurement, normalised per frame | `evals/eval-frontend-cost.sh`: run `frame_dump --time` on GBA (mgba, gpsp) and NES/SNES test ROMs; mean µs/frame for convert + publish + upload from `SLOT_TRACE`; fail if NES or SNES exceeds max(GBA) by more than 5% |
| Cart variants recognisable | Visual likeness | `evals/eval-cart-likeness.sh`: render variants via T38; pair with `docs/cart-art/refs/<variant>.jpg`; blind reviewer, shuffled, labels stripped; pass at 4/4 matched and none "unrecognisable" |
| Colour table accuracy | Source verification | `evals/eval-colour-sources.sh`: every row of `NES_TITLES`/`SNES_TITLES` has a `VARIANTS.md` row with a URL; fail on any orphan |

### Acceptance gates

- **Phase 1 ships when:** T1 to T14 and T45 are green under `SLOT_REQUIRE_CORES=1` on macOS; upstream test code is unmodified; control and compare show 0 diffs; bench is within 2%; fceumm's licence gate is recorded; and a NES game boots, saves and resumes on the RG34XXSP from the zip.
- **Phase 2 ships when:** T1 to T22b are green; `eval-frontend-cost.sh` passes for SNES; and the SNES buttons and chords are verified on device.
- **Phase 3 ships when:** T1 to T33 are green; the AC table is fully ticked; nestopia's licence gate is recorded; all 6 cores open on device; and the gate numbers are recorded.
- **Phase 4 ships when:** T34 to T40 are green and both cart evals pass.
- **Phase 5 / v1 ships when:** both CI jobs are green on the tag; zip-check passes on the downloaded asset; and the device gate passes on all 11 titles.
- **Adoption success is declared when:** two consecutive slot releases are each rebased in one session with zero GBA regressions reported.

## Open questions

1. **Can "unmodified" hold for every upstream test?**
   - Default: yes. `Platform::ALL`, `Core::ALL`, `QuickRow::SCREEN`, `CorePicker::open`, the `Host` field list and all in-source test blocks stay intact.
   - Override: amend `platform.rs:5,11` and `core.rs:203` and restate the bar.
   - Owner: Phase 1 (proceeds with the default).
   - Failed search: `slot NES SNES quick menu shader rows upstream tests unmodified` (wing `workspace`) returned the spec only.
2. **Cart Studio round-trip.** Does studio.slot-cfw.fyi keep unknown `cart_shell.txt` lines when it rewrites them?
   - Default: document that NES/SNES overrides go in `Config/cart_shell.txt`.
   - Owner: Phase 4 check.
   - Failed search: `NES Famicom SNES cart variants colours verified` (wing `workspace`) returned the user decision only.

Resolved by the user on 2026-10-11:
- **NES/SNES shaders:** no new quick menu rows. Shaders change with in-game SELECT+B/A only, stored as `shader_nes`/`shader_snes`.
- **SNES video mode:** a SELECT+X chord toggles Stretch/Actual on SNES only (T22, T22b).

Resolved, not open: **the bezel.** NES and SNES keep the GBA SP bezel and the 640x427 window on the RG35XXSP (user decision).

## Resume point

Phase 1, step 1: in `this repo`, write `SLOT_PIN`, `scripts/fetch-slot.sh`, `scripts/apply-patches.sh` and `scripts/device-sh.sh`, then run `task work:init` and `task upstream:build` on macOS, against `docs/QUALITY-BAR.md`.

### Critical Files for Implementation
- upstream slot: crates/slot-retro/src/libretro.rs
- upstream slot: crates/slot-gfx/src/pipeline.rs
- upstream slot: crates/slot-gfx/src/fbo.rs
- upstream slot: crates/slot/src/app.rs
- upstream slot: crates/slot/src/core_picker.rs
