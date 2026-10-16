---
title: "Pace PAL titles at 50 Hz on NES, Master System, Mega Drive and PS1"
phase: 8
area: video
type: feature
size: M
depends_on: [56-ps1-tracking]
---

## Why
PAL titles run about 20% fast because slot paces at 60 fps. omega-zero paces each core at its own fps (`Pace`, `emu.rs:44-110`, commit 726cc34). The maintainer wants it after PS1 step 2. It replaces the deferred issue 34 and amends the PAL non-goal in docs/QUALITY-BAR.md and docs/PLAN.md.

## Scope
- [ ] An ADR first: it amends the PAL non-goal and replaces our `av_rate` stretch (patch 0006).
- [ ] Pace from the core's reported fps (`SET_SYSTEM_AV_INFO`, already in `HostExtra`) for NES, SMS, MD and PS1. GBA, GB and GBC pacing unchanged.
- [ ] Credit oauramos (omega-zero) in the patch and LICENSING.md.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/pal_pacing.rs` | a 50 fps core runs 50 frames a second; a 60 fps core is unchanged; audio rate follows |

## Edge cases
| Case | Expected handling |
|---|---|
| Core changes fps mid-game | Pacing follows the new rate |

## Acceptance
- [ ] ADR recorded; GBA harness compare at 0 diffs; README and QUALITY-BAR known gaps updated.

## Device check (RG34XXSP)
A PAL NES and a PAL PS1 game at 50 fps with zero underruns.

## References
- issue 34 (superseded by this one); docs/QUALITY-BAR.md Known gaps
