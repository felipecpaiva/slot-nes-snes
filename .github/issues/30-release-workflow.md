---
title: "Add release.yml with ship checks, the GPL source tarball and release notes"
phase: 5
area: release
type: chore
size: M
depends_on: [29-ci-test-workflow]
---

## Why
Every release must carry the snes9x licence and the GPL-3 corresponding-source tarball, and must fail the build if either is missing (docs/PLAN.md Phase 5 deliverables, Build steps 27, 28, 29).

## Scope
- [ ] `.github/workflows/release.yml` on tag: needs both `test.yml` jobs; builds the zip and `slot-nes-snes-src-<tag>.tar.gz`; runs ship checks; creates a GitHub release with both assets.
- [ ] Ship checks (also in `scripts/zip-check.sh`): `file | grep aarch64` for `slot` and all 6 cores; `test -x System/slot`; licence, `.meta` and patch files for every core; `System/licenses/slot-nes-snes-src-<tag>.tar.gz`; `System/licenses/snes9x-LICENSE.txt` and the snes9x2005 licence; `Games/NES` and `Games/SNES`.
- [ ] Release notes: non-commercial snes9x notice (use the "Notice text" quote in LICENSING.md, snes9x section); "do not report to slot's tracker"; install and update steps.
- [ ] README known-gaps section: SNES loses the L/R picture toggle (SELECT+X instead); hi-res blended 2:1; no colour correction on NES/SNES; Turbo quick row is a no-op on SNES; PAL titles run about 20% fast; stem-keyed settings collide across systems; zip ROMs unsupported.

## Tests
| ID | File | Asserts |
|---|---|---|
| T43 | `release.yml` on a test tag | Full release: ship checks pass; zip and source tarball attached |
| T44 | `scripts/zip-check.sh` on the downloaded asset | Clean SD install: same checks as T13 on the published artifact |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| snes9x licence or GPL source tarball missing from the zip | Ship checks in `release.yml` fail the build |

## Acceptance
- [ ] A test tag produces a release with the zip and source tarball attached.
- [ ] Failure injection: remove `licenses/snes9x-LICENSE.txt` and run `zip-check.sh`; it fails.
- [ ] Release notes contain both notices.

## Device check (RG34XXSP)
None separate. Installing the downloaded asset is in the phase device check in 28-phase-5-release.

## Review notes
- Gotcha 10 (the snes9x licence and the GPL-3 source must ship): both are release-blocking ship checks. snes9x is non-commercial.
- Tag format `v1.6.0-ns.N`; zip `slot-nes-snes-v1.6.0-ns.N-h700.zip` with a top folder of the same name.

## References
- docs/PLAN.md: Phase 5 deliverables (release.yml), Build steps 27, 28, 29, Edge cases by layer (Release), Verification (failure injection)
- docs/QUALITY-BAR.md: Known gaps
