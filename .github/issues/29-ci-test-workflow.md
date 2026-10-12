---
title: "Add test.yml: required macOS host job and Linux arm device job"
phase: 5
area: infra
type: chore
size: M
depends_on: [03-task-check-and-upstream-guard, 10-dist-zip-deploy]
---

## Why
Upstream has no test workflow. Slot's host core tasks, `.dylib` test paths and headless render tests are macOS-only, so tests run on macOS and Linux only builds device artefacts (docs/PLAN.md Approach "CI is macOS-primary", Build step 29). Decision: macOS is the primary test job (docs/DECISIONS.md).

## Scope
- [x] `.github/workflows/test.yml`:
  - Job `host` (`macos-14`, required): Rust toolchain, `brew install cmake`, `task core:host` (all 6 dylibs), `task check`. That covers the upstream suite with the shared vendor, the new tests under `SLOT_REQUIRE_CORES=1`, `check-upstream-tests.sh`, `harness:control`, `harness:compare`, the render tests and `bench:compare` (informational on CI runners).
  - Job `device` (`ubuntu-24.04-arm`, container `rust:1-bullseye`): `task dist:device`, `task zip`, `scripts/zip-check.sh`. No host tests.

## Tests
| ID | File | Asserts |
|---|---|---|
| T41 | `.github/workflows/test.yml` | On push: `host` (macos-14) job green with no real-core test in the skip report; `device` job green building the zip |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | gpSP dylib drift and vacuous passes are caught by `task check` (03-task-check-and-upstream-guard) |

## Acceptance
- [ ] Both jobs green on a push to main.
- [ ] `host` job skip report lists only ROM-dependent upstream tests.
- [ ] `host` is a required status check.

## Device check (RG34XXSP)
None, CI only. The phase device check is in 28-phase-5-release.

## Review notes
- Gotcha 12 (CI must be macOS for tests): host core tasks assert Mach-O (`slot: taskfile.yml:83-127`), slot-retro tests hardcode `.dylib`, and `HeadlessSurface` is macOS-only (`slot: crates/slot-gfx/src/lib.rs:7,23`). Do not move tests to Linux.
- `bench:compare` must not fail the CI job on runner noise; it stays gating locally.

## References
- docs/PLAN.md: Phase 5 deliverables (test.yml), Approach (CI is macOS-primary), Build step 29
- `slot: taskfile.yml:83-127`; `slot: crates/slot-gfx/src/lib.rs:7,23`
