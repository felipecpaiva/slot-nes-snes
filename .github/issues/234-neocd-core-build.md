---
title: "Pin and build NeoCD for the host and the device, and record its licences"
phase: 23
area: cores
type: feature
size: S
depends_on: [233-neocd-tracking]
---

## Why
Neo Geo CD discs need a core slot does not ship. NeoCD reads CHD, offers the three console BIOSes and loads fast with its speed hack.

## Scope
- [x] `SLOT_PIN` `neocd_commit` b1e04c7 and `neocd_tarball_sha256`; `cores/neocd/build.sh` (`HAVE_CDROM=0 USE_LTO=0`, the C++ runtime static); `cores/neocd/glibc-2.17.h` (exp, logf, pow).
- [x] taskfile `core:neocd:src`, `core:neocd:host`, `core:device:neocd`; core:host, core:device, check, dist.
- [x] `licenses/neocd-LGPL-3.0.txt`, `neocd-GPL-3.0.txt`, `neocd-notices.txt`, `neocd-headerless-files.txt`; LICENSING.md; dist-device.sh, zip-check.sh, run-tests.sh, bench-device.sh.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `slot/tests/neocd_core.rs` | the options slot answers are declared with their values |
| C2 | `slot/tests/neocd_core.rs` | no BIOS: no `neocd_bios` and the disc still loads (the high-level BIOS slot must refuse) |
| C3 | `slot/tests/neocd_core.rs` | the three models are declared as `<file> (<model>)` |
| C4 | `slot/tests/neocd_core.rs` | 59.60 fps, 44.1 kHz, 8 KB save RAM that loads back, a state of about 8 MB that loads into a fresh core |
| C5 | `slot/tests/neocd_core.rs` | the core's own backup RAM file is the shared `neocd.srm` |
| C6 | `slot/tests/neocd_core.rs` | each real BIOS starts a real disc with picture and sound (`SLOT_NEOCD_BIOS`, `SLOT_NEOCD_DISC`) |

## Edge cases
| Case | Expected handling |
|---|---|
| LTO back on | `task core:device:neocd` fails on GLIBC_2.29 |

## Acceptance
- [x] C1 to C6 pass (C6 skips without the env vars).

## Device check (RG34XXSP)
Issue 238.

## References
- ADR 0107
