---
title: "Add Platform::Fds with its own shelf and the NES policy, on fceumm alone"
phase: 18
area: platform
type: feature
size: M
depends_on: [194-fds-tracking]
---

## Why
Disks need their own shelf: `.fds` never lands on the NES shelf, and the save, BIOS and disk-control rules differ.

## Scope
- [x] `Platform::Fds` appended to `SHELVES`, `Games/FDS`, `.fds`, titled by the stem; Saves, States and Labels folders made at boot.
- [x] Every policy method answers the Disk System explicitly, the NES way; `Core::runs` gives it to fceumm alone, no picker.
- [x] Shader in `Config/fds_shader.txt`; `RELEASED` row 1986-02-21.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `slot-store/tests/fds_platform.rs` | shelf position, scan, policy, core, resume key, shader file |

## Edge cases
| Case | Expected handling |
|---|---|
| a `.fds` in `Games/NES` | not listed on either shelf |
| a `.nes` in `Games/FDS` | not listed |

## Acceptance
- [x] P1 passes; upstream site (b) takes its token.

## Device check (RG34XXSP)
Issue 202.

## References
- ADR 0101
