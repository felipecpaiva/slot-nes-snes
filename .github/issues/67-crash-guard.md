---
title: "Do not auto-resume a game whose start crashed"
phase: 8
area: platform
type: fix
size: M
depends_on: [56-ps1-tracking]
---

## Why
Upstream v1.7.0 resumes the last game on boot unconditionally (`session.rs:475`). A game that crashes on start then crashes every boot. omega-zero keeps such a game on the shelf with a notice (commit be6eb11). PS1 makes a bad start more likely. The fix is about slot itself, so it is upstream-first (ADR 0047).

## Scope
- [ ] Mark a start in progress before `load_game`, clear it after the first frames run; on boot, a mark still set means the game is left on the shelf with a notice.
- [ ] Upstream twin PR in `~/contrib/slot` with its own tests; our patch says "drop when the upstream PR lands".
- [ ] Credit oauramos (omega-zero).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/crash_guard.rs` | a mark left set stops the resume; a clean start resumes as today |

## Edge cases
| Case | Expected handling |
|---|---|
| Power loss during a normal start | One missed resume, then normal |

## Acceptance
- [ ] Tests green; GBA harness compare at 0 diffs; upstream PR opened.

## Device check (RG34XXSP)
None needed beyond a normal resume.

## References
- ADR 0047
