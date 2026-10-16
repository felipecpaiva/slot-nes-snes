# 0030. Keep the ALSA device open while a game feeds the ring

- Status: Accepted
- Date: 2026-10-13, amended 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 47](../../.github/issues/47-audio-reopen.md), [patch 0018](../../patches/0018-audio-reopen.patch), [DEVICE-GATE.md](../DEVICE-GATE.md)

## Context

Measured on the RG34XXSP with plug:default: `snd_pcm_open` 1 to 4 ms, `snd_pcm_set_params` about
251 ms, release (`drop` and `close`) about 242 ms. The audio thread blocks in both while the emu
pushes into a 133 ms ring with a 50 ms push wait, so a release lost 8474 samples and the reopen
another 11150 (Battletoads), and every reopen clipped the first ~170 ms of returning sound. The
2048 to 4096 starved samples per title had another cause: the shelf drains the ring dry while the
cart is inserted and the priming hold counts its silence as starved.

## Decision

slot keeps the ALSA device open while a game feeds the ring (even with silence), reopens it as
soon as a cart starts loading, and tops the ring up with silence to half capacity when the game's
sound starts flowing after a load, a pause or any other speed change (amended 2026-10-15, below). The 3 s release still applies on the shelf, in pause and the quick menu, and in muted
fast-forward.

## Consequences

- After the fix Battletoads, Super Mario RPG, Kirby's Adventure and Golden Sun read 0 dropped,
  0 starved.
- Known cost: in-game silence no longer releases the device, so the buzz can return there (not
  checked by ear).
- A resume after more than 3 s of pause still pays one reopen.

## Amendment 2026-10-15: the cushion starts with the sound

Context. On slot v1.7.0 Super Mario RPG (snes9x) read 2560 starved samples, all before the first
audio trace line, while Battletoads and Golden Sun read 0. The port had moved the top-up to once
before the worker loop, because upstream's `runahead.rs` sound test caught the gate-time top-up
depending on when the worker first saw Normal. Both top-ups ran at a speed change, and both marked
the ring live (`set_idle(false)`) there, but the core's sound only arrives at its first push:
after the worker locks and waits for a display tick, and after the first frame runs. snes9x on an
SA-1 title is slow there, and v1.7.0 also starts a resumed core during boot, so the 66 ms cushion
drained while the ring counted. 2560 is half a period short plus two held 1024-sample periods: a
ring refilled by the game at 1x needs four periods to clear the priming hold, so the hold was
ended by a top-up, which places the starve before the game's first push. A host test that parks
the worker before its first pass, and one that parks the first frame, starved 12014 samples each
on the port and read 0 after the change.

Decision. The worker marks the ring idle from load and on every speed change, and on the first
push of each stretch of play it tops the ring up to half with silence and then marks it live. The
wait for the first frame plays the same silence the cushion held, but no longer spends the
cushion or counts as starved. The top-up is tied to a push, so the amount never depends on which
speed the worker saw first, and upstream's `runahead.rs` stays deterministic (20 of 20 runs).

Consequences.

- The top-up stays at normal speed only, so upstream's fast-forward sound test keeps its exact
  count; fast-forward with sound marks the ring live at its first push without one, and muted
  fast-forward and rewind push nothing and stay idle.
- Tests: `crates/slot/tests/audio_start.rs` (our file, in patch 0018).
- Device check: `task readout:device` starved and dropped on Super Mario RPG, Star Fox,
  Battletoads and Golden Sun, `DATE=2026-10-15-audiostart`.
