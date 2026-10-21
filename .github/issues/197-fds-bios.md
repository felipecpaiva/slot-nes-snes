---
title: "Check BIOS/disksys.rom before a disk starts"
phase: 18
area: platform
type: feature
size: S
depends_on: [195-platform-fds]
---

## Why
fceumm refuses a disk without `disksys.rom`. slot never ships or fetches it, so it says so before the disk goes in (the Lynx shape, ADR 0093).

## Scope
- [x] 8192 bytes and crc32 5e607dcf (libretro System.dat, md5 ca30b50f880eb660a320674ed365ef7a): launch.
- [x] Missing or the wrong size: refuse, "FDS needs BIOS/disksys.rom". Another 8 KB file: launch, one toast a session.

## Tests
| ID | File | Asserts |
|---|---|---|
| B1 | `fds_bios.rs` | the check, refusal, resume at boot, unknown dump, known dump (SLOT_FDS_BIOS), toast places |

## Edge cases
| Case | Expected handling |
|---|---|
| 0-byte placeholder | missing |

## Acceptance
- [x] B1 passes.

## Device check (RG34XXSP)
Issue 202, step 8.

## References
- ADR 0101
