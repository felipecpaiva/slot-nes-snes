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
   release. `scripts/check-upstream-tests.sh` enforces it. The only allowed exception is
   the single line `#[cfg(test)] mod env_tests;` in `libretro.rs` (issue 14).
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
| Upstream files get one-token hunks | `if !self.platform.owns_shoulders()` replacing `if self.platform != Platform::Gba` | Reformat, reorder or "tidy" surrounding upstream lines |
| Enums are append-only | `Nes` after `Gbc`, `Fceumm` after `Gpsp` | Insert in the middle, reorder, rename |
| Pinned shapes stay | Add `Platform::SHELVES`, `Core::EVERY`, `CorePicker::open_pair` | Change `Platform::ALL` (3), `Core::ALL` (2), `QuickRow::SCREEN` (4), `CorePicker::open` |
| `Host` stays | New state in `HostExtra` (issue 09) | Add a field to `Host` in `libretro.rs` (its in-source test lists every field) |
| `slot_state.rs` settings line stays | New keys written by a separate `push_str` after the upstream `format!`, parsed with `unwrap_or` | Edit the `format!` line, or parse new keys with `?` |
| Match arms stay exhaustive | Add an explicit `Platform::Nes =>` arm | Add or keep a `_ =>` wildcard over `Platform`, `Core`, `Outline` or `Shape` |
| `app.rs` stays small | 25 changed lines or fewer in total (`task diffsurface`) | Put logic in `app.rs` |

## 4. Rust style (match upstream exactly)

- **Toolchain:** Rust 1.96 from `rust-toolchain.toml`. No nightly features.
- **Format:** default rustfmt settings. There is no `rustfmt.toml`; do not add one.
  `task fmt:check` runs `rustfmt --check` on every file we add or change, not the whole
  tree.
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
- **Unsafe:** only in `slot-retro` where the libretro FFI already lives, each block with a
  `// SAFETY:` line.
- **Dependencies:** none added. Not to `Cargo.toml`, not to the workspace. A real need
  goes to a new row in `docs/DECISIONS.md` first.
- **No silent fallbacks.** An unknown platform, core, outline word or region gives an
  explicit result (`None`, the platform default, the stem as title) and a `slot:` log
  line when it is surprising. Never a plausible value that hides a failure.
- **Hot paths:** `video_refresh`, the emu loop and the upload path allocate nothing per
  frame. Any change to the RGB565 path must be bit-identical (it is shared with gpSP).

## 5. Tests

- **Where:** new test files only, named `nes_*.rs`, `snes_*.rs` or after their feature
  (`canvas.rs` in-source tests live in the new file). Never add a test to an upstream file.
- **Names:** a plain sentence, like upstream:
  `fn a_nes_cart_lands_on_its_own_shelf()`, `fn select_x_never_reaches_the_snes_game()`.
- **One behaviour per test.** Assert the actual value, not just "it did not crash".
- **Real cores:** every test that needs a core calls `require_core("fceumm")` first. It
  skips locally when the dylib is missing and **fails** under `SLOT_REQUIRE_CORES=1`,
  which `task check` and CI set. A test that silently skipped proves nothing.
- **ROMs:** generated inside the test (`nes_rom(battery)`, `snes_rom(map, sram)` in the
  shared helpers) or freely licensed homebrew in `harness/roms/` with its licence file
  next to it. **Never commit a commercial ROM**, not even a few bytes of one. Device-gate
  titles are the tester's own dumps and stay on the SD card.
- **Render tests** (`HeadlessSurface`) run on macOS only. Gate them with
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
  - [ ] `task check` green (fmt on files we add or change, no new clippy warnings in both runs, all tests,
    `SLOT_REQUIRE_CORES=1`)
  - [ ] `scripts/check-upstream-tests.sh` green
  - [ ] `task harness:compare` 0 differing frames (when the change touches a shared path)
  - [ ] `task bench:compare` within 2% (when the change touches a hot path)
  - [ ] `task diffsurface` within budget
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
