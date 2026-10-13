# 0030. Keep the ALSA device open while a game feeds the ring

- Status: Accepted
- Date: 2026-10-13
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 47](../../.github/issues/47-audio-reopen.md), [patch 0021](../../patches/0021-audio-reopen.patch), [DEVICE-GATE.md](../DEVICE-GATE.md)

## Context

Measured on the RG34XXSP with plug:default: `snd_pcm_open` 1 to 4 ms, `snd_pcm_set_params` about
251 ms, release (`drop` and `close`) about 242 ms. The audio thread blocks in both while the emu
pushes into a 133 ms ring with a 50 ms push wait, so a release lost 8474 samples and the reopen
another 11150 (Battletoads), and every reopen clipped the first ~170 ms of returning sound. The
2048 to 4096 starved samples per title had another cause: the shelf drains the ring dry while the
cart is inserted and the priming hold counts its silence as starved.

## Decision

slot keeps the ALSA device open while a game feeds the ring (even with silence), reopens it as
soon as a cart starts loading, and tops the ring up with silence to half capacity when play starts
or resumes. The 3 s release still applies on the shelf, in pause and the quick menu, and in muted
fast-forward.

## Consequences

- After the fix Battletoads, Super Mario RPG, Kirby's Adventure and Golden Sun read 0 dropped,
  0 starved.
- Known cost: in-game silence no longer releases the device, so the buzz can return there (not
  checked by ear).
- A resume after more than 3 s of pause still pays one reopen.
