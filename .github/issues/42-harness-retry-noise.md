---
title: "Stop scheduler noise from failing the harness retry rule"
phase: 1
area: tests
type: chore
size: S
depends_on: [05-gba-harness-and-bench]
---

## Why
The harness failed (in its first form) when the patched tree needed more than upstream + 1 retries. During issue 9's review, 2 of 10 `harness:control` runs failed that rule on H2 and B1 retries alone, with no patch involved in those legs, and one upstream H2 run used all its tries. The retries come from slot's emu thread running a frame by itself after 25 ms without a tick (`slot: crates/slot/src/emu.rs`, `STALL`), which the harness detects and reruns. A rule that fails 1 run in 5 on noise trains people to rerun until green, which hides the real regressions it exists to catch.

## Scope
- [x] Measure: run `harness:control` 30 times on an idle machine and record retries per leg and tree, and the exit-3 message for each.
- [x] Find the frames that retry most (H2 296, 1008, 1577; B1 170; H3 338 seen so far) and see whether the harness can step there differently, for example waiting for the emulator to report the lock before the tick, without patching slot.
- [x] Replace the fixed upstream + 1 rule with one that holds across 30 idle runs with no false failures and still fails the faked "patched needs 2 more retries" case from issue 5's review. 30 runs with the rule and the lock wait: 30 of 30 passed; the old 30 logs also pass it.
- [x] Document the measured noise and the chosen rule in `scripts/harness.sh`'s header and in the issue.

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
- [x] 30 consecutive idle `harness:control` runs pass (30 of 30 exit 0 after the change, 2026-10-13).
- [x] The faked extra-retry injection still fails (`HARNESS_FAKE_LATE="H2 2" task harness:control` failed twice with "H2 needed 2 retries in the patched tree against upstream's 0").

## Acceptance notes
Measured 2026-10-12, 30 `harness:control` runs on an idle M5 Max with the old rules: 28 passed, 2 failed (run 7: patched 2 retries on H2 and B1, upstream 0; run 11: H3 needed 2 in one run). Retries per run: patched 0 in 17, 1 in 11 (upstream 1 in 9 runs), 2 in 2. Per leg and tree never more than 1 retry in the 232 samples with a known tree, so the noise is one retry on one leg, sometimes on two legs of one tree. Causes by frame:
- 296 x8 (H2), 170 x2 (B1), 1921 x3 (H1G), 338 x5 and 2725 (H3), 2281 (H2): "not locked 23 ms after the update", all the first step after an insert. The emulator thread sets its lock a variable time after the core reports ready (it spawns the rewind thread first), and `step_emulator` returns false at once when unlocked. Fix in `harness/frame_dump.rs`: the core part waits for `emu().locked()` and then ticks; the stall clock starts at the lock, so the tick is in time. The composite part cannot see the lock (`Frontend` has no accessor, and upstream's API is all frame_dump may use), so it still retries there.
- 1564 x4 (H1, H1G): "1 core frames published, expected 0". The polaroid frame takes longer than the emulator's 25 ms stall, so it runs a frame alone. Only a slot change would avoid it; it stays a retry.
- 869 x2, 2153, 2235, 2854: 22 to 37 ms between ticks, scheduler noise.
Rule now: a patched leg fails when it needed at least 2 retries and more than upstream's for that leg; patched in all fails above upstream + 2 (seen at most +2 before the lock wait, +1 after); one H3 run fails above 2 retries (seen 2). It catches lateness concentrated on one leg or well above upstream's total. It does not catch spread-out lateness: 1 retry per leg, up to upstream + 2 in total, passes.
After the change (30 runs, 2026-10-13): 30 of 30 exit 0. Retries (upstream/patched total): 0/0 in 19 runs, 0/1 in 3 (plus one run with 0/0 and H3 1), 1/0 in 5, 1/1 in 1, 2/0 in 1. Late lines 13 (down from 29): 296 x6, 1921 x2, 338 x1, 1564 x2, and 2 tick gaps (2854, 1431). The 20 "not locked" lines before became 9 after. Both log sets (60 runs) pass the rule, checked from the logged counts (before logs print totals only, per leg maxima from the 232 samples above). 60 runs with 0 false failures bound the false-failure rate at about 5% (95%), not 0.
Which part the remaining "not locked" lines (296 x6, 1921 x2, 338 x1) come from: the composite part, by elimination. The core part now waits for `emu().locked()` and ticks at once, so it cannot report the emulator unlocked; the composite rig has no lock accessor and never waits. The marks before each late line are printed by both parts alike, so the logs alone do not show it. A patched-only `Frontend::emu` accessor would remove these, and it is left out because `frame_dump` is built in the upstream tree too.
Injection: `HARNESS_FAKE_LATE="H2 2" task harness:control` fails with `slot-nes-snes: H2 needed 2 retries in the patched tree against upstream's 0` (2 of 2 tries). The full `task check` passed after the change (compare 0 diffs).

## Device check (RG34XXSP)
None, host only.

## Review notes
- Do not loosen the rule until it hides the faked regression; numbers first, then the rule.

## References
- Issue 9 review notes (H3 retries, frame 338); issue 5 (retry rule); `slot: crates/slot/src/emu.rs` (`STALL`, `Wait::Late`)
