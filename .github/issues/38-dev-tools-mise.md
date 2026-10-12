---
title: "Pin the developer toolchain with mise"
phase: 1
area: infra
type: chore
size: S
depends_on: []
---

## Why
`cd` into the repo should give the right tool versions with no manual installs. The maintainer already uses mise globally, so a repo-level `mise.toml` pins the toolchain the taskfile and the core builds need (docs/PLAN.md "Approach"). Docker is not pinned: it stays on Homebrew with colima.

## Scope
- [ ] `mise.toml` at the repo root: `rust = { version = "1.96", components = "rustfmt,clippy", profile = "minimal" }`, `task = "3.54"`, `cmake = "3.31"`.
- [ ] Rust 1.96 matches upstream slot's `rust-toolchain.toml` (channel `1.96`, components `rustfmt` and `clippy`).
- [ ] cmake stays on 3.x (newest offered by mise: 3.31.12) because upstream mGBA's `CMakeLists.txt` may not configure under CMake 4 without `CMAKE_POLICY_VERSION_MINIMUM`. Moving to 4.x needs a decision first.
- [ ] README "Setup" section: `brew install mise colima docker`, `mise trust && mise install`, `colima start`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. The version output in Acceptance covers it |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| Upstream trees under `build/` carry their own `rust-toolchain.toml` (channel `1.96`) | Both resolve to the same toolchain. Verified: `cargo --version` in a directory holding that file prints `cargo 1.96.1` under mise |
| `1.96` is a floating minor | mise installs the latest 1.96.x (1.96.1 today); the channel `1.96` in upstream does the same, so they agree |
| A newer cmake (4.x) is already on the PATH via Homebrew | mise puts its 3.31 first inside the repo; `which cmake` points at the mise install |

## Acceptance
- [ ] `mise trust && mise install` in a fresh clone installs rust, task and cmake.
- [ ] `mise exec -- cargo --version` prints `cargo 1.96.x`, and `cargo fmt --version` and `cargo clippy --version` both work.
- [ ] `mise exec -- task --version` prints `3.54.0`.
- [ ] `mise exec -- cmake --version` prints `cmake version 3.31.12`.
- [ ] The README Setup section is present.

## Device check (RG34XXSP)
None, infra only. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Do not pin docker or colima. They stay on Homebrew.
- Keep the rust pin in step with upstream's `rust-toolchain.toml` on every slot release (docs/REBASE.md once issue 31 lands).

## References
- docs/PLAN.md: Approach
- slot: `rust-toolchain.toml`, `cores/mgba/build.sh`
