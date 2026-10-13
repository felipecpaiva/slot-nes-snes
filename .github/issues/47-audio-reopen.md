---
title: "Patch: Stop losing audio when slot reopens the ALSA device"
phase: 5
area: device
type: fix
size: S
depends_on: [39-cross-platform-performance]
---

## Why
The 2026-10-13 device gate failed every title, the GBA reference included, on the 0-underrun rule. slot releases the PCM after 3 s of silence (upstream v1.5.0, against the speaker buzz) and reopens it when sound returns. Measured on the RG34XXSP with a timing build (plug:default, 32768 Hz, 40 ms latency):

- `snd_pcm_open` takes 1 to 4 ms, but `snd_pcm_set_params` takes about 251 ms, at boot and on every reopen.
- The release (`snd_pcm_drop` then `snd_pcm_close`) takes about 242 ms.
- The audio thread blocks in both, the ring holds 133 ms and `push_blocking` waits 50 ms, then the emu's samples are dropped: 8474 samples across one release and another 11150 across the reopen (Battletoads). A game's quiet stretch released the device mid-game, so the first ~170 ms of the sound that came back was lost.
- The starved count (2048 to 4096) is a different cause: the shelf drains the ring dry while the cart is inserted (the emu is paused until the insert ends), so the first fills after play starts are short and the priming hold then holds silence until the ring is half full. All of it is counted as starved.

## Scope
`patches/0021-audio-reopen.patch`:
- [x] New `crates/slot/src/audio/hold.rs`: `Hold` decides whether the device stays open. A ring that grew since the last fill means a game is feeding it, so the device is held, even while the game is silent. With no feed, upstream's 3 s silence rule still releases it (shelf, pause, quick menu, muted fast-forward). Fed means "queue grew", not "queue non-empty", so a queue parked by the priming hold cannot keep the device open.
- [x] `wake_device()`, called when a cart starts loading (`Session::spawn_core`), reopens a released device at once, so the 251 ms open runs during the insert and core load, before the emu is unpaused.
- [x] `prefill_silence(ring)`, called by the emu when it returns to normal speed from pause, rewind or fast-forward (only at normal speed, so upstream's fast-forward audio tests keep their exact counts), tops the ring up with silence to half its capacity, the same cushion upstream's `Ring::reopen` lays down. Half is rounded up, because `fill` holds while the queue is below `buf.len() / 2` samples and `drc_target` is one sample short of that at 32768 Hz.
- [x] Upstream hooks: `alsa.rs` uses `Hold` in place of `Silence` (fill moves into `Hold::listen`) and takes the wake; one line in `session.rs`; three lines in `emu.rs`; `audio/mod.rs` declares and exports.

## Tests
| ID | File | Asserts |
|---|---|---|
| T70 | `slot/src/audio/hold.rs` | a game feeding silence keeps the device open |
| T71 | `slot/src/audio/hold.rs` | with nothing feeding, the device is released after exactly 3 s |
| T72 | `slot/src/audio/hold.rs` | a queue parked by the priming hold still releases |
| T73 | `slot/src/audio/hold.rs` | a wake restarts the 3 s |
| T74 | `slot/src/audio/hold.rs` | after the ring ran dry, prefill then fill counts 0 starved |
| T75 | `slot/src/audio/hold.rs` | prefill never adds to a queue already at half, and drops nothing |
| T76 | `slot/src/audio/hold.rs` | a wake is taken once |

Each test was proved red by breaking the code once: `fed = false` (T70), silence never counted (T71), `fed = queued > 0` (T72), `wake` doing nothing (T73), half rounded down (T74), prefill ignoring the queue (T75), `take_wake` not clearing (T76). Upstream tests stay unmodified.

## Edge cases
| Case | Expected handling |
|---|---|
| Shelf for more than 3 s | Released, as upstream (`audio released after silence`) |
| Paused or quick menu for more than 3 s | Released, as upstream |
| Resume after a pause of more than 3 s, or after more than 3 s of muted fast-forward | Still pays one 251 ms reopen and drops samples: nothing tells the audio thread ahead of the resume. Not measured; follow-up if it shows in play |
| Core fails to load after the wake | No feed, released 3 s later |
| A game silent for minutes | Device stays open; the buzz upstream fixed can return during in-game silence. Not checked by ear |

## Acceptance
- [x] T70 to T76 green.
- [x] rustfmt --check clean on files added or changed.
- [x] `task check` green.
- [x] `docs/UPSTREAM-TOUCHPOINTS.md` regenerated with the new hunks and reasons.
- [x] Device: Battletoads, Super Mario RPG, Kirby's Adventure and Golden Sun at 0 dropped and 0 starved.

## Device check (RG34XXSP)
`task perf:play` style runs, 2 minutes each (`docs/perf/2026-10-13-audio/`), and one scripted shelf run: boot to the shelf, wait 10 s, insert with A, play 30 s, eject. Expect `audio released after silence` on the shelf before the insert and again after the eject, `audio reopened at` during the insert, and `0 samples dropped, 0 starved`. Results in `docs/DEVICE-GATE.md`.

## References
- docs/DECISIONS.md (2026-10-13, audio reopen)
- docs/perf/2026-10-13-gate/ (before), docs/perf/2026-10-13-audio/ (after)
