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
- [x] Mark a start in progress before `load_game`, clear it after the first frames run; on boot, a mark still set means the game is left on the shelf with a notice. Patch `0052-crash-guard` (ADR 0084): `Config/starting.txt` is written in `Session::spawn_core` before the core opens, removed after 300 published frames or a resume flush or autosave; `App::start` keeps the named cart selected on the shelf with a "Last start failed" banner, resume state untouched.
- [ ] Upstream twin PR in `~/contrib/slot` with its own tests; our patch says "drop when the upstream PR lands". PR text ready in `docs/contributions/upstream-crash-guard-pr.md`, not sent. Upstream main has no crash guard to backport (checked 2026-10-18, 24 commits past v1.7.0).
- [x] Credit oauramos (omega-zero). In the patch commit, ADR 0084 and LICENSING.md (idea only, no code).

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/crash_guard.rs` `a_start_that_never_got_through_leaves_the_cart_on_the_shelf` | a mark left by a start that ran no frames keeps the cart selected on the shelf with the banner |
| (new) | `crash_guard.rs` `a_start_that_never_got_through_keeps_its_resume_state` | the resume state is untouched |
| (new) | `crash_guard.rs` `a_cart_kept_on_the_shelf_stays_there_until_a_start_gets_through` | a second boot still shows the shelf |
| (new) | `crash_guard.rs` `the_mark_stays_down_until_the_300th_published_frame` | 299 frames keep the mark (shelf on the next boot), 300 clear it (resume, no banner); no core, no wall clock |
| (new) | `crash_guard.rs` `a_start_that_runs_its_first_frames_resumes_on_the_next_boot` | 300 published frames clear the mark; the next boot resumes, no banner; through a real Session, waiting on the frame count with a 120 s bound |
| (new) | `crash_guard.rs` `a_flush_before_the_first_frames_also_clears_the_mark` | a resume flush clears it too |
| (new) | `crash_guard.rs` `the_mark_holds_back_only_the_cart_it_names` | another seated cart resumes as today |
| (new) | `crash_guard.rs` `the_start_failed_banner_uploads_in_its_own_place` | the banner has its own place in `Toast::every()` |

Seen to fail: dropping the check in `App::start` fails the shelf tests; dropping the settle call in `Session::update` fails the 300-frame test; dropping it from `flush_resume` fails the flush test.

## Edge cases
| Case | Expected handling |
|---|---|
| Power loss during a normal start | One missed resume, then normal |
| Power off, eject or doze in the first 5 seconds | The resume flush clears the mark, so the next boot resumes |
| Core reports `Failed` | Mark stays; that boot and the next show the shelf (the banner is true: the start failed) |
| Single-cart card | Covered: the shelf with the one cart, as upstream does for a core that will not load |

## Acceptance
- [ ] Tests green; GBA harness compare at 0 diffs; upstream PR opened.

## Device check (RG34XXSP)
1. Normal resume: play any game over 5 seconds, power off, power on. It resumes, no banner, and
   `Config/starting.txt` is gone.
2. Simulated crash, safe (no real crash needed): seat a game, play over 5 seconds, then over ssh
   `kill -9 $(pidof slot)` within 5 seconds of the next start (power on, and kill while it is
   loading or in its first seconds). Restart slot (or reboot). The shelf shows with that cart
   selected and the "Last start failed" banner; `grep 'start guard' Logs/*` shows the line;
   the resume state file under `States/<SYS>/<core>/<stem>/resume.state` is still there.
   Alternatively write the mark by hand: `printf 'GBA/<stem>\n' > Config/starting.txt` with
   that cart seated, then reboot.
3. From that shelf, tap A: the game resumes as before; after 5 seconds the mark is gone.

## References
- ADR 0047
