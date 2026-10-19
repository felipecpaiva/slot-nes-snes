# Code standards

Read this before writing any code or opening a pull request. These rules are not
suggestions. If a rule and an issue disagree, stop and ask on the issue. Do not pick one.

The short version: **write code that looks like Brandon wrote it, touch as little of his
code as possible, and prove GBA did not change.**

---

## 1. The three rules that cannot break

1. **GBA, GB and GBC stay byte-identical.** The frame harness (`task harness:compare`)
   must report 0 differing frames, and the GBA `core_bench` median must stay within 2%.
   A pull request that moves one GBA pixel is rejected, whatever else it fixes.
2. **Upstream tests stay unmodified.** Every file under upstream `crates/*/tests/` and
   every `#[cfg(test)]` block in an upstream source file is byte-identical to the pinned
   release. `scripts/check-upstream-tests.sh` enforces it. The only allowed sites are these
   eight, and the guard checks each one exactly:
   - (a) `crates/slot-retro/src/libretro.rs`: one new `#[cfg(test)] mod env_tests;` declaration (issue 14). It is compared after whitespace is collapsed, so rustfmt's one-line and two-line forms both pass.
   - (b) `label_band` in `crates/slot-ui/tests/chrome.rs`: its Game Boy arm `Platform::Gb | Platform::Gbc` gains `| Platform::Nes` and then optionally `| Platform::Snes`, `| Platform::Gg`, `| Platform::Sms`, `| Platform::Md`, `| Platform::Ps1`, `| Platform::Tg16`, `| Platform::Ws` and `| Platform::Lynx`, in that order (the Sega, PlayStation, TurboGrafx-16, WonderSwan and Lynx tokens by the standing rule below, ADR 0055, ADR 0065, ADR 0091, ADR 0092 and ADR 0093). The file must equal upstream byte for byte once those tokens are removed from that one line, so a reflowed arm, a whitespace edit or a token on the GBA arm fails. (Site (c), `label_top` in `render_shelves.rs`, was retired in v1.7.0-ns.1 when upstream deleted that helper, ADR 0044; the letters of the other sites stay as they were.)
   - (d) `an_unreadable_platform_reads_as_a_card_that_never_said` in `crates/slot-store/tests/durability.rs`: the single value `cart_platform=nes` becomes `cart_platform=pce` (a system this project will never add), because `nes` is now a real platform.
   - (e) `both_cores_are_told_about_colour_correction_in_their_own_words` in `crates/slot/tests/gpsp.rs`: the colour-correction match gains `| Core::Fceumm` on its `Core::Mgba` arm, then optionally `| Core::Nestopia`, `| Core::Snes9x`, `| Core::Snes9x2005Plus`, `| Core::GenesisPlusGx`, `| Core::PcsxRearmed`, `| Core::MednafenPceFast`, `| Core::MednafenWswan` and `| Core::MednafenLynx`, in that order, and nothing else (ADR 0091, ADR 0092, ADR 0093).
   - (f) `a_card_from_before_the_settings_keeps_all_its_values` in `crates/slot-store/tests/durability.rs`: its full `SlotState` literal gains exactly `shader_nes: Shader::Off,` and `shader_snes: Shader::Off,`, in that order, directly after `shader_gb: Shader::Simpletex,`, because that literal has no `..Default::default()` and the new fields are required. Approved by the maintainer on 2026-10-13 (issue 21). Any other line of that file changing still fails.
   - (g) `the_rows_run_in_the_order_the_user_chose` in `crates/slot-ui/tests/quick_menu.rs`: the line `        ["Game Boy Advance", "Game Boy Color", "Game Boy"]` becomes `        ["Game Boy Advance", "Game Boy Color", "Game Boy", "NES", "SNES"]`, because `QuickRow::SCREEN` lists NES and SNES (ADR 0048, approved by the maintainer on 2026-10-15), and then optionally gains `, "Game Gear", "Master System", "Mega Drive"` before the `]` (ADR 0055), and after those optionally `, "PlayStation"` (ADR 0065), and after that optionally `, "TurboGrafx-16"` (ADR 0091), then `, "WonderSwan"` (ADR 0092), then `, "Lynx"` (ADR 0093).
   - (h) the same test: the line `            QuickRow::ControlsInGame` (last entry of the rows that open pages) becomes `            QuickRow::ControlsInGame, QuickRow::ScreenNes, QuickRow::ScreenSnes`, on that one line (ADR 0048), then optionally `, QuickRow::ScreenGg, QuickRow::ScreenSms, QuickRow::ScreenMd` on the same line (ADR 0055), and after those optionally `, QuickRow::ScreenPs1` (ADR 0065), and after that optionally `, QuickRow::ScreenTg16` (ADR 0091), then `, QuickRow::ScreenWs` (ADR 0092), then `, QuickRow::ScreenLynx` (ADR 0093). Up to v1.7.0 the last entry was `QuickRow::ScreenGb`; upstream main 1b20432 appended its Controls rows after it, so the tokens moved to the new last entry (ADR 0083). Any other line of that file changing still fails.
   (Site (i), upstream 3b6349c's backlight-floor lines in `slot-power/tests/device.rs`, was retired on the
   rebase onto upstream main 1b20432, which ships that commit, ADR 0083.)
   - (j) approved by the maintainer on 2026-10-18 (ADR 0085): `the_rows_run_in_the_order_the_user_chose` in
     `crates/slot-ui/tests/quick_menu.rs` gains the single line `            "CPU",` between
     `            "Game Titles",` and `            "Lid Power Off",` in the General labels, because
     `QuickRow::GENERAL` gains the CPU row. Approved on v1.7.0 between `"Game Titles",` and
     `"Date & Time"`; upstream main 1b20432 put its `"Lid Power Off",` row between those two, and
     its `the_arrows_stand_only_around_the_selected_rows_value` (`slot/tests/quick_menu.rs`) pins
     Date & Time directly after Lid Power Off, so the line stays right after `"Game Titles",`. The guard removes exactly that
     line before comparing and also accepts the file without it. Together with (g) and (h), any other
     line of that file changing still fails.

   **Standing rule for future sites:** a new site may be added without asking only if it
   appends a new variant token to an existing arm of an existing exhaustive match. It must
   be named in `scripts/check-upstream-tests.sh` and checked byte for byte, and it is added
   to the list above. Any other kind of upstream test change, a value swap like (d)
   included, stops and asks the maintainer.

   An upstream test that already fails on the unpatched tree on the test machine is never
   edited or skipped silently: `scripts/run-tests.sh` runs its binary in both trees and fails
   if the patched tree fails a test the upstream tree passes. Today that is
   `slot-gfx/tests/layout.rs` (two frame-hash tests, ADR 0045) and `slot/tests/render_in_game_menu.rs`
   (both tests failed on the macOS runner only after the 1b20432 rebase, ADR 0083).
3. **Never decide what the issue did not decide.** No new scope, no new dependency, no
   change to a decision in [docs/DECISIONS.md](docs/DECISIONS.md). See section 9.

## 2. How the repo works

- `SLOT_PIN` names the upstream release and commit. `work/slot` is a git checkout of that
  commit with our patches applied as commits. `build/` and `work/` are never committed.
- **You edit code in `work/slot`, one commit per patch, then run
  `scripts/export-patches.sh`.** Never hand-edit a file in `patches/`.
- Commits inside `work/slot` use the patch slug as their subject (`canvas`,
  `platform-nes`), so the exported file is `0004-canvas.patch`. The sentence-style rule in
  section 7 is for commits in this repo.
- `patches/NNNN-<concern>.patch` apply in name order. One patch is one concern, and the
  concern matches its issue (for example `0004-canvas.patch` is issue 09).
- A patch that adds a binary file (PNG) is exported with `--binary`. `task patches:check`
  fails if a binary is missing.

## 3. Patch hygiene (this is what keeps rebases cheap)

Every upstream release means re-applying our patches. Each rule below exists because
breaking it causes a conflict on most releases.

| Rule | Do | Do not |
|---|---|---|
| New code goes in new files | `platform_policy.rs`, `core_policy.rs`, `canvas.rs`, `nes_*.rs` tests | Grow an upstream file with a new function block |
| Upstream files get one-token hunks | `&& self.platform.owns_shoulders()` replacing `&& self.platform != Platform::Gba` | Reformat, reorder or "tidy" surrounding upstream lines |
| Enums are append-only | `Nes` after `Gbc`, `Fceumm` after `Gpsp` | Insert in the middle, reorder, rename |
| Pinned shapes stay | Add `Platform::SHELVES`, `Core::EVERY`, `CorePicker::open_pair` | Change `Platform::ALL` (3), `Core::ALL` (2), `QuickRow::SCREEN` (5 since ADR 0048), `CorePicker::open` |
| `Host` stays | New state in `HostExtra` (issue 09) | Add a field to `Host` in `libretro.rs` (its in-source test lists every field) |
| `slot_state.rs` settings line stays | New keys written by a separate `push_str` after the upstream `format!`, parsed with `unwrap_or` | Edit the `format!` line, or parse new keys with `?` |
| Match arms stay exhaustive | Add an explicit `Platform::Nes =>` arm | Add or keep a `_ =>` wildcard over `Platform`, `Core`, `Outline` or `Shape` |
| Every upstream touch point is tracked | `docs/UPSTREAM-TOUCHPOINTS.md` lists every hunk where a patch changes a file upstream already has (net diff against the pinned release), with the patches that touch the file and one line of reason. `task diffsurface` regenerates it and keeps existing reasons; `task check` runs `task diffsurface:check`, which fails on a stale map or a row without a reason. There is no fixed line limit (decided 2026-10-13); keep upstream edits small and put logic in new files where you can | Edit an upstream file without regenerating the map, or leave `TODO: explain` in it |

**Upstream-first fixes (ADR 0047).** If a problem's right fix belongs in upstream
BrandonKowalski/slot, we also open a PR there, carry our patch only until upstream ships it, and
drop it on the next rebase.

## 4. Rust style (match upstream exactly)

- **Toolchain:** Rust 1.96 from `rust-toolchain.toml`. No nightly features.
- **Format:** default rustfmt settings. There is no `rustfmt.toml`; do not add one.
  `task fmt:check` runs `rustfmt --check` on every file we add or change, not the whole
  tree. Upstream test files are skipped: rule 2 holds them byte for byte, so a token added
  at a named site stays on its line even when rustfmt would reflow it.
- **Lint:** `task lint` runs `cargo clippy --workspace --all-targets` and
  `cargo clippy -p slot --no-default-features --features device` in both trees. We must add
  zero warnings compared with upstream. No `#[allow(...)]` unless upstream already has one
  at that spot.
- **Why only new problems fail:** upstream's own `crates/slot/tests/prefetch.rs` fails fmt
  and clippy on Rust 1.96.1, and upstream tests must not be edited.
- **Comments: none.** Upstream has one comment line in its whole source tree, a
  `// SAFETY:` note. Names carry the meaning. The only comment allowed is `// SAFETY:`
  above every `unsafe` block you add, saying why it is sound. No doc comments (`///`), no
  commented-out code, no `TODO`. A deliberate shortcut is written in the PR body and in a
  follow-up issue, not in the code.
- **Naming:** snake_case functions that read as plain English (`owns_shoulders`,
  `picker_cores`, `has_gb_palettes`). British spelling like upstream: `colour`, `centre`,
  `licence` (noun). Keep API names as they are (`GL_RGB`, `PixelFormat`).
- **Errors:** no new error crates (`anyhow`, `thiserror`). Return `Option` or the crate's
  existing error type. Log with `eprintln!("slot: <area>: <what happened>")`, lowercase,
  the same shape as `slot: emu: stopping at ...`.
- **No panics in `src/`:** no `unwrap()`, `expect()`, `panic!` or indexing that can go out
  of bounds on data from a ROM, a file or a core. Use `get`, `?`, or a guarded early
  return. (The `SOCKET_U[2]` crash in the plan is exactly this.)
- **Unsafe:** only in `slot-retro` where the libretro FFI already lives, plus the GL texture
  re-allocation in `slot-gfx` `GamePass::set_canvas`, the NES and SNES shader program in
  `slot-gfx/src/pipeline/retro.rs`, the Linux `HeadlessSurface` in
  `slot-gfx/src/headless_egl.rs` (ADR 0088), and in our own new test files where a test
  must read GL output or a core symbol that slot does not expose (`nes_window.rs`,
  `nes_fceumm.rs`). Each block has a single-line `// SAFETY:` comment.
- **Dependencies:** none added. Not to `Cargo.toml`, not to the workspace. A real need
  goes to a new ADR in `docs/adr/` first.
- **No silent fallbacks.** An unknown platform, core, outline word or region gives an
  explicit result (`None`, the platform default, the stem as title) and a `slot:` log
  line when it is surprising. Never a plausible value that hides a failure.
- **Hot paths:** `video_refresh`, the emu loop and the upload path allocate nothing per
  frame. Any change to the RGB565 path must be bit-identical (it is shared with gpSP).

## 5. Tests

- **Where:** new test files only, named `nes_*.rs`, `snes_*.rs` or after their feature
  (`canvas.rs` in-source tests live in the new file). Never add a test to an upstream file.
  A helper several of our tests need lives in a new shared module, because upstream
  `common/mod.rs` cannot be edited: `crates/slot/tests/nes_common/mod.rs` (`require_core(name)`,
  `fceumm()`, `nes_rom(name, battery)`) and `crates/slot/tests/snes_common/mod.rs`
  (`snes_rom(name, map, copier, sram_kb)`, `Map`, `SNES_TITLE`), `sega_common/mod.rs` for the
  Sega platforms, `ps1_common/mod.rs` for PlayStation (`pcsx_rearmed()`, `disc(dir, stem)`:
  a generated PS-X EXE on a generated ISO9660 `.bin` and `.cue`; tests force
  `pcsx_rearmed_bios=HLE`, so no BIOS is ever needed), and `tg16_common/mod.rs` for TurboGrafx-16
  (`pce_fast()`, `hucard(dir, stem)`: a generated 8 KB HuCard that paints the screen red). A shared test module starts with `#![allow(dead_code)]`, as upstream's
  `common/mod.rs` does, because each test binary uses only part of it; nothing else allows it.
- **Names:** a plain sentence, like upstream:
  `fn a_nes_cart_lands_on_its_own_shelf()`, `fn select_x_never_reaches_the_snes_game()`.
- **One behaviour per test.** Assert the actual value, not just "it did not crash".
- **Real cores:** every test that needs a core calls `require_core("fceumm")` first. It
  skips locally when the dylib is missing and **fails** under `SLOT_REQUIRE_CORES=1`,
  which `task check` and CI set. A test that silently skipped proves nothing.
- **ROMs:** generated inside the test (`nes_rom(name, battery)`,
  `snes_rom(name, map, copier, sram_kb)` in the shared helpers) or freely licensed homebrew in `harness/roms/` with its licence file
  next to it. **Never commit a commercial ROM**, not even a few bytes of one. Device-gate
  titles are the tester's own dumps and stay on the SD card.
- **Render tests** (`HeadlessSurface`) run on macOS, and on Linux under GLES2 through
  surfaceless Mesa EGL (ADR 0088). Gate a new one with
  `#![cfg(any(target_os = "macos", target_os = "linux"))]`; if it needs no core and lives in
  slot-gfx or slot-ui, add it to the render step of the `device` job in
  `.github/workflows/test.yml`. A test that needs a core or the slot crate keeps
  `#![cfg(target_os = "macos")]` like upstream.
- **Every test from the issue's table is written, with the ID in the PR body.** No issue is
  done with a test missing.
- **Prove the test can fail.** For each new test, break the code once locally and check
  the test goes red. Say in the PR which line you broke.

## 6. Scripts and build files

- Shell: POSIX `sh` with `set -eu`, shaped like upstream `cores/mgba/build.sh`
  (`usage`, `stamp`, `build` functions). No bashisms.
- Tooling in Python: python3 standard library only.
- Core build scripts write a `.meta` stamp in the same format as upstream, assert the
  output is the right binary type (`Mach-O` on macOS, `ELF aarch64` for the device), and
  use `make platform=unix` for the libretro cores, never `platform=arm64`.

## 7. Commits

Match upstream's history:

- One imperative sentence that says what changes **for the player or the maintainer**, no
  prefix, no trailing period. Examples from upstream: *"Keep the GBA cartridge clock
  running on gpSP while the game is off"*, *"Cut each rumble buzz off at 150 ms"*.
- Ours: *"Give NES carts their own shelf (#7)"*, *"Draw NES games at 2x inside the GBA
  window (#9)"*.
- No `feat:` / `fix:` prefixes. No body unless the why is not obvious from the sentence.
- No co-author or tool attribution lines.

## 8. Pull requests

- **One issue, one pull request, one branch** named `<issue>-<slug>`, for example
  `9-canvas`. Base is `main`.
- Fill every section of the template (`.github/pull_request_template.md`). Paste real
  command output, not a summary of it.
- A pull request is ready only when all of this is true:
  - [ ] `task check` green (fmt on files we add or change, no new clippy warnings in both
    runs, all tests with `SLOT_REQUIRE_CORES=1`)
  - [ ] `sh scripts/check-upstream-tests.sh` green
  - [ ] `task harness:compare` 0 differing frames (when the change touches a shared path)
  - [ ] `task bench:compare` within 2% (when the change touches a hot path)
  - [ ] `docs/UPSTREAM-TOUCHPOINTS.md` regenerated (`task diffsurface`) and every new row has a reason (`task diffsurface:check` exits 0)
  - [ ] every test ID from the issue present and passing
  - [ ] every acceptance box in the issue ticked or explained
  - [ ] device check done, or marked "needs device" for the maintainer

## 9. Stop and ask instead of deciding

Stop, write the question on the issue, and wait when:

- the issue and the code disagree (a line number moved, a function is not where the issue
  says);
- a fix needs a new dependency, a new upstream file edit not listed in the issue, or a
  change to a pinned shape (section 3);
- an upstream test fails and the only fix is to change it;
- the harness shows a GBA difference you cannot explain;
- a value has to be invented (a cart colour, a region offset, a core option key). Values
  come from a cited source (the research issue, the core's source at the pinned commit),
  never from memory.

Guessing and moving on is the one thing that costs more than asking.

## 10. Writing (docs, issues, PR text)

- Plain, short sentences. Concrete numbers and file paths.
- No em dashes or en dashes. Use commas, periods or parentheses.
- British spelling, like the code.
