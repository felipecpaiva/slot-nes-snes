---
title: "Disk saves: the live disk as the ordinary .sav, the .fds never written"
phase: 18
area: platform
type: feature
size: S
depends_on: [195-platform-fds]
---

## Why
FDS games save by writing the disk. fceumm exposes the live disk as save RAM, so the ordinary `.sav` holds it and the dump on the shelf stays as dumped.

## Scope
- [x] `Saves/FDS/<stem>.sav`, every side without the fwNES header; a RetroArch `.srm` loads the same way.
- [x] A save of the wrong size is renamed `<stem>.sav.mismatch` and not loaded.

## Tests
| ID | File | Asserts |
|---|---|---|
| V1 | `fds_saves.rs` | the sav is the disk, the .fds untouched, a saved disk comes back, a wrong size is kept aside, expected sizes |

## Edge cases
| Case | Expected handling |
|---|---|
| a disk never written | still leaves a full-size `.sav` (a copy of the disk) |

## Acceptance
- [x] V1 passes.

## Device check (RG34XXSP)
Issue 202, step 7.

## References
- ADR 0101
