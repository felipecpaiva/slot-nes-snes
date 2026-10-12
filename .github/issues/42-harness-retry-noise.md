---
title: "Stop scheduler noise from failing the harness retry rule"
phase: 1
area: tests
type: chore
size: S
depends_on: [05-gba-harness-and-bench]
---

## Why
The harness fails when the patched tree needs more than upstream + 1 retries. During issue 9's review, 2 of 10 `harness:control` runs failed that rule on H2 and B1 retries alone, with no patch involved in those legs, and one upstream H2 run used all its tries. The retries come from slot's emu thread running a frame by itself after 25 ms without a tick (`slot: crates/slot/src/emu.rs`, `STALL`), which the harness detects and reruns. A rule that fails 1 run in 5 on noise trains people to rerun until green, which hides the real regressions it exists to catch.

## Scope
- [ ] Measure: run `harness:control` 30 times on an idle machine and record retries per leg and tree, and the exit-3 message for each.
- [ ] Find the frames that retry most (H2 296, 1008, 1577; B1 170; H3 338 seen so far) and see whether the harness can step there differently, for example waiting for the emulator to report the lock before the tick, without patching slot.
- [ ] Replace the fixed upstream + 1 rule with one that holds across 30 idle runs with no false failures and still fails the faked "patched needs 2 more retries" case from issue 5's review.
- [ ] Document the measured noise and the chosen rule in `scripts/harness.sh`'s header and in the issue.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | `scripts/harness.sh` | 30 idle control runs, 0 false failures; the faked extra-retry case still fails |

## Edge cases
| Case | Expected handling |
|---|---|
| A real intermittent regression on one leg | Still fails: the rule compares per leg, not only totals |
| A busy machine | Still fails closed, never a false match |

## Acceptance
- [ ] 30 consecutive idle `harness:control` runs pass.
- [ ] The faked extra-retry injection still fails.

## Device check (RG35XXSP)
None, host only.

## Review notes
- Do not loosen the rule until it hides the faked regression; numbers first, then the rule.

## References
- Issue 9 review notes (H3 retries, frame 338); issue 5 (retry rule); `slot: crates/slot/src/emu.rs` (`STALL`, `Wait::Late`)
