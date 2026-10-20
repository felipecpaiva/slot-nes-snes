---
title: "Build FinalBurn Neo with only the Neo Geo and CPS drivers from a pinned commit for host and device, and record its licence"
phase: 16
area: cores
type: feature
size: M
depends_on: [153-arcade-tracking]
---

## Why
FBNeo is one large core; slot needs only three boards. Its own subset makefiles build them, and its licence is non-commercial with a no-donations clause.

## Scope
- [x] `cores/fbneo/build.sh` and `Makefile.arcade` (FBNeo's neogeo and cps12 subsets together, driver list regenerated).
- [x] `SLOT_PIN` `fbneo_commit` and `fbneo_tarball_sha256`; `task core:fbneo:src`, `core:fbneo:host`, `core:device:fbneo`.
- [x] Device core needs only glibc 2.17 (`log` and `pow` bound, `cores/fbneo/glibc-2.17.h`).
- [x] LICENSING.md section, `licenses/fbneo-*` files, dist-device.sh and zip-check.sh.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `task core:device:fbneo` | aarch64 ELF, NEEDED libc, libm, libpthread, no symbol above GLIBC_2.17 |
| C2 | `scripts/zip-check.sh` | the core, its source, meta and licence files are in System/ |

## Edge cases
| Case | Expected handling |
|---|---|
| A build that pulls a driver outside the subset | link fails; the driver list is regenerated from the subset sources |
| A libm symbol re-versioned again | needs_old_glibc_only fails the task |

## Acceptance
- [x] C1 and C2 pass.

## Device check (RG34XXSP)
Issue 163.

## References
- ADR 0097
