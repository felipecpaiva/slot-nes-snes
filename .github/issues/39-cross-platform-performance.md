---
title: "Evaluate performance across every platform and core so each one feels like GBA"
phase: 5
area: device
type: test
size: L
depends_on: [17-device-gate-log, 22-ff-and-rewind, 26-cart-art, 30-release-workflow]
---

## Why
The goal of the project is one platform experience: a NES or SNES cart must feel exactly like a GBA cart in slot. Correctness is covered by the harness and the parity tests; this issue measures speed and smoothness for every platform and core against the same baseline, once all implementation is done (maintainer request, 2026-10-12).

## Scope
- [x] `scripts/perf-eval.sh` and `task perf:eval`: one run per platform and core on the RG34XXSP with the release zip: GBA (mGBA, gpSP), GB and GBC (mGBA), NES (fceumm, nestopia), SNES (snes9x, snes9x2005_plus). Done 2026-10-13: all 8 platform and core pairs that have workloads ran (GB and GBC card pairs have no cart on the card, so the free harness carts were used); results in docs/PERFORMANCE.md and docs/perf/2026-10-13/. Remaining scope items stay open: the manual metrics (boot and insert times, p99, underruns, input latency, shelf and state UI time) and the follow-up issues for misses are pending.
- [ ] Baseline: unpatched slot v1.6.0 playing GBA on mGBA on the same device, same firmware, same CPU governor, same battery state (on charger), measured in the same session.
- [ ] Metrics per platform and core, each with median and worst case over at least 3 runs:
  - boot to first shelf frame, and cart insert to first game frame (`slot: boot:` log lines, `SLOT_TRACE`)
  - frame time median and p99 in game, and dropped or late presents (`SLOT_TRACE_LATENCY`)
  - audio underruns per 10 minutes
  - fast-forward speed reached (x times real time) and frame time while fast-forwarding
  - rewind: serialize cost per frame and emu thread stalls
  - save state and load state time, including the thumbnail
  - shelf scroll and quick menu frame time with the platform's carts on screen
  - input to picture latency (button press to first changed frame), using the latency trace
- [ ] Workloads: the five SNES gate titles and the NES set from docs/DEVICE-GATE.md (the tester's own dumps), plus the free harness carts for GBA, GB and GBC.
- [ ] `docs/PERFORMANCE.md`: one table per metric, every platform and core side by side with the GBA baseline, the device and governor recorded, and raw logs kept under `docs/perf/<date>/`.
- [ ] Every metric where a platform is worse than the GBA baseline beyond its threshold gets its own follow-up issue with the numbers attached.

## Tests
| ID | File | Asserts |
|---|---|---|
| T46 | `scripts/perf-eval.sh` | Produces the full table for all 8 platform and core pairs; fails if any run is missing or any log is unparsable |
| T47 | `docs/PERFORMANCE.md` | Every pair within its threshold, or a linked follow-up issue |

## Edge cases
| Case | Expected handling |
|---|---|
| CPU governor or thermal throttling changes between runs | Record the governor and SoC temperature per run; discard and repeat runs that start above the idle temperature |
| SNES enhancement chip titles (Super FX, SA-1) are heavier than any GBA game | Report them separately against the same thresholds; a miss is a follow-up issue, not hidden in an average |
| A metric cannot be read from slot's logs | Add the trace through a patch only if the upstream log has no equivalent; prefer existing `SLOT_TRACE` lines |
| Run to run noise | At least 3 runs; thresholds compare medians, worst cases are reported but not gated |

## Acceptance
- [ ] `task perf:eval` runs end to end on the RG34XXSP for all 8 pairs.
- [ ] Thresholds against the GBA baseline: frame time median within 5%, p99 within 10%, zero audio underruns, insert to first frame within 10%, save and load state within 20%, fast-forward reaches at least the GBA multiple.
- [ ] `docs/PERFORMANCE.md` published with every table, and a follow-up issue for every miss.

## Device check (RG34XXSP)
This whole issue runs on the device.

## Review notes
- Same device, same session, same governor for baseline and candidates, or the comparison is meaningless.
- Do not tune a platform's numbers by turning a feature off; a feature that is off for one platform is a parity gap, not a fix.

## References
- docs/PLAN.md: Spec (success criteria), Quality bar, Outcome verification mechanisms
- docs/QUALITY-BAR.md
- `slot: crates/slot/src/latency.rs`, `slot: crates/slot/src/boot_time.rs`, `slot: crates/slot-retro/examples/core_bench.rs`
