---
title: "Give the Disk System its own Screen section with Shader and Picture"
phase: 18
area: video
type: feature
size: S
depends_on: [195-platform-fds]
---

## Why
Every system has its own Screen section. The NES rows minus PAL Speed: fceumm forces NTSC for every disk.

## Scope
- [x] Shader (retro list) and Picture (Crop default, Stretch, Actual, 4:3) after CPS2, shown only with disks on the card.
- [x] `fds` in `Config/picture.txt`; neither row touches the NES choices.

## Tests
| ID | File | Asserts |
|---|---|---|
| S1 | `fds_screen.rs` | rows, labels, hidden without disks, picture and shader files |

## Edge cases
| Case | Expected handling |
|---|---|
| Release-year shelf order | the section sits after the Master System |

## Acceptance
- [x] S1 passes; upstream sites (g) and (h) take their token.

## Device check (RG34XXSP)
Issue 202.

## References
- ADR 0101
