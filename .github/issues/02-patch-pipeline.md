---
title: "Pin slot v1.6.0 and build both trees from the patch set"
phase: 1
area: infra
type: chore
size: M
depends_on: []
---

## Why
Everything else is a patch over a pinned slot commit, applied the way slot applies `cores/<core>/*.patch` (docs/PLAN.md "Approach", Build steps 1 to 3). Decision: patch set over pinned slot releases, not a fork (docs/DECISIONS.md).

## Scope
- [ ] `SLOT_PIN`: tag `v1.6.0`, commit `9d7c795`, tarball sha256.
- [ ] `scripts/fetch-slot.sh`: fetch and verify the tarball into `build/<tree>`, then symlink `build/<tree>/vendor` to the repo-level `vendor/`.
- [ ] `scripts/apply-patches.sh`: `git init`, `git apply` each `patches/*.patch` in glob order, write a `.meta` stamp (`slot_commit=`, `source=`, `patch=<f> sha256:<hex>`), mirroring `slot: cores/mgba/build.sh`. Stop at the first failure, print the patch name and the rejected hunk, exit non-zero. Never `--reject`.
- [ ] `scripts/export-patches.sh`: `git format-patch --binary` from `work/slot` (branch `nes-snes`) into `patches/NNNN-<concern>.patch`.
- [ ] `.gitignore`: `work/`, `build/`, `vendor/`.
- [ ] `taskfile.yml` with `work:init` (pinned tarball into `work/slot`, branch `nes-snes`), `upstream:build` (`build/slot-upstream`, no patches), `build` (`build/slot`, patches applied), `patches:export`, `patches:check` (re-apply onto a clean tarball and diff the tree against `work/slot` HEAD).

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | No T-id. The failure-injection check in Acceptance covers the apply script |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| A patch fails `git apply` on a new slot release | `apply-patches.sh` stops at the first failure, names the patch and the rejected hunk, exits non-zero. Fix by rebasing `nes-snes` in `work/slot` and re-exporting |
| Binary assets (lettering PNGs) dropped from a text patch | Export with `git format-patch --binary`; `task patches:check` re-applies onto a clean tarball and diffs against `work/slot` HEAD |
| A one-byte change inside an added line applies cleanly | Only patches:check (byte-identical round trip) and the .meta patch sha256 reveal it; patches:check runs in task check (issue 03) |

## Acceptance
- [ ] `task work:init` leaves `work/slot` on branch `nes-snes` with one base commit whose tree equals slot 9d7c795, tagged `slot-v1.6.0`.
- [ ] `task upstream:build` and `task build` produce `build/slot-upstream` and `build/slot`; both `vendor/` entries are symlinks to the repo `vendor/`.
- [ ] A tarball sha256 mismatch fails `fetch-slot.sh`.
- [ ] Failure injection: corrupt one byte of a patch (for example `patches/0004-canvas.patch` once it exists) and run `task build`; it stops naming that patch and exits non-zero.
- [ ] `task patches:check` reports no tree difference.

## Device check (RG35XXSP)
None, infra only. The phase device check is in 01-phase-1-nes-boots.

## Review notes
- Gotcha 15 (binary assets in patches): `--binary` is mandatory in the export script.
- No `--reject` and no silent fallbacks: a failing patch must stop the build loudly.
- Keep the `.meta` format in line with slot's core stamps so provenance reads the same way.

## References
- docs/PLAN.md: Approach, Build steps 1 to 3, Edge cases by layer (Patch infra), Verification step 1
- `slot: cores/mgba/build.sh` (apply and stamp pattern)
