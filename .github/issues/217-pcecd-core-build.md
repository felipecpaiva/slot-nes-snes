---
title: "Build Beetle PCE Fast with its CHD reader and record the notices it now carries"
phase: 21
area: cores
type: feature
size: S
depends_on: [216-pcecd-tracking]
---

## Why
Every owned disc is CHD, and ADR 0091 built the core with `HAVE_CHD=0`.

## Scope
- [x] `cores/mednafen_pce_fast/build.sh`: `HAVE_CDROM=0 HAVE_CHD=1`; `host_cflags="-Dfdopen=fdopen"` for zlib 1.2.11 on the macOS SDK, through a new optional `host_cflags` in `cores/lib.sh` (host stamp only).
- [x] `task core:mednafen_pce_fast:host` and `core:device:mednafen_pce_fast` (still only GLIBC_2.17 symbols).
- [x] `licenses/mednafen_pce_fast-chd-notices.txt` (libchdr, zstd, zlib, LZMA SDK, dr_flac, verbatim); LICENSING.md; dist-device.sh checks the file.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `slot/tests/pcecd_core.rs` | a generated cue and bin boots the placeholder card at 59.82 fps and 44.1 kHz and fills 256x240 |
| C2 | `slot/tests/pcecd_core.rs` | no card, no load; a 512-byte header is skipped; 2 KB HUBM save RAM; the state round-trips (415 KB) |
| C3 | `slot/tests/pcecd_core.rs` | the binary carries the CHD reader |
| C4 | `slot/tests/pcecd_core.rs` | a real card and disc (`SLOT_PCECD_BIOS`, `SLOT_PCECD_DISC`) give picture and sound |

## Edge cases
| Case | Expected handling |
|---|---|
| Someone flips HAVE_CHD back to 0 | C3 fails |

## Acceptance
- [x] C1 to C4 pass (C4 skips without the env vars).

## Device check (RG34XXSP)
Issue 221.

## References
- ADR 0104; ADR 0091
